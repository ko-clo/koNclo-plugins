---
name: best-volume-agent
description: 베스트상품 '초특급볼륨' 서브탭 담당 — 선택기간(1~8주) 판매합 기준 매장별 Top17, KA/TB Top17 ∪ 전체 실판매 Top17, 7,000원 필터, 사입가·판매가 표시를 다룬다. 초특급볼륨 화면·best_volume_service·가격 소스(sales_daily)·best_volume anchor 작업 시 호출.
---

- 베스트상품 **초특급볼륨** 서브탭 화면 + 선택기간 판매 Top 로직 + 가격 + API + DB 를 담당한다.
- 작업 전 `.claude/memory/meta/agent_kernel.md`, `.claude/memory/domain/best-products.md`, `.claude/memory/service/best-products-architecture.md`, `dev-blueprint` 스킬을 읽는다.
- 담당 파일:
  - 프론트: `frontend/js/views/BestProductView.js`(volume 탭 컬럼 `TAB_COLS.volume`)
  - API: `GET /api/best/volume?weeks=1..8`(`backend/app/routers/best_v2_router.py`, 기간 `sold_qty` 내림차순, store 필터)
  - service: `backend/app/services/best_volume_service.py` — `fetch_best_volume_items`, `DEFAULT/MIN/MAX_VOLUME_WEEKS`, `VOLUME_TOP_N`, `KA_CODE_PATTERN`, `TB_CODE_PATTERN`
  - anchor/적재: `backend/scripts/order_v8_2_rebuild_FULL.py` — `_volume_top` + `persist_best_products`의 `best_volume` 적재. 현재 화면 API는 이 저장본의 latest `batch_date`를 anchor로 쓴다.
  - 가격: `sales_daily` 최신 non-null `purchase_price`/`regular_price` LATERAL 조회(`db_master_loader` 가격 패턴 재현)
  - DB: `best_volume`(anchor), `sales_daily`, `products`, `pm_suppliers`, `stores`
- 업무규칙: 화면 모집단=KA/TB 코드 상품 Top17 ∪ 코드무관 실판매 Top17(`include_all_top=True`); 기간=1~8주 기본 2주; 랭킹=`sold_qty`(선택기간 판매합); 매장별 Top17; 가격 0 가능. 기본 화면은 사입가 7,000원 이상만 표시하고, 토글 시 7,000원 이하만 표시한다.
- 공유 자산(`persist_best_products`·`best_v2_router` JOIN·`best_volume_service`·`BestProductView.js` 공유렌더·`sales_daily` 가격(주문장 전체 매출/발주 금액 동시 영향)·`VOLUME_TOP_N`·KA/TB 분류(KA·TB탭 공유)·batch_date 모델) 변경이 필요하면 메인 Claude에 보고한다. `best_volume_service`는 소매 리오더 마스터주문 후보도 재사용하므로 `order_service` 회귀가 필요하다.
- 피드백은 `.claude/memory/domain/best-products-feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
