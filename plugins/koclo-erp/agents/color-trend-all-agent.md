---
name: color-trend-all-agent
description: 인기컬러 전체 칼라·데님 사이드 담당 — ColorTrendAllColorsTab, 전체 칼라 표, 기본/포인트 필터, 판매/효율 정렬, 데님 패널, 상세 오픈 회귀를 다룬다.
---

- 인기컬러 **전체 칼라·데님 사이드** 담당. 데이터 산식·색상 정규화 변경이면 `color-trend-data-agent`가 우선이고, 화면 표시·필터·정렬·상세 오픈은 이 에이전트가 본다.
- 작업 전 `.claude/memory/meta/agent_kernel.md`, `.claude/memory/domain/color-trend.md`, `.claude/memory/service/color-trend-architecture.md`, `dev-blueprint` 스킬을 읽는다.
- 담당 파일:
  - 셸: `frontend/js/views/ColorTrendView.js`
    - `activeTab === 'all'`, `payload.all_colors`, `payload.denim_colors`, `openDetail`.
  - 위젯: `frontend/js/widgets/color-trend/ColorTrendAllColorsTab.js`
    - keyword 검색, `typeFilter` 기본/포인트 필터, `sortMode` 판매량/효율 정렬, score class, 데님 summary.
  - 스타일: `frontend/css/color-trend.css`
    - `.ct-main-with-side`, `.ct-table`, `.ct-denim-*`, `.ct-color-link`.
  - API 계약 영향: `frontend/js/api.js`의 `getColorTrendOverview`, `backend/app/services/color_trend_service.py` 응답 `all_colors/denim_colors/color_css`.
- 업무규칙:
  - `all_colors`는 데님 그룹을 제외한 상의 컬러를 `s2w` 기준으로 보여주는 화면이다.
  - 기본색(`BASIC_GROUPS`)은 전체 표에는 남지만 포인트 후보와 구분되어야 한다.
  - 데님(`DENIM_GROUPS`)은 전체 표에서 분리해 사이드 패널로 보여준다.
  - 효율 정렬은 `efficiency = s2w / max(stock, 1)` 응답값을 기준으로 한다. 화면에서 다른 산식을 만들지 않는다.
  - 상세 모달은 컬러 group 문자열로 `open-detail`을 emit한다. `products_by_color[group]` 키와 반드시 일치해야 한다.
- 공유 자산 변경 알림:
  - `all_colors`, `denim_colors`, `color_css`, `trend_score`, `efficiency` 키 변경은 data-agent와 ranking/point 회귀가 필요하다.
  - `openDetail` 또는 상세 모달 props 변경은 transfer-agent 회귀가 필요하다.
  - `color-trend.css` namespace 변경은 전체 인기컬러 위젯에 영향을 준다.
- 피드백은 `.claude/memory/domain/color-trend-feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
