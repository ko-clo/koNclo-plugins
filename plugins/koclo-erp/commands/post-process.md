---
description: 후처리마스터 탭 영역 에이전트 목록 표시 · 직접 호출 라우팅
argument-hint: "[영역 또는 요청 내용] (생략 시 에이전트 목록 표시)"
---
사용자가 `/post-process $ARGUMENTS` 를 실행했다. 후처리마스터 탭(상품등급 그리드·워크북/시트 편집·증가/차감 주문·데이터/캐시 파이프라인) 작업을 전담 에이전트로 위임하는 진입점이다.
라우팅·회귀검증 규범은 `post-process` 스킬, 업무규칙은 `.claude/memory/domain/post-process.md`, 구조는 `.claude/memory/service/post-process-architecture.md` 를 따른다.

## 인자가 없을 때 (`/post-process` 단독) — 에이전트 목록 표시

아래 표를 그대로 출력하고, "번호·영역명·에이전트명 중 무엇으로든 지정하면 해당 에이전트로 바로 위임합니다. 여러 영역이면 함께 적어주세요."라고 안내한 뒤 사용자의 선택을 기다린다. 임의로 에이전트를 먼저 호출하지 않는다.

| # | 영역 | 에이전트 | 담당 |
|---|---|---|---|
| 0 | 상품등급 그리드·매입차감 | `post-process-grid-agent` | 여자/남자 상품등급, 검색·정렬·페이지, 메모, 하이라이트, 매입차감/성과, Excel/JSON |
| 1 | 워크북·시트·모달 편집 | `post-process-workbook-agent` | 시트 전환/이름/선택 이동·복사, 서버저장/불러오기, 상품추가, 샘플집계 |
| 2 | 증가주문·차감주문 | `post-process-order-agent` | 증가/차감 상품 추가, 티어 최소수량, 하위컬러 자동선택, Excel, 서버 시트 append |
| 3 | 데이터 파이프라인·캐시 | `post-process-data-agent` | `/api/post-process/grid`, `/aggs`, DB direct, `post_process_products`, cache clear, 야간 프리컴퓨트 |

> 공통 셸(`ProductMasterView.js`)·`postProcessStore.js`·`/api/master-sheets*`·`post_process_service` 응답 키는 여러 영역에 걸친 변경이다.
> 경계: 스코어랭킹 선택/전송 화면 → `score-ranking-*`, 소매 리오더 소비 화면 → `retail-reorder-*`, 실제 주문장 생성/xls 운영 → `order-agent`.

## 인자가 있을 때 (`/post-process <요청>`) — 직접 라우팅

1. `$ARGUMENTS` 에서 대상 영역(들)을 위 표로 식별한다. 모호하면 AskUserQuestion 으로 1회 확인한다.
2. 식별된 에이전트를 Agent 도구로 즉시 위임한다(요청 원문 + 관련 파일 컨텍스트 전달). 여러 영역이면 단일 메시지로 병렬 위임한다.
3. 에이전트가 공유 자산 변경을 보고하면 영향 영역을 추가 위임하거나 메인이 조정한다.
4. 작업 후 `post-process` 스킬 §3 회귀 게이트로 검증한다.

예)
- `/post-process 남자 상품등급 정렬 이상해` → `post-process-grid-agent`.
- `/post-process 서버저장하면 기본 시트까지 저장돼` → `post-process-workbook-agent` + master-sheet API면 data 영향 확인.
- `/post-process 증가주문 티어 최소수량 바꿔` → `post-process-order-agent`.
- `/post-process grid 느려` → `post-process-data-agent` + 프론트 로딩/에러 영향이면 grid 회귀.
- `/post-process 스코어랭킹에서 전송 실패` → 경계상 `score-ranking-list-agent`와 `/api/master-sheets*` 공유 영향 확인.
