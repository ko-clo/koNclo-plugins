# mobile-blueprint — 절차와 결정 포인트

> 본체 `SKILL.md` 에서 분리. 작업을 진행하는 동안에 읽는다.

## 절차

### 0. 대상 탭 식별
- `/mobile <탭이름>` 처럼 **인자가 있으면** 그 탭이 대상.
- **인자가 없으면** `frontend/js/navTabs.js` 의 탭 카탈로그를 근거로 목록을 제시하고
  **AskUserQuestion 으로 대상 탭을 묻는다**(임의 진행 금지).
- 이미 모바일 뷰가 있는 탭이면(`mobile-architecture.md` §5) **신설이 아니라 수정임을 알리고** 범위를 확인한다.

### 1. 탐색 (읽기 전용 — 파일 생성·수정 전)

1. **정본 3종 필독**: `mobile-architecture.md` → 대상 탭의 `.claude/memory/service/<tab>-architecture.md`
   → `.claude/memory/domain/<tab>.md`(+`<tab>-feedback.md` 있으면).
2. **데스크톱 뷰**: `frontend/js/views/<Tab>View.js` — 서브탭 구성·상태·로딩 흐름.
3. **위젯**: `frontend/js/widgets/<Tab>*.js` — 각 서브탭의 표 구조와 열.
4. **공유 로직 소재 파악** (이 스킬의 핵심 판단):
   판정·집계·포맷 함수가 **이미 공유 모듈에 있는지**, 아니면 **위젯 안에 갇혀 있는지**.
   갇혀 있으면 → **추출 대상**으로 목록화(동작 무변경 리팩터링).
5. **API**: 데스크톱이 호출하는 `frontend/js/api.js` 함수 — 모바일도 **그대로 재사용**한다.
6. **정본 팔레트**: `frontend/css/<tab>.css`(또는 위젯 인라인)에서 강조색 5개를 뽑는다.
7. **제외 후보 식별**: iframe 서브탭 · 엑셀 다운로드 · 대량 편집 그리드 · 차트 밀집 영역
   (`mobile-architecture.md` §4).

### 2. Plan 제시 (필수 — 승인 전 파일 생성·수정 절대 금지)

→ `references/plan-template.md`.

### 3. 구현 (승인 후) — `mobile-view-agent` 에 위임

`Agent` 도구로 `mobile-view-agent` 를 호출하고 **승인된 plan 전문**을 전달한다.
서브탭이 많아 병렬이 유리하면 서브탭 묶음별로 나눠 위임하되, **CSS 델타·라우트 래핑은 1곳에서만** 수행한다(충돌 방지).

**공유 로직 추출이 판정 규칙 변경을 수반하면** 그 탭 전담 에이전트(`<tab>-*-agent`)에 함께 위임한다.
모바일 작업이 판정을 바꾸는 것은 범위 밖이다.

### 4. 검증

`mobile-architecture.md` §6 을 그대로 수행한다. 특히:
- **수치 일치**(데스크톱 == 모바일 핵심 집계) — 다르면 로직 이중화 사고다.
- **데스크톱 무손상**(폭 > 768px).
- 돌린 명령과 결과를 보고에 명시한다. **못 돌린 것은 못 돌렸다고 쓴다.**

### 5. 마무리
- `mobile-architecture.md` §5 현황 표에 행 추가.
- 새로 배운 지뢰가 있으면 `/learn` 으로 `.claude/memory/domain/mobile-feedback.md` 에 F 누적.
- 커밋은 **명시 승인 후에만**.

## 결정 포인트 (plan 단계에서 AskUserQuestion)

1. **이식 범위** — 전 서브탭 vs 핵심 서브탭만(나머지 데스크톱 안내).
2. **편집 허용** — 조회 전용 vs 핵심 편집 1~2개 저장 허용.
3. **공유 로직 추출** — 위젯에 갇힌 계산을 지금 추출 vs 이번엔 조회 범위만 이식해 추출 회피.
