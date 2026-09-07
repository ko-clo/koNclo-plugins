---
name: mobile-blueprint
description: 임의의 탭(View)에 모바일(<=768px) 전용 뷰를 신설하는 메타 스킬. "/mobile <탭이름>", "이 탭 모바일로", "모바일 버전 만들어", "모바일 전용 뷰", "폰에서 안 보여", "탭 모바일 대응" 등에서 호출. 정본 레퍼런스=샘플반납 모바일. 탭 이름 미입력 시 대상 탭을 먼저 묻고, 파일 생성 전 반드시 plan 을 제시해 승인받는다.
---

# mobile-blueprint — 탭 모바일 전용 뷰 생성기

> 한 탭에 대해 **데스크톱 뷰를 수정하지 않고** 좁은 화면 전용 뷰를 병행 투입한다.
> **구조 정본 = `.claude/memory/service/mobile-architecture.md`** (여기 내용을 중복 서술하지 않는다 — 반드시 먼저 읽는다).
> **레퍼런스 구현 = 샘플반납** `frontend/js/views/mobile/SampleReturnMobile.js`.
> 탭 개발 표준은 `dev-blueprint`, 에이전트 공통 규칙은 `.claude/memory/meta/agent_kernel.md`.

## 산출물 (탭 1개당)

```
frontend/
├── js/views/mobile/<Tab>Mobile.js     ← 신규 (표현만 — 판정·API 는 데스크톱과 공유)
├── css/mobile/<tab>.css               ← 신규 (.mv-<tab> 변수 + 탭 고유 규칙만, ~30줄)
├── js/app.js                          ← 수정 (해당 라우트 component 를 responsive() 로 래핑 — 1줄)
├── index.html                         ← 수정 (델타 CSS <link> 1줄 + 캐시버스터)
└── js/widgets/<tab>Logic.js           ← 필요 시 (데스크톱 위젯에 갇힌 계산을 공유 모듈로 추출)

.claude/memory/service/mobile-architecture.md  ← 수정 (§5 현황 표에 행 추가)
```

**`responsive.js` · `mobile.css` 의 `.mv-*` 베이스 · 앱 셸(상단바·드로어)은 이미 완성 — 신규 탭에서 수정하지 않는다.**

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

**EnterPlanMode 로 진입**해 아래를 담고 **ExitPlanMode 로 승인**받는다.

- **대상 탭 요약**: 서브탭 목록과 각각의 데이터 출처.
- **이식 범위 표** — 서브탭별로 `이식 / 축약 / 제외` + 사유:

  | 서브탭 | 처리 | 모바일 표현 | 사유 |
  |---|---|---|---|
  | … | 이식 | 카드 + 펼침 | |
  | … | 제외 | 데스크톱 안내 | iframe 미이관 |

- **공유 로직 추출 목록**: 위젯 → 공유 모듈로 옮길 함수와 그 이유(없으면 "추출 불필요" 명시).
- **남길 편집 기능**: 모바일에서도 저장 가능하게 둘 핵심 편집 1~2개.
- **팔레트 매핑**: `--mv-*` 5개 변수 ← 탭 정본 CSS 의 실제 값.
- **변경 파일 목록**: 신규/수정 구분, 수정은 몇 줄인지.
- **검증 계획**: `mobile-architecture.md` §6 항목.

**결정 포인트는 AskUserQuestion 으로 확인** (아래 §결정 포인트).

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

## 금지

- **plan 제시·승인 전 파일 생성·수정** (이 스킬의 1순위 규칙).
- **판정·계산 로직을 모바일 뷰에 복사** — 정본 이중화. 반드시 공유 모듈 import.
- **모바일 전용 API 신설** — 데스크톱과 동일 엔드포인트를 쓴다.
- **데스크톱 뷰 동작 변경** — 라우트는 감싸기만, 위젯 수정은 무동작 추출에 한정.
- `responsive.js` · `.mv-*` 베이스 · `.srm-*`(운영 중) 수정.
- 새 팔레트 발명 — 값은 탭 정본 CSS 에서 가져온다.
- `mobile-architecture.md` 내용 중복 서술(참조만).
- 미승인 커밋 · 미승인 `/server-test`.
