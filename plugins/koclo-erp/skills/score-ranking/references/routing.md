# score-ranking — 영역 ↔ 에이전트 ↔ 파일 매핑 (§0)

> 본체 `SKILL.md` 에서 분리. 어느 에이전트에 맡길지 고를 때에 읽는다.

## 0. 영역 ↔ 에이전트 ↔ 파일 매핑

| # | 영역 | 에이전트 | 프론트 | API | DB/service |
|---|---|---|---|---|---|
| 0 | 오버뷰 셸·KPI·필터 | `score-ranking-overview-agent` | `ScoreView.js`, `theme.css`(`.score-ranking-page`, `.sr-*`) | `GET /api/score-ranking/overview`, `api.getScoreRankingOverview` | 응답 `meta/items` 소비. 산식·SQL 변경은 data-agent |
| 1 | 상품/색상 리스트·선택·마스터시트 전송 | `score-ranking-list-agent` | `ScoreRankingProductList.js`, `theme.css`(`.sr-product-*`, `.sr-color-*`, `.sr-sel-bar`) | `/api/order/product-image`, `/api/master-sheets*` | 선택 row source=`score-ranking`, master-sheet 공용 계약 |
| 2 | 데이터 파이프라인·점수 산식·응답 계약 | `score-ranking-data-agent` | `api.js` 계약 영향, `ScoreRankingList.js`(composer 위젯 레거시 소비 주의) | `score_ranking_router.py` `GET /overview` | `score_ranking_service.py`; `sales_daily`, `purchase_daily`, `inventory_flow`, `products`, `pm_suppliers`, `stores` |

공통 셸: `frontend/js/views/ScoreView.js`, `frontend/js/api.js`.
공통 백엔드: `backend/app/routers/score_ranking_router.py`, `backend/app/services/score_ranking_service.py`.
앱 라우트는 `/score`, 커맨드/스킬 진입점은 `/score-ranking`, API prefix는 `/api/score-ranking`이다.
