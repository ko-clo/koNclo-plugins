---
description: 위험 작업 게이트 — 비가역/파괴 명령 기본 차단, 한시 허용 (on/off/status)
argument-hint: "on [분] | off | status"
---
사용자가 `/danger $ARGUMENTS` 를 실행했다. 위험 작업 게이트 파일 `.claude/.danger-unlock`
(만료 epoch 초 한 줄)을 아래에 따라 처리하라. 게이트가 열려 있어야 비가역/파괴 패턴
(`git push --force`, `git reset --hard`, `git clean`, `docker compose down -v`,
`docker * prune`, `rm -rf`, SQL `DROP/TRUNCATE`, 마이그레이션 다운 등)이 담긴 Bash 명령이
PreToolUse 훅(`.claude/hooks/danger-guard.sh`)을 통과한다.

여닫이는 **반드시 `.claude/hooks/gate.sh` 로 한다** — 게이트 파일에 직접 쓰는 길은 하네스가
차단하므로 사용자가 `/danger on` 을 눌러도 열리지 않는다. `permissions.allow` 에 등록된 진입점은
이 스크립트뿐이며, 다른 명령과 `&&`·`;` 로 이어붙이면 접두 매칭이 깨져 역시 차단된다.

- **on [분]** (분 생략 시 15, 상한 480): `.claude/hooks/gate.sh danger on <분>`
- **off**: `.claude/hooks/gate.sh danger off`
- **status** 또는 인자 없음: `.claude/hooks/gate.sh danger status`

출력 문구는 스크립트가 만든다 — 여기서 따로 지어내지 않는다.

게이트를 연 뒤에도 **CLAUDE.md의 Dangerous Action Safety Rules** 를 따른다 — 실행 전
영향받는 대상과 복구 방법을 알리고, 작업이 끝나면 `/danger off` 로 다시 잠그도록 안내한다.
게이트는 짧게(기본 15분) 열고 즉시 닫는 것을 원칙으로 한다.
