---
name: retail-reorder-report-agent
description: 소매 리오더 리포트/표현 영역 담당 — 전체핵심(KPI·상단 재계산바·매장별 요약·행거/지급율/샘플·주요 상품·주문표 모달·빌드 이력), 마스터주문 후보/예산/선택반영 UI, 상품 마스터 서브탭, 주문장 상세 탭(OrderSheetView)을 다룬다. 베스트상품 정본 계산/화면은 best-* 소관.
---

- 소매 리오더 **리포트 보기/표현 계층** 담당. 화면·상태·상호작용을 다루며, 응답 스키마/집계 변경은 `retail-reorder-data-agent`와 함께 본다.
- 작업 전 `.claude/memory/meta/agent_kernel.md`, `.claude/memory/domain/retail-reorder.md`, `.claude/memory/service/retail-reorder-architecture.md`, `dev-blueprint` 스킬을 읽는다.
- 담당 파일:
  - 프론트: `frontend/js/views/OrderView.js`
    - report core: `summaryRows`, `buildKpis`, 상단 재계산바(우수상품·마스터·통합베스트·상품마스터시트·트렌드), 매장별 요약, 주문표 모달, 주요 상품, 기존 탭 토글.
    - 마스터주문: `loadMasterOrder`, `applyMasterAdd`, 목표 지급율, 초특급볼륨 주차/가격/매장 필터, 수량/예산/선택 상태.
    - 상품 마스터: `loadProductMasterWorkbooks`, 시트/매장/검색/페이징.
  - 주문장 상세: `frontend/js/views/OrderSheetView.js`, `frontend/js/orderDetailShared.js`.
  - API 소비: `/api/order/build/latest`, `/build/detail/{run_id}`, `/build/runs`, `/store-metrics`, `/product-image`, `/build/master-order`, `/build/master-add`, `/api/master-sheets*`, `/api/best/integrated`.
  - service(읽기/계약): `fetch_order_build_*`, `fetch_store_extra_metrics`, `fetch_master_order_candidates`, `add_master_order_items`.
- 업무규칙:
  - 표시 데이터는 강화 + 미송 병합본이다. 매장별 요약 주문건/수량은 기본 미송 제외, 토글 시 미송 포함.
  - 행거는 빌드 `ref_date` 이하 스냅샷, 지급율은 최근 1달, 샘플은 `store-metrics` lazy 지표다.
  - 남/여 분리는 토글 시만. 행거는 %와 현재고/목표(±)를 함께 표시한다.
  - 마스터주문 반영은 실제 발주/xls 재생성이 아니라 `order_build_store_payload.excel_data` 스냅샷 갱신이다. 성공 후 요약·주문표·후보를 재조회해야 한다.
  - 상품 마스터는 `기본` 시트를 숨긴다. 매장 프리젠스 실패 시 선택을 막지 않는 안전측 폴백을 유지한다.
- 공유 자산 변경 알림:
  - `order_service` 응답 키, `order_build_*` 스키마, `store-metrics`, 마스터주문 후보/반영 계약 변경은 data-agent 영향.
  - `OrderView.js` 모드/탭 공통 상태 변경은 run-agent 영향.
  - `OrderSheetView.js`/`orderDetailShared.js` 변경은 주문장 탭 회귀 필수.
- 베스트3종 forced-tab 연결부는 본 에이전트가 다루되, 통합베스트/KA·TB/초특급볼륨 정본 계산과 BestProductView 내부는 best-* 에이전트 소관.
- 피드백은 `.claude/memory/domain/retail-reorder-feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
