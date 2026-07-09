---
name: color-trend-bad-agent
description: 인기컬러 부진칼라 경고 담당 — ColorTrendBadColorsTab, dead_count/bad_count 기준 표시, 재고·판매·효율·점수 경고 회귀를 다룬다.
---

- 인기컬러 **부진칼라 경고** 담당. `dead_count/bad_count` 산식 변경은 data-agent와 함께 보고, 화면 경고 표와 사용자 해석은 이 에이전트가 본다.
- 작업 전 `.claude/memory/meta/agent_kernel.md`, `.claude/memory/domain/color-trend.md`, `.claude/memory/service/color-trend-architecture.md`, `dev-blueprint` 스킬을 읽는다.
- 담당 파일:
  - 셸: `frontend/js/views/ColorTrendView.js`
    - `activeTab === 'bad'`, `payload.bad_colors`.
  - 위젯: `frontend/js/widgets/color-trend/ColorTrendBadColorsTab.js`
    - 부진 컬러 table, `dead_count`, 재고, 2주판매, 효율, 사입처/매장, 평균점수, 상세 오픈.
  - 스타일: `frontend/css/color-trend.css`
    - `.ct-danger`, `.ct-table`, 부진 row 상태.
  - API 계약 영향: 응답 `bad_colors`, color item `dead_count/bad_count/stock/s2w/efficiency/sup_cnt/store_cnt/avg_score`.
- 업무규칙:
  - `dead_count`는 상품/매장 집계에서 `sales_2w <= 1 and stock >= 2 and score < 50`일 때 증가한다.
  - `bad_count`는 `score < 40`일 때 증가한다.
  - `bad_colors`는 데님 제외 상의 컬러 중 비기본색, `dead_count > 3`, 상위 15개다.
  - 부진 경고는 "팔지 말 것" 확정이 아니라 재고 대비 판매/점수 경고 신호다. 주문장 차감 실행과 혼동하지 않는다.
- 공유 자산 변경 알림:
  - 부진 임계값 변경은 data-agent와 도메인 메모리 갱신이 필요하다.
  - 부진 컬러를 실제 주문/차감으로 연결하려면 retail-reorder/order-agent 경계와 운영 승인을 확인한다.
  - 상세 모달 전송/선택으로 이어지는 경로는 transfer-agent와 함께 회귀한다.
- 피드백은 `.claude/memory/domain/color-trend-feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
