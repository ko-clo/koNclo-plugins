---
description: 지급율 관리 탭 에이전트 목록 표시 · 직접 호출 라우팅
argument-hint: "[서브탭/영역 또는 요청 내용] (생략 시 에이전트 목록 표시)"
---
사용자가 `/payrate $ARGUMENTS` 를 실행했다. 지급율 관리 탭(`/payrate`, `PayrateOverviewView.js`) 작업을 전담 에이전트로 위임하는 진입점이다.
라우팅·회귀검증은 `payrate` 스킬, 업무규칙은 `${CLAUDE_PLUGIN_ROOT}/skills/payrate/references/domain.md`, 구조는 `${CLAUDE_PLUGIN_ROOT}/skills/payrate/references/architecture.md` 를 따른다.

## 인자가 **없을 때** (`/payrate` 단독) — 에이전트 목록 표시
아래 표를 **그대로 출력**하고, "번호·영역·에이전트명 중 무엇으로든 지정하면 바로 위임합니다. 여러 영역이면 함께 적어주세요."라고 안내한 뒤 선택을 기다린다. (임의로 먼저 호출하지 않는다.)

| # | 영역 | 에이전트 | 담당 |
|---|---|---|---|
| 1 | 오버뷰 서브탭 | `payrate-overview-agent` | KPI·성별 지급율·매장별 표·주간추이·역마진/무매출 |
| 2 | 지급관리 서브탭 | `payrate-management-agent` | 목표대비실적·주별추이·이동평균·고액외상 |
| 3 | 본사물류 서브탭 | `payrate-logistics-agent` | 물류/직거래 6지표·흐름도·본사지급·물류vs직거래 |
| 4 | 백엔드/데이터 | `payrate-data-agent` | 지급율 계산·SQL·`/api/payrate/overview` 응답 스키마·DB |

> 이 탭은 **단일 API·단일 View 파일**이라 결합도가 높다. 응답 스키마·공통부·공유 위젯 변경은 `payrate` 스킬 §2대로 영향 영역을 함께 위임한다.
> ⚠️ 별개 탭 **지급관리**(`/payment`, 자동지급/영수증OCR)는 `auto-payment-agent` 소관 — 여기 아님.

## 인자가 **있을 때** (`/payrate <요청>`) — 직접 라우팅
1. `$ARGUMENTS` 에서 대상 영역(들)을 위 표로 식별한다. 모호하면 AskUserQuestion 1회.
2. 식별된 에이전트를 **Agent 도구로 즉시 위임**(요청 원문 + 관련 파일 컨텍스트). 여러 영역이면 **단일 메시지 병렬 위임**.
3. 응답 스키마/공통부 변경이면 소비 서브탭을 추가 위임하거나 메인이 조정.
4. 작업 후 `payrate` 스킬 §3 회귀(import 스모크·3탭 렌더·분자/분모 동일기간·밴딩 일치·콘솔 0)로 검증.

예) `/payrate 역마진 표 정렬 바꿔` → overview 단독 · `/payrate 지급율 분모 SQL 수정` → data(+소비 서브탭 회귀) · `/payrate 응답에 신규 지표 추가` → data + 3 서브탭 병렬.
