---
name: 베스트상품 대시보드 도메인 규칙
description: 베스트상품 탭의 용어·업무규칙·3개 서브탭 관계·공유 의존. 베스트상품/통합베스트/KA·TB마스터/초특급볼륨/점수가중치/적재/batch 키워드 매칭 시 호출. 베스트상품 탭 작업 전 항상 참조.
type: reference
---

# 베스트상품 대시보드 — 도메인 규칙

## 정의 (이 ERP 한정)

베스트상품 탭은 주문장 생성 시 계산된 **"잘 나가는 상품"을 3가지 관점으로** 보여주는 읽기전용 대시보드.
핵심: 화면은 계산하지 않는다 — `order_v8_2`가 적재한 DB(`best_*` 3테이블)를 읽어 표시만 한다. 표시값은 `product_id`/`store_id` FK를 JOIN으로 복원.

## 용어

| 용어 | 의미 |
|---|---|
| batch_date | 주문기준일(`TO_DATE`). 적재 단위. 화면은 항상 최신 batch만 표시 |
| 점수(total) | 통합베스트 랭킹값. 6요소 percentile 가중합(합계 100) — `BEST_SCORE_WEIGHTS` |
| lr/svr/str | 점수 컴포넌트 — lr=판매추세 기울기, svr=판매속도, str=회전율 (각 percentile) |
| c1w/c2w/new | 1주/2주 색상소진율 + 신상가점(`NEW_SCORE_TIERS`) |
| momentum | 전주대비 판매 증감% (통합베스트 필터, `BEST_MOMENTUM_FLOOR_PCT` 이하 제외) |
| sold_2w | 실판매 2주 합(통합·KA·TB 주 수량) |
| replenish_qty | 보충필요량 `Σmax(0, sold_2w−현재고)` — **판매량 아님**(통합베스트 병기값) |
| sold_qty | 초특급볼륨 누적 실판매(=total_sales). 전체기간 누적이라 오래된 상품 유리 |
| KA/TB | product_code 11~12자리(또는 부분일치) 코드. KA=강제볼륨 계열, TB=마스터. **둘 다면 TB 우선** |

## 3개 서브탭 역할·관계

| # | 서브탭 | 모집단 | 랭킹 지표 | grain | 컷 | 쓰기 |
|---|---|---|---|---|---|---|
| 0 | 통합베스트 | 전 상품 | `avg_score`(점수) | SKU(교차매장 집계) | 매장수임계+점수≥60+momentum>-20 → 여30+남20 | 읽기(적재는 order_v8_2) |
| 1 | KA·TB 마스터 | product_code KA/TB | `score` | 매장별 SKU | 전수(필터 없음) | 읽기 |
| 2 | 초특급볼륨 | product_code KA/TB | `sold_qty`(누적 실판매) | 매장별 SKU | 매장별 Top `VOLUME_TOP_N`(=17) | 읽기 |

## 업무 규칙 (상수·임계 — 임의 단순화 금지)

- **통합베스트 점수**: `lr×35 + svr×20 + str×17.5 + c1w×12 + c2w×5.5 + new(0~10)` = 100 (`BEST_SCORE_WEIGHTS`, assert 합=100).
- **통합베스트 선정 4관문**: ①매장수 ≥ `ceil(BEST_STORE_RATIO_{FEMALE 3/5, MALE 2/5} × 전체매장)` ②`avg_score ≥ BEST_MIN_AVG_SCORE(60)` ③`momentum > BEST_MOMENTUM_FLOOR_PCT(-20)` ④여`BEST_TOP_N_FEMALE(30)`+남`BEST_TOP_N_MALE(20)`.
- **성별 판정**: `is_mens = 공급사명 'M)'로 시작`. 통합베스트만 성별 분리·필터.
- **KA/TB 분류**: `'TB' in product_code → TB, elif 'KA' → KA`(TB 우선). KA·TB/볼륨 모집단 동일.
- **초특급볼륨 가격**: `purchase_price`/`sale_price`는 `db_master_loader`(sales_daily 최신 non-null) 유래. **미판매 상품은 0**(레거시 폴백 제거). 가격 수정 후 MASTER_DATA 캐시 삭제 필요.
- **수량 명칭 분리**: `sold_2w`/`sold_qty`(실판매) vs `replenish_qty`(판매−재고, 판매 아님) — 오독 차단(이름·값 일치 규칙).
- **product_id 필수**: 모든 행이 products FK. 미매칭 상품은 `get_or_create_product`로 products에 추가(중복생성 방지 정본 리졸버).

## 공유 의존 (한 곳 변경 → 교차 영향)

- **3탭 전부 `persist_best_products` 한 함수**가 적재. 스키마/적재 로직 변경은 3탭 회귀.
- **`best_v2_router.py` JOIN** 공유: products/pm_suppliers/stores 조인이 3탭 표시값 복원.
- **`BestProductView.js` 단일 파일** 공유: 이미지/프리뷰/모달·`fmt`·필터.
- **`db_master_loader` 가격** 공유: 초특급볼륨 + 주문장 전체 매출/발주 금액 동시.
- **점수 상수**(`BEST_SCORE_WEIGHTS` 등): 통합·볼륨 선정.

구조·파일·API·DB 상세는 [[베스트상품 대시보드 아키텍처]] 참조. 작업 라우팅은 `best-products` 스킬, 공통 규칙은 [[에이전트 공통 KERNEL]].

## 경계 — md-agent(기획)와 구분

`md-agent` description에 "베스트/적중률"이 있으나 **역할이 다르다**: md-agent는 베스트를 *입력 축*으로 쓰는 주문추천·포트폴리오 결정, best-\*-agent는 베스트상품 **탭 자체**(계산·저장·API·표시)의 개발/수정. "탭 수정/기능추가/조회 화면/적재" → best-products, "무엇을 넣을지/주문추천/적중률 기획" → md-agent.
