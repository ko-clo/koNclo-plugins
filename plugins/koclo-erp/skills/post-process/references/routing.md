# post-process — 영역 ↔ 에이전트 ↔ 파일 매핑 (§0)

> 본체 `SKILL.md` 에서 분리. 어느 에이전트에 맡길지 고를 때에 읽는다.

## 0. 영역 ↔ 에이전트 ↔ 파일 매핑

| # | 영역 | 에이전트 | 프론트 | API | DB/service |
|---|---|---|---|---|---|
| 0 | 상품등급 그리드·매입차감 | `post-process-grid-agent` | `ProductMasterView.js`, `PostProcessMainGrid.js`, `PostProcessMaleGrade.js`, `PostProcessPurchaseCut.js`, `postProcessShared.js`, `post-process.css` | `GET /api/post-process/grid`, `api.getPostProcessGrid` | 응답 `meta/products` 소비. 계산·캐시 변경은 data-agent |
| 1 | 워크북·시트·모달 편집 | `post-process-workbook-agent` | `postProcessStore.js`, `PostProcessSheetBar.js`, `PostProcessSelectionBar.js`, `PostProcessAddModal.js`, `PostProcessAggModal.js`, `PostProcessServerModal.js` | `/api/master-sheets*`, `GET /api/post-process/aggs` | `master_sheet_router.py`, `product_master_sheets`, `product_master_sheet_rows` |
| 2 | 증가주문·차감주문 | `post-process-order-agent` | `PostProcessBoostGrid.js`, `PostProcessCutGrid.js`, `postProcessStore.js`의 `boostData/cutData/tierConfig` | `POST /api/master-sheets/{id}/sheets` | append source=`boost_order`/`cut_order`, 로컬스토리지 `pm_boost_data`/`pm_cut_data`/`pm_tier_config` |
| 3 | 데이터 파이프라인·프리컴퓨트·캐시 | `post-process-data-agent` | `api.js` 계약 영향, 그리드/모달 응답 키 영향 | `post_process_router.py` `GET /grid`, `GET /aggs`, `POST /cache/clear` | `post_process_service.py`, `post_process_products`, `rebuild_post_process_products_db.py`, `post_process_db_direct.py`, `post_process_data.py` |

공통 셸: `frontend/js/views/ProductMasterView.js`, `frontend/js/stores/postProcessStore.js`, `frontend/js/api.js`.
공통 백엔드: `backend/app/routers/post_process_router.py`, `backend/app/services/post_process_service.py`, `backend/app/routers/master_sheet_router.py`.
앱 라우트와 커맨드는 `/post-process`, 탭 id는 `analytics-post`, API prefix는 `/api/post-process`다.
