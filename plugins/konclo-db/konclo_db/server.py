# -*- coding: utf-8 -*-
"""KONCLO DB 조회 MCP 서버 — Claude / Codex 에 조회 도구를 노출한다.

여기서는 도구를 정의하고 결과를 전달하기만 한다. 접속정보는 config,
허용 판정은 guard, 실행은 db, 출력 형태는 render 가 맡는다.
"""
import asyncio
import functools
import os
import sys

from . import config, db, guard, render

SERVER_NAME = "konclo-db"

# 저장 파일이 흩어지지 않도록 한 폴더로 모은다.
EXPORT_DIRNAME = "KONCLO-DB조회"

SERVER_INSTRUCTIONS = (
    "KO&CLO 기획팀용 읽기전용 DB 조회 도구다. 사용자는 개발을 모르므로 "
    "SQL·테이블·컬럼 같은 용어 대신 표와 쉬운 한국어로 답한다. "
    "컬럼명을 추측하지 말고 describe_table 로 먼저 확인한다."
)


def _find_desktop_directory() -> str:
    """바탕화면 폴더를 찾는다. 못 찾으면 홈 폴더를 돌려준다.

    한국어 Windows 는 바탕화면 폴더 이름이 'Desktop' 이 아니고(`바탕 화면`),
    회사 PC 는 OneDrive 로 리디렉션돼 있는 경우가 흔하다. 'Desktop' 하나만
    보면 저장 파일이 홈 폴더로 떨어져 사용자가 찾지 못한다.
    """
    home = os.path.expanduser("~")
    onedrive = os.environ.get("OneDrive") or os.environ.get("ONEDRIVE") or ""

    candidates = []
    for base in (onedrive, home):
        if not base:
            continue
        for folder_name in ("Desktop", "바탕 화면", "바탕화면"):
            candidates.append(os.path.join(base, folder_name))
    candidates.append(os.path.join(home, "OneDrive", "Desktop"))

    for candidate in candidates:
        if os.path.isdir(candidate):
            return candidate
    return home


def _resolve_export_directory() -> str:
    """저장 폴더 — 바탕화면 아래 전용 폴더."""
    return os.path.join(_find_desktop_directory(), EXPORT_DIRNAME)


def _safe_export_path(filename: str) -> str:
    """파일명만 받아 저장 폴더 안의 경로로 만든다 (경로 이탈 차단)."""
    bare_name = os.path.basename((filename or "").strip())
    if not bare_name:
        bare_name = "결과.csv"
    if not bare_name.lower().endswith(".csv"):
        bare_name += ".csv"
    directory = _resolve_export_directory()
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, bare_name)


def _open_database() -> db.ReadOnlyDatabase:
    return db.ReadOnlyDatabase(config.load_credentials())


# ─── 도구 본체 (MCP 와 무관한 순수 함수 — 그대로 테스트할 수 있다) ───

def run_check_connection() -> str:
    summary = _open_database().check_connection()
    return f"✅ DB 에 정상 연결됩니다.\n{summary}"


def run_list_tables(schema: str = "public") -> str:
    _, rows, _ = _open_database().list_tables(schema)
    names = [row[0] for row in rows]
    if not names:
        return f"'{schema}' 안에 표가 없습니다."
    return f"표 {len(names)}개:\n" + "\n".join(f"- {name}" for name in names)


def run_describe_table(table_name: str, schema: str = "public") -> str:
    columns, rows, _ = _open_database().describe_table(table_name, schema)
    if not rows:
        return f"'{table_name}' 이라는 표를 찾지 못했습니다."
    return f"### {table_name}\n" + render.to_markdown_table(columns, rows)


def run_query(sql: str, max_rows: int = None) -> str:
    row_limit = guard.clamp_row_limit(max_rows)
    columns, rows, was_truncated = _open_database().run_select(sql, max_rows=row_limit)
    table = render.to_markdown_table(columns, rows)
    summary = render.describe_result(columns, rows, was_truncated, row_limit)
    return f"{table}\n\n{summary}"


def run_export(sql: str, filename: str, max_rows: int = None) -> str:
    row_limit = guard.clamp_row_limit(max_rows)
    columns, rows, was_truncated = _open_database().run_select(sql, max_rows=row_limit)
    target_path = _safe_export_path(filename)
    with open(target_path, "w", newline="", encoding="utf-8") as handle:
        handle.write(render.to_csv_text(columns, rows))
    message = f"📁 저장했습니다: {target_path}\n{len(rows)}행 — 엑셀로 바로 열 수 있습니다."
    if was_truncated:
        message += f"\n⚠ {row_limit}행 상한에서 잘렸습니다 — 조건을 좁혀 다시 저장해 주세요."
    return message


def _explain(error: Exception) -> str:
    """예외를 비개발자가 읽을 수 있는 한 문단으로. 추적문을 노출하지 않는다."""
    if isinstance(error, config.CredentialsError):
        return f"⚙️ {error}"
    if isinstance(error, guard.QueryRejected):
        return f"🚫 {error}"
    if isinstance(error, db.DatabaseUnavailable):
        return f"⚠️ {error}"
    return f"예상하지 못한 오류가 발생했습니다: {type(error).__name__}: {error}"


def _as_tool(function):
    """동기 함수를 MCP 도구로 감싼다 — 스레드로 넘기고 오류를 문장으로 바꾼다.

    조회는 블로킹 I/O 라 이벤트 루프에서 직접 돌리면 서버가 멈춘다.
    """
    @functools.wraps(function)
    async def wrapper(*args, **kwargs):
        try:
            return await asyncio.to_thread(function, *args, **kwargs)
        except Exception as error:  # 어떤 오류도 세션을 죽이지 않는다
            return _explain(error)
    return wrapper


def _read_only_annotations(title: str):
    """DB 를 읽기만 하는 도구임을 호스트에 알린다.

    호스트(Claude 데스크톱 앱 등)는 이 힌트를 보고 승인 절차를 얼마나 걸지 정한다.
    계정 자체가 읽기전용이고 guard 가 SELECT 만 통과시키므로 사실과 일치한다.
    """
    from mcp.types import ToolAnnotations

    return ToolAnnotations(
        title=title,
        readOnlyHint=True,       # 어떤 데이터도 바꾸지 않는다
        destructiveHint=False,   # 지우거나 덮어쓰지 않는다
        idempotentHint=True,     # 같은 요청을 반복해도 결과가 같다
        openWorldHint=False,     # 정해진 DB 한 곳만 본다
    )


def _file_writing_annotations(title: str):
    """DB 는 읽기만 하지만 **로컬에 파일을 쓴다**.

    readOnlyHint 를 참으로 두면 호스트가 파일 덮어쓰기를 조용히 승인할 수 있으므로
    거짓으로 둔다 — 힌트는 사실대로 적어야 의미가 있다.
    """
    from mcp.types import ToolAnnotations

    return ToolAnnotations(
        title=title,
        readOnlyHint=False,      # 저장 폴더에 CSV 를 만든다
        destructiveHint=False,   # 같은 이름이 있으면 덮어쓰지만 DB 는 건드리지 않는다
        idempotentHint=True,
        openWorldHint=False,
    )


def build_server():
    """MCP 서버 인스턴스. 도구 스키마는 타입힌트와 설명문에서 자동 생성된다."""
    from mcp.server.mcpserver import MCPServer

    server = MCPServer(name=SERVER_NAME, instructions=SERVER_INSTRUCTIONS)

    server.tool(
        name="check_connection",
        description="DB 에 연결되는지 확인한다. 설정 직후나 오류 진단에 쓴다.",
        annotations=_read_only_annotations("연결 확인"),
    )(_as_tool(run_check_connection))

    server.tool(
        name="list_tables",
        description="조회할 수 있는 표(테이블) 목록을 돌려준다.",
        annotations=_read_only_annotations("표 목록"),
    )(_as_tool(run_list_tables))

    server.tool(
        name="describe_table",
        description=(
            "표 하나의 항목(컬럼) 구조를 돌려준다. "
            "컬럼 이름을 추측하지 말고 반드시 이 도구로 먼저 확인한다."
        ),
        annotations=_read_only_annotations("표 구조 보기"),
    )(_as_tool(run_describe_table))

    server.tool(
        name="run_select",
        description=(
            "조회(SELECT 또는 WITH)를 실행하고 결과를 표로 돌려준다. "
            f"30초·{guard.MAX_ROWS}행 상한이 걸려 있고 데이터 변경은 불가능하다."
        ),
        annotations=_read_only_annotations("조회 실행"),
    )(_as_tool(run_query))

    server.tool(
        name="export_csv",
        description=(
            "조회 결과를 CSV 파일로 저장한다(엑셀에서 바로 열림). "
            "사용자가 '엑셀로 저장해줘' 라고 하면 이 도구를 쓴다."
        ),
        annotations=_file_writing_annotations("엑셀(CSV)로 저장"),
    )(_as_tool(run_export))

    return server


def main() -> None:
    try:
        from mcp.server.mcpserver import MCPServer  # noqa: F401
    except ImportError:
        print(
            "MCP 부품이 설치돼 있지 않거나 버전이 맞지 않습니다. "
            "명령 프롬프트에서 `pip install --upgrade \"mcp>=2\" psycopg2-binary` 를 "
            "실행해 주세요.",
            file=sys.stderr,
        )
        sys.exit(1)
    build_server().run("stdio")


if __name__ == "__main__":
    main()
