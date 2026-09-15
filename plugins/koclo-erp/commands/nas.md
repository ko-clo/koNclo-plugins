---
description: NAS 접근 게이트 — 기본 차단, 한시 허용 (on/off/status)
argument-hint: "on [분] | off | status"
---
사용자가 `/nas $ARGUMENTS` 를 실행했다. NAS 접근 게이트 파일 `.claude/.nas-unlock`
(만료 epoch 초 한 줄)을 아래에 따라 처리하라. 게이트가 열려 있어야 NAS 마커가 포함된
Bash 명령(`100.99.51.88`, `orderhead1@`, `/volume1/`, `testerp-dev-app` 등)이
PreToolUse 훅을 통과한다.

여닫이는 **반드시 `.claude/hooks/gate.sh` 로 한다** — 게이트 파일에 직접 쓰는 길은 하네스가
차단하므로 사용자가 `/nas on` 을 눌러도 열리지 않는다. `permissions.allow` 에 등록된 진입점은
이 스크립트뿐이며, 다른 명령과 `&&`·`;` 로 이어붙이면 접두 매칭이 깨져 역시 차단된다.

- **on [분]** (분 생략 시 30, 상한 480): `.claude/hooks/gate.sh nas on <분>`
- **off**: `.claude/hooks/gate.sh nas off`
- **status** 또는 인자 없음: `.claude/hooks/gate.sh nas status`

출력 문구는 스크립트가 만든다 — 여기서 따로 지어내지 않는다.

게이트를 연 뒤에도 **CLAUDE.md의 NAS Access Safety Rules** 를 따른다 — 읽기 전용은 자유,
파일 변경·동기화·서비스/Docker·시스템·Git/배포는 사용자 승인 후에만.
작업이 끝나면 `/nas off` 로 다시 잠그도록 사용자에게 안내한다.
