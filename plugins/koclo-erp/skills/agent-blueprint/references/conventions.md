# agent-blueprint — 컨벤션 (VMD 정본 모방)

> 본체 `SKILL.md` 에서 분리. 이름·형식을 정할 때에 읽는다.

## 컨벤션 (VMD 정본 모방)

**스킬** `skills/<tab>/SKILL.md`: frontmatter `name:<tab>` + 트리거 키워드 description(`Use when <탭> 탭/서브탭의 수정·조회·기능추가 요청을 받았을 때. 트리거 — "…", "…"` + 있으면 괄호 안 경계 안내. 스킬이 **무엇을 하는지**(위임·회귀 검증 요약)는 적지 않는다 — 적으면 본문을 읽지 않고 그 요약대로 움직인다). 본문 = ⓪서브탭↔에이전트↔파일 표 ①작업흐름(식별→위임→병렬→통합→회귀) ②공유 자산 위임 규칙 ③회귀검증(`dev-blueprint` §6 재사용) ④작업 전 필독(domain/service 메모리).

**에이전트** `agents/<tab>-<subtab>-agent.md`: frontmatter = `name` + `description`만(최소). 본문 = 담당 범위·작업 전 필독(kernel·domain·architecture·dev-blueprint)·담당 파일(프론트/API/service/DB)·공유 자산 변경 시 메인 보고·피드백 누적·보고 형식.

**커맨드** `commands/<tab>.md`: frontmatter `description`+`argument-hint`. 인자 없으면 **에이전트 목록 표 출력 후 선택 대기**, 인자 있으면 **식별→Agent 도구 즉시 위임→회귀검증**. (`commands/vmd.md` 그대로 변형)

**메모리** `memory/domain/<tab>.md`(용어·서브탭 역할·밴딩·임계·공유의존, `type: reference`, `[[<tab>-architecture]]` cross-ref) / `memory/service/<tab>-architecture.md`(파일 매핑·API↔service·DB 테이블·응답 키 출처·데이터 흐름·성능 메모) / `memory/domain/<tab>-feedback.md`(kernel §1 F번호 포맷, 초기 빈 템플릿).

**인덱스·커널**: `MEMORY.md` 에 "`<탭>` — 탭 개발 시스템" 섹션 추가(추가만). `agent_kernel.md` §1 표에 `<tab>-* (N개)` → feedback/통합규칙 행 추가 + 인트로 보강.
