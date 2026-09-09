# -*- coding: utf-8 -*-
"""읽기전용 DB 접근 계층 — 접속과 실행만 담당한다. 판정은 guard 가 한다.

접속정보는 생성자로 주입받는다(직접 파일을 읽지 않는다).
"""
from . import guard

# 조회 결과를 담아 돌려주는 형태: (컬럼명 목록, 행 목록, 잘렸는지 여부)
QueryResult = tuple


class DatabaseUnavailable(Exception):
    """DB 에 닿지 못했을 때. 메시지는 비개발자가 읽을 수 있어야 한다."""


def _import_driver():
    """psycopg2 를 늦게 불러온다 — 미설치 시 추적문 대신 안내문을 보여주기 위해."""
    try:
        import psycopg2
        import psycopg2.errors
    except ImportError as error:
        raise DatabaseUnavailable(
            "DB 접속 부품(psycopg2)이 설치돼 있지 않습니다.\n"
            "명령 프롬프트에서 `pip install psycopg2-binary` 를 한 번 실행해 주세요."
        ) from error
    return psycopg2


class ReadOnlyDatabase:
    """konclo 계정으로 조회만 수행하는 얇은 래퍼."""

    CONNECT_TIMEOUT_SECONDS = 10

    def __init__(self, credentials: dict):
        self._credentials = credentials

    def _connect(self):
        psycopg2 = _import_driver()
        session_options = (
            f"-c statement_timeout={guard.STATEMENT_TIMEOUT_MS} "
            "-c default_transaction_read_only=on"
        )
        try:
            connection = psycopg2.connect(
                host=self._credentials["host"],
                port=self._credentials["port"],
                dbname=self._credentials["dbname"],
                user=self._credentials["user"],
                password=self._credentials["password"],
                connect_timeout=self.CONNECT_TIMEOUT_SECONDS,
                options=session_options,
            )
        except psycopg2.OperationalError as error:
            raise DatabaseUnavailable(self._explain_connection_failure(error)) from error
        connection.set_session(readonly=True)
        return connection

    @staticmethod
    def _explain_connection_failure(error: Exception) -> str:
        """psycopg2 오류를 비개발자가 조치할 수 있는 문장으로 바꾼다."""
        detail = str(error).strip()
        lowered = detail.lower()
        if "password authentication failed" in lowered or "authentication" in lowered:
            return (
                "아이디 또는 비밀번호가 맞지 않습니다. "
                "`/konclo-db-setup` 으로 다시 등록해 주세요."
            )
        if "does not exist" in lowered:
            return (
                "그런 이름의 데이터베이스가 없습니다. "
                "`/konclo-db-setup` 에서 DB 이름을 확인해 주세요."
            )
        if "timeout" in lowered or "could not connect" in lowered or "refused" in lowered:
            return (
                "DB 서버에 연결하지 못했습니다. Tailscale(회사망)이 켜져 있는지 "
                f"확인해 주세요.\n(원문: {detail})"
            )
        return f"DB 연결에 실패했습니다.\n(원문: {detail})"

    def _run(self, statement: str, parameters=None, max_rows: int = None):
        """내부 공통 실행기 — (컬럼, 행, 잘림여부) 를 돌려준다."""
        psycopg2 = _import_driver()
        row_limit = guard.clamp_row_limit(max_rows)
        connection = self._connect()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute(statement, parameters)
            except psycopg2.errors.QueryCanceled as error:
                timeout_seconds = guard.STATEMENT_TIMEOUT_MS // 1000
                raise DatabaseUnavailable(
                    f"조회가 {timeout_seconds}초를 넘어 중단됐습니다 — "
                    "기간이나 조건을 좁혀 다시 시도해 주세요."
                ) from error
            except psycopg2.Error as error:
                raise DatabaseUnavailable(
                    f"조회를 실행하지 못했습니다.\n(원문: {str(error).strip()})"
                ) from error

            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchmany(row_limit + 1)
            was_truncated = len(rows) > row_limit
            return columns, rows[:row_limit], was_truncated
        finally:
            connection.close()

    def run_select(self, sql: str, max_rows: int = None):
        """가드를 통과한 조회만 실행한다."""
        statement = guard.validate_select(sql)
        return self._run(statement, max_rows=max_rows)

    def list_tables(self, schema: str = "public"):
        """스키마 안의 표 목록."""
        statement = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        return self._run(statement, (schema,))

    def describe_table(self, table_name: str, schema: str = "public"):
        """표 하나의 컬럼 구조."""
        if not (table_name or "").strip():
            raise DatabaseUnavailable("표 이름이 비어 있습니다.")
        statement = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """
        return self._run(statement, (schema, table_name.strip()))

    def check_connection(self) -> str:
        """연결 확인용 최소 조회. 성공하면 서버 버전 요약을 돌려준다."""
        _, rows, _ = self._run("SELECT current_database(), current_user, version()")
        if not rows:
            raise DatabaseUnavailable("DB 가 응답했지만 결과가 비어 있습니다.")
        database_name, user_name, version_text = rows[0]
        short_version = str(version_text).split(",")[0]
        return f"{database_name} / {user_name} / {short_version}"
