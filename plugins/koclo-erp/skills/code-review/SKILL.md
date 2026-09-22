---
name: code-review
description: Use when 특정 브랜치/PR의 수정·추가 로직을 정밀검사해야 할 때. 트리거 — "코드리뷰", "코드 리뷰", "/pr-review", "이 브랜치 리뷰", "PR 리뷰", "리뷰해줘", "변경분 검사", "머지 전 점검". (빌트인 code-review 와 별개 — 이 스킬은 KOCLO 전용 브랜치 리뷰 절차서)
---

# KOCLO 코드리뷰 — 라우팅 스킬

> 코드리뷰 요청이 오면 **대상 브랜치를 worktree로 격리**하고, base 와의 **merge-base 이후 변경분만** 정밀검사한다.
> 이 스킬은 **메인 Claude가 따르는 절차서**다: 격리 → diff 산출 → 4개 전담 에이전트 병렬 위임 → 통합·등급화 → 채팅 요약 + 마크다운 리포트 → worktree 정리.
> 검사 차원·체크리스트·심각도 기준은 `.claude/memory/service/code-review-architecture.md` 를 정본으로 따른다.

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/code-review/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/branch-rules.md` | §2 · §3 | 리뷰 범위를 잡을 때 |
| `references/flow.md` | §1 | 리뷰를 진행할 때 |
| `references/report.md` | §4 · §5 | 판정하고 리포트를 쓸 때 |
| `references/routing.md` | §0 | 어느 차원을 돌릴지 고를 때 |

## 0. 검사 차원 ↔ 에이전트 매핑

→ `references/routing.md`.

## 1. 작업 흐름

→ `references/flow.md`.

## 2. base / merge-base 규칙

→ `references/branch-rules.md`.

## 3. worktree 안전장치 (확정 방식)

→ `references/branch-rules.md`.

## 4. 심각도 등급 & 종합 판정

→ `references/report.md`.

## 5. 리포트 출력

→ `references/report.md`.

## 6. 작업 전 필독

- `.claude/memory/service/code-review-architecture.md` — 차원별 체크리스트·심각도·worktree 규약(정본)
- `CLAUDE.md` — 개발 규칙(이름·예외·모듈화·DDL 정규화 기준의 근거)
- `dev-blueprint` 스킬 — 3계층(service/router/Vue) 표준 (계층 정합 판단 기준)
- 해당 탭의 `.claude/memory/service/*-architecture.md` / `domain/*.md` — 비즈니스 의도 대조용
