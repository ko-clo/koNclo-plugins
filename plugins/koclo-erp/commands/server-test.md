---
description: 로컬 워킹트리 변경분을 NAS dev(koclo-dev/develop)에 임시 반영해 테스트 (배포 아님)
argument-hint: "(인자 없음) | --files 경로1,경로2"
---
사용자가 `/server-test $ARGUMENTS` 를 실행했다. **현재 로컬 워킹트리의 변경분**을 NAS 개발
환경 `/Volume1/docker/koclo-dev`(브랜치 `develop`) 에 **임시로 오버레이**해 서버에서 동작을
확인한다. 이건 정식 배포가 아니라 일시 반영이며, 끝나면 `/server-clear` 로 원복한다.

## 🚫 절대 금지 (어기면 즉시 중단)
- **git add / commit / push 금지.** dev 레포에 커밋·푸시·태그·브랜치 변경을 하지 않는다.
  파일만 워킹트리에 덮어쓴다. (`git revert` 도 커밋을 만들므로 금지.)
- **PROD 반영 절대 금지.** 대상 경로가 `testerp`(`/volume1/docker/testerp` 등) 를 포함하거나
  브랜치가 `main`/`master` 이면 **즉시 중단**한다. 오직 `koclo-dev` + `develop` 만 허용.
- 로컬→dev **단방향**. dev 의 내용을 로컬로 끌어오지 않는다.

## 전제 — NAS 게이트 (이 명령이 자동으로 연다)
`100.99.51.88` 접속이므로 NAS 게이트가 필요하다. 이 명령은 **먼저 게이트를 30분 연다**:
```
EXP=$(( $(date +%s) + 1800 )); echo "$EXP" > .claude/.nas-unlock
```
"✅ NAS 게이트 30분 오픈" 한 줄 출력. (작업 후 `/server-clear` 또는 `/nas off` 로 닫는다.)

## SSH / 경로 (실측값 — 2026-06)
- 접속: `ssh -p 2323 -i "$HOME/.ssh/id_rsa" saykim4195@100.99.51.88` (SSH/post-quantum 경고줄은
  `2>/dev/null` 또는 grep 필터). 접속 실패 시 계정/키 확인받고 중단(임의 계정 시도 금지).
  - ⚠ 키 경로에 `~` 를 **큰따옴표 안에서 쓰지 말 것** — 틸드가 확장 안 돼 인증 실패한다.
    반드시 `$HOME/.ssh/id_rsa` (또는 절대경로) 사용.
- docker: PATH 에 없음 → `sudo -n /usr/local/bin/docker`. dev 컨테이너 = `koclo_erp-dev-app`.
- dev 경로: **`/volume1/docker/koclo-dev`** (소문자 실측). 이하 `<DEV>`.
- ⚠ dev 레포는 소유자 root(perm 777) → git 이 `dubious ownership` 으로 거부한다. **모든 dev git
  명령에 `git -c safe.directory="<DEV>" -C "<DEV>" ...` 인라인 플래그를 붙인다**(NAS 설정 변경 없이 우회).
  디렉터리는 world-writable 이라 saykim4195 로 파일 쓰기는 가능.

## 실행 절차

### 1) dev 경로·브랜치 검증 (읽기 전용, prod 가드)
```
ssh -p 2323 -i "$HOME/.ssh/id_rsa" saykim4195@100.99.51.88 2>/dev/null \
  'P=/volume1/docker/koclo-dev; [ -d "$P" ] || { echo "NO_PATH"; exit 0; };
   echo "PATH=$P"; git -c safe.directory="$P" -C "$P" branch --show-current'
```
- `NO_PATH` → 중단.
- `PATH` 가 `testerp` 를 포함하면 **중단(PROD 가드)**.
- 브랜치가 `develop` 이 아니면 **경고하고 중단**(브랜치를 바꾸지 않는다).

### 2) dev 워킹트리 사전 상태 기록 (clear 안전판용)
```
ssh ... 2>/dev/null 'git -c safe.directory=<DEV> -C <DEV> status --porcelain'
```
- 출력이 비어있지 않으면(이미 더티) 그 파일 목록을 매니페스트의 `PRE_DIRTY` 로 보관한다.
  (반영 전부터 dev 에 있던 변경 → `/server-clear` 가 이걸 우리 변경과 구분해 보호한다.)

### 3) 반영할 로컬 파일 집합 산출
- 인자 `--files a,b` 가 있으면 그 목록만.
- 없으면 **워킹트리 변경분**:
  - 추적 수정: `git diff --name-only HEAD`
  - 미추적 신규: `git ls-files --others --exclude-standard`
  - **제외**: `.claude/` (내부 상태), `.git/`.
- 집합이 비면 "반영할 변경 없음" 출력하고 종료(게이트는 열어둔 채 안내).
- 목록을 임시 파일 `.claude/.server-test-files` 에 한 줄씩 기록.

> ⚠ **"워킹트리 변경분" ≠ "내 변경분".** 이 레포는 worktree 4개를 동시에 쓰고, 한 워킹트리에
> **여러 작업의 미커밋 변경이 공존하는 게 정상**이다(세션 시작 시점의 `gitStatus: (clean)`
> 스냅샷은 세션 중 갱신되지 않으므로 근거로 쓸 수 없다). dev 는 공유 자원이고
> `backend/app/**` 이 하나라도 끼면 6) 에서 컨테이너 재시작까지 자동 수행된다 —
> 남의 미완성 코드를 올리고 재시작하면 공유 dev 가 통째로 죽는다(2026-08-03: 다른 세션의
> `main.py` 가 라우터 4개 import 를 제거한 중간 상태였다).
> **그래서 오버레이 전에 반드시**: ① `git status --short` 전체 목록을 뽑고 ② **이번 세션에
> 내가 편집한 파일과 대조**해 ③ 남는 게 있으면 `git diff HEAD -- <file>` 로 성격을 확인한 뒤
> ④ **내 파일만 목록에 넣는다.** 제외한 파일과 이유는 보고에 반드시 남긴다.

### 4) 오버레이 — tar-over-ssh (단방향, no delete)
rsync 의 `-e` 가 띄우는 ssh 가 이 환경에서 키 인증에 실패하는 사례가 있어, **확실히 되는 단일
ssh 에 tar 를 파이프**한다(경로구조 보존, 목록 외 파일은 건드리지 않음):
```
tar -czf - -T .claude/.server-test-files | \
  ssh -p 2323 -i "$HOME/.ssh/id_rsa" saykim4195@100.99.51.88 \
  'tar -xzf - -C <DEV>/ && echo EXTRACT_OK'
```
- `EXTRACT_OK` 안 나오면 원인 보고 후 중단. (rsync 를 쓰려면 `-e "ssh ... -i $HOME/..."` 로 키
  경로의 `~` 확장 문제를 피하고 `--delete` 는 절대 쓰지 말 것.)

### 5) 매니페스트 기록 (clear 가 읽는다)
`.claude/.server-test-manifest` 에 아래를 쓴다:
```
DEV_PATH=<DEV>
BRANCH=develop
TS=<date +%s>
PRE_DIRTY=<2)에서 더티였던 경로들, 공백구분 / 없으면 빈칸>
DEPLOYED=
<3)의 파일 목록 한 줄씩>
```

> ⚠ **매니페스트는 오버레이할 때마다 함께 갱신한다.** `DEPLOYED` 는 `.server-test-files` 와
> **항상 같아야** 한다 — 여기 없는 파일은 `/server-clear` 가 되돌리지 못하고 dev 에 남는다.
> **한 세션에서 파일을 추가해 다시 올릴 때는 덮어쓰지 말고 이전 `DEPLOYED` 와 합집합**으로
> 기록한다(2026-08-03: 2차 오버레이 때 갱신을 빠뜨려 `PostProcessPurchaseCut.js` 가
> 매니페스트에서 누락됐다). 목록을 바꿨으면 tar 대상과 매니페스트를 **같은 단계에서** 쓴다.

### 6) 컨테이너 반영 (필요하면 재시작까지 이 명령이 끝낸다)
- dev 컨테이너 = `koclo_erp-dev-app`. (해석 시 `docker ps --format '{{.Names}}' | grep koclo_erp-dev`.)
- 실측 마운트: `frontend` `backend/app` `backend/scripts` `configs` 모두 **bind-mount(ro)**.
  반영 방식이 경로마다 다르니 **반영 파일 목록으로 판단**한다:

  | 경로 | 반영 | 재시작 |
  |---|---|---|
  | `frontend/**` (js·html·css) | 즉시 | 불필요 |
  | `backend/scripts/**` | 즉시 (`docker exec python3 …` 가 매번 새 프로세스) | 불필요 |
  | `configs/**` | 즉시(읽는 시점에 로드) | 불필요 |
  | **`backend/app/**`** (FastAPI) | uvicorn 이 기동 시 1회 import | **필요** |

- **`backend/app/` 하위 파일이 반영 목록에 하나라도 있으면 재시작을 수행한다.**
  ```
  ssh … 'sudo -n /usr/local/bin/docker restart koclo_erp-dev-app'
  ```
  `/server-test` 실행 자체가 "dev 에 반영해 확인하라"는 승인이므로 **재시작을 따로 다시 묻지 않는다.**
  재시작한 사실과 대상 컨테이너는 보고에 명시한다. (`backend/app/` 변경이 없으면 재시작하지 않는다 —
  불필요한 재시작으로 dev 세션을 끊지 않는다.)
- 재시작이 필요한 이유: dev/prod 모두 uvicorn `--reload` 를 제거했다(2026-07-28, compose 주석 참조).
  `--reload-dir` 이 cwd 하위면 uvicorn 이 그 값을 버리고 `/app` 전체를 감시하는데, `/app` 은 NAS
  바인드 마운트라 호스트 공유 inotify 한도(8192)를 고갈시켜 **리로더가 기동 즉시 죽고** 겉보기엔
  정상인 채 구코드를 서빙했다(2회 발생). 그래서 "붙었지만 안 도는 리로더" 대신 재시작을 정본으로 삼는다.
- **재시작 후 실제로 새 코드가 떴는지 확인한다** — 재시작 없이(또는 실패한 채) 측정하면 구코드를
  측정하게 된다. 워커 프로세스 기동 시각이 반영 파일 mtime 보다 나중인지 대조한다:
  ```
  docker inspect -f '{{.State.StartedAt}}' koclo_erp-dev-app   # UTC. KST 는 +9h
  docker exec koclo_erp-dev-app stat -c '%y %n' /app/app/<반영파일>
  ```

## 보고
- 반영한 파일 수/목록, dev 경로/브랜치, (있으면) PRE_DIRTY 경고를 요약한다.
- **재시작 여부**를 명시한다 — 했으면 대상 컨테이너와 기동 시각, 안 했으면 `backend/app/` 변경이
  없어 불필요했다는 사실. (재시작했는데 새 코드가 안 떴으면 그것도 그대로 보고한다.)
- **git add/commit/push 안 함 · prod 미반영**을 명시한다.
- 확인 끝나면 **`/server-clear`** 로 원복하라고 안내한다.

## 규칙
- 비밀번호·토큰·DSN 출력 금지. `StrictHostKeyChecking=no` 등 우회 금지.
- CLAUDE.md 의 NAS / Dangerous Action 규칙을 따른다.
