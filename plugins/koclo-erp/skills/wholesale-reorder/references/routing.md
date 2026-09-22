# wholesale-reorder — 영역 ↔ 에이전트 ↔ 파일 매핑 (§0)

> 본체 `SKILL.md` 에서 분리. 어느 에이전트에 맡길지 고를 때에 읽는다.

## 0. 영역 ↔ 에이전트 ↔ 파일 매핑

| # | 영역 | 에이전트 | 프론트 | API | DB/service |
|---|---|---|---|---|---|
| 0 | 리포트·카드 | `wholesale-reorder-report-agent` | `WholesaleView.js`·`WholesaleCard.js`(소스필터·키워드섹션·KPI·기주문추적·도매외부·원천점검) | `GET /api/wholesale/overview`·`/image` | `filter_overview`(소스필터) / `card_public`·`variant_public`·`order_public` |
| 1 | 액션·재계산 | `wholesale-reorder-action-agent` | `WholesaleView.js`(매장 이동·정리 섹션·다운로드·재계산 버튼·발주확정) | `POST /api/wholesale/refresh`·`GET /api/wholesale/action-plan.xlsx`·`POST /api/wholesale/reorder` | `refresh_snapshot`·`_ingest_then_compute`·`ingest_workbook` / `action_public`·`build_actions` |
| 2 | 데이터 파이프라인 | `wholesale-reorder-data-agent` | — (백엔드 owner) | `wholesale_router` 전체 | `wholesale_service`·`wholesale/compute_data`·`db_adapters`·`ingest`·`serialize`·`_vendor` 빌더·스냅샷 스키마 |

공통 셸: `frontend/js/views/WholesaleView.js`(소스탭·키워드섹션·액션·원천점검) · `frontend/js/widgets/WholesaleCard.js` · `frontend/js/api.js`(wholesale 메서드).
공통 백엔드: `backend/app/routers/wholesale_router.py` · `backend/app/services/wholesale_service.py` · `backend/app/services/wholesale/`(compute_data·db_adapters·ingest·serialize·_vendor).
`_vendor/`(build_reorder_fresh 등)은 **PRD 빌더 100% 원본** — 산식 변경은 재복사 동기화이며 임의 수정 금지(§경계).
