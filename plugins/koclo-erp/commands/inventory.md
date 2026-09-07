---
description: 통합재고관리 서브탭 에이전트 목록 표시 · 직접 호출 라우팅
argument-hint: "[서브탭 또는 요청 내용] (생략 시 에이전트 목록 표시)"
---
사용자가 `/inventory $ARGUMENTS` 를 실행했다. 통합재고관리 탭(9개 서브탭) 작업을 전담 에이전트로 위임하는 진입점이다.
라우팅·회귀검증 규범은 `inventory` 스킬, 업무규칙은 `.claude/memory/domain/inventory.md`, 구조는 `.claude/memory/service/inventory-architecture.md` 를 따른다.

## 인자가 **없을 때** (`/inventory` 단독) — 에이전트 목록 표시

아래 표를 **그대로 출력**하고, "번호·서브탭명·에이전트명 중 무엇으로든 지정하면 해당 에이전트로 바로 위임합니다. 여러 탭이면 함께 적어주세요."라고 안내한 뒤 사용자의 선택을 기다린다. (임의로 에이전트를 먼저 호출하지 않는다.)

| # | 서브탭 | 에이전트 | 담당 |
|---|---|---|---|
| 0·7 | 종합 · 로직표 | `inventory-summary-agent` | KPI 카드, 매장별 요약(등급·커트오프·유형별 카운트), 판정 파라미터 13상수 표시 |
| 1·5 | 반품관리 · 60%무판매 | `inventory-returns-agent` | 반품 판정표(재고·2주판매·점수·경과일·신뢰도·사유), 무판매율표, 검색·Excel |
| 2·3 | 이고관리 · 깔교관리 | `inventory-transfer-agent` | 이고 5유형(약→강/강→강/강→약/약→약/대거래처) 보내는·받는 매장, Bad/Good 칼라 교환계획 |
| 4 | 진행중샘플 | `inventory-sample-agent` | 매장별 진행중 샘플표 ⚠ 판정은 샘플반납 정본과 동기 |
| 6·8 | 주간플랜 · 반품검수장 | `inventory-plan-agent` | 반품+이고 일·월·화 예산 그리디 배분, 검수장 3목록 조회/추가/삭제(**탭 유일 쓰기**) |
| — | 백엔드·데이터 | `inventory-data-agent` | router 4EP·service 응답 계약·`inventory_action_items`/`inventory_snapshots`·야간 빌드 판정 산식 |

> 공통 셸(`InventoryReportView.js`)·공용 헬퍼(`inventoryShared.js`)·`/api/inventory/overview` 응답 9키·
> `LOGIC_PARAMS`·`_TRANSFER_TYPES` 등 **여러 서브탭에 걸친 변경**은 `inventory` 스킬 §2(공유 자산)대로
> 영향 에이전트를 함께 위임한다.

## 인자가 **있을 때** (`/inventory <요청>`) — 직접 라우팅

1. `$ARGUMENTS` 에서 대상 서브탭(들)을 위 표로 식별한다. 모호하면 AskUserQuestion 으로 1회 확인.
2. 식별된 에이전트를 **Agent 도구로 즉시 위임**한다(요청 원문 + 관련 파일 컨텍스트 전달). 여러 서브탭이면 **단일 메시지로 병렬 위임**.
3. 에이전트가 공유 자산 변경을 보고하면 영향 서브탭을 추가 위임하거나 메인이 조정한다.
4. 작업 후 `inventory` 스킬 §3 회귀 게이트(import 스모크·9탭 렌더·콘솔 0·탭 카운트 배지 실측·스냅샷 없음 경로·빌드리스·타 탭 무손상)로 검증한다.

예) `/inventory 60%무판매에 사입처 컬럼 추가` → `inventory-returns-agent` 단독.
`/inventory 이고 신규 유형 추가` → `inventory-transfer-agent` + `inventory-data-agent` + `inventory-summary-agent`(KPI) 병렬.
`/inventory 진행중샘플 판정 규칙 변경` → `inventory-sample-agent` + **`sample-return-logic-agent`**(교차 정본) 병렬.

## 경계

「무엇을 반품·이고·깔교할지 결정하고 실행」은 이 커맨드가 아니라 **`returns-agent`** 다.
이 커맨드는 **탭 화면·API·DB 개발/수정** 전용이다.
