---
name: agent-blueprint
description: 임의의 탭(View)에 대해 "서브탭 단위 작업 시스템"(Skill 라우팅 + 서브탭 전담 Agent + domain/architecture/feedback Memory + /command 메뉴)을 VMD와 동일 구조로 생성하는 메타 스킬. "/agent-blueprint <탭이름>", "탭 에이전트 시스템 만들어", "서브탭 에이전트 구축", "이 탭도 vmd처럼" 등에서 호출. 탭 이름 미입력 시 대상 탭을 먼저 묻고, 파일 생성 전 반드시 plan을 제시해 승인받는다.
---

# agent-blueprint — 탭 작업 시스템 생성기

> 한 탭(View)에 대해 **서브탭 단위 작업을 라우팅·위임·검증하는 3계층 시스템**을 생성한다.
> **정본 레퍼런스 = VMD 시스템**(이미 구축 완료). 그 구조·포맷을 `<tab>` 에 **그대로 복제**한다.
> 탭 개발 표준 자체는 `dev-blueprint` 스킬, 에이전트 공통 규칙은 `.claude/memory/meta/agent_kernel.md` 를 따른다(중복 서술 금지).

## 산출물 (탭 1개당)

```
.claude/
├── skills/<tab>/SKILL.md                    ← 서브탭 식별→위임→회귀검증 라우팅
├── agents/<tab>-<subtab>-agent.md           ← 서브탭 1개당 1 에이전트
│   └── … (서브탭 수만큼)
├── commands/<tab>.md                        ← 인자 없으면 에이전트 목록, 있으면 직접 위임
└── memory/
    ├── domain/<tab>.md                      ← 용어·서브탭 관계·업무규칙·공유의존
    ├── domain/<tab>-feedback.md             ← 피드백 누적(F1~)  ※포함 결정 시
    ├── service/<tab>-architecture.md        ← 화면파일·API·DB·데이터 흐름
    ├── MEMORY.md  (수정)                     ← 인덱스 섹션 추가
    └── meta/agent_kernel.md  (수정)          ← §1 피드백 표에 <tab>-* 행 추가
```

복제 원본(그대로 모방할 파일): `skills/vmd/SKILL.md`, `agents/vmd-*.md`, `commands/vmd.md`, `memory/domain/vmd.md`, `memory/domain/vmd-feedback.md`, `memory/service/vmd-architecture.md`.

## 절차

### 0. 대상 탭 식별
- `/agent-blueprint <탭이름>` 처럼 **인자가 있으면** 그 탭을 대상으로 한다.
- **인자가 없으면** `frontend/js/views/*View.js` 목록을 제시하고 **AskUserQuestion 으로 대상 탭을 묻는다**(임의 진행 금지).

### 1. 탐색 (Explore, 읽기 전용 — 파일 생성 전)
대상 탭의 다음을 매핑한다(VMD에서 한 것과 동일):
1. **공통 셸**: `frontend/js/views/<Tab>View.js` — 탭 라우팅·로딩·서브탭 목록.
2. **서브탭(=위젯)**: `frontend/js/widgets/<Tab>*.js` 각각이 어느 서브탭인지. 공유 계산 모듈(예: `*Compute.js`)도 식별.
3. **백엔드**: `backend/app/routers/<tab>_router.py`(엔드포인트), `backend/app/services/<tab>_service.py`(함수·SQL·응답 키), `backend/scripts/`(빌드/정본 생성기).
4. **DB**: service의 SQL/ORM에서 읽고 쓰는 테이블 전부.
5. **공유 자산**: 여러 서브탭이 함께 의존하는 것(공통 API 응답 키·계산식·공유 DB테이블·service 상수) — 교차 영향 경계.
6. **컨벤션 확인**: `skills/vmd/*`·`agents/vmd-*`·`memory/domain/vmd.md`·`memory/service/vmd-architecture.md` 를 원본으로, 기존 `agent_kernel.md`·`MEMORY.md` 포맷.

> 기존 에이전트/스킬과 **트리거 키워드 충돌**이 있는지 확인한다(예: VMD↔md-agent). 있으면 경계를 메모리·에이전트에 명시한다.

### 2. Plan 제시 (필수 — 승인 전 파일 생성 절대 금지)
**EnterPlanMode 로 진입**해 아래를 담은 계획을 작성하고 **ExitPlanMode 로 승인**받는다(VMD 작업과 동일 절차):
- **Context**: 왜 이 시스템이 필요한지 + 대상 탭/서브탭 요약.
- **산출물 트리**: 위 구조에 실제 서브탭·파일명을 채운 것.
- **서브탭 ↔ 에이전트 ↔ 파일/API/DB 매핑 표**(탐색 결과).
- **결정 포인트(질문)** — 아래 §결정 포인트를 AskUserQuestion 으로 확인.
- **검증 계획**.

### 3. 생성 (승인 후)
VMD 산출물을 **템플릿으로 그대로 따라** 작성한다(아래 §컨벤션). 파일은 모두 `.claude/**`(직접 쓰기 허용). 운영 코드/DB는 건드리지 않는다. 커밋은 별도 승인 시에만.

### 4. 검증 (VMD 검증 체크리스트 재사용)
- 산출 파일 전부 존재 + 에이전트 frontmatter `name` 정상.
- 새 세션에서 `<tab>-*-agent` 가 Agent 도구 목록에 노출, `<tab>` 스킬/`/<tab>` 커맨드 인식.
- `architecture.md` 의 엔드포인트·DB테이블·API 키가 **실제 router/service와 일치**(코드 직접 대조).
- 기존 항목 무손상(추가만, 삭제 0), 트리거 충돌 경계 명시.

## 컨벤션 (VMD 정본 모방)

**스킬** `skills/<tab>/SKILL.md`: frontmatter `name:<tab>` + 트리거 키워드 description. 본문 = ⓪서브탭↔에이전트↔파일 표 ①작업흐름(식별→위임→병렬→통합→회귀) ②공유 자산 위임 규칙 ③회귀검증(`dev-blueprint` §6 재사용) ④작업 전 필독(domain/service 메모리).

**에이전트** `agents/<tab>-<subtab>-agent.md`: frontmatter = `name` + `description`만(최소). 본문 = 담당 범위·작업 전 필독(kernel·domain·architecture·dev-blueprint)·담당 파일(프론트/API/service/DB)·공유 자산 변경 시 메인 보고·피드백 누적·보고 형식.

**커맨드** `commands/<tab>.md`: frontmatter `description`+`argument-hint`. 인자 없으면 **에이전트 목록 표 출력 후 선택 대기**, 인자 있으면 **식별→Agent 도구 즉시 위임→회귀검증**. (`commands/vmd.md` 그대로 변형)

**메모리** `memory/domain/<tab>.md`(용어·서브탭 역할·밴딩·임계·공유의존, `type: reference`, `[[<tab>-architecture]]` cross-ref) / `memory/service/<tab>-architecture.md`(파일 매핑·API↔service·DB 테이블·응답 키 출처·데이터 흐름·성능 메모) / `memory/domain/<tab>-feedback.md`(kernel §1 F번호 포맷, 초기 빈 템플릿).

**인덱스·커널**: `MEMORY.md` 에 "`<탭>` — 탭 개발 시스템" 섹션 추가(추가만). `agent_kernel.md` §1 표에 `<tab>-* (N개)` → feedback/통합규칙 행 추가 + 인트로 보강.

## 결정 포인트 (plan 단계에서 AskUserQuestion)
1. **서브탭 커버리지** — 모든 서브탭 1:1 에이전트 vs 일부(예: 단순 오버뷰)는 스킬이 직접 담당 vs 범위 제외.
2. **피드백 학습 메모리** — `<tab>-feedback.md` + kernel §1 학습 구조 포함(기존 컨벤션) vs 메모리 최소(domain+architecture 2개).
3. **트리거 충돌** — 기존 에이전트와 키워드가 겹치면 경계 규칙을 어떻게 명시할지.

## 금지
- **plan 제시·승인 전 파일 생성** (이 스킬의 1순위 규칙).
- 운영 코드/DB 수정, 미승인 커밋.
- VMD와 다른 임의 구조 신설(정본 모방 — 벗어나려면 plan에 사유 명시).
- `dev-blueprint`/`agent_kernel.md` 내용 중복 서술(참조만).
