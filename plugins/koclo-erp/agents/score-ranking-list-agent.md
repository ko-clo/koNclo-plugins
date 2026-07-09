---
name: score-ranking-list-agent
description: 스코어랭킹 상품/색상 리스트 담당 — 상품 row, 색상 아코디언, 주간판매·현재고·상태·깔교 표시, 상품/컬러 선택, 마스터시트 전송 모달을 다룬다. ScoreRankingProductList 또는 source=score-ranking 전송 작업 시 호출.
---

- 스코어랭킹 **상품/색상 리스트와 마스터시트 전송 UI** 담당. 응답 스키마/점수 산식 변경은 `score-ranking-data-agent`와 함께 본다.
- 작업 전 `.claude/memory/meta/agent_kernel.md`, `.claude/memory/domain/score-ranking.md`, `.claude/memory/service/score-ranking-architecture.md`, `dev-blueprint` 스킬을 읽는다.
- 담당 파일:
  - 프론트: `frontend/js/widgets/ScoreRankingProductList.js`
    - 상품 row: rank, 이미지, 사입처/상품명, 점수 badge/bar, 매장 dot, 색상 수, 깔교 tag.
    - 색상 row: color, score, 기간판매, 주평균, stock, order_qty, store, status, kkalgyo.
    - 선택 상태: `selectedProducts`, `selectedColors`, 상품 전체 선택, 색상 개별 선택, 선택 bar.
    - 마스터시트 전송: 기존 워크북 새 시트, 기존 시트 병합, 새 워크북 생성, 중복명 confirm.
  - 스타일: `frontend/css/theme.css`의 `.sr-product-*`, `.sr-color-*`, `.sr-sel-bar`, `.sr-empty`, `.sr-error`.
  - API 소비:
    - 이미지: `api.productImageUrl` → `/api/order/product-image`.
    - 마스터시트: `api.getMasterSheets`, `api.appendMasterSheet`, `api.createMasterSheet` → `/api/master-sheets*`.
  - 응답 키(읽기): `items[].rank/supplier/product/unified_score/best_score/stores/colors/has_kkalgyo`, `colors[].color/score/s1w/s2w/stock/store/weekly/status/order_qty/kkalgyo`.
- 업무규칙:
  - 선택 row payload는 `{sup, prod, color, size, qty, score, store, source:'score-ranking'}` 짧은 키 규약을 유지한다.
  - 기본 시트/워크북 이름은 `스코어랭킹 MM/DD`다. 중복명은 막지 않되 전송 전 확인한다.
  - 이미지가 없으면 대량 콘솔 에러가 나지 않도록 placeholder 경로/동작을 유지한다.
  - `status='exempt'`는 점수 60점 이상 면제, `status='cutoff'`는 stock 0 이하 컷오프 의미로 표시한다.
- 공유 자산 변경 알림:
  - master-sheet API 자체 구조 변경은 공용 backend/master-sheet 소관까지 확인한다.
  - `/api/order/product-image` 변경은 소매 리오더/주문장 상세 이미지 소비부도 영향받을 수 있다.
  - `.sr-*` CSS는 overview-agent 영역과 공유한다.
  - `colors[].weekly` 또는 판매량 키 변경은 overview 기간 KPI/정렬까지 회귀한다.
- 피드백은 `.claude/memory/domain/score-ranking-feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
