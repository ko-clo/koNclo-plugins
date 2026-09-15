---
description: PR base 게이트 — main 직행 PR 기본 차단, 한시 허용 (main [분] | off | status)
argument-hint: "main [분] | off | status"
---
사용자가 `/prbase $ARGUMENTS` 를 실행했다. PR base 게이트 파일 `.claude/.prbase-unlock`
(만료 epoch 초 한 줄)을 아래에 따라 처리하라.

기본 규칙(CLAUDE.md §PR base 기본값은 `develop`): `gh pr create` 는 **항상 `--base develop`**
을 명시한다. `--base` 생략이나 `--base main` 은 PreToolUse 훅 `pr-base-guard.sh` 가 차단한다 —
`main` push 가 prod 자동배포를 트리거하기 때문이다.

여닫이는 **반드시 `.claude/hooks/gate.sh` 로 한다** — 게이트 파일에 직접 쓰는 길은 하네스가
차단하므로 사용자가 `/prbase main` 을 눌러도 열리지 않는다. `permissions.allow` 에 등록된 진입점은
이 스크립트뿐이며, 다른 명령과 `&&`·`;` 로 이어붙이면 접두 매칭이 깨져 역시 차단된다.

- **main [분]** (분 생략 시 30, 상한 480): `.claude/hooks/gate.sh prbase on <분>`
- **off**: `.claude/hooks/gate.sh prbase off`
- **status** 또는 인자 없음: `.claude/hooks/gate.sh prbase status`

출력 문구는 스크립트가 만든다 — 여기서 따로 지어내지 않는다.
(스크립트의 하위명령은 `on` 이다 — `/prbase` 의 사용자 인자만 `main` 이라는 뜻이며,
 이 게이트가 여는 것은 `--base main` 하나뿐이다.)

게이트를 여는 것은 **오발 방지 해제일 뿐 승인이 아니다.** 열려 있어도 PR 을 올릴지는
사용자에게 따로 묻고, `main` 을 base 로 쓰는 이유(develop → main 승격인지 핫픽스인지)를
밝힌다. 끝나면 `/prbase off` 로 다시 잠그도록 안내한다.
