---
name: vmd
description: Use when VMD 탭/서브탭의 수정·조회·기능추가 요청을 받았을 때. 트리거 — "VMD", "행거탭", "행거 대시보드", "행거 조정", "기온 시즌", "월별 수량", "검증 조정", "VMD 오버뷰", "VMD 서브탭"
---

# VMD 탭 작업 — 라우팅 스킬

> VMD 행거 대시보드(`VmdView.js`)는 5개 서브탭으로 구성된다. 이 스킬은 **메인 Claude가 따르는 절차서**다.
> 서브탭을 식별 → 전담 에이전트로 위임(Agent 도구) → 결과 통합 → 전체 탭 회귀 검증.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다(중복 서술 금지).

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/vmd/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/delegation.md` | §2 · §경계 | 위임 대상·경계를 정하기 전 |
| `references/routing.md` | §0 | 어느 에이전트에 맡길지 고를 때 |
| `references/verification.md` | §3 | 변경 후 회귀 검증할 때 |

## 0. 서브탭 ↔ 에이전트 ↔ 파일 매핑

→ `references/routing.md`.

## 1. 작업 흐름

1. **요청 서브탭 식별** — 사용자 요청이 어느 서브탭(들)인지 §0 표로 판별. 불명확하면 AskUserQuestion.
2. **단일 서브탭** → 해당 에이전트 1개에 위임.
3. **여러 서브탭** → **병렬 위임**(단일 메시지에 다중 Agent 호출).
4. **결과 통합** — 각 에이전트 변경/리스크를 메인이 취합.
5. **전체 탭 회귀 검증** — §3.

## 2. 위임 규칙 (공유 자산 주의)

→ 위임 대상을 정하거나 공유 자산(응답 계약·공용 API·산식)을 건드릴 때 `references/delegation.md` 를 읽는다.

## 3. 회귀 검증 (dev-blueprint 스킬 §6 게이트 재사용)

→ `dev-blueprint` 스킬 §6 게이트를 따른다. 이 탭 고유 항목은 `references/verification.md` 에 있다.

## 4. 작업 전 필독

- `.claude/memory/domain/vmd.md` — 업무 규칙·용어·서브탭 관계
- `.claude/memory/service/vmd-architecture.md` — Vue/API/DB/데이터 흐름
- `dev-blueprint` 스킬 — 탭 개발 표준(상위 규범)
