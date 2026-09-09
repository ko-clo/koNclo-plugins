# -*- coding: utf-8 -*-
"""조회 결과를 사람이 읽는 형태로 바꾼다. DB 도 MCP 도 알지 못한다."""
import csv
import io

# 표가 이보다 길면 화면에 다 뿌리지 않고 앞부분만 보여 준다.
PREVIEW_ROW_LIMIT = 50


def _cell_to_text(value) -> str:
    if value is None:
        return ""
    return str(value)


def to_markdown_table(columns, rows, preview_limit: int = PREVIEW_ROW_LIMIT) -> str:
    """마크다운 표. 행이 많으면 앞부분만 보여 주고 남은 수를 알린다."""
    if not columns:
        return "(결과 없음)"
    if not rows:
        return "조건에 맞는 자료가 없습니다."

    shown_rows = rows[:preview_limit]
    header = "| " + " | ".join(str(column) for column in columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = [
        "| " + " | ".join(_cell_to_text(cell) for cell in row) + " |"
        for row in shown_rows
    ]

    lines = [header, separator, *body]
    hidden_count = len(rows) - len(shown_rows)
    if hidden_count > 0:
        lines.append("")
        lines.append(f"_위 {len(shown_rows)}행만 표시했습니다. (조회된 전체 {len(rows)}행)_")
    return "\n".join(lines)


def to_csv_text(columns, rows) -> str:
    """엑셀에서 한글이 깨지지 않도록 BOM 을 붙인 CSV 문자열."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(columns)
    writer.writerows(rows)
    # utf-8-sig 의 BOM 을 직접 붙인다 — 호출부가 그대로 파일에 쓰면 엑셀이 한글을 읽는다.
    return "﻿" + buffer.getvalue()


def describe_result(columns, rows, was_truncated: bool, row_limit: int) -> str:
    """표 아래에 붙일 요약 한 줄."""
    summary = f"조회 결과 {len(rows)}행 · {len(columns)}개 항목"
    if was_truncated:
        summary += (
            f"\n⚠ 결과가 {row_limit}행 상한에서 잘렸습니다 — "
            "기간이나 조건을 좁혀 다시 조회해 주세요."
        )
    return summary
