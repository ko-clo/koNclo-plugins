---
name: agent-blueprint
description: Use when 임의의 탭(View)에 서브탭 단위 작업 시스템(Skill 라우팅 + 서브탭 전담 Agent + domain/architecture/feedback Memory + /command 메뉴)을 만들 때. 트리거 — "/agent-blueprint <탭이름>", "탭 에이전트 시스템 만들어", "서브탭 에이전트 구축", "이 탭도 vmd처럼".
---

# agent-blueprint — 탭 작업 시스템 생성기

> 한 탭(View)에 대해 **서브탭 단위 작업을 라우팅·위임·검증하는 3계층 시스템**을 생성한다.
> **정본 레퍼런스 = VMD 시스템**(이미 구축 완료). 그 구조·포맷을 `<tab>` 에 **그대로 복제**한다.
> 탭 개발 표준 자체는 `dev-blueprint` 스킬, 에이전트 공통 규칙은 `.claude/memory/meta/agent_kernel.md` 를 따른다(중복 서술 금지).

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/agent-blueprint/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/conventions.md` |  | 이름·형식을 정할 때 |
| `references/outputs.md` |  | 파일을 만들기 전 · 경계를 확인할 때 |
| `references/procedure.md` |  | 작업을 진행하는 동안 |

## 산출물 (탭 1개당)

→ `references/outputs.md`.

## 절차

→ `references/procedure.md`.

## 컨벤션 (VMD 정본 모방)

→ `references/conventions.md`.

## 결정 포인트 (plan 단계에서 AskUserQuestion)

→ `references/procedure.md`.

## 금지

→ `references/outputs.md`.
