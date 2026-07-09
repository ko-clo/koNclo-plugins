---
name: color-trend-point-agent
description: 인기컬러 포인트 칼라·효율·선택 컨펌 담당 — ColorTrendPointColorsTab, ColorTrendConfirmBar, selectedColorGroups, VMD 컨펌 체크/복사 UI를 다룬다.
---

- 인기컬러 **포인트 칼라·판매효율·선택 컨펌** 담당. 포인트 선정 산식은 data-agent 소관이고, 카드 UI·선택 상태·하단 액션바는 이 에이전트가 본다.
- 작업 전 `.claude/memory/meta/agent_kernel.md`, `.claude/memory/domain/color-trend.md`, `.claude/memory/service/color-trend-architecture.md`, `dev-blueprint` 스킬을 읽는다.
- 담당 파일:
  - 셸: `frontend/js/views/ColorTrendView.js`
    - `selectedColorGroups`, `selectedColors`, `toggleColorSelect`, `confirmSelected`, `copySelected`.
  - 위젯: `frontend/js/widgets/color-trend/ColorTrendPointColorsTab.js`
    - `colors`, `efficiencyColors`, `selectedGroups`, sort mode, checkbox, badge.
  - 위젯: `frontend/js/widgets/color-trend/ColorTrendConfirmBar.js`
    - 선택 수, confirm/copy 이벤트, 하단 고정 액션바.
  - 스타일: `frontend/css/color-trend.css`
    - `.ct-card-grid`, `.ct-color-card`, `.ct-confirm-bar`, `.ct-toggle-btn`.
  - API 계약 영향: 응답 `point_colors/efficiency_colors`와 각 color item의 `group/s2w/s1w/stock/efficiency/sup_cnt/store_cnt/trend_score`.
- 업무규칙:
  - `point_colors`는 비기본색 중 `trend_score > 0`인 상위 30개다.
  - `efficiency_colors`는 비기본색 중 `s2w >= 3`, `stock >= 1`인 상위 20개 효율 컬러다.
  - 선택 컨펌은 현재 실제 VMD DB 저장이 아니라 화면상 선택/복사 보조 흐름이다. 실제 VMD 행거 조정과 혼동하지 않는다.
  - `copySelected()`의 TSV 컬럼은 group, `s2w`, `s1w`, `stock`, `efficiency`, `sup_cnt`, `store_cnt` 순서다.
  - 카드 클릭은 상세 모달 열기이고, checkbox 변경은 선택 토글이다. 이벤트 중첩으로 선택/상세가 의도와 다르게 동시에 동작하지 않는지 확인한다.
- 공유 자산 변경 알림:
  - 포인트/효율 산식 또는 응답 키 변경은 data-agent와 all/ranking 회귀가 필요하다.
  - 하단 액션바 위치/표시 조건 변경은 모바일 화면과 다른 인기컬러 탭 전환 회귀가 필요하다.
  - VMD 저장 기능을 실제로 추가하려면 vmd-agent 경계와 별도 API/DB 승인 필요성을 메인에 보고한다.
- 피드백은 `.claude/memory/domain/color-trend-feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
