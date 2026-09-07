---
description: PR base 게이트 — main 직행 PR 기본 차단, 한시 허용 (main [분] | off | status)
argument-hint: "main [분] | off | status"
---
사용자가 `/prbase $ARGUMENTS` 를 실행했다. PR base 게이트 파일 `.claude/.prbase-unlock`
(만료 epoch 초 한 줄)을 아래에 따라 처리하라.

기본 규칙(CLAUDE.md §PR base 기본값은 `develop`): `gh pr create` 는 **항상 `--base develop`**
을 명시한다. `--base` 생략이나 `--base main` 은 PreToolUse 훅 `pr-base-guard.sh` 가 차단한다 —
`main` push 가 prod 자동배포를 트리거하기 때문이다.

- **main [분]** (분 생략 시 30):
  `EXP=$(( $(date +%s) + <분>*60 )); echo "$EXP" > .claude/.prbase-unlock`
  를 실행하고, "✅ main 직행 PR <분>분 허용 (만료 HH:MM)" 를 출력한다.
- **off**:
  `rm -f .claude/.prbase-unlock` 를 실행하고 "🔒 main 직행 PR 잠금 (base=develop 만 허용)" 을 출력한다.
- **status** 또는 인자 없음:
  게이트 파일 존재 여부와 만료까지 남은 시간을 계산해 출력한다. 없거나 만료면 "🔒 잠김".

게이트를 여는 것은 **오발 방지 해제일 뿐 승인이 아니다.** 열려 있어도 PR 을 올릴지는
사용자에게 따로 묻고, `main` 을 base 로 쓰는 이유(develop → main 승격인지 핫픽스인지)를
밝힌다. 끝나면 `/prbase off` 로 다시 잠그도록 안내한다.
