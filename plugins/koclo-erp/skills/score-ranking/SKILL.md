---
name: score-ranking
description: 스코어랭킹 탭 작업 라우팅. "스코어랭킹", "스코어 랭킹", "score-ranking", "score ranking", "/score-ranking", "종합 TOP", "주문장 베스트", "깔교대상", "색상 아코디언", "마스터시트 전송", "점수 산식", "랭킹 필터" 등 스코어랭킹 탭/영역의 수정·조회·기능추가 요청 시 호출. 요청 영역을 식별해 전담 에이전트로 위임하고 전체 탭 회귀를 검증한다.
---

# 스코어랭킹 탭 작업 — 라우팅 스킬

> 스코어랭킹은 `ScoreView.js`(`/score`)의 **오버뷰 셸 · 상품/색상 리스트 · DB 직접 점수 파이프라인**으로 구성된다.
> 이 스킬은 영역 식별 → 전담 에이전트 위임 → 결과 통합 → 전체 회귀 검증 순서로 쓴다.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다.

## 0. 영역 ↔ 에이전트 ↔ 파일 매핑

| # | 영역 | 에이전트 | 프론트 | API | DB/service |
|---|---|---|---|---|---|
| 0 | 오버뷰 셸·KPI·필터 | `score-ranking-overview-agent` | `ScoreView.js`, `theme.css`(`.score-ranking-page`, `.sr-*`) | `GET /api/score-ranking/overview`, `api.getScoreRankingOverview` | 응답 `meta/items` 소비. 산식·SQL 변경은 data-agent |
| 1 | 상품/색상 리스트·선택·마스터시트 전송 | `score-ranking-list-agent` | `ScoreRankingProductList.js`, `theme.css`(`.sr-product-*`, `.sr-color-*`, `.sr-sel-bar`) | `/api/order/product-image`, `/api/master-sheets*` | 선택 row source=`score-ranking`, master-sheet 공용 계약 |
| 2 | 데이터 파이프라인·점수 산식·응답 계약 | `score-ranking-data-agent` | `api.js` 계약 영향, `ScoreRankingList.js`(composer 위젯 레거시 소비 주의) | `score_ranking_router.py` `GET /overview` | `score_ranking_service.py`; `sales_daily`, `purchase_daily`, `inventory_snapshot`, `products`, `pm_suppliers` |

공통 셸: `frontend/js/views/ScoreView.js`, `frontend/js/api.js`.
공통 백엔드: `backend/app/routers/score_ranking_router.py`, `backend/app/services/score_ranking_service.py`.
앱 라우트는 `/score`, 커맨드/스킬 진입점은 `/score-ranking`, API prefix는 `/api/score-ranking`이다.

## 1. 작업 흐름

1. **요청 영역 식별** — 사용자 요청이 어느 영역인지 §0 표로 판별한다. 모호하면 한 번만 질문한다.
2. **단일 영역** → 해당 에이전트 1개에 위임한다.
3. **여러 영역** → 영향 에이전트를 함께 위임한다. 특히 `ScoreView.js`, `ScoreRankingProductList.js`, `score_ranking_service` 응답 키, master-sheet 전송 계약은 교차 영향이다.
4. **결과 통합** — 각 에이전트 변경/리스크를 메인이 취합한다.
5. **전체 탭 회귀 검증** — §3.

## 2. 위임 규칙 (공유 자산 주의)

- **`/api/score-ranking/overview` 응답 계약**: `meta.stores`, `meta.ref_date`, `meta.generated_at`, `items[].rank/unified_score/best_score/store_count/stores/colors/has_kkalgyo`는 화면이 직접 소비한다. 키 추가/변경은 overview+list+data 회귀.
- **점수 산식 상수**: `SCORE_WEIGHTS`, `MIN_STORE_COUNT`, `MIN_AVG_SCORE`, `MIN_MOMENTUM`, `EXEMPT_SCORE`는 업무 규칙이다. 임의 단순화하지 말고 domain 메모리와 기존 계산을 함께 확인한다.
- **DB 원천**: `sales_daily`, `purchase_daily`, `inventory_snapshot`, `products`, `pm_suppliers`를 직접 읽는다. MASTER_DATA나 HTML 생성기를 새 기능 소스로 쓰지 않는다.
- **`score_ranking_service.py` 재사용**: `color_trend_service.py`가 일부 헬퍼를 재사용한다. helper/상수/응답 구조 변경은 컬러 트렌드 회귀까지 확인한다.
- **마스터시트 전송**: `ScoreRankingProductList.js`는 `/api/master-sheets*` 공용 API를 소비한다. master-sheet API 자체 구조 변경은 공용 backend/master-sheet 소관까지 확인한다.
- **상품 이미지**: `api.productImageUrl`은 `/api/order/product-image`를 쓴다. 이미지 placeholder/404 정책 변경은 소매 리오더 등 주문 계열 화면 영향도 확인한다.
- **레거시 HTML**: `/reports/score_ranking_v3.html`, `rebuild_score_db.py`, `rebuild_full.py`, `run_report.py score`는 대조/폴백 경로다. 신규 Vue 기능은 DB 직접 `/score` 경로에 추가한다.
- **composer 위젯**: `ScoreRankingList.js`는 `FunctionView` 계열에서 쓰던 별도 위젯이다. 메인 `/score` 탭 변경과 혼동하지 않는다.

## 3. 회귀 검증

- **import 스모크**(백엔드 변경 시 필수): `python -c "from app.routers import score_ranking_router"` 무에러, 또는 배포 후 `Application startup complete` + `/docs` 200. `py_compile`만으로는 미충족.
- **오버뷰 셸**: `/score` 라우트, 헤더, stale warning, `종합 TOP`/`주문장 베스트`/매장 칩, 기간·날짜·정렬·필터, KPI 5종이 정상.
- **리스트/상세**: 상품 펼침, 색상 행, 점수/주간판매/현재고/상태/깔교 표시, 이미지 placeholder, 선택/해제가 정상.
- **마스터시트 전송**: 기존 워크북 새 시트, 기존 시트 병합, 새 워크북 생성, 중복명 확인, source=`score-ranking` row가 정상.
- **데이터 계약**: `from_date > to_date`는 400, `limit`은 1~200, 매장 id/short/label 정규화, 빈 결과 payload가 프론트에서 깨지지 않음.
- **공유 회귀**: `color_trend_service` 재사용 helper 변경, `/api/master-sheets*`, `/api/order/product-image`, 레거시 리포트 링크를 건드렸으면 해당 소비 화면까지 확인.
- **빌드리스 유지**: CDN Vue + ES모듈, 번들러 도입 없음. 다른 탭 라우팅 무손상, 콘솔 에러 0.

## 4. 작업 전 필독

- `.claude/memory/domain/score-ranking.md` — 업무 규칙·용어·영역 관계·경계
- `.claude/memory/domain/score-ranking-feedback.md` — 누적 피드백(F1~)
- `.claude/memory/service/score-ranking-architecture.md` — Vue/API/DB/데이터 흐름
- `dev-blueprint` 스킬 — 탭 개발 표준(상위 규범)

## 경계 — best-* / retail-reorder / order-agent / md-agent 와 혼동 금지

- **score-ranking-\*-agent** = `/score` 탭 자체의 화면, 리스트 선택, 조회 API, 점수 산식과 응답 계약.
- **best-\*-agent** = 베스트상품 탭 정본 계산·화면. 점수 개념이 있어도 `/best` 영역은 별도 소관이다.
- **retail-reorder-\*-agent** = 소매 리오더 탭에서 스코어/베스트 결과를 소비하는 경로. 스코어랭킹 탭 자체 수정과 분리한다.
- **order-agent** = 주문장 생성 산식·xls 생성·검수·배포 운영.
- **md-agent** = 스코어랭킹 결과를 입력으로 쓰는 주문추천·포트폴리오 기획.
