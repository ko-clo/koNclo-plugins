# -*- coding: utf-8 -*-
"""접속정보 로드 — 자격증명은 오직 사용자 홈의 설정 파일 한 곳에서만 읽는다.

플러그인 코드·공유 폴더·저장소 어디에도 비밀번호를 두지 않는다. 설정 파일은
`konclo-db-setup` 이 소유자 전용(0600) 권한으로 만들어 준다.
"""
import os
import stat

# 서버 위치는 기획팀이 입력할 필요가 없어 기본값으로 굳힌다.
# (사용자는 dbname·user·password 만 입력한다. 다른 서버를 봐야 하면 설정 파일에
#  PGHOST·PGPORT 를 적어 덮어쓸 수 있다.)
#
# ★ 이 주소는 NAS 다. 운영 서빙은 koclo-vm 이지만, 기획팀 조회 대상은
#   NAS 로 두는 것이 사용자 결정이다(2026-09-09). 운영 DB 에 조회 부하를
#   얹지 않기 위한 선택이므로 "운영이 아니니 고쳐야 한다"고 바꾸지 말 것.
#   바꿔야 할 이유가 생기면 반드시 사용자에게 먼저 확인한다.
DEFAULT_HOST = "100.99.51.88"
DEFAULT_PORT = 5434

CREDENTIALS_DIRNAME = ".koandclo"
CREDENTIALS_FILENAME = "konclo-db.env"

# 설정 파일 경로를 옮기고 싶을 때 쓰는 환경변수 (테스트·다중 프로필용).
CREDENTIALS_PATH_ENV = "KONCLO_DB_ENV"

REQUIRED_KEYS = ("PGDATABASE", "PGUSER", "PGPASSWORD")

# 데스크톱 확장(.mcpb)은 설치 화면에서 받은 값을 환경변수로 넘겨준다.
# 표준 PG* 이름을 쓰면 사용자 PC 에 이미 있는 값과 섞일 수 있어 접두사를 붙였다.
ENV_CREDENTIAL_KEYS = {
    "dbname": "KONCLO_DB_NAME",
    "user": "KONCLO_DB_USER",
    "password": "KONCLO_DB_PASSWORD",
    "host": "KONCLO_DB_HOST",
    "port": "KONCLO_DB_PORT",
}


class CredentialsError(Exception):
    """접속정보를 읽을 수 없을 때. 메시지는 비개발자가 읽을 수 있어야 한다."""


def resolve_credentials_path() -> str:
    """설정 파일의 절대 경로. 환경변수 지정이 있으면 그것을 우선한다."""
    override = os.environ.get(CREDENTIALS_PATH_ENV)
    if override:
        return os.path.abspath(os.path.expanduser(override))
    home = os.path.expanduser("~")
    return os.path.join(home, CREDENTIALS_DIRNAME, CREDENTIALS_FILENAME)


def parse_env_text(text: str) -> dict:
    """KEY=값 형식의 텍스트를 딕셔너리로. 빈 줄과 `#` 주석은 건너뛴다."""
    values = {}
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise CredentialsError(
                f"접속정보 파일 {line_number}번째 줄의 형식이 잘못됐습니다 "
                f"(`이름=값` 형태여야 합니다): {line!r}"
            )
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_credentials_from_env(environment: dict = None) -> dict:
    """환경변수에서 연결 인자를 만든다. 필수값이 하나라도 없으면 None.

    데스크톱 확장(.mcpb)이 설치 화면 입력값을 이 경로로 넘긴다.
    """
    source = environment if environment is not None else os.environ

    dbname = (source.get(ENV_CREDENTIAL_KEYS["dbname"]) or "").strip()
    user = (source.get(ENV_CREDENTIAL_KEYS["user"]) or "").strip()
    password = source.get(ENV_CREDENTIAL_KEYS["password"]) or ""
    if not (dbname and user and password):
        return None

    port_text = (source.get(ENV_CREDENTIAL_KEYS["port"]) or "").strip()
    try:
        port = int(port_text) if port_text else DEFAULT_PORT
    except ValueError as error:
        raise CredentialsError(
            f"포트는 숫자여야 합니다 (지금 값: {port_text!r})"
        ) from error

    return {
        "host": (source.get(ENV_CREDENTIAL_KEYS["host"]) or "").strip() or DEFAULT_HOST,
        "port": port,
        "dbname": dbname,
        "user": user,
        "password": password,
    }


def load_credentials(path: str = None) -> dict:
    """연결 인자를 만든다 — 환경변수가 먼저, 없으면 설정 파일.

    환경변수 경로는 데스크톱 확장(.mcpb), 파일 경로는 Claude Code 플러그인이 쓴다.

    Returns: {"host", "port", "dbname", "user", "password"}
    Raises: CredentialsError — 어느 쪽에서도 읽지 못했을 때.
    """
    if path is None:
        from_environment = load_credentials_from_env()
        if from_environment is not None:
            return from_environment

    credentials_path = path or resolve_credentials_path()

    if not os.path.exists(credentials_path):
        raise CredentialsError(
            "DB 접속정보가 아직 등록되지 않았습니다.\n"
            "· Claude 데스크톱 앱: 설정 → 확장 → KONCLO DB 조회 에서 "
            "DB 이름·아이디·비밀번호를 입력해 주세요.\n"
            "· Claude Code / Codex: `DB 연결 설정해줘` 라고 말하거나 "
            "`/konclo-db-setup` 을 실행해 주세요."
        )

    try:
        with open(credentials_path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as error:
        raise CredentialsError(
            f"접속정보 파일을 열 수 없습니다: {credentials_path} ({error})"
        ) from error

    values = parse_env_text(text)

    missing = [key for key in REQUIRED_KEYS if not values.get(key)]
    if missing:
        raise CredentialsError(
            f"접속정보에 {', '.join(missing)} 항목이 비어 있습니다. "
            "`/konclo-db-setup` 으로 다시 등록해 주세요."
        )

    port_text = values.get("PGPORT") or str(DEFAULT_PORT)
    try:
        port = int(port_text)
    except ValueError as error:
        raise CredentialsError(
            f"PGPORT 는 숫자여야 합니다 (지금 값: {port_text!r})"
        ) from error

    return {
        "host": values.get("PGHOST") or DEFAULT_HOST,
        "port": port,
        "dbname": values["PGDATABASE"],
        "user": values["PGUSER"],
        "password": values["PGPASSWORD"],
    }


def save_credentials(dbname: str, user: str, password: str,
                     host: str = DEFAULT_HOST, port: int = DEFAULT_PORT,
                     path: str = None) -> str:
    """접속정보를 소유자 전용(0600) 파일로 저장하고 경로를 돌려준다."""
    for label, value in (("dbname", dbname), ("user", user), ("password", password)):
        if not str(value).strip():
            raise CredentialsError(f"{label} 이(가) 비어 있습니다.")

    credentials_path = path or resolve_credentials_path()
    parent = os.path.dirname(credentials_path)
    os.makedirs(parent, exist_ok=True)

    lines = [
        "# KONCLO DB 조회 접속정보 — 이 파일 밖 어디에도 비밀번호를 두지 마세요.",
        "# 이 파일은 공유 폴더(예: NAS 드라이브)에 복사하면 안 됩니다.",
        f"PGHOST={host}",
        f"PGPORT={int(port)}",
        f"PGDATABASE={dbname.strip()}",
        f"PGUSER={user.strip()}",
        f"PGPASSWORD={password}",
        "",
    ]

    # 먼저 0600 으로 만들고 쓴다 — 잠깐이라도 남이 읽을 수 있는 창을 두지 않는다.
    file_descriptor = os.open(
        credentials_path,
        os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
        stat.S_IRUSR | stat.S_IWUSR,
    )
    with os.fdopen(file_descriptor, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    # 이미 존재하던 파일이면 os.open 이 권한을 바꾸지 않으므로 명시적으로 조인다.
    try:
        os.chmod(credentials_path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        # Windows 는 POSIX 권한이 없다 — 저장 자체는 성공했으므로 계속 진행한다.
        pass

    return credentials_path
