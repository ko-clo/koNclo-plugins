---
description: /server-test 로 NAS dev(koclo-dev)에 임시 반영한 변경분을 매니페스트 경로만 파일 단위로 원복
argument-hint: "(인자 없음)"
---
사용자가 `/server-clear` 를 실행했다. `/server-test` 로 `/volume1/docker/koclo-dev`(`develop`)
워킹트리에 임시 반영했던 변경분을 **원복**한다.

원복은 **매니페스트에 적힌 파일만 한 개씩** 되돌린다. 파일마다 dev 의 `HEAD` 에 그 경로가
있는지 물어보고 —
- **있으면**(우리가 덮어쓴 추적 파일) → `git show HEAD:<경로>` 의 내용을 그 파일에 다시 쓴다.
- **없으면**(우리가 새로 만든 파일) → 그 경로 하나만 지운다.

**커밋을 만들지 않으므로** add/commit/push 금지와 무관하다.

## 🛑 전체 트리 파괴 명령 금지 — 이게 이 명령의 설계 핵심
`/server-clear` 는 **우리가 건드린 파일만** 되돌린다. 따라서 아래를 **절대 쓰지 않는다**:

- **`git reset --hard` 금지.** dev 워킹트리의 *모든* 추적파일 변경을 폐기한다 — 다른 사람이
  작업 중이던 미커밋 변경까지 함께 날아간다. 우리는 그럴 권한이 없다.
- **`git clean` 금지(scoped 포함).** dev 에는 앱이 런타임에 쓰는 rw 볼륨(`reports_dev/`,
  `data_dev/`)이 untracked 로 존재하고, `git status --porcelain` 은 **빈 untracked 디렉터리를
  표시하지 않지만** `git clean -d` 는 그것까지 삭제한다(2026-06 실제 사고).
- **`git restore` / `git checkout -- <경로>` 금지.** 결과는 같지만 danger-guard 하드 차단
  대상이라 게이트를 열어야 한다 → 되돌리기가 되돌리기 게이트에 막히는 순환 의존이 생긴다.

> **왜 이 설계인가**: 위 셋은 전부 "영향 범위가 명령 자체로는 안 드러나는" 파괴 명령이라
> 차단되는 게 옳다. 반면 `git show HEAD:<경로>` 는 **읽기**이고, 그 결과를 **우리가 덮어쓴 그
> 파일 하나에만** 되쓴다. 영향 범위가 경로 목록으로 완전히 드러나므로 게이트가 필요 없다.
> **danger 게이트를 여는 단계는 이 명령에 없다.** 열려고 시도하지 말 것.

## 🚫 절대 금지
- **git add / commit / push / revert 금지.** (revert 는 커밋을 만든다.)
- **PROD 금지.** 대상 경로가 `testerp` 를 포함하거나 브랜치가 `main`/`master` 면 즉시 중단.
  오직 `koclo-dev` + `develop`.

## ⚠ 안전판 — 우리가 반영하지 않은 변경은 건드리지 않는다
파일 단위 복원이라 **매니페스트에 없는 경로는 구조적으로 영향을 받을 수 없다.** `PRE_DIRTY`
(반영 전부터 dev 에 있던 변경)도, 다른 사람의 미커밋 변경도, 런타임 데이터도 그대로 남는다.
- 그래도 원복 전 `git status --porcelain` 으로 현재 더티 목록을 찍어 **매니페스트 `DEPLOYED`
  와 대조**한다. 목적은 폐기 동의를 받기 위해서가 아니라, **매니페스트가 실제 반영분을 제대로
  담고 있는지 확인**하기 위해서다(누락 = 원복 안 되고 남는 파일이 생긴다).
- 더티인데 매니페스트에 없는 파일은 **외부 변경**이다. 목록만 보고하고 **건드리지 않는다.**

## 게이트 — NAS 하나만, 이 명령이 자동으로 연다
대상이 NAS(`100.99.51.88` · `/volume1/`)라 NAS 게이트만 필요하다. 원복 직전 짧게(10분) 연다.
```
N=$(( $(date +%s) + 600 )); echo "$N" > .claude/.nas-unlock; echo "✅ NAS 게이트 10분 오픈"
```
**danger 게이트는 필요 없다** — 파괴 명령을 쓰지 않기 때문이다. 사용자에게 `/danger on` 을
치게 만들지 말 것. 작업이 끝나면 NAS 게이트를 닫는다(마지막 단계).

## 실행 절차

### 0) 매니페스트 로드
`.claude/.server-test-manifest` 를 읽는다. 없으면 "반영 이력 없음(매니페스트 부재)" 출력하고
중단(원복 대상 불명 → 임의 복원하지 않는다). `<DEV>`=`DEV_PATH`, `DEPLOYED` 파싱.
- `.claude/.server-test-files` 가 함께 있으면 **두 목록의 합집합**을 원복 대상으로 삼는다.
  (과거 매니페스트 갱신 누락으로 목록이 어긋난 사례가 있다 — 합집합이 안전측.)

### 접속 / dev git (실측값)
- ssh: `ssh -p 2323 -i "$HOME/.ssh/id_rsa" saykim4195@100.99.51.88` (`~` 를 큰따옴표 안에 쓰면
  키 확장 실패 → 반드시 `$HOME`). `<DEV>` = `/volume1/docker/koclo-dev` (소문자).
- dev 레포는 root 소유라 git 이 `dubious ownership` 으로 거부 → **모든 git 명령에
  `git -c safe.directory=<DEV> -C <DEV> ...` 인라인 플래그 필수**.

### 1) prod 가드 + 매니페스트 대조 (읽기 전용)
```
ssh -p 2323 -i "$HOME/.ssh/id_rsa" saykim4195@100.99.51.88 2>/dev/null \
  'P=<DEV>; case "$P" in *testerp*) echo "PROD 감지 — 중단"; exit 1;; esac
   B=$(git -c safe.directory="$P" -C "$P" branch --show-current)
   [ "$B" = "develop" ] || { echo "브랜치 $B — 중단"; exit 1; }
   echo "가드 통과: $P ($B)"; git -c safe.directory="$P" -C "$P" status --porcelain'
```
더티 목록 ∖ `DEPLOYED` = 외부 변경 → 목록만 보고(건드리지 않음).

### 2) 원복 실행 — 파일 단위 (게이트 불필요)
`DEPLOYED` 의 각 경로 F 에 대해 dev `HEAD` 존재 여부로 분기한다. **한 번의 ssh 로 루프**를 돈다:
```
ssh -p 2323 -i "$HOME/.ssh/id_rsa" saykim4195@100.99.51.88 2>/dev/null \
  'P=<DEV>; G="git -c safe.directory=$P -C $P";
   for F in <DEPLOYED 목록>; do
     if $G cat-file -e "HEAD:$F" 2>/dev/null; then
       $G show "HEAD:$F" > "$P/$F" && echo "restored: $F"
     else
       echo "new-file(삭제 대상): $F"
     fi
   done'
```
- `git show` 는 **읽기**다. 리다이렉트 대상은 우리가 덮어쓴 그 파일 하나뿐 → danger-guard
  패턴에 걸리지 않고 게이트도 필요 없다.
- **신규 파일 삭제는 별도 호출**로 분리한다. `rm` 은 `permissions.ask` 라 확인 프롬프트가 뜨는데,
  덮어쓴 파일만 되돌리는 일반적인 경우엔 아예 실행할 일이 없다. `new-file` 로 찍힌 게 있을 때만:
  ```
  ssh … 'P=<DEV>; rm -f "$P/<경로1>" "$P/<경로2>"; echo removed'
  ```
  **`rm -rf` 금지 · 매니페스트에 없는 경로 금지 · 디렉터리 통째 삭제 금지.**

### 3) 검증
```
ssh ... 2>/dev/null 'P=<DEV>; git -c safe.directory="$P" -C "$P" status --porcelain'
```
- `DEPLOYED` 경로가 목록에서 **전부 사라져야** 정상. `PRE_DIRTY`·외부 변경·런타임 데이터
  (`reports_dev/`, `data_dev/`)는 **그대로 남아 있어야** 정상이다(사라졌으면 사고 — 즉시 보고).
- 가능하면 서빙 응답으로 한 항목만 실측한다(예: 반영 때 넣었던 키워드가 0건인지).

### 4) 정리 + 게이트 재잠금 (반드시)
```
rm -f .claude/.server-test-manifest .claude/.server-test-files .claude/.nas-unlock
```
"🔒 NAS 게이트 잠금 · 매니페스트 정리" 출력.

### 막히면
이 절차에는 파괴 명령이 없어 게이트·분류기에 막힐 이유가 없다. 그래도 막힌다면
**우회하지 말고**(=`reset --hard`·`git clean`·`git restore` 로 바꿔치기 절대 금지) 중단하고,
`!` 접두로 사용자가 직접 실행할 수 있게 2) 의 명령문을 그대로 제시한다.
**이때 매니페스트를 지우지 않는다** — 원복이 끝나지 않았으므로 다음 시도에 필요하다.

## 보고
- 원복한 dev 경로/브랜치, 파일별 restored/removed 결과, 검증 결과를 요약.
- 외부 변경이 있었으면 "건드리지 않았음"을 명시.
- NAS 게이트를 다시 닫았음을 확인.

## 규칙
- 비밀번호·토큰 출력 금지. 우회 옵션 금지.
- CLAUDE.md 의 NAS / Dangerous Action 규칙을 따른다. 게이트는 짧게 열고 즉시 닫는다.
