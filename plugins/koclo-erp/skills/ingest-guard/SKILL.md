---
name: ingest-guard
description: Use when 새 인입 경로(CSV/XLSX→DB)에 포맷 방어로직을 붙일 때, 고정 컬럼 인덱스 파서가 컬럼 밀림이나 다른 양식을 에러 없이 인입해 잘못된 데이터가 저장됐을 때, 또는 정상 파일이 포맷 검사에 막혀 인입이 멈췄을 때. 트리거 — "포맷 검증", "인입 방어", "format guard", "잘못된 데이터 저장", "컬럼 밀림", "ingest 검증", "다른 인입에도 적용".
---

# 인입 포맷 방어로직(format guard) 표준

**목적**: 외부에서 받은 파일(CSV/XLSX)을 DB로 인입하기 전에 **양식 구조를 빠르게 검증**해,
잘못된 양식이 그대로 인입돼 **잘못된 데이터가 저장되는 사고를 차단**한다.
(데이터타입·셀 단위 정합은 차단 대상이 아니다 — §2 참고.)

**정본 구현(레퍼런스)**: `backend/scripts/ingest_format_validator.py` + `ingest_incremental.py` 의 가드 연결.
새 인입 경로에 적용할 때 이 구조를 **그대로 복제**한다.

---

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/ingest-guard/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/background.md` | §1 · §6 | 왜 필요한지 · 같은 실수를 되풀이할 때 |
| `references/checklist.md` | §3 | 새 인입 경로에 붙일 때 |
| `references/pattern.md` | §2 | 검증기를 작성하기 전 |
| `references/rules.md` | §4 | 방어로직을 쓰는 내내 |

## 1. 막으려는 실패 모드 (왜 필요한가)

→ `references/background.md`.

## 2. 방어 패턴 4요소 (반드시 모두 갖춘다)

→ `references/pattern.md`.

## 3. 새 인입 경로에 적용하는 절차 (체크리스트)

→ `references/checklist.md`.

## 4. 핵심 규칙 (어기면 방어로직이 무의미)

→ `references/rules.md`.

## 5. 검증·실행

```bash
# 단일 파일 포맷만 점검(인입 안 함, DB 미접근)
python3 ingest_incremental.py --check --file /path/증분사입흐름_YYYYMMDD_오늘.csv
# 미처리 신규 파일 전부 점검
python3 ingest_incremental.py --check
# 단위 테스트(독립 실행) — 레포에 두지 않는다. scratchpad 에 만든 스크립트를 backend/ 에서 돌린다
PYTHONPATH=. python3 <scratchpad>/test_<대상>_validator.py
```

검증기 import 에 DB DSN 환경변수가 필요하면 더미로 채운다(`--check`/테스트는 DB 미접근):
`export KOCLO_ERP_DB_DSN="host=localhost port=5432 dbname=x user=x password=x"`.

---

## 6. 함정 (반복 실수)

→ `references/background.md`.

## 관련

- 정본 구현: `backend/scripts/ingest_format_validator.py`, `ingest_incremental.py`(가드/`--check`).
  (옛 테스트 선례 `test_ingest_format_validator.py` 는 `ed9427d` 에서 레포에서 빠졌다 — `git show ed9427d^:backend/scripts/test_ingest_format_validator.py` 로 패턴을 볼 수 있다.)
- 인입 파이프라인 맥락: `/order-cycle`, `/order-manual`, `db-sync`.
- 배포: backend/scripts 는 바인드마운트 → NAS `git pull` 로 반영(승인 필요, 임의 배포 금지).
