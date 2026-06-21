---
description: KOCLO 브랜치 코드리뷰 — 대상 브랜치를 worktree 격리하고 merge-base 변경분을 4차원(의도·품질·계층·데이터) 병렬 정밀검사 후 통합 리포트 생성
argument-hint: "[브랜치|PR번호] [onto <base>] (생략 시 현재 브랜치, base 생략 시 develop)"
---
사용자가 `/pr-review $ARGUMENTS` 를 실행했다. 특정 브랜치/PR의 **수정·추가된 로직**을 정밀 코드리뷰하는 진입점이다.
절차·검사 차원·심각도·worktree 규약은 `code-review` 스킬, 체크리스트 정본은 `.claude/memory/service/code-review-architecture.md` 를 따른다.

## 인자가 **없을 때** (`/pr-review` 단독) — 사용법·차원 표시

아래를 **그대로 출력**하고 대상 브랜치를 묻는다(임의로 현재 브랜치를 리뷰하지 않는다).

```
/pr-review <브랜치|PR번호> [onto <base>]
  예) /pr-review feature/x            → feature/x 를 develop 과의 merge-base 기준 리뷰
      /pr-review feature/x onto main  → base 를 main 으로
      /pr-review 123                  → PR #123 (PR target 을 base 로)
```

| # | 차원 | 에이전트 | 담당 |
|---|---|---|---|
| 0 | 의도·비즈니스 | `code-review-intent-agent` | 왜 수정/추가했는지, 의도 대비 구현 정합, 회귀 위험 |
| 1 | 코드 품질 | `code-review-quality-agent` | 에러·예외 처리·리팩토링·네이밍·매직값·책임 분리 |
| 2 | 계층(step) | `code-review-layer-agent` | UI↔API↔DB IO 계약 정합, 기대값 정합, import 스모크 |
| 3 | 데이터·스키마 | `code-review-data-agent` | DDL/DML 정규화·FK/인덱스·마이그레이션 안전성 |

## 인자가 **있을 때** (`/pr-review <대상>`) — 즉시 리뷰

1. `$ARGUMENTS` 에서 대상(브랜치|PR번호)과 `onto <base>`(생략 시 `develop`)를 추출. 모호하면 AskUserQuestion 1회.
2. `code-review` 스킬 §1 흐름 실행: base/merge-base 산출 → worktree 격리(§3) → diff 분류 → **해당 차원 에이전트 병렬 위임**(단일 메시지) → 통합·등급화 → 채팅 요약 + `docs/reviews/<branch>_<MBshort>.md` 리포트.
3. **종료 시 worktree 정리 필수**(스킬 §3 cleanup). 현재 작업 브랜치는 절대 전환하지 않는다.

예) `/pr-review feature/best-tab` → 프론트+서비스 변경이면 intent·quality·layer·data 4종 병렬. 프론트 위젯만이면 data-agent 생략.
