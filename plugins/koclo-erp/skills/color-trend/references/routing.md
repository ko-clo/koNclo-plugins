# color-trend — 영역 ↔ 에이전트 ↔ 파일 매핑 (§0)

> 본체 `SKILL.md` 에서 분리. 어느 에이전트에 맡길지 고를 때에 읽는다.

## 0. 영역 ↔ 에이전트 ↔ 파일 매핑

| # | 영역 | 에이전트 | 프론트 | API | DB/service |
|---|---|---|---|---|---|
| 0 | 전체 칼라·데님 사이드 | `color-trend-all-agent` | `ColorTrendView.js`, `ColorTrendAllColorsTab.js`, `color-trend.css` | `api.getColorTrendOverview`, `GET /api/color-trend/overview` | 응답 `all_colors/denim_colors/color_css` 소비. 계산 변경은 data-agent |
| 1 | 포인트 칼라·효율·선택 컨펌 | `color-trend-point-agent` | `ColorTrendPointColorsTab.js`, `ColorTrendConfirmBar.js`, `ColorTrendView.js` 선택/복사 메서드 | 동일 overview API | 응답 `point_colors/efficiency_colors` 소비. 포인트 산식은 data-agent |
| 2 | VMD 팔레트 | `color-trend-vmd-agent` | `ColorTrendVmdPaletteTab.js`, `ColorTrendView.js` | 동일 overview API | 응답 `vmd_palette` 소비. VMD 탭 자체가 아니라 인기컬러 내부 팔레트 |
| 3 | 인기종합순 | `color-trend-ranking-agent` | `ColorTrendRankingTab.js`, `ColorTrendView.js` | 동일 overview API | 응답 `trend_colors/denim_colors`, `trend_score` 소비 |
| 4 | 부진칼라 경고 | `color-trend-bad-agent` | `ColorTrendBadColorsTab.js`, `ColorTrendView.js` | 동일 overview API | 응답 `bad_colors`, `dead_count/bad_count` 소비 |
| 5 | 외부 트렌드 | `color-trend-external-agent` | `ColorTrendExternalTrendsTab.js`, `ColorTrendView.js` | 동일 overview API | 응답 `external_trends`. 현재는 service 상수 기반 캐시 소스 |
| 6 | 상세 모달·마스터시트 전송 | `color-trend-transfer-agent` | `ColorTrendDetailModal.js`, `api.js`, `ColorTrendView.js` detail state | `/api/master-sheets*`, `api.productImageUrl` | `master_sheet_router.py`, `product_master_sheets`, `product_master_sheet_rows` |
| 7 | 데이터 파이프라인·정규화·API | `color-trend-data-agent` | `api.js` 계약, 모든 위젯 응답 키 영향 | `color_trend_router.py`, `snapshot_router.py` | `color_trend_service.py`, `score_ranking_service.py`, `sales_daily/purchase_daily/inventory_snapshot/products/pm_suppliers`, 레거시 생성기 |

공통 셸: `frontend/js/views/ColorTrendView.js`, `frontend/js/api.js`, `frontend/css/color-trend.css`.
공통 백엔드: `backend/app/routers/color_trend_router.py`, `backend/app/services/color_trend_service.py`, `backend/app/routers/snapshot_router.py`.
앱 라우트와 커맨드는 `/color-trend`, 탭 id는 `order-color`, API prefix는 `/api/color-trend`, snapshot report type은 `color_trend`다.
