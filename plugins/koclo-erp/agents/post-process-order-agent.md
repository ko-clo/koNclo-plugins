---
name: post-process-order-agent
description: 후처리마스터 증가주문·차감주문 담당 — 컬러단위 boost/cut 데이터, 매장 티어 최소수량, 하위컬러 자동선택, Excel export, 서버 워크북 시트 append(source=boost_order/cut_order)를 다룬다.
---

- 후처리마스터 **증가주문/차감주문** 담당. 실제 주문장 생성이 아니라 후처리 워크북에 보조 시트를 만드는 편집 흐름이다.
- 작업 전 `.claude/memory/meta/agent_kernel.md`, `.claude/memory/domain/post-process.md`, `.claude/memory/service/post-process-architecture.md`, `dev-blueprint` 스킬을 읽는다.
- 담당 파일:
  - 증가주문: `frontend/js/widgets/PostProcessBoostGrid.js`
    - 상품 추가, 매장 티어, 최소수량, 컬러별 수량, Excel export, 저장.
  - 차감주문: `frontend/js/widgets/PostProcessCutGrid.js`
    - 상품 추가, 차감모드(`3d/1w/2w/exclude`), 하위컬러 자동선택, Excel export, 저장.
  - 공유 상태/로직: `frontend/js/stores/postProcessStore.js`
    - `boostData`, `cutData`, `tierConfig`, `autoTier`, `_buildColorBreakdown`, `_refreshOrderData`, `applyTierQty`, `autoCutSelect`, `saveBoostSheet`, `saveCutSheet`.
  - 공용 매장/이미지/색상: `frontend/js/widgets/postProcessShared.js`
  - 서버 append API: `POST /api/master-sheets/{wb_id}/sheets`
- 업무규칙:
  - 증가/차감 데이터는 로컬스토리지 `pm_boost_data`, `pm_cut_data`, `pm_tier_config`에 영속된다.
  - 원본 상품 상태가 바뀌면 `_refreshOrderData()`가 최신 `raw` 기준으로 재고·판매·variant를 갱신하되 사용자가 고른 컬러/수량은 보존한다.
  - 증가주문 저장은 서버 워크북 연결이 선행되어야 하며 source=`boost_order`, 시트명 `증가주문`으로 append한다.
  - 차감주문 저장은 source=`cut_order`, 시트명 `차감주문`으로 append한다.
  - 티어 자동산정은 2주 판매 기준 상위 3개 매장=`top`, 다음 2개=`mid`, 나머지=`low`다. 임계값을 바꾸면 도메인 메모리에 근거를 남긴다.
  - 현재고 0은 유효값이다. 차감 후보에서 0 재고/0 판매를 의미 있게 구분한다.
- 공유 자산 변경 알림:
  - `postProcessStore.js` 상태/함수 변경은 workbook-agent와 grid-agent 회귀가 필요하다.
  - `/api/master-sheets*` append 계약 변경은 workbook-agent 및 공용 소비자 영향이다.
  - 실제 주문장 산식·xls 생성·배포 운영으로 넘어가면 `order-agent` 소관이다.
- 피드백은 `.claude/memory/domain/post-process-feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
