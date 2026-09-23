---
description: 일상 작업 자동승인 게이트 — 편집·조회 확인을 건너뛰고 끝까지 진행 후 결과 보고 (on/off/status)
argument-hint: "on [분] | off | status | <작업 설명>"
---
사용자가 `/all-pass $ARGUMENTS` 를 실행했다. 게이트 파일 `.claude/.all-pass-unlock`
(만료 epoch 초 한 줄)이 열려 있는 동안 PreToolUse 훅
`.claude/hooks/allpass-gate.sh` 가 일상 작업을 `permissionDecision=allow` 로
통과시켜 yes/no 확인을 건너뛴다.

여닫이는 **반드시 `.claude/hooks/gate.sh` 로 한다** — 게이트 파일에 직접 쓰는 길은
하네스가 차단한다. 다른 명령과 `&&`·`;` 로 이어붙이면 접두 매칭이 깨져 역시 차단된다.

## 인자 분기

- **on [분]** (분 생략 시 60, 상한 480): `.claude/hooks/gate.sh all-pass on <분>`
- **off**: `.claude/hooks/gate.sh all-pass off`
- **status** 또는 인자 없음: `.claude/hooks/gate.sh all-pass status`
- **그 외(작업 설명)**: `.claude/hooks/gate.sh all-pass on 60` 으로 열고, 그 설명을
  작업 지시로 받아 아래 §진행 방식대로 끝까지 수행한 뒤 마지막에 결과를 보고한다.

출력 문구는 스크립트가 만든다 — 여기서 따로 지어내지 않는다.

## 자동승인 범위

| 구분 | 대상 |
|---|---|
| 자동승인 | Write·Edit·MultiEdit·NotebookEdit, 조회·실행 Bash(`cat`·`grep`·`python3`·`node`·`ls`·`git status/diff/log/show`) |
| 확인 유지 | `git` 쓰기(commit·push·add·switch…)·`gh pr`·`docker`·`rm`·`chmod`·`chown`·`sudo`·`npm install`·마이그레이션·`ssh`/`scp`·`curl`·NAS 마커·SQL 쓰기 |
| 하드 차단 | 기존 가드 그대로 — design·danger·testfile·nas·server·prbase·date-bind·imported-at |

게이트가 열려 있어도 **`backend/**`·`frontend/**` 편집은 `design-gate.sh` 가 막는다.**
운영 코드를 고치려면 `/design` 절차(모드 분류 → 조사 → 설계 → 승인)를 그대로 거친다.
자동승인은 승인 게이트를 대체하지 않는다 — 확인창을 줄이는 장치일 뿐이다.

## 진행 방식 (작업 설명이 주어졌을 때)

1. 작업을 끝까지 수행한다. **중간에 진행 여부를 묻지 않는다** — 합리적 기본값으로 판단하고
   나아간다. 단, 확인 유지 대상 명령이 필요해지면 그때는 평소처럼 확인을 받는다.
2. 실패해도 멈추지 않는다. 남은 독립 작업을 모두 마친 뒤, 막힌 항목을 이유와 함께 보고한다.
3. 코드를 고쳤으면 CLAUDE.md §검증 명령으로 최소 1개 검증을 실행한다.
   검증을 못 돌렸으면 "완료"라고 쓰지 않고 그 사실과 이유를 적는다.
4. 끝나면 **한 번에** 다음을 표로 보고한다: 변경 파일 · 검증 결과 · 남은 리스크 ·
   확인이 필요해 건너뛴 항목.
5. 보고 후 `/all-pass off` 로 잠그도록 안내한다. 게이트는 짧게 열고 즉시 닫는 것이 원칙이다.
