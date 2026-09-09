# -*- coding: utf-8 -*-
"""조회 가드 — 무엇을 실행해도 되는지 판정한다. DB 접속을 알지 못한다.

기존 기획팀 통로(`query.py`)와 같은 규칙을 쓴다. 규칙을 바꿀 일이 생기면
여기 한 곳만 고친다.
"""
import re

# ─── 부하 방어 상한 (서버에 시간제한이 없어 클라이언트가 건다) ───
STATEMENT_TIMEOUT_MS = 30_000   # 쿼리 1건 최대 30초
MAX_ROWS = 5_000                # 결과 최대 행수

# 갱신이 중단된 테이블 — 조회는 되지만 데이터가 낡아 업무 판단에 쓰면 안 된다.
STALE_TABLE_PREFIXES = ("trade_ledger", "sales_data", "purchase_data", "bak_")

# 조회로 인정하는 시작 키워드.
_READ_ONLY_STATEMENT_RE = re.compile(r"^(select|with)\b", re.IGNORECASE | re.DOTALL)


class QueryRejected(Exception):
    """가드가 거부한 요청. 메시지는 비개발자가 읽을 수 있어야 한다."""


def normalize_sql(sql: str) -> str:
    """앞뒤 공백과 끝의 세미콜론 하나를 떼어 낸 실행용 문장."""
    return (sql or "").strip().rstrip(";").strip()


def validate_select(sql: str) -> str:
    """조회 문장만 통과시키고, 정규화된 SQL 을 돌려준다.

    Raises: QueryRejected — 조회가 아니거나, 여러 문장이거나, 금지 테이블을 건드릴 때.
    """
    statement = normalize_sql(sql)

    if not statement:
        raise QueryRejected("실행할 조회 내용이 없습니다.")

    if not _READ_ONLY_STATEMENT_RE.match(statement):
        raise QueryRejected(
            "조회(SELECT)만 실행할 수 있습니다 — "
            "데이터를 바꾸거나 지우는 명령은 이 통로로 불가능합니다."
        )

    if ";" in statement:
        raise QueryRejected("한 번에 한 가지만 조회할 수 있습니다.")

    lowered = statement.lower()
    for table_prefix in STALE_TABLE_PREFIXES:
        if re.search(r"\b" + re.escape(table_prefix), lowered):
            raise QueryRejected(
                f"'{table_prefix}' 는 갱신이 멈춘 낡은 데이터라 사용할 수 없습니다. "
                "다른 표를 써 주세요."
            )

    return statement


def clamp_row_limit(requested_limit) -> int:
    """요청한 행수를 1 ~ MAX_ROWS 범위로 자른다. 값이 없으면 상한을 쓴다."""
    if requested_limit is None:
        return MAX_ROWS
    try:
        limit = int(requested_limit)
    except (TypeError, ValueError):
        return MAX_ROWS
    if limit < 1:
        return 1
    return min(limit, MAX_ROWS)
