---
name: code-review
description: KOCLO 브랜치 코드리뷰 라우팅. "코드리뷰", "코드 리뷰", "/pr-review", "이 브랜치 리뷰", "PR 리뷰", "리뷰해줘", "변경분 검사", "머지 전 점검" 등 특정 브랜치/PR의 수정·추가 로직을 정밀검사하는 요청 시 호출. merge-base diff를 worktree로 격리해 4개 차원(의도·품질·계층·데이터) 전담 에이전트로 병렬 리뷰하고 통합 리포트를 생성한다. (빌트인 code-review 와 별개 — 이 스킬은 KOCLO 전용 브랜치 리뷰 절차서)
---

# KOCLO 코드리뷰 — 라우팅 스킬

> 코드리뷰 요청이 오면 **대상 브랜치를 worktree로 격리**하고, base 와의 **merge-base 이후 변경분만** 정밀검사한다.
> 이 스킬은 **메인 Claude가 따르는 절차서**다: 격리 → diff 산출 → 4개 전담 에이전트 병렬 위임 → 통합·등급화 → 채팅 요약 + 마크다운 리포트 → worktree 정리.
> 검사 차원·체크리스트·심각도 기준은 `.claude/memory/service/code-review-architecture.md` 를 정본으로 따른다.

## 0. 검사 차원 ↔ 에이전트 매핑

| # | 차원 | 에이전트 | 담당 검사 (요청 검사내용 매핑) |
|---|---|---|---|
| 0 | 의도·비즈니스 | `code-review-intent-agent` | **왜 수정/추가했는지** — 커밋메시지·도메인 메모리 대조, 의도 대비 구현 정합, 요구 누락/과잉, 회귀 위험 |
| 1 | 코드 품질 | `code-review-quality-agent` | **기본 리뷰 절차** — 에러 요소, 예외 처리, 리팩토링·네이밍·매직값, 책임 분리(CLAUDE.md 개발규칙) + **보안·시크릿·주입**(하드코딩 비밀·SQL 인젝션·민감정보 노출·인증 우회) ⭐ |
| 2 | 계층(step) | `code-review-layer-agent` | **각 step 체크** — UI(Vue)↔API(router)↔DB IO(service/SQL) 계약 정합, 누락 계층, **기대값(결과값)** 정합 + import 스모크 |
| 3 | 데이터·스키마 | `code-review-data-agent` | **DDL/DML** — 정규화, FK/UNIQUE/인덱스, 마이그레이션 안전성, 데이터 영향 + **배포·마이그레이션 정합**(ORM↔DDL 존재·운영DB 선적용) + **인입 포맷 가드**(컬럼 밀림 방어) ⭐ |

> diff에 해당 차원이 **전혀 없으면** 그 에이전트는 생략한다(예: 프론트만 바뀌면 data-agent 스킵). 어느 차원이 걸리는지는 §2의 diff 분류로 판단.

## 1. 작업 흐름

1. **입력 파싱** — `$ARGUMENTS` 에서 대상(브랜치명 | PR번호 | 생략=현재 브랜치)과 base override(`onto <base>`)를 추출.
2. **base 결정** — 기본 `develop`. `onto <base>` 가 있으면 그것. PR번호면 PR target 브랜치를 base로.
3. **merge-base 산출** — §2.
4. **worktree 격리** — §3. 대상 브랜치를 임시 worktree에 detach 체크아웃(현재 워킹트리 무손상).
5. **변경 분류** — diff 파일을 프론트/라우터/서비스·SQL/DDL·스크립트로 분류해 위임할 차원 선택.
6. **병렬 위임** — 선택된 에이전트를 **단일 메시지로 병렬 호출**. 각 에이전트에 `{worktree 경로, base, branch, merge-base, 변경 파일 목록, 요청 원문}` 전달.
   - 위임 프롬프트 끝에 **"최종 메시지에 발견사항 전문을 담아라. '완료'로 끝내지 말 것"**을 명시한다(에이전트 정의에도 MUST로 박혀 있으나 재강조).
   - **폴백**: 에이전트가 "완료" 등 본문 없는 짧은 답만 반환하면, ① SendMessage로 "발견사항 전문 재출력" 1회 요청, ② 그래도 비면 해당 에이전트 transcript(`tasks/<agentId>.output` JSONL)에서 `## 코드리뷰`/등급 이모지 포함 assistant 텍스트 블록을 추출해 회수한다.
7. **통합·등급화** — 각 에이전트의 발견사항을 dedup·병합하고 심각도(§4) 부여, 종합 판정 산출.
8. **리포트 출력** — 채팅 요약 + 마크다운 리포트 파일(§5).
9. **정리** — §3 cleanup. worktree 제거.

## 2. base / merge-base 규칙

```bash
BASE=${base:-develop}                       # onto <base> 없으면 develop
MB=$(git merge-base "$BASE" "$BRANCH")       # 공통조상
git diff --stat "$MB".."$BRANCH"             # 변경 요약
git diff "$MB".."$BRANCH"                    # 정밀 검사 대상 (이것만 리뷰)
```

- **merge-base 이후 변경분만** 리뷰한다 — base가 그동안 앞서 나간 커밋은 노이즈로 섞지 않는다(`..` 2-dot diff가 정확히 이 범위).
- diff는 메인 repo에서 산출 가능(worktree 불필요). worktree는 에이전트가 **브랜치 상태의 전체 파일 컨텍스트·import 스모크**를 보기 위함.
- 변경 파일 분류:
  - `frontend/js/**` → 계층(layer)
  - `backend/app/routers/**` → 계층(layer)
  - `backend/app/services/**`, `backend/scripts/**`, `*.sql`, `text("""...""")` 쿼리 → 계층 + 데이터
  - `CREATE/ALTER/DROP TABLE`, `init.sql`, 마이그레이션 → 데이터(DDL)
  - 전 차원에 **의도·품질**은 항상 포함.

## 3. worktree 안전장치 (확정 방식)

```bash
SHORT=$(git rev-parse --short "$MB")
SAFE=$(echo "$BRANCH" | tr '/' '-')
WT=".git/cr-worktrees/${SAFE}-${SHORT}"
git worktree add --detach "$WT" "$BRANCH"     # 현재 체크아웃 손실 없음
# ... 리뷰 ...
git worktree remove "$WT" --force             # 종료 시 항상
git worktree prune                            # 잔여 정리
```

- **절대 `git checkout`/`switch` 로 현재 브랜치를 바꾸지 않는다** (CLAUDE.md: 브랜치 전환 승인 필요). worktree만 사용.
- 에이전트는 worktree 안에서 **읽기·import 스모크·read-only 검증만**. 파일 수정·커밋·운영 DB/NAS 접근 금지(danger/NAS 규칙).
- PR번호 입력 시: `gh pr checkout` 대신 `gh pr view <n> --json headRefName,baseRefName` 로 브랜치명만 얻어 위 흐름에 태운다(원격이면 먼저 `git fetch origin <headRef>`).
- 리뷰 도중 실패해도 **반드시 cleanup**(worktree remove + prune) 실행.

## 4. 심각도 등급 & 종합 판정

| 등급 | 의미 |
|---|---|
| 🔴 Blocker | 머지 불가 — 버그·데이터 손상·정규화 위반·계층 계약 깨짐·예외 미처리로 인한 장애 |
| 🟠 Major | 머지 전 수정 권장 — 비즈니스 로직 오류 가능성, 누락 예외, 회귀 위험 |
| 🟡 Minor | 개선 권장 — 리팩토링, 네이밍, 매직값, 중복 |
| ⚪ Nit | 취향·사소 — 선택 반영 |

종합 판정: Blocker 1개↑ = **Changes Requested**. Major만 = **Conditional**. Minor/Nit만 = **Approve (with comments)**.

각 발견사항 출력 스키마(에이전트 공통):
`{차원, 파일:라인, 등급, 무엇이/왜 문제, 근거(코드 인용), 수정 제안}`

## 5. 리포트 출력

- **채팅**: 종합 판정 + 등급별 발견사항 요약 표(파일:라인·한 줄 설명). kernel §3 보고 형식.
- **파일**: `docs/reviews/<branch-sanitized>_<MBshort>.md` 에 차원별 전체 발견 + 코드 인용 상세본.
  - *docs/ 는 명시적 "리뷰 커밋해" 지시 전까지 커밋하지 않는다(파일 생성만).*

## 6. 작업 전 필독

- `.claude/memory/service/code-review-architecture.md` — 차원별 체크리스트·심각도·worktree 규약(정본)
- `CLAUDE.md` — 개발 규칙(이름·예외·모듈화·DDL 정규화 기준의 근거)
- `dev-blueprint` 스킬 — 3계층(service/router/Vue) 표준 (계층 정합 판단 기준)
- 해당 탭의 `.claude/memory/service/*-architecture.md` / `domain/*.md` — 비즈니스 의도 대조용

## 7. koNclo-plugins 동기화

- 이 스킬·커맨드·에이전트 파일은 PostToolUse `sync-plugins.sh` 훅이 `../koNclo-plugins/plugins/koclo-erp/` 로 자동 미러(working tree 복사). plugins 측 커밋은 별도 수행(자동 안 함).
