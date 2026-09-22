# agent-blueprint — 절차와 결정 포인트

> 본체 `SKILL.md` 에서 분리. 작업을 진행하는 동안에 읽는다.

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

## 결정 포인트 (plan 단계에서 AskUserQuestion)
1. **서브탭 커버리지** — 모든 서브탭 1:1 에이전트 vs 일부(예: 단순 오버뷰)는 스킬이 직접 담당 vs 범위 제외.
2. **피드백 학습 메모리** — `<tab>-feedback.md` + kernel §1 학습 구조 포함(기존 컨벤션) vs 메모리 최소(domain+architecture 2개).
3. **트리거 충돌** — 기존 에이전트와 키워드가 겹치면 경계 규칙을 어떻게 명시할지.
