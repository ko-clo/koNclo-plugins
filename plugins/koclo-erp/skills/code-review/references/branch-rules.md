# code-review — base·merge-base 규칙과 worktree 안전장치 (§2 · §3)

> 본체 `SKILL.md` 에서 분리. 리뷰 범위를 잡을 때에 읽는다.

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
