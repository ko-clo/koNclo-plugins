# -*- coding: utf-8 -*-
"""DB 접속정보 등록 — 한 번 실행해 두면 이후 모든 세션이 자동 연결된다.

사용 (권장 — 비밀번호가 화면·기록에 남지 않는다):
    konclo-db-setup

사용 (자동화):
    konclo-db-setup --dbname testerp --user konclo --password-stdin
    konclo-db-setup --check          # 등록된 정보로 연결만 확인
"""
import argparse
import getpass
import sys

from . import config, db


def _prompt_credentials(defaults: dict) -> tuple:
    """대화형 입력. 비밀번호는 화면에 찍지 않는다."""
    print("KONCLO DB 조회 — 접속정보를 등록합니다.")
    print("(개발팀에서 받은 값을 그대로 입력하세요. 엔터만 치면 [] 안의 값이 쓰입니다.)\n")

    default_dbname = defaults.get("dbname", "testerp")
    default_user = defaults.get("user", "")

    dbname = input(f"DB 이름 [{default_dbname}]: ").strip() or default_dbname
    user_prompt = f"사용자 이름 [{default_user}]: " if default_user else "사용자 이름: "
    user = input(user_prompt).strip() or default_user
    password = getpass.getpass("비밀번호 (입력해도 화면에 보이지 않습니다): ")
    return dbname, user, password


def _read_password(arguments) -> str:
    if arguments.password_stdin:
        return sys.stdin.read().rstrip("\n")
    if arguments.password is not None:
        return arguments.password
    return getpass.getpass("비밀번호 (입력해도 화면에 보이지 않습니다): ")


def _verify_and_report(credentials_path: str) -> int:
    """등록 직후 실제로 연결되는지 확인한다 — 저장 성공은 연결 성공이 아니다."""
    print(f"\n저장했습니다: {credentials_path}")
    print("연결을 확인하는 중...")
    try:
        summary = db.ReadOnlyDatabase(config.load_credentials()).check_connection()
    except (config.CredentialsError, db.DatabaseUnavailable) as error:
        print(f"\n❌ 연결에 실패했습니다.\n{error}", file=sys.stderr)
        print("\n값을 확인한 뒤 이 명령을 다시 실행해 주세요.", file=sys.stderr)
        return 1
    print(f"\n✅ 연결 성공 — {summary}")
    print("이제 Claude 나 Codex 에서 바로 질문하시면 됩니다.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="KONCLO DB 조회 접속정보를 등록한다.")
    parser.add_argument("--dbname", help="DB 이름 (예: testerp)")
    parser.add_argument("--user", help="사용자 이름 (예: konclo)")
    parser.add_argument("--password", help="비밀번호 (권장하지 않음 — 기록에 남는다)")
    parser.add_argument("--password-stdin", action="store_true",
                        help="비밀번호를 표준입력으로 받는다")
    parser.add_argument("--host", default=config.DEFAULT_HOST,
                        help=f"DB 서버 주소 (기본 {config.DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=config.DEFAULT_PORT,
                        help=f"포트 (기본 {config.DEFAULT_PORT})")
    parser.add_argument("--check", action="store_true",
                        help="등록된 정보로 연결만 확인하고 끝낸다")
    arguments = parser.parse_args()

    if arguments.check:
        try:
            summary = db.ReadOnlyDatabase(config.load_credentials()).check_connection()
        except (config.CredentialsError, db.DatabaseUnavailable) as error:
            print(f"❌ {error}", file=sys.stderr)
            return 1
        print(f"✅ 연결 성공 — {summary}")
        return 0

    # 이미 등록된 값이 있으면 기본값으로 재사용한다(비밀번호는 재사용하지 않는다).
    try:
        existing = config.load_credentials()
    except config.CredentialsError:
        existing = {}

    if arguments.dbname and arguments.user:
        dbname, user = arguments.dbname, arguments.user
        password = _read_password(arguments)
    else:
        dbname, user, password = _prompt_credentials(existing)

    try:
        credentials_path = config.save_credentials(
            dbname=dbname, user=user, password=password,
            host=arguments.host, port=arguments.port,
        )
    except config.CredentialsError as error:
        print(f"❌ {error}", file=sys.stderr)
        return 1

    return _verify_and_report(credentials_path)


if __name__ == "__main__":
    sys.exit(main())
