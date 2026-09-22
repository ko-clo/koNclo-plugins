# retail-reorder — 영역 ↔ 에이전트 ↔ 파일 매핑 (§0)

> 본체 `SKILL.md` 에서 분리. 어느 에이전트에 맡길지 고를 때에 읽는다.

## 0. 영역 ↔ 에이전트 ↔ 파일 매핑

| # | 영역 | 에이전트 | 프론트 | API | DB/service |
|---|---|---|---|---|---|
| 0 | 리포트·전체핵심·주문장 상세 | `retail-reorder-report-agent` | `OrderView.js`(core: KPI·상단 재계산바·매장별요약·주요상품·주문표 모달·기존 탭 토글), `OrderSheetView.js`, `orderDetailShared.js` | `GET /api/order/build/latest`·`/build/detail/{id}`·`/build/runs`·`/store-metrics`·`/product-image` | `fetch_order_build_*`·`fetch_store_extra_metrics` / `order_build_*`·`backorder_products`·`sample_products`·`sample_ledger` |
| 1 | 마스터주문·상품 마스터 | `retail-reorder-report-agent` + 스키마/계산 변경 시 `retail-reorder-data-agent` | `OrderView.js`(마스터주문 후보/예산/선택반영, 상품 마스터 서브탭), `api.js` | `GET /api/order/build/master-order`·`POST /api/order/build/master-add`·`/api/master-sheets*`·`/api/best/integrated` | `fetch_master_order_candidates`·`add_master_order_items`·`volume_capacity_service`·best_*·master_sheets·inventory_snapshot·purchase_daily |
| 2 | 실행·생성 UI | `retail-reorder-run-agent` | `OrderView.js`(주문 파라미터·안전재고·데이터 상태·생성/취소·진행 폴링) | 현재 UI: `POST /api/reports/regenerate`·`GET /api/reports/task/{id}`·`POST /api/order/cancel/{id}`·`GET /api/order/data-status`; 직접 실행 API: `/api/order/run`·`/status/{id}`·`/history`; 보조: `/api/reports/cache-status`·`/api/config/safety_stock_config` | `task_runner`, `order_progress`, `fetch_order_data_status`; 실제 생성 산식은 order-agent 경계 |
| 3 | 데이터 파이프라인·응답 계약 | `retail-reorder-data-agent` | `api.js` 계약 영향 | `order_router` 전체 + report/config/master-sheet/best API 의존 | `order_service` 전체 + `vmd_service`/`payrate_service`/`best_volume_service`/`volume_capacity_service` 재사용·`order_build_*` 스냅샷 스키마 |

공통 셸: `frontend/js/views/OrderView.js`, `frontend/js/api.js`.
공통 백엔드: `backend/app/routers/order_router.py`, `backend/app/services/order_service.py`.
분리 상세 탭: `frontend/js/views/OrderSheetView.js`, `frontend/js/orderDetailShared.js`.
