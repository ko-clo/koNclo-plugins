# best-products — 영역 ↔ 에이전트 ↔ 파일 매핑 (§0)

> 본체 `SKILL.md` 에서 분리. 어느 에이전트에 맡길지 고를 때에 읽는다.

## 0. 서브탭 ↔ 에이전트 ↔ 파일 매핑

| # | 서브탭 | 에이전트 | 프론트 | API | 생성/계산 | DB |
|---|---|---|---|---|---|---|
| 0 | 통합베스트 | `best-integrated-agent` | `BestProductView.js`(integrated 탭·TAB_COLS) | `GET /api/best/integrated` | order_v8_2 `best_candidates`(점수 가중치)+`persist_best_products` | `best_integrated` |
| 1 | KA·TB 마스터 | `best-ka-tb-agent` | `BestProductView.js`(ka_tb 탭) | `GET /api/best/ka-tb` | order_v8_2 KA/TB 코드 추출+persist | `best_ka_tb` |
| 2 | 초특급볼륨 | `best-volume-agent` | `BestProductView.js`(volume 탭·판매기간·7천원 필터) | `GET /api/best/volume?weeks=1..8` | `best_volume_service.fetch_best_volume_items` — 최신 `best_volume` batch anchor + `sales_daily` 기간판매 Top17 재계산 | `best_volume`(anchor), `sales_daily`, `products`, `pm_suppliers`, `stores` |

공통 셸: `frontend/js/views/BestProductView.js`(3탭 라우팅·이미지/프리뷰/모달·컬럼 렌더).
공통 백엔드: `backend/app/routers/best_v2_router.py`(읽기 API) · `backend/app/services/best_volume_service.py`(초특급볼륨 기간 재계산) · `backend/scripts/order_v8_2_rebuild_FULL.py`(`persist_best_products` 적재) · `backend/app/db/models.py`(Best* 모델).
메타: `GET /api/best/meta`(3탭 최신 batch_date·건수).
