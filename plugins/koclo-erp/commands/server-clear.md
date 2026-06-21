---
description: /server-test 로 NAS dev(koclo-dev)에 임시 반영한 변경분을 원복 (git reset --hard / clean -fd)
argument-hint: "(인자 없음)"
---
사용자가 `/server-clear` 를 실행했다. `/server-test` 로 `/volume1/docker/koclo-dev`(`develop`)
워킹트리에 임시 반영했던 변경분을 **원복**한다. 원복은 ① `git reset --hard` 로 우리가 덮어쓴
**추적 파일**을 복원하고, ② 우리가 새로 만든 **미추적 파일은 매니페스트의 그 경로만 `git clean`
으로 한 번에 하나씩** 지운다 — **커밋을 만들지 않으므로** add/commit/push 금지와 무관하다.

## 🛑 blanket `git clean` 금지 — 반드시 경로별 scoped (사고 재발 방지)
- **`git clean -fd` 를 인자 없이(전체 트리에) 절대 실행하지 않는다.** dev 레포에는 앱이 런타임에
  쓰는 rw 볼륨(`reports_dev/`, `data_dev/`)이 untracked 로 존재하고, `git status --porcelain` 은
  **빈 untracked 디렉터리를 표시하지 않지만** 전체 `git clean -d` 는 그것까지 삭제한다 → 우리가
  반영하지 않은 런타임 데이터가 날아간다(2026-06 실제 사고).
- **대신 매니페스트 `DEPLOYED` 의 경로를 인자로 명시해 `git clean -fd -- <경로>` 를 한 번에 하나씩**
  실행한다(pathspec 으로 영향 범위를 그 경로로 한정). 추적 파일이면 git clean 이 무시하므로 안전.
  목록에 없는 경로는 어떤 경우에도 clean 대상이 되지 않는다.

## 🚫 절대 금지
- **git add / commit / push / revert 금지.** (revert 는 커밋을 만든다.)
- **PROD 금지.** 대상 경로가 `testerp` 를 포함하거나 브랜치가 `main`/`master` 면 즉시 중단.
  오직 `koclo-dev` + `develop`.

## ⚠ 핵심 안전판 — 우리가 반영하지 않은 변경 보호
`git reset --hard` 는 **dev 워킹트리의 모든 추적파일 변경을 폐기**한다. 따라서 원복 전 dev 의
현재 더티(추적) 파일 중 **이번 `/server-test` 가 반영한 것이 아닌 파일**(매니페스트 `DEPLOYED` 에
없고 `PRE_DIRTY` 로 기록되지도 않은 것)이 있는지 반드시 확인한다.
- 그런 **'외부 변경'이 하나라도 있으면**: 그 목록을 보여주고 **"이 파일들도 함께 폐기됩니다.
  진행할까요?" 라고 사용자에게 확인을 받은 뒤에만** 진행한다. 확인 없으면 중단.
- `PRE_DIRTY`(반영 전부터 있던 변경)도 reset 으로 사라진다는 점을 함께 1줄 경고한다.
- 미추적(신규) 파일은 reset 이 건드리지 않는다 → 3-(b) 에서 **매니페스트 경로를 인자로 명시한**
  scoped `git clean -fd -- <경로>` 로 한 번에 하나씩 제거. 런타임 데이터(`reports_dev/`,
  `data_dev/`)는 매니페스트에 없어 인자가 되지 않으므로 절대 손대지 않는다.

## 게이트 — 이 명령이 NAS + danger 를 자동으로 연다
`git reset --hard` 와 `git clean` 이 danger-guard 하드 차단 대상이므로 게이트 둘 다 필요하다.
원복 직전 짧게(10분) 연다:
```
N=$(( $(date +%s) + 600 )); echo "$N" > .claude/.nas-unlock
D=$(( $(date +%s) + 600 )); echo "$D" > .claude/.danger-unlock
```
"✅ NAS+danger 게이트 10분 오픈" 출력. **작업이 끝나면 반드시 둘 다 닫는다(아래 마지막 단계).**

## 실행 절차

### 0) 매니페스트 로드
`.claude/.server-test-manifest` 를 읽는다. 없으면 "반영 이력 없음(매니페스트 부재)" 출력하고
중단(원복할 대상 불명 → 임의 reset 하지 않는다). `<DEV>`=`DEV_PATH`, `DEPLOYED`/`PRE_DIRTY` 파싱.

### 접속 / dev git (실측값)
- ssh: `ssh -p 2323 -i "$HOME/.ssh/id_rsa" saykim4195@100.99.51.88` (`~` 를 큰따옴표 안에 쓰면
  키 확장 실패 → 반드시 `$HOME`). `<DEV>` = `/volume1/docker/koclo-dev` (소문자).
- dev 레포는 root 소유라 git 이 `dubious ownership` 으로 거부 → **모든 git 명령에
  `git -c safe.directory=<DEV> -C <DEV> ...` 인라인 플래그 필수**(이게 빠지면 reset 이 exit 128).

### 1) prod 가드 재확인
`<DEV>` 가 `testerp` 포함이면 중단. 브랜치 확인:
```
ssh -p 2323 -i "$HOME/.ssh/id_rsa" saykim4195@100.99.51.88 2>/dev/null \
  'git -c safe.directory=<DEV> -C <DEV> branch --show-current'
```
`develop` 아니면 중단.

### 2) 현재 더티 목록 ↔ 매니페스트 대조 (외부 변경 탐지)
```
ssh ... 2>/dev/null 'git -c safe.directory=<DEV> -C <DEV> status --porcelain'
```
- 현재 더티 경로 집합에서 `DEPLOYED` ∪ `PRE_DIRTY` 를 뺀 나머지 = **외부 변경**.
- 외부 변경이 있으면 위 '핵심 안전판'대로 목록 제시 + 사용자 확인. 없으면 다음으로.

### 3) 원복 실행 (게이트 오픈 상태에서) — clean 금지, scoped 만
**(a) 추적 파일 복원** — `reset --hard` 로 우리가 덮어쓴 추적 파일을 `develop` HEAD 로 되돌린다:
```
ssh -p 2323 -i "$HOME/.ssh/id_rsa" saykim4195@100.99.51.88 2>/dev/null \
  'P=<DEV>; git -c safe.directory="$P" -C "$P" reset --hard'
```
**(b) 우리가 만든 미추적 파일만 경로별 scoped clean** — `DEPLOYED` 의 각 경로 F 에 대해
**그 경로를 인자로 명시해 한 번에 하나씩** `git clean -fd -- "$F"` 를 실행한다(전체 트리 clean 금지).
pathspec 으로 F 외에는 절대 영향이 없고, F 가 추적 파일이면 git clean 이 무시한다.
```
ssh -p 2323 -i "$HOME/.ssh/id_rsa" saykim4195@100.99.51.88 2>/dev/null \
  'P=<DEV>; for F in <DEPLOYED 목록>; do
     git -c safe.directory="$P" -C "$P" clean -fd -- "$F" && echo "cleaned: $F";
   done'
```
- **반드시 `-- "$F"` pathspec 을 붙인다.** 인자 없는 `git clean -fd` 는 금지(런타임 데이터 삭제 사고).
- 매니페스트에 없는 경로(`reports_dev/`, `data_dev/` 등)는 인자가 아니므로 손대지 않는다.
- NAS 마커(`koclo-dev`) 포함 → nas-guard 통과. `reset --hard`·`git clean` 은 danger-guard
  하드 차단 대상 → 게이트(둘 다 오픈됨)로 통과. 실패 시 원인 보고.

### 4) 검증
```
ssh ... 2>/dev/null 'git -c safe.directory=<DEV> -C <DEV> status --porcelain'
```
- 출력이 비어야 정상(클린). 비지 않으면 남은 항목을 보고하고 사용자 판단을 구한다.

### 5) 정리 + 게이트 재잠금 (반드시)
```
rm -f .claude/.server-test-manifest .claude/.server-test-files
rm -f .claude/.nas-unlock .claude/.danger-unlock
```
"🔒 NAS+danger 게이트 잠금 · 매니페스트 정리" 출력.

## 보고
- 원복된 dev 경로/브랜치, reset/clean 결과, 검증(클린 여부)을 요약.
- (있었다면) 외부 변경/`PRE_DIRTY` 폐기 여부를 명시.
- 게이트를 다시 닫았음을 확인.

## 규칙
- 비밀번호·토큰 출력 금지. 우회 옵션 금지.
- CLAUDE.md 의 NAS / Dangerous Action 규칙을 따른다. 게이트는 짧게 열고 즉시 닫는다.
