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

### 6) 컨테이너 반영 확인 (읽기 전용)
- dev 컨테이너 = `koclo_erp-dev-app`. (해석 시 `docker ps --format '{{.Names}}' | grep koclo_erp-dev`.)
- 실측 마운트: `frontend` `backend/app` `backend/scripts` `configs` 모두 **bind-mount(ro)** →
  **프론트(js/html) 변경은 즉시 반영, 재시작 불필요**. 게시 포트는 없음(리버스 프록시 경유).
- 백엔드(.py) 변경이 포함됐고 uvicorn reload 가 아니면 반영이 안 될 수 있다 → 그 경우
  **컨테이너 restart 가 필요할 수 있음**을 1줄 안내하고, 재시작은 **사용자 승인 후에만**
  (`docker restart koclo_erp-dev-app`) 수행한다(임의 재시작 금지).

## 보고
- 반영한 파일 수/목록, dev 경로/브랜치, (있으면) PRE_DIRTY 경고를 요약한다.
- **git add/commit/push 안 함 · prod 미반영**을 명시한다.
- 확인 끝나면 **`/server-clear`** 로 원복하라고 안내한다.

## 규칙
- 비밀번호·토큰·DSN 출력 금지. `StrictHostKeyChecking=no` 등 우회 금지.
- CLAUDE.md 의 NAS / Dangerous Action 규칙을 따른다.
