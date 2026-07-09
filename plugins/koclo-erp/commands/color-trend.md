---
description: 인기컬러 탭 영역 에이전트 목록 표시 · 직접 호출 라우팅
argument-hint: "[영역 또는 요청 내용] (생략 시 에이전트 목록 표시)"
---
사용자가 `/color-trend $ARGUMENTS` 를 실행했다. 인기컬러 탭(전체 칼라·포인트 칼라·VMD 팔레트·인기종합순·부진칼라·외부 트렌드·상세 전송·데이터 파이프라인) 작업을 전담 에이전트로 위임하는 진입점이다.
라우팅·회귀검증 규범은 `color-trend` 스킬, 업무규칙은 `.claude/memory/domain/color-trend.md`, 구조는 `.claude/memory/service/color-trend-architecture.md` 를 따른다.

## 인자가 없을 때 (`/color-trend` 단독) — 에이전트 목록 표시

아래 표를 그대로 출력하고, "번호·영역명·에이전트명 중 무엇으로든 지정하면 해당 에이전트로 바로 위임합니다. 여러 영역이면 함께 적어주세요."라고 안내한 뒤 사용자의 선택을 기다린다. 임의로 에이전트를 먼저 호출하지 않는다.

| # | 영역 | 에이전트 | 담당 |
|---|---|---|---|
| 0 | 전체 칼라·데님 | `color-trend-all-agent` | 전체 칼라 표, 기본/포인트 필터, 판매/효율 정렬, 데님 사이드, 상세 오픈 |
| 1 | 포인트 칼라·선택 | `color-trend-point-agent` | 포인트/효율 카드, HOT/급상승/효율 badge, VMD 컨펌 체크, 선택바, 복사 |
| 2 | VMD 팔레트 | `color-trend-vmd-agent` | 매장별 비기본·비데님 컬러 TOP 10, 빈 매장 표시, 상세 오픈 |
| 3 | 인기종합순 | `color-trend-ranking-agent` | `trend_score` 순위/바, 데님 사이드, 상세 오픈 |
| 4 | 부진칼라 경고 | `color-trend-bad-agent` | dead/bad 컬러 표, 재고·판매·효율·점수 표시 |
| 5 | 외부 트렌드 | `color-trend-external-agent` | 캐시 글로벌 팔레트, 외부 source 성공/실패, 출처/링크 표시 |
| 6 | 상세·마스터시트 전송 | `color-trend-transfer-agent` | 상세 모달 필터/선택/이미지, 신규 워크북 생성, 기존 워크북 append |
| 7 | 데이터 파이프라인 | `color-trend-data-agent` | `/api/color-trend/overview`, 색상 정규화, trend/dead 산식, snapshot, 레거시 대조 |

> 공통 셸(`ColorTrendView.js`)·`color_trend_service.py`·`/api/color-trend/overview` 응답 키·`/api/master-sheets*`는 여러 영역에 걸친 변경이다.
> 경계: `/vmd` 행거 대시보드 → `vmd-*`, 점수 랭킹 화면 → `score-ranking-*`, 후처리마스터 워크북 자체 → `post-process-*`, 실제 주문장 생성/xls 운영 → `order-agent`.

## 인자가 있을 때 (`/color-trend <요청>`) — 직접 라우팅

1. `$ARGUMENTS` 에서 대상 영역(들)을 위 표로 식별한다. 모호하면 AskUserQuestion 으로 1회 확인한다.
2. 식별된 에이전트를 Agent 도구로 즉시 위임한다(요청 원문 + 관련 파일 컨텍스트 전달). 여러 영역이면 단일 메시지로 병렬 위임한다.
3. 에이전트가 공유 자산 변경을 보고하면 영향 영역을 추가 위임하거나 메인이 조정한다.
4. 작업 후 `color-trend` 스킬 §3 회귀 게이트로 검증한다.

예)
- `/color-trend 전체 칼라 검색이 안돼` → `color-trend-all-agent`.
- `/color-trend 포인트 컬러 선택 복사가 이상해` → `color-trend-point-agent`.
- `/color-trend VMD 팔레트 매장별로 비어 보여` → `color-trend-vmd-agent` + 응답 키면 data 영향 확인.
- `/color-trend 부진칼라 기준 바꿔` → `color-trend-bad-agent` + `color-trend-data-agent`.
- `/color-trend 외부 트렌드 출처 추가` → `color-trend-external-agent` + cached source 변경이면 data-agent.
- `/color-trend 마스터시트로 보내면 상품이 누락돼` → `color-trend-transfer-agent`.
- `/color-trend 색상 그룹 산식 다시 봐` → `color-trend-data-agent` + 영향 화면 에이전트.
