---
description: 베스트상품 대시보드 서브탭 에이전트 목록 표시 · 직접 호출 라우팅
argument-hint: "[서브탭 또는 요청 내용] (생략 시 에이전트 목록 표시)"
---
사용자가 `/best-products $ARGUMENTS` 를 실행했다. 베스트상품 대시보드(3개 서브탭, 읽기전용) 작업을 전담 에이전트로 위임하는 진입점이다.
라우팅·회귀검증 규범은 `best-products` 스킬, 업무규칙은 `.claude/memory/domain/best-products.md`, 구조는 `.claude/memory/service/best-products-architecture.md` 를 따른다.

## 인자가 **없을 때** (`/best-products` 단독) — 에이전트 목록 표시

아래 표를 **그대로 출력**하고, "번호·서브탭명·에이전트명 중 무엇으로든 지정하면 해당 에이전트로 바로 위임합니다. 여러 탭이면 함께 적어주세요."라고 안내한 뒤 사용자의 선택을 기다린다. (임의로 에이전트를 먼저 호출하지 않는다.)

| # | 서브탭 | 에이전트 | 담당 |
|---|---|---|---|
| 0 | 통합베스트 | `best-integrated-agent` | 전사 교차 점수 랭킹(6요소 가중합), 성별 분리(여30+남20), 매장수임계·momentum 선정, 실판매2주·보충필요 |
| 1 | KA·TB 마스터 | `best-ka-tb-agent` | product_code KA/TB 코드상품 전수(필터 없음), 매장별 SKU, score 정렬 |
| 2 | 초특급볼륨 | `best-volume-agent` | KA/TB 누적 실판매(sold_qty) 매장별 Top17, 사입가·판매가(db_master_loader) |

> 공통 셸(`BestProductView.js`)·적재(`persist_best_products`)·`best_v2_router` JOIN·`db_master_loader` 가격 등 **여러 서브탭에 걸친 변경**은 `best-products` 스킬 §2(공유 자산)대로 영향 에이전트를 함께 위임한다.

## 인자가 **있을 때** (`/best-products <요청>`) — 직접 라우팅

1. `$ARGUMENTS` 에서 대상 서브탭(들)을 위 표로 식별한다. 모호하면 AskUserQuestion 으로 1회 확인.
2. 식별된 에이전트를 **Agent 도구로 즉시 위임**한다(요청 원문 + 관련 파일 컨텍스트 전달). 여러 서브탭이면 **단일 메시지로 병렬 위임**.
3. 에이전트가 공유 자산 변경을 보고하면 영향 서브탭을 추가 위임하거나 메인이 조정한다.
4. 작업 후 `best-products` 스킬 §3 회귀 게이트(import 스모크·적재 검증·3탭 렌더·이미지/품번·콘솔 0·JOIN 복원·빌드리스·타 탭 무손상)로 검증한다.

예) `/best-products 초특급볼륨 가격 0 고쳐` → `best-volume-agent`(+ db_master_loader 공유 영향 보고). `/best-products persist에 컬럼 추가` → 3 서브탭 병렬(적재 공유).

## 경계 — md-agent 와 혼동 금지
"탭 수정/기능추가/조회 화면/적재 로직" → 이 커맨드(best-products). "베스트 활용 주문추천/적중률 기획/무엇을 넣을지" → md-agent.
