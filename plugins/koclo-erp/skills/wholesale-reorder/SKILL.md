---
name: wholesale-reorder
description: Use when 도매 리오더 탭/영역의 수정·조회·기능추가 요청을 받았을 때. 트리거 — "도매리오더", "도매 리오더", "wholesale-reorder", "도매 탭", "리오더 카드", "분배", "이고", "회수", "실행지시 엑셀", "풀 재계산", "워크북 인입", "원천점검", "도매외부", "코스/본사 소스탭", "기주문 추적" (batch CSV *인입·cron 운영*은 batch-ingest, _vendor 빌더 *산식*은 PRD 정본 — §경계)
---

# 도매 리오더 탭 작업 — 라우팅 스킬

> 도매 리오더(`WholesaleView.js`)는 **단일 탭**(서브탭 없음)이며 **리포트·카드 표시 · 액션·재계산 · 데이터 파이프라인** 세 영역으로 본다.
> 이 스킬은 **메인 Claude가 따르는 절차서**다: 영역 식별 → 전담 에이전트 위임(Agent 도구) → 결과 통합 → 전체 탭 회귀 검증.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다(중복 서술 금지).

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/wholesale-reorder/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/delegation.md` | §2 · §경계 | 위임 대상·경계를 정하기 전 |
| `references/routing.md` | §0 | 어느 에이전트에 맡길지 고를 때 |
| `references/verification.md` | §3 | 변경 후 회귀 검증할 때 |

## 0. 영역 ↔ 에이전트 ↔ 파일 매핑

→ `references/routing.md`.

## 1. 작업 흐름

1. **요청 영역 식별** — 사용자 요청이 어느 영역(들)인지 §0 표로 판별. 불명확하면 AskUserQuestion.
2. **단일 영역** → 해당 에이전트 1개에 위임.
3. **여러 영역** → **병렬 위임**(단일 메시지에 다중 Agent 호출).
4. **결과 통합** — 각 에이전트 변경/리스크를 메인이 취합.
5. **전체 탭 회귀 검증** — §3.

## 2. 위임 규칙 (공유 자산 주의)

→ 위임 대상을 정하거나 공유 자산(응답 계약·공용 API·산식)을 건드릴 때 `references/delegation.md` 를 읽는다.

## 3. 회귀 검증 (dev-blueprint 스킬 §6 게이트 재사용)

→ `dev-blueprint` 스킬 §6 게이트를 따른다. 이 탭 고유 항목은 `references/verification.md` 에 있다.

## 4. 작업 전 필독

- `.claude/memory/domain/wholesale-reorder.md` — 업무 규칙·용어·영역 관계·경계
- `.claude/memory/domain/wholesale-reorder-feedback.md` — 누적 피드백(F1~)
- `.claude/memory/service/wholesale-reorder-architecture.md` — Vue/API/DB/데이터 흐름
- `dev-blueprint` 스킬 — 탭 개발 표준(상위 규범)
