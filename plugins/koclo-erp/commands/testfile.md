---
description: 테스트 파일 커밋 게이트 — 커밋 포함 기본 차단, 한시 허용 (on/off/status)
argument-hint: "on [분] | off | status"
---
사용자가 `/testfile $ARGUMENTS` 를 실행했다. 테스트 파일 커밋 게이트 `.claude/.testfile-unlock`
(만료 epoch 초 한 줄)을 아래에 따라 처리하라. 게이트가 열려 있는 동안에만 테스트 파일이 담긴
`git add` / `git commit` 이 PreToolUse 훅(`.claude/hooks/testfile-commit-guard.sh`)을 통과한다.

차단 대상 = `test_*.py` · `*_test.py` · `*_scenarios.py` · `*.test.*` / `*.spec.*` · `tests/` 경로.
신규 생성분과 **기존 테스트 파일 수정분 모두** 포함한다.

여닫이는 **반드시 `.claude/hooks/gate.sh` 로 한다** — 게이트 파일에 직접 쓰는 길은 하네스가
차단하므로 사용자가 `/testfile on` 을 눌러도 열리지 않는다. `permissions.allow` 에 등록된 진입점은
이 스크립트뿐이며, 다른 명령과 `&&`·`;` 로 이어붙이면 접두 매칭이 깨져 역시 차단된다.

- **on [분]** (분 생략 시 15, 상한 480): `.claude/hooks/gate.sh testfile on <분>`
- **off**: `.claude/hooks/gate.sh testfile off`
- **status** 또는 인자 없음: `.claude/hooks/gate.sh testfile status`

출력 문구는 스크립트가 만든다 — 여기서 따로 지어내지 않는다.

## 게이트를 여는 것은 사용자만 한다

Claude 는 게이트를 임의로 열지 않는다. 테스트 파일이 커밋에 필요하다고 판단되면 **왜 필요한지,
어떤 파일인지, 몇 줄인지** 를 먼저 보고하고 사용자의 명시 승인을 받는다.

특히 다음은 게이트를 열 사유가 **아니다**:
- "검증이 필요해서 만들었다" → 확인은 scratchpad 에서 하고 커밋하지 않는다.
  CLAUDE.md §완료 기준은 "검증 스크립트가 없으면 **없다고 보고한다**" 이지 "만들어라"가 아니다.
- "기존 테스트가 깨져서 고쳐야 한다" → 테스트를 고쳐야만 통과하는 변경은 **설계를 되짚을 신호**다.
  기존 단정을 바꾸기 전에 그 단정을 건드리지 않는 대안이 있는지 먼저 검토하고 사용자에게 보고한다.

작업이 끝나면 `/testfile off` 로 즉시 잠근다. 게이트는 짧게(기본 15분) 연다.
