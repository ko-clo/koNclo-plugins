# score-ranking — 위임 규칙·경계 (§2 · §경계)

> 본체 `SKILL.md` 에서 분리. 위임 대상을 정하거나 인접 스킬과의 경계를 판단할 때 읽는다.
> 영역 매핑(§0)과 작업 흐름(§1)은 본체에 있다.

## 2. 위임 규칙 (공유 자산 주의)

- **`/api/score-ranking/overview` 응답 계약**: `meta.stores`, `meta.ref_date`, `meta.generated_at`, `items[].rank/unified_score/best_score/store_count/stores/colors/has_kkalgyo`는 화면이 직접 소비한다. 키 추가/변경은 overview+list+data 회귀.
- **점수 산식 상수**: `SCORE_WEIGHTS`, `MIN_STORE_COUNT`, `MIN_AVG_SCORE`, `MIN_MOMENTUM`, `EXEMPT_SCORE`는 업무 규칙이다. 임의 단순화하지 말고 domain 메모리와 기존 계산을 함께 확인한다.
- **DB 원천**: `sales_daily`, `purchase_daily`, `inventory_flow`(현재고 — 날짜별 이력), `products`, `pm_suppliers`, `stores`(매장 레지스트리)를 직접 읽는다. MASTER_DATA나 HTML 생성기를 새 기능 소스로 쓰지 않는다. (주의: `inventory_snapshot`은 주문빌드/VMD 계열이 쓰는 PKL 유래 별개 테이블 — 이 탭 원천 아님.)
- **`score_ranking_service.py` 재사용**: `color_trend_service.py`가 일부 헬퍼를 재사용한다. helper/상수/응답 구조 변경은 컬러 트렌드 회귀까지 확인한다.
- **마스터시트 전송**: `ScoreRankingProductList.js`는 `/api/master-sheets*` 공용 API를 소비한다. master-sheet API 자체 구조 변경은 공용 backend/master-sheet 소관까지 확인한다.
- **상품 이미지**: `api.productImageUrl`은 `/api/order/product-image`를 쓴다. 이미지 placeholder/404 정책 변경은 소매 리오더 등 주문 계열 화면 영향도 확인한다.
- **레거시 HTML**: `/reports/score_ranking_v3.html`, `rebuild_score_db.py`, `rebuild_full.py`, `run_report.py score`는 대조/폴백 경로다. 신규 Vue 기능은 DB 직접 `/score` 경로에 추가한다.
- **composer 위젯**: `ScoreRankingList.js`는 `FunctionView` 계열에서 쓰던 별도 위젯이다. 메인 `/score` 탭 변경과 혼동하지 않는다.

## 경계 — best-* / retail-reorder / order-agent / md-agent 와 혼동 금지

- **score-ranking-\*-agent** = `/score` 탭 자체의 화면, 리스트 선택, 조회 API, 점수 산식과 응답 계약.
- **best-\*-agent** = 베스트상품 탭 정본 계산·화면. 점수 개념이 있어도 `/best` 영역은 별도 소관이다.
- **retail-reorder-\*-agent** = 소매 리오더 탭에서 스코어/베스트 결과를 소비하는 경로. 스코어랭킹 탭 자체 수정과 분리한다.
- **order-agent** = 주문장 생성 산식·xls 생성·검수·배포 운영.
- **md-agent** = 스코어랭킹 결과를 입력으로 쓰는 주문추천·포트폴리오 기획.
