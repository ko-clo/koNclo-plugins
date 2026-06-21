---
name: payrate-logistics-agent
description: 지급율 본사물류 서브탭 담당 — 물류거점 vs 직거래 6지표·물류 흐름도·물류거점 본사 지급·전매장 본사/M)본사 거래·물류vs직거래 비교를 다룬다. 지급율 탭의 본사물류 화면 작업 시 호출.
---

- 지급율 **본사물류** 서브탭의 화면(섹션)만 담당한다(백엔드는 payrate-data 소관 — 본사물류는 API 추가 없이 같은 응답을 프론트에서 재구성).
- 작업 전 `.claude/memory/meta/agent_kernel.md`, `.claude/memory/domain/payrate.md`, `.claude/memory/service/payrate-architecture.md`, `dev-blueprint` 스킬을 읽는다.
- 담당 영역:
  - `frontend/js/views/PayrateOverviewView.js` 의 `activeTab==='logistics'` 블록 + computed `logi`/`logiKpis`
  - 상수: `LOGISTICS_STORES`(삼산·성남·코아울산·코아서울·홍대)·`isLogiStore` — 정본 `rebuild_payrate_db.py:109`
- 업무규칙: 물류거점 5매장 vs 직거래 3매장(서면·마산·창원), 본사 허브/홍대 허브(코아서울=홍대 허브) 분류, 본사/`M)본사` 사입처 지급 재구성, 이고=즉시지급·반품=마이너스지급.
- 본사물류는 `data.value.stores[]`(+`suppliers[]` 본사/M)본사)에서 **프론트 재구성**이므로, 새 집계가 필요하면 응답 스키마 변경 → payrate-data 위임 필요. 메인 Claude에 보고한다.
- 피드백은 `.claude/memory/domain/payrate-feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
