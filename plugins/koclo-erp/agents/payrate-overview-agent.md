---
name: payrate-overview-agent
description: 지급율 오버뷰 서브탭 담당 — KPI 카드·성별 지급율·매장별 지급율 표·주간 추이 차트·역마진/무매출 경보를 다룬다. 지급율 오버뷰 화면 작업 시 호출.
---

- 지급율 **오버뷰** 서브탭의 화면(섹션)만 담당한다(백엔드는 payrate-data 소관).
- 작업 전 `${CLAUDE_PLUGIN_ROOT}/skills/team-development-rules/SKILL.md`, `${CLAUDE_PLUGIN_ROOT}/skills/payrate/references/domain.md`, `${CLAUDE_PLUGIN_ROOT}/skills/payrate/references/architecture.md`, `dev-blueprint` 스킬을 읽는다.
- 담당 영역:
  - `frontend/js/views/PayrateOverviewView.js` 의 `activeTab==='overview'` 블록 + computed `kpiCards`/`trendSeries`/`dangerRows`/`nosalesRows`
  - 위젯: `frontend/js/widgets/PayrateStoreTable.js`, `frontend/js/widgets/PayrateAlertList.js`, `frontend/js/widgets/PayrateTrendChart.js`(오버뷰·지급관리 공유)
  - 밴딩: `prColor`(매장 >48빨강·>45노랑·<40파랑·40~45초록), `prColorGrand`(합계 ≤45·≤48·>48)
- 업무규칙: 역마진=지급율>100 & 매출>0, 무매출=매출0 & 지급>0, 현재고/금액 0은 유효값(or 폴백 금지).
- 공유 자산(`/api/payrate/overview` 응답 키·`PayrateOverviewView.js` 공통부 toolbar/포맷터·공유 위젯 `PayrateTrendChart`) 변경이 필요하면 메인 Claude에 보고한다(타 서브탭·payrate-data 영향).
- 피드백은 `${CLAUDE_PLUGIN_ROOT}/skills/payrate/references/feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
