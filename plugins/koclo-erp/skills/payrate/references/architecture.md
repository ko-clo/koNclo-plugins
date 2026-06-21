---
name: 지급율 관리 탭 아키텍처
description: 지급율 탭의 Vue 파일·API 엔드포인트·DB 테이블·응답 키·데이터 흐름 매핑. 지급율 탭 작업 시 무엇을 어디서 고칠지 판단하는 구조도. 새 지급율 작업 전 항상 참조.
type: reference
---

# 지급율 관리 탭 — 아키텍처

블루프린트 표준 탭(iframe 제거, DB 직접 쿼리). 계산은 `payrate_service` 위임, 표현은 Vue.
**핵심 특징**: 3개 서브탭이 **단일 API 응답 1개**를 공유 — 백엔드는 하나의 파이프라인, 서브탭은 프론트 view-switch.

## 파일 매핑

### 프론트엔드 (`frontend/js/`)
| 파일 | 역할 |
|---|---|
| `views/PayrateOverviewView.js` | **단일 셸**(811줄) — 3 서브탭을 `activeTab` v-show로 전환. 공통 toolbar(기간/전체기간)·날짜 fetch·포맷터(`fmtPr`/`fmtAmt`/`fmtWon`/`fmtAmtLg`)·밴딩(`prColor`/`prColorGrand`/`prColorSup`) |
| `widgets/PayrateStoreTable.js` | 오버뷰 — 매장별 지급율 표 |
| `widgets/PayrateTrendChart.js` | 주간/주별 추이 차트 — **오버뷰·지급관리 공유** |
| `widgets/PayrateAlertList.js` | 오버뷰 — 역마진/무매출 경보 리스트 |
| `api.js` | `getPayrateOverview(from, to)` |

### 백엔드 (`backend/app/`)
| 파일 | 역할 |
|---|---|
| `routers/payrate_router.py` | `APIRouter(prefix="/api/payrate")` — 1 엔드포인트. `validate_period`로 입력검증(400) 후 service 위임 |
| `services/payrate_service.py` | 지급율 집계 — 분자(지급)/분모(매출) 동일기간, 매장별/성별/주간추이. DB in, dict out |

### 스크립트 (`backend/scripts/`)
| 파일 | 역할 |
|---|---|
| `rebuild_payrate_db.py` | **정본(DB모드, 1575줄)** — SQL·밴딩·물류 분류 이식 출처 |
| `generate_payment_rate_report.py` | 구 파일모드(1499줄) — 오라클/폴백으로 보존(삭제 금지) |

## API 1엔드포인트 → service

| 메서드 · 경로 | service 함수 | 용도 |
|---|---|---|
| `GET /api/payrate/overview?from_date=&to_date=` | `fetch_payrate_overview_via_engine` → `fetch_payrate_overview` | 매장별/합계/성별/주간추이 (3 서브탭 공용 단일 응답) |

service 내부: `validate_period`(입력검증) · `_resolve_period`(기간 확정, 없으면 trade_history min/max) · `_load_numerator`(지급) · `_load_denominator`(매출) · `_process_store`(매장 집계) · `_load_weekly_trend`(주간) · `_is_male`(성별).

## DB 5테이블

| 테이블 | 역할 |
|---|---|
| `trade_history` | **지급=분자**: `SUM(TRUNC(payment_amount))`. buy/ret/credit 도 여기서 |
| `sales_daily` | **매출=분모**: `SUM(quantity × regular_price)`(regular_price>0) |
| `products` | sales_daily→supplier_id JOIN |
| `pm_suppliers` | 사입처명·성별판정(`M)%`) |
| `stores` | 8매장(본사01·물류11 제외) |

## 응답 키 (top-level 4)

- **`meta`**: `txn_start`·`txn_end`·`period_label`·`target_payrate`(42)·`explicit_period`
- **`grand`**: `total_pr`·`pr_f`·`pr_m`·`total_pay`/`total_sal`(+`_f`/`_m`)·`danger_cnt`·`nosales_cnt`·`high_credit_cnt`
- **`stores[]`**: 매장별 `total_pr`·`total_pay`/`total_sal`·성별·`suppliers[]`(supplier/pay_amount/buy_amount/credit_amount/pay_rate/sales_amount …)·`danger_cnt`/`nosales_cnt`/`high_credit_cnt`
- **`weekly_trend`**: `{매장명|전체: [{wk_label, rate, pay, buy, ret}]}` — ⚠️ 주간 `rate`는 `pay/buy`(**사입대비**), 매장 `total_pr`의 `pay/sal`(매출대비)과 기준이 다름

> 본사물류·지급관리 서브탭은 이 응답(특히 `stores[].suppliers[]`·`weekly_trend`)을 **프론트에서 재구성**(API 추가 없음). 새 집계가 필요하면 응답 스키마 확장 → payrate-data.

## 데이터 흐름

```
trade_history (지급)          sales_daily × products × pm_suppliers (매출)
        │                              │
        └────────────┬─────────────────┘  (분자·분모 동일 기간)
                     ▼  payrate_service (집계·성별·주간추이)
                     ▼  GET /api/payrate/overview
                     ▼  PayrateOverviewView.js  → activeTab v-show (오버뷰/지급관리/본사물류)
                     ▼  위젯 3종 + logi 프론트 재구성
```

## 정합 주의 (사고 이력)
- **분자·분모 동일 기간** — 분모를 다른 기간으로 좁혀 0 만들지 않는다('지급율 0%' 사건).
- **수치 동등성** — 정본이 `int(float())` 행단위 절사 → SQL은 `SUM(TRUNC(...))`로 동일 결과 보장.
- **밴딩 임계 이식** — 정본 그대로(매장 >48/>45/<40, 합계 ≤45/≤48, 사입처 >100/>80).
- 입력 역전/형식오류 → 400(조용한 전체범위 폴백 없음).

상세 업무규칙·용어는 [[지급율 관리 탭 도메인 규칙]] 참조.
