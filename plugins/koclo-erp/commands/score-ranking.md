---
description: 스코어랭킹 탭 영역 에이전트 목록 표시 · 직접 호출 라우팅
argument-hint: "[영역 또는 요청 내용] (생략 시 에이전트 목록 표시)"
---
사용자가 `/score-ranking $ARGUMENTS` 를 실행했다. 스코어랭킹 탭(오버뷰 셸·상품/색상 리스트·데이터 파이프라인) 작업을 전담 에이전트로 위임하는 진입점이다.
라우팅·회귀검증 규범은 `score-ranking` 스킬, 업무규칙은 `.claude/memory/domain/score-ranking.md`, 구조는 `.claude/memory/service/score-ranking-architecture.md` 를 따른다.

## 인자가 없을 때 (`/score-ranking` 단독) — 에이전트 목록 표시

아래 표를 그대로 출력하고, "번호·영역명·에이전트명 중 무엇으로든 지정하면 해당 에이전트로 바로 위임합니다. 여러 영역이면 함께 적어주세요."라고 안내한 뒤 사용자의 선택을 기다린다. 임의로 에이전트를 먼저 호출하지 않는다.

| # | 영역 | 에이전트 | 담당 |
|---|---|---|---|
| 0 | 오버뷰 셸·KPI·필터 | `score-ranking-overview-agent` | `/score` 화면 헤더, stale warning, 종합/주문장/매장 칩, 기간·날짜·정렬·필터, KPI |
| 1 | 상품/색상 리스트·마스터시트 전송 | `score-ranking-list-agent` | 상품 row, 색상 아코디언, 이미지, 선택/해제, 기존/새 워크북 전송 |
| 2 | 데이터 파이프라인·점수 산식 | `score-ranking-data-agent` | `/api/score-ranking/overview`, 점수 산식, DB 원천, 응답 계약, 컬러 트렌드 재사용 영향 |

> 공통 셸(`ScoreView.js`)·`ScoreRankingProductList.js`·`score_ranking_service` 응답 키·마스터시트 전송 계약은 여러 영역에 걸친 변경이다.
> 경계: 베스트상품 정본 계산/화면 → `best-*`, 소매 리오더 소비 화면 → `retail-reorder-*`, 주문장 생성 산식·xls 운영 → `order-agent`, 기획/주문추천 → `md-agent`.

## 인자가 있을 때 (`/score-ranking <요청>`) — 직접 라우팅

1. `$ARGUMENTS` 에서 대상 영역(들)을 위 표로 식별한다. 모호하면 AskUserQuestion 으로 1회 확인한다.
2. 식별된 에이전트를 Agent 도구로 즉시 위임한다(요청 원문 + 관련 파일 컨텍스트 전달). 여러 영역이면 단일 메시지로 병렬 위임한다.
3. 에이전트가 공유 자산 변경을 보고하면 영향 영역을 추가 위임하거나 메인이 조정한다.
4. 작업 후 `score-ranking` 스킬 §3 회귀 게이트로 검증한다.

예)
- `/score-ranking KPI 숫자 이상해` → `score-ranking-overview-agent` + 응답 계약이면 `score-ranking-data-agent`.
- `/score-ranking 색상 펼침에서 주간판매 컬럼 추가` → `score-ranking-list-agent` + 데이터 키 필요 시 `score-ranking-data-agent`.
- `/score-ranking 점수 산식 바꿔` → `score-ranking-data-agent` + 화면 표시 영향이면 overview/list 회귀.
- `/score-ranking 마스터시트 전송 실패` → `score-ranking-list-agent`(master-sheet API 자체 변경이면 공용 backend 소관 확인).
- `/score-ranking 베스트상품 탭 점수 고쳐` → 경계상 **best-\*** 로 라우팅.
