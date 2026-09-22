# best-products — 위임 규칙·경계 (§2 · §경계)

> 본체 `SKILL.md` 에서 분리. 위임 대상을 정하거나 인접 스킬과의 경계를 판단할 때 읽는다.
> 영역 매핑(§0)과 작업 흐름(§1)은 본체에 있다.

## 2. 위임 규칙 (공유 자산 주의 — VMD보다 결합도 높음)

3 서브탭은 **단일 파이프라인**을 공유한다. 아래 **공유 자산**을 건드리는 작업은 영향받는 서브탭 에이전트를 **모두** 위임하거나 메인이 직접 조정한다(`service/best-products-architecture.md`로 영향 범위 확인):

- **`persist_best_products`**(order_v8_2) — 3테이블을 **한 함수**에서 batch_date 단위로 적재. 컬럼/스키마/적재 로직 변경은 3탭 전부 회귀.
- **`best_v2_router.py`** — 4 엔드포인트 한 파일. JOIN(products/pm_suppliers/stores) 변경은 소비 서브탭 전부.
- **`best_volume_service.py`** — 초특급볼륨 탭과 소매 리오더 마스터주문 후보가 공유하는 기간판매 Top 계산. `weeks`/`include_all_top`/가격 조회 변경은 양쪽 회귀.
- **`BestProductView.js`** — 3탭 한 파일. 공유 이미지/프리뷰/모달·`fmt`·필터 변경은 3탭 전부.
- **`sales_daily` 가격 소스**(regular/purchase 최신 non-null) — 초특급볼륨 가격 + 주문장 전체 매출/발주 금액에 동시 영향. 적재본 가격은 `db_master_loader`, 조회 재계산 가격은 `best_volume_service` LATERAL 조회 패턴.
- **점수 상수**(`BEST_SCORE_WEIGHTS`·`BEST_MIN_AVG_SCORE`·`VOLUME_TOP_N` 등) — 통합·볼륨 선정에 영향.
- **batch_date 스냅샷 모델**(Best* 3테이블 공통 키).

단일 서브탭에 갇힌 작업(예: KA·TB탭 표시 컬럼만 변경)은 해당 에이전트 단독.

## 경계 — md-agent 와 혼동 금지

- **이 스킬/best-\*-agent** = 베스트상품 **탭 자체**의 계산·저장(DB)·API·화면 표시 개발/수정.
- **md-agent**(기획) = 베스트 데이터를 *입력 축*으로 쓰는 주문추천·포트폴리오 결정('무엇을 넣을지').
- "탭 수정/기능추가/조회 화면/적재 로직" → 이 스킬. "베스트 활용 주문추천/적중률 기획" → md-agent.
