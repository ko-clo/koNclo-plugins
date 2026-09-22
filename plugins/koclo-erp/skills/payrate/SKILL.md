---
name: payrate
description: Use when 지급율 탭/서브탭의 수정·조회·기능추가 요청을 받았을 때. 트리거 — "지급율", "지급율 관리", "payrate", "지급율 오버뷰", "본사물류", "역마진", "무매출", "고액외상", "물류거점", "주간추이 지급율" (별개 탭 '지급관리'/자동지급은 auto-payment 담당 — §경계)
---

# 지급율 관리 탭 작업 — 라우팅 스킬

> 지급율 관리 대시보드(`PayrateOverviewView.js`, `/payrate`)는 3개 서브탭이 **단일 API 응답 1개를 공유**하는
> 모놀리식 구조다(VMD처럼 서브탭=위젯=API 1:1이 아님). 이 스킬은 **메인 Claude가 따르는 절차서**다.
> 요청 영역 식별 → 전담 에이전트 위임(Agent 도구) → 결과 통합 → 전체 탭 회귀 검증.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다(중복 서술 금지).

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/payrate/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/delegation.md` | §2 · §5 | 위임 대상·경계를 정하기 전 |
| `references/verification.md` | §3 | 변경 후 회귀 검증할 때 |

## 0. 영역 ↔ 에이전트 ↔ 담당 매핑

| 영역 | 에이전트 | 담당 |
|---|---|---|
| 오버뷰 서브탭 | `payrate-overview-agent` | KPI·성별 지급율·매장별 표·주간추이·역마진/무매출. `PayrateStoreTable`·`PayrateAlertList`·`PayrateTrendChart`(공유) |
| 지급관리 서브탭 | `payrate-management-agent` | 목표대비실적·주별추이·이동평균·고액외상. `PayrateTrendChart`(공유) |
| 본사물류 서브탭 | `payrate-logistics-agent` | 물류/직거래 6지표·흐름도·본사/M)본사 지급·물류vs직거래. `logi`/`logiKpis` |
| 백엔드/데이터 | `payrate-data-agent` | 지급율 계산·SQL·`/api/payrate/overview` 응답 스키마. `payrate_service.py`·`payrate_router.py`·`rebuild_payrate_db.py`·DB·`api.js` |

공통 셸: `frontend/js/views/PayrateOverviewView.js`(단일 파일, `activeTab` v-show로 3 서브탭 전환 + 공통 toolbar/날짜/포맷터).

## 1. 작업 흐름
1. **요청 영역 식별** — §0 표로 어느 서브탭/백엔드인지 판별. 불명확하면 AskUserQuestion.
2. **단일 영역** → 해당 에이전트 1개 위임.
3. **여러 영역** → **병렬 위임**(단일 메시지 다중 Agent 호출).
4. **결과 통합** → 5. **전체 탭 회귀 검증**(§3).

## 2. 위임 규칙 (공유 자산 — 이 탭은 결합도가 높다)

→ 위임 대상을 정하거나 공유 자산(응답 계약·공용 API·산식)을 건드릴 때 `references/delegation.md` 를 읽는다.

## 3. 회귀 검증 (dev-blueprint 스킬 §6 게이트 재사용)

→ `dev-blueprint` 스킬 §6 게이트를 따른다. 이 탭 고유 항목은 `references/verification.md` 에 있다.

## 4. 작업 전 필독
- `.claude/memory/domain/payrate.md` — 업무 규칙·용어·서브탭 관계
- `.claude/memory/service/payrate-architecture.md` — 파일/API/DB/데이터 흐름
- `dev-blueprint` 스킬 — 탭 개발 표준
