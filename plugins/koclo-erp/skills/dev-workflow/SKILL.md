---
name: dev-workflow
description: Use when 운영 코드(backend/**·frontend/**)를 바꾸는 요청을 받았을 때 — 코드를 쓰기 전에 호출한다. 기능추가·기능수정·버그해결 어느 것이든 해당한다. 트리거 — "기능 추가해", "이거 수정해", "버그 고쳐", "안 돼", "에러 나", "/design", "작업 모드", 또는 PreToolUse 훅 design-gate.sh 가 편집을 차단했을 때.
---

# dev-workflow — 개발 작업 3모드 절차

> **요청을 받으면 즉시 코드를 작성하지 않는다.** 먼저 모드를 분류하고, 설계를 제시하고, 승인을 받는다.
> 이 스킬은 **메인 Claude가 따르는 절차서**다. 구현은 기존 탭 에이전트, 리뷰는 `code-review-*`,
> 마감 검증은 `post-verification` 스킬을 **재사용**한다 — 여기서 재서술하지 않는다.
> 강제: `PreToolUse` 훅 `.claude/hooks/design-gate.sh` 가 승인 전 `backend/**`·`frontend/**` 편집을 차단한다.

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/dev-workflow/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/flow.md` | §1 · §5 | 스텝을 진행할 때 · 구현을 넘길 때 |
| `references/gate-ops.md` | §4 · §7 | 승인 후 게이트를 열 때 · 다른 절차와 헷갈릴 때 |
| `references/routing.md` | §0 | 모드를 분류하고 설계를 맡길 때 |
| `references/step-banner.md` | §1 | **③ 설계를 출력하기 전에** (① 분류 배너는 §2 템플릿만으로 낼 수 있다) |
| `forms/approval-gate.md` | §3 | 코드 작성 전 필수 출력 |
| `forms/completion.md` | §6 | 작업을 마치고 |
| `forms/mode-classify.md` | §2 | 첫 응답에서 |
| `forms/step-banner.md` | §1 | 모든 스텝 출력 직전 |
| `examples/step-banner.md` |  | 양식이 채워진 결과가 헷갈릴 때 |

## 0. 모드 ↔ 전담 에이전트 매핑

→ `references/routing.md`.

## 1. 작업 흐름과 스텝 배너

→ `references/flow.md`.

## 2. 모드 분류 (첫 응답에서 반드시)

→ `forms/mode-classify.md`.

## 3. 승인 게이트 템플릿 (코드 작성 전 필수 출력)

→ `forms/approval-gate.md`.

## 4. 게이트 개방·잠금 (승인 후에만)

→ `references/gate-ops.md`.

## 5. 구현 위임 (새 구현 에이전트를 만들지 않는다 — DRY)

→ `references/flow.md`.

## 6. 완료 보고 (작업 후 필수)

→ `forms/completion.md`.

## 7. 다른 절차와의 경계

→ `references/gate-ops.md`.

## 8. 작업 전 필독

- `.claude/memory/meta/agent_kernel.md` (§1 피드백·§2 절대금지·§3 보고형식·§4 경로규약)
- `.claude/memory/meta/dev-workflow.md` (이 절차의 배경·게이트 운용)
- `.claude/memory/domain/dev-workflow-feedback.md` (F 교훈)
- 변경이 닿는 탭의 `.claude/memory/domain/*.md` · `service/*-architecture.md`
