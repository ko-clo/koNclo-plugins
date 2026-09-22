---
name: order-audit
description: Use when 생성된 매장별 주문장(.xls)의 이상 데이터를 점검하거나 주문수량 산식을 역추적하거나 빌드/시스템 간 산출물을 비교할 때. 트리거 — "주문장 검수", "주문장 점검", "이 수량 왜 이래", "주문장 이상치", "주문장 비교", "왜 1장만". (주문장을 새로 생성하지 않는 읽기 전용 점검 — 생성은 order-cycle 소관)
---

# 주문장 검수 스킬

**목적**: 이미 생성된 주문장(.xls)에서 *잘못된/의심스러운 데이터*를 찾고, 특정 품목의
주문수량이 **왜 그 값으로 나왔는지** 산식을 역추적한다. 주문장을 새로 만들지 않는다.

**필독(맥락)**: `domain/order.md` · `domain/order-feedback.md` · `service/order-architecture.md`
**관련 스킬**: 생성은 `order-cycle`(자동) / `/order-manual`(수동). 본 스킬은 *검수만*.

---

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/order-audit/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/anomalies.md` |  | 이상치를 판정할 때 |
| `references/formula.md` |  | 수량을 역추적할 때 |
| `references/procedure.md` |  | 검수를 진행할 때 |
| `references/systems.md` |  | 어느 산출물인지 가릴 때 |

## 검수 도구 (읽기 전용)

`backend/scripts/audit_order_xls.py` — DB·NAS 없이 .xls + 비고(2w/점수/상태/태그)만으로 검증.
현재고는 .xls 에 없으므로 주문 산식에서 **역산한 추정값**으로 표시한다.

```bash
# 1) 이상치 스캔 (폴더 또는 단일 파일)
python3 backend/scripts/audit_order_xls.py scan <폴더|파일> [--store 09]

# 2) 특정 품목 주문수량 산식 역추적
python3 backend/scripts/audit_order_xls.py explain <파일> --product 레시피반팔 [--color 스카이]

# 3) 두 산출물(빌드/시스템) 동일 품목 비교
python3 backend/scripts/audit_order_xls.py compare <파일A> <파일B> [--product 레시피반팔]
```

산출물 위치(로컬 마운트): `/Volumes/자동주문/cache/주문장_업로드/주문장_YYYYMMDD/*.xls`

---

## 주문수량 산식 (검수 기준)

→ `references/formula.md`.

## 알려진 이상 패턴 (검수 체크리스트)

→ `references/anomalies.md`.

## 시스템 구분 (혼동 주의)

→ `references/systems.md`.

## 검수 절차

→ `references/procedure.md`.

## 절대 원칙

- **읽기 전용** — 주문장 재생성·운영 DB 변경 금지. 생성이 필요하면 `order-cycle`/`/order-manual`.
- 검수 스크립트 상수(안전재고 테이블·상위5% 산식)는 `order_v8_2`/`auto_order_db` 와 항상 동기화.
- 새 이상 패턴은 위 체크리스트에 누적.
