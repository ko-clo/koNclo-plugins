---
name: prod-sync
description: NAS prod 운영서버에 직접 반영된(아직 커밋 안 된) 변경분을 로컬 워킹트리로 회수. "prod-sync", "prod 변경 로컬 반영", "운영 수정 가져와", "prod에 직접 고친거 로컬로", "prod 미커밋 반영" 키워드 매칭 시 호출. 정본 절차는 /prod-sync 명령.
---

# prod-sync — 운영서버 미커밋 변경 회수

## 언제 쓰나
누군가(또는 AI가) **NAS prod `/volume1/docker/testerp` 에서 직접 편집**해 두었는데 아직
git 에 커밋/푸시되지 않은 tracked 변경이 있고, 그걸 **정식 버전관리에 넣기 위해 로컬로
가져오려** 할 때. 이미 origin 에 있는 커밋은 `git pull` 이 담당하므로 대상 아님.

## 정본 = `/prod-sync` 명령
실행 절차·가드는 전부 `.claude/commands/prod-sync.md` 에 있다. 이 스킬이 뜨면 그 명령 절차를 따른다.

- `/prod-sync` 또는 `/prod-sync status` → prod 미커밋 변경 **미리보기**(읽기 전용).
- `/prod-sync go` → 실변경분을 **현재 로컬 워킹트리에 반영**.
- `/prod-sync go --files a,b` → 지정 파일만. `--repo testerp-legacy` → 레거시 저장소.

## 핵심 원칙 (반드시 지킴)
1. **prod 읽기 전용** — prod 에서 커밋/편집/docker 조작 금지. `git status`/`diff`/`show` 만.
2. **방향 prod→로컬 단방향** — dev/로컬을 prod 로 밀지 않는다.
3. **EOL 노이즈 제외** — prod 워킹트리는 CRLF↔LF 재저장으로 파일 전체가 바뀐 듯 보인다.
   `git diff --ignore-all-space` 로 **실변경만** 추려 반영하고, 로컬로 EOL 을 옮기지 않는다.
4. **untracked 생성물 제외** — `??`(data/·reports/ 등 런타임 산출물)는 가져오지 않는다.
5. **로컬 커밋/푸시 안 함** — 워킹트리만 수정. 검토 후 사용자가 정식 흐름으로 커밋.
6. **베이스 불일치는 플래그** — 로컬 브랜치가 prod HEAD 와 달라 앵커를 못 찾으면 강제 적용하지
   말고 "미적용(앵커 없음)"으로 보고. prod 원본의 명백한 버그는 그대로 옮겼음을 밝히고 수정안 제시.
7. **NAS 게이트** — 명령이 30분 자동 오픈(읽기전용). 끝나면 `/nas off`.

## 관련
- 반대 방향(로컬→dev 임시 반영)은 `/server-test`, 원복은 `/server-clear`.
- prod↔origin 정합·revert 는 정식 PR 흐름(develop→main). prod 직접 커밋은 원칙 위반.
