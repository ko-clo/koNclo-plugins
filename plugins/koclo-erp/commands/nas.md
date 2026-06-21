---
description: NAS 접근 게이트 — 기본 차단, 한시 허용 (on/off/status)
argument-hint: "on [분] | off | status"
---
사용자가 `/nas $ARGUMENTS` 를 실행했다. NAS 접근 게이트 파일 `.claude/.nas-unlock`
(만료 epoch 초 한 줄)을 아래에 따라 처리하라. 게이트가 열려 있어야 NAS 마커가 포함된
Bash 명령(`100.99.51.88`, `orderhead1@`, `/volume1/`, `testerp-dev-app` 등)이
PreToolUse 훅을 통과한다.

- **on [분]** (분 생략 시 30):
  `EXP=$(( $(date +%s) + <분>*60 )); echo "$EXP" > .claude/.nas-unlock`
  를 실행하고, "✅ NAS 접근 <분>분 허용 (만료 HH:MM)" 를 출력한다.
- **off**:
  `rm -f .claude/.nas-unlock` 를 실행하고 "🔒 NAS 접근 잠금" 을 출력한다.
- **status** 또는 인자 없음:
  게이트 파일 존재 여부와 만료까지 남은 시간(`.claude/.nas-unlock` 의 epoch − 현재시각)을
  계산해 출력한다. 없거나 만료면 "🔒 잠김".

게이트를 연 뒤에도 **CLAUDE.md의 NAS Access Safety Rules** 를 따른다 — 읽기 전용은 자유,
파일 변경·동기화·서비스/Docker·시스템·Git/배포는 사용자 승인 후에만.
작업이 끝나면 `/nas off` 로 다시 잠그도록 사용자에게 안내한다.
