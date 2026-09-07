---
description: 샘플반납 탭 영역 에이전트 목록 표시 · 직접 호출 라우팅
argument-hint: "[영역 또는 요청 내용] (생략 시 에이전트 목록 표시)"
---
사용자가 `/sample-return $ARGUMENTS` 를 실행했다. 샘플반납 탭(셸·매장상세·판정·데이터) 작업을 전담 에이전트로 위임하는 진입점이다.
라우팅·회귀검증 규범은 `sample-return` 스킬, 업무규칙은 `.claude/memory/domain/sample-return.md`, 구조는 `.claude/memory/service/sample-return-architecture.md` 를 따른다.

## 인자가 **없을 때** (`/sample-return` 단독) — 에이전트 목록 표시

아래 표를 **그대로 출력**하고, "번호·영역명·에이전트명 중 무엇으로든 지정하면 해당 에이전트로 바로 위임합니다. 여러 영역이면 함께 적어주세요."라고 안내한 뒤 사용자의 선택을 기다린다. (임의로 에이전트를 먼저 호출하지 않는다.)

| # | 영역 | 에이전트 | 담당 |
|---|---|---|---|
| 0 | 셸 · 리포트 상단 | `sample-return-report-agent` | 3모드 전환(데이터뷰·반납리포트·교차추천), 시뮬박스(여/남 기한·점수컷), 전체 핵심지표 6카드, 매장간 비교표, 전매장 통합엑셀 2종, 경고 배너 |
| 1 | 매장 상세 | `sample-return-store-agent` | 매장 KPI + 5서브탭(샘플집계명 상세·반납대상·집계샘플·상품 상세·반품집계), 정렬·이미지 토글, 매장엑셀 2종, 배치 폴더 서버 저장 |
| 2 | 판정 정본 | `sample-return-logic-agent` | 반납 사유 판정(기한초과·과락·무판매·교차부진·협의연장), 점수 컷오프, 컬러 규칙 — **JS↔py 2곳 정합 소유** |
| 3 | 백엔드·데이터 | `sample-return-data-agent` | router 4EP·계약 JSON(ref_date/pkl_date/meta/stores)·매장 병렬 빌드·버전스탬프 캐시·DB 11테이블·rebuild/batch |

> `sampleReturnLogic.js` 함수 시그니처·`appliedSim` 4파라미터·`items._checked` 모델·
> `sample_ledger`+`sample_products` LATERAL 규칙 등 **여러 영역에 걸친 변경**은
> `sample-return` 스킬 §2(공유 자산)대로 영향 에이전트를 함께 위임한다.
> 특히 **판정 규칙 변경은 `logic` + `data` 를 반드시 동시 위임**한다(정본 이중화).

## 인자가 **있을 때** (`/sample-return <요청>`) — 직접 라우팅

1. `$ARGUMENTS` 에서 대상 영역(들)을 위 표로 식별한다. 모호하면 AskUserQuestion 으로 1회 확인.
2. 식별된 에이전트를 **Agent 도구로 즉시 위임**한다(요청 원문 + 관련 파일 컨텍스트 전달). 여러 영역이면 **단일 메시지로 병렬 위임**.
3. 에이전트가 공유 자산 변경을 보고하면 영향 영역을 추가 위임하거나 메인이 조정한다.
4. 작업 후 `sample-return` 스킬 §3 회귀 게이트(import 스모크·3모드 렌더·매장 5서브탭·시뮬 왕복·엑셀 4종·판정 정합·빌드리스·타 탭 무손상)로 검증한다.

예) `/sample-return 매장간 비교표에 금액 컬럼 추가` → `sample-return-report-agent` 단독.
`/sample-return 반납 기한을 여4주로` → `sample-return-logic-agent` + `sample-return-data-agent` 병렬(정본 2곳).
`/sample-return 반납대상이 0건이다` → `sample-return-data-agent` 먼저(원천 확인) → 필요 시 `logic` 추가.

## 경계

「실제로 무엇을 반납·반품할지 결정하고 실행」은 이 커맨드가 아니라 **`returns-agent`** 다.
「샘플 진행/종결 판정 규칙 자체」의 정본은 `.claude/memory/domain/sample-judgment-rule.md`.
「통합재고관리 진행중샘플」은 **`/inventory`** 이지만 판정을 공유하므로 함께 회귀한다.
