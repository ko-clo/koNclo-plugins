---
name: mobile-blueprint
description: Use when 임의의 탭(View)에 모바일(<=768px) 전용 뷰를 신설할 때. 트리거 — "/mobile <탭이름>", "이 탭 모바일로", "모바일 버전 만들어", "모바일 전용 뷰", "폰에서 안 보여", "탭 모바일 대응".
---

# mobile-blueprint — 탭 모바일 전용 뷰 생성기

> 한 탭에 대해 **데스크톱 뷰를 수정하지 않고** 좁은 화면 전용 뷰를 병행 투입한다.
> **구조 정본 = `.claude/memory/service/mobile-architecture.md`** (여기 내용을 중복 서술하지 않는다 — 반드시 먼저 읽는다).
> **레퍼런스 구현 = 샘플반납** `frontend/js/views/mobile/SampleReturnMobile.js`.
> 탭 개발 표준은 `dev-blueprint`, 에이전트 공통 규칙은 `.claude/memory/meta/agent_kernel.md`.

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/mobile-blueprint/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/outputs.md` |  | 파일을 만들기 전 · 경계를 확인할 때 |
| `references/procedure.md` |  | 작업을 진행하는 동안 |
| `forms/plan.md` |  | 승인용 plan 을 낼 때 |

## 산출물 (탭 1개당)

→ `references/outputs.md`.

## 절차

→ `references/procedure.md`.

## 결정 포인트 (plan 단계에서 AskUserQuestion)

→ `references/procedure.md`.

## 금지

→ `references/outputs.md`.
