---
description: 서버(koclo-vm) 접속 게이트 — 기본 차단, 한시 허용 (on/off/status)
argument-hint: "on [분] | off | status"
---
사용자가 `/server $ARGUMENTS` 를 실행했다. 서버 접속 게이트 파일 `.claude/.server-unlock`
(만료 epoch 초 한 줄)을 아래에 따라 처리하라. 게이트가 열려 있어야 koclo-vm 으로 나가는
접속 명령(`ssh`·`scp`·`rsync`·`sftp` + `koclo-vm`)이 PreToolUse 훅
(`.claude/hooks/server-gate.sh`)을 통과한다.

여닫이는 **반드시 `.claude/hooks/gate.sh` 로 한다** — 게이트 파일에 직접 쓰는 길은 하네스가
차단하므로 사용자가 `/server on` 을 눌러도 열리지 않는다. `permissions.allow` 에 등록된 진입점은
이 스크립트뿐이며, 다른 명령과 `&&`·`;` 로 이어붙이면 접두 매칭이 깨져 역시 차단된다.

- **on [분]** (분 생략 시 30, 상한 480): `.claude/hooks/gate.sh server on <분>`
- **off**: `.claude/hooks/gate.sh server off`
- **status** 또는 인자 없음: `.claude/hooks/gate.sh server status`

출력 문구는 스크립트가 만든다 — 여기서 따로 지어내지 않는다.

## 열린 뒤에도 지키는 것

- 게이트가 열리면 koclo-vm 위의 **조회·로그 확인·DB 인입/수정까지** 확인 절차 없이 수행된다.
  그러니 **짧게 열고 즉시 닫는다**(기본 30분).
- **파괴 패턴은 게이트가 열려 있어도 자동 허용되지 않는다** — `rm -rf`, `git push --force`,
  `git reset --hard`, `docker compose down -v`, `docker * prune`, SQL `DROP`/`TRUNCATE`,
  `alembic downgrade` 는 훅이 allow 를 내리지 않고 정상 권한 확인으로 넘긴다.
- 운영 데이터 수정·서비스 재시작·배포는 게이트와 별개로 **CLAUDE.md 의 Dangerous Action
  Safety Rules** 를 따른다. 실행 전 대상·영향·복구 방법을 알리고 승인을 받는다.
- koclo-vm 은 NAS 가 아니라 Hyper-V VM 이다. NAS(`100.99.51.88`) 자체를 다루는 작업은
  이 게이트가 아니라 `/nas on` 소관이다. 단 koclo-vm 에는 NAS 공유가 CIFS 로 마운트돼
  있으므로(`/volume1/자동주문`), 그 경로를 **쓰는** 작업은 NAS 안전 규칙을 함께 적용한다.

## 혼동 주의 — 이름이 비슷한 다른 명령

- `/server-test` : 로컬 워킹트리 변경분을 NAS dev(koclo-dev)에 임시 반영해 테스트. 배포가 아님.
- `/server-clear`: `/server-test` 로 반영한 변경분을 매니페스트 경로만 원복.
- `/server`      : (이 명령) koclo-vm 접속 게이트 여닫기. 파일을 반영하지 않는다.

작업이 끝나면 `/server off` 로 다시 잠그도록 사용자에게 안내한다.
