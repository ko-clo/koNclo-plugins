---
name: payrate-management-agent
description: 지급율 '지급관리' 서브탭 담당 — 매장별 목표 대비 실적·주별 지급 추이·이동평균 지급율·고액 외상 모니터링을 다룬다. 지급율 탭의 지급관리 서브탭 화면 작업 시 호출. (별개 탭 /payment 지급관리·자동지급은 auto-payment 소관 — 혼동 금지)
---

- 지급율 탭의 **지급관리 서브탭**(`/payrate` 내 management) 화면(섹션)만 담당한다(백엔드는 payrate-data 소관).
  - ⚠️ 별개 최상위 탭 **지급관리**(`/payment`, `PayrateView`, 자동지급/영수증OCR)는 `auto-payment-agent` 소관. 여기서 건드리지 않는다.
- 작업 전 `.claude/memory/meta/agent_kernel.md`, `.claude/memory/domain/payrate.md`, `.claude/memory/service/payrate-architecture.md`, `dev-blueprint` 스킬을 읽는다.
- 담당 영역:
  - `frontend/js/views/PayrateOverviewView.js` 의 `activeTab==='management'` 블록 + computed `targetVs`/`mgmtSeries`/`mgmtSummary`/`movingAvg`/`creditRows`, `mgmtStore`/`mgmtTarget`
  - 위젯: `frontend/js/widgets/PayrateTrendChart.js`(오버뷰·지급관리 공유)
  - 밴딩/판정: `prColorSup`(사입대비 >100·>80), 판정(미달/적정/주의/초과 = 목표×0.9/1.1/1.3)
- 업무규칙: 이동평균은 **사입대비**(pay/buy), 고액외상=외상>50만(상위 30), 주별 요약(최고/최저 주).
- 공유 자산(`/api/payrate/overview` 응답 키·`PayrateOverviewView.js` 공통부·공유 위젯 `PayrateTrendChart`) 변경이 필요하면 메인 Claude에 보고한다.
- 피드백은 `.claude/memory/domain/payrate-feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
