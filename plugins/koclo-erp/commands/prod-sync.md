---
description: NAS prod(/volume1/docker/testerp)의 미커밋 변경분을 로컬 워킹트리에 반영 (status | go) — EOL 노이즈 제외·prod 읽기전용
argument-hint: "(status) | go | go --files 경로1,경로2 | [--repo testerp|testerp-legacy]"
---
사용자가 `/prod-sync $ARGUMENTS` 를 실행했다. **NAS prod 저장소의 아직 커밋되지 않은
워킹트리 변경분**(누군가 운영 서버에서 직접 편집한 tracked 파일)을 **현재 로컬 워킹트리에
반영**한다. 정상 배포분(이미 origin 에 있는 커밋)은 `git pull` 이 담당하므로 이 명령의
대상이 아니다 — 이 명령은 **origin 에 없는, prod 에만 있는 미커밋 수정**을 로컬로 회수한다.

## 방향·대상
- 방향: **prod → 로컬 (단방향)**. prod 는 **읽기 전용** — 절대 쓰지 않는다.
- 대상 로컬: **현재 워크트리/브랜치** (명령을 실행한 레포). 파일 경로는 레포 루트 기준 1:1 매핑.
- prod 저장소(기본): `/volume1/docker/testerp`. `--repo testerp-legacy` 면 `/volume1/docker/testerp-legacy`.

## 🚫 절대 금지 (어기면 즉시 중단)
- **prod(NAS) 에 쓰기 금지.** prod 에서 `git add/commit/checkout/restore/stash/reset`, 파일 편집,
  docker 조작을 하지 않는다. 오직 `git status` / `git diff` / `git show` 등 **읽기 전용**만.
- **로컬 커밋/푸시 금지.** 로컬 워킹트리 파일만 수정한다. `git add/commit/push` 하지 않는다
  (사용자가 검토 후 정식 흐름으로 커밋). 되돌리기용 `git restore`/`checkout --` 는 하드 차단이므로,
  적용을 물릴 때도 Edit 로 역적용한다.
- **untracked 생성물 제외.** prod status 의 `??`(예: `data/auto_judge/`, `reports/auto_judge/`)는
  런타임 산출물이니 절대 가져오지 않는다. tracked 수정(` M`/`MM`/`A `/`R `)만 대상.
- `.claude/`, `.git/` 는 반영 대상에서 제외.

## 전제 — NAS 게이트 (이 명령이 자동으로 연다)
`100.99.51.88` 접속이므로 NAS 게이트가 필요하다. prod 는 **읽기 전용**으로만 만지므로 이 명령은
**먼저 게이트를 30분 연다**:
```
EXP=$(( $(date +%s) + 1800 )); echo "$EXP" > .claude/.nas-unlock
```
"✅ NAS 게이트 30분 오픈 (prod 읽기전용)" 한 줄 출력. (끝나면 `/nas off` 안내.)

## SSH / 경로
- 접속: `ssh -p 2323 -i "$HOME/.ssh/id_rsa" saykim4195@100.99.51.88`
  (SSH/post-quantum 경고줄은 `2>/dev/null` 또는 `grep -v` 필터. 키 경로의 `~` 는 큰따옴표 안에서
  확장 안 되니 **`$HOME/.ssh/id_rsa`** 사용). 접속 실패 시 계정/키 확인받고 중단(임의 계정 금지).
- git 은 PATH 에 있음(`/usr/bin/git`) → `git -C <REPO>` 로 호출. docker 불필요(파일/ git 만 읽는다).
- `<REPO>` = 위 저장소 경로. `<TOP>` = 로컬 `git rev-parse --show-toplevel`.

## 실행 절차

### 1) prod 미커밋 변경 목록 (읽기 전용)
```
ssh -p 2323 -i "$HOME/.ssh/id_rsa" saykim4195@100.99.51.88 2>/dev/null \
  'R=<REPO>; git -C $R rev-parse --abbrev-ref HEAD; git -C $R status --porcelain=v1'
```
- `??`(untracked) 줄은 버린다. `XY 경로` 에서 X 또는 Y 가 `M/A/D/R/C` 인 **tracked 수정만** 추린다.
- 대상이 없으면 "prod 에 미커밋 변경 없음" 출력하고 종료(게이트는 열어둔 채 `/nas off` 안내).
- `--files a,b` 인자가 있으면 그 목록으로 제한.

### 2) 파일별 EOL/공백 노이즈 분류 (핵심)
prod 워킹트리는 CRLF↔LF 재저장으로 **파일 전체가 바뀐 것처럼 보이는 노이즈**가 흔하다
(예: `main.py` 1300+줄 diff 인데 실변경은 4줄). 파일마다 **실변경량**을 따로 잰다:
```
git -C $R diff --ignore-all-space --numstat -- <파일>   # 공백무시 실변경
git -C $R diff                     --numstat -- <파일>   # 원본(노이즈 포함)
```
- 공백무시 numstat 이 `0  0`(또는 빈 출력) → **EOL/공백 전용 노이즈 → 반영 안 함**(목록에 "노이즈 스킵"으로 보고).
- 실변경이 있으면 그 파일만 3) 이후로.

### 3) 미리보기 (status / go 공통 — 먼저 보여준다)
각 실변경 파일의 **실제 diff(공백무시)** 를 보여준다:
```
git -C $R diff --ignore-all-space -- <파일> | sed 's/\r//g'
```
표로 요약: `파일 | 실변경 라인 | 노이즈여부`. 여기서 **`status`(또는 인자 없음)면 멈춘다**(로컬 미변경).

### 4) 로컬 반영 — `go` 일 때만
각 실변경 파일을, prod 의 **실제 변경 hunk 만** 로컬 파일에 적용한다. **EOL 은 절대 로컬로 옮기지 않는다.**

1. 로컬 파일이 없으면(경로 신규) prod 워킹트리 내용을 `git show` 대신 파일을 받아 그대로 생성하되,
   `tr -d '\r'` 로 LF 정규화해서 `<TOP>/<파일>` 에 Write.
2. 로컬 파일이 있으면 **hunk 단위 Edit** 로 적용한다:
   - prod 의 공백무시 diff 에서 추가/삭제된 **실제 코드 라인**만 추린다(EOL 전용 라인 무시).
   - 로컬 파일에서 그 hunk 의 **앵커(주변 코드)** 를 찾아 Edit 로 삽입/치환한다.
   - ⚠ **베이스 불일치 주의**: 로컬 브랜치가 prod HEAD 와 다르면(누락 커밋 등) 앵커가 로컬에 없을 수
     있다. 앵커를 못 찾으면 **강제로 끼워넣지 말고 그 hunk 를 "미적용(앵커 없음)"으로 보고**한다.
   - 빠른 경로(선택): 노이즈가 없는 파일은 prod 패치를 받아 `git -C <TOP> apply --3way --whitespace=nowarn`
     로 적용 시도하고, 실패하면 위 hunk Edit 로 폴백.
3. 반영 후 **문법 검증**: `.py`→`python3 -m py_compile`, `.js`→`node --check`, `.yml`→YAML 로드(가능하면).

### 5) 보고
- 반영한 파일/실변경 라인, **EOL 노이즈로 스킵한 파일**, **앵커 없어 미적용한 hunk**(있으면)를 표로.
- prod 원본에서 발견한 **명백한 버그**(예: 미정의 변수 참조)가 있으면 그대로 옮겼음을 밝히고 수정안 1줄 제시.
- **prod 무변경 · 로컬 커밋/푸시 안 함**을 명시. 검토 후 사용자가 정식 흐름으로 커밋하도록 안내.
- 끝나면 `/nas off` 로 게이트 잠그도록 안내.

## 규칙
- prod 는 읽기 전용, 방향은 prod→로컬 단방향. 비밀번호·토큰·DSN 출력 금지.
- `StrictHostKeyChecking=no` 등 SSH 우회 옵션 금지.
- CLAUDE.md 의 NAS / Dangerous Action 안전 규칙을 따른다.
