---
name: retail-reorder
description: 소매 리오더 탭 작업 라우팅. "소매리오더", "소매 리오더", "retail-reorder", "리오더 탭", "주문장 탭", "리포트 보기", "매장별 요약", "전체핵심", "행거 컬럼", "지급율 컬럼", "주문표 모달", "빌드 이력", "안전재고 설정", "주문장 생성 화면", "store-metrics" 등 소매 리오더 탭/영역의 수정·조회·기능추가 요청 시 호출. 요청 영역을 식별해 전담 에이전트로 위임하고 전체 탭 회귀를 검증한다. (주문장 *생성·배포 운영*은 order-agent, 리포트 내 베스트3종은 best-* 소관 — §경계)
---

# 소매 리오더 탭 작업 — 라우팅 스킬

> 소매 리오더(`OrderView.js`)는 **실행(주문장 생성 UI) · 리포트 보기(전체핵심 + 베스트3종) · 빌드 이력** 으로 구성된다.
> 이 스킬은 **메인 Claude가 따르는 절차서**다: 영역 식별 → 전담 에이전트 위임(Agent 도구) → 결과 통합 → 전체 탭 회귀 검증.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다(중복 서술 금지).

## 0. 영역 ↔ 에이전트 ↔ 파일 매핑

| # | 영역 | 에이전트 | 프론트 | API | DB/service |
|---|---|---|---|---|---|
| 0 | 리포트·전체핵심 | `retail-reorder-report-agent` | `OrderView.js`(report mode: 매장별요약·KPI·행거/지급율·주문표 모달·빌드이력) | `GET /api/order/build/latest`·`/build/detail/{id}`·`/build/runs`·`/store-metrics` | `fetch_order_build_*`·`fetch_store_extra_metrics` / `order_build_runs`·`order_build_store_summary`·`order_build_store_payload`·`backorder_products` |
| 1 | 실행·생성 UI | `retail-reorder-run-agent` | `OrderView.js`(run mode: 주문 파라미터·안전재고 설정·PKL 상태·진행 폴링) | `POST /api/order/run`·`GET /api/order/status/{task}`·`/history`·`GET /api/reports/cache-status` | `task_runner`(실제 생성 로직은 order-agent 경계) |
| 2 | 데이터 파이프라인 | `retail-reorder-data-agent` | — (백엔드 owner) | `order_router` 전체·`/store-metrics` 병렬집계 | `order_service` 전체 + `vmd_service`/`payrate_service` 재사용·`order_build_*` 스냅샷 스키마 |

공통 셸: `frontend/js/views/OrderView.js`(모드 라우팅·리포트 서브탭) · `frontend/js/api.js`(order 메서드).
공통 백엔드: `backend/app/routers/order_router.py` · `backend/app/services/order_service.py`.
리포트 내 베스트3종(통합베스트/KA·TB 마스터/초특급볼륨)은 `BestProductView`(forced-tab) 재사용 → **best-* 에이전트 소관**(§경계).

## 1. 작업 흐름

1. **요청 영역 식별** — 사용자 요청이 어느 영역(들)인지 §0 표로 판별. 불명확하면 AskUserQuestion.
2. **단일 영역** → 해당 에이전트 1개에 위임.
3. **여러 영역** → **병렬 위임**(단일 메시지에 다중 Agent 호출).
4. **결과 통합** — 각 에이전트 변경/리스크를 메인이 취합.
5. **전체 탭 회귀 검증** — §3.

## 2. 위임 규칙 (공유 자산 주의)

영역은 독립이 아니다. 아래 **공유 자산**을 건드리는 작업은 영향받는 에이전트를 **모두** 위임하거나 메인이 직접 조정한다(`service/retail-reorder-architecture.md`로 영향 범위 확인):

- **`order_service` 응답 dict 키**(`fetch_order_build_detail`의 stores/items/meta, `fetch_store_extra_metrics`의 hanger/payrate/hanger_date) — report-agent가 소비, data-agent가 owner. 키 추가/변경은 양쪽 회귀.
- **`order_build_*` 스냅샷 스키마**(runs/store_summary/store_payload) — `order_v8_2_rebuild_FULL.py`의 dual-write가 쓰고 report 조회가 읽음. 컬럼 변경은 생성기(order-agent 경계)·조회 동시 영향.
- **`/store-metrics` 재사용 의존**(`vmd_service.fetch_vmd_overview_via_engine`·`payrate_service.fetch_payrate_overview_via_engine`) — VMD/지급율 service 시그니처·응답 키 변경 시 store-metrics 회귀. 그 service 자체 수정은 vmd-*/payrate-* 소관.
- **`OrderView.js` 공통 셸**(mode 라우팅·reportTabs·summaryRows computed) — run/report 모드가 공유. 모드 전환·서브탭 구조 변경은 report+run 함께 확인.

단일 영역에 갇힌 작업(예: 매장별 요약 셀 색만 변경)은 해당 에이전트 단독.

## 3. 회귀 검증 (dev-blueprint 스킬 §6 게이트 재사용)

- **import 스모크**(필수): `python -c "from app.routers import order_router"` 무에러 — 또는 배포 후 `Application startup complete` + `/docs` 200. (`py_compile`만으론 미충족)
- **탭 렌더**: 실행/리포트(전체핵심)/빌드이력 전부 정상 표시, **콘솔 에러 0**. 베스트3종 서브탭 전환도 정상(best 컴포넌트 재사용).
- **인터랙션**: 주문장 생성 폴링·안전재고 저장·리포트 매장별 요약(행거/지급율 lazy·남여토글)·주문표 모달 필터/정렬/미송·빌드 이력 보기 동작.
- **빌드리스 유지**(CDN Vue + ES모듈), **다른 탭 무손상**(라우팅 독립).
- 공유 자산 변경 시 §2의 교차 영향 영역을 실제로 다시 확인.

## 4. 작업 전 필독

- `.claude/memory/domain/retail-reorder.md` — 업무 규칙·용어·영역 관계·경계
- `.claude/memory/domain/retail-reorder-feedback.md` — 누적 피드백(F1~)
- `.claude/memory/service/retail-reorder-architecture.md` — Vue/API/DB/데이터 흐름
- `dev-blueprint` 스킬 — 탭 개발 표준(상위 규범)

## 경계 — order-agent / best-* / md-agent 와 혼동 금지

- **이 스킬/retail-reorder-\*-agent** = 소매 리오더 **탭 자체**의 화면(OrderView.js)·조회 API·order_service 개발/수정.
- **order-agent** = 주문장 **생성·검증·배포 운영**(testerp NAS 루프, auto_order_db, order_v8_2_rebuild_FULL, sales_daily/purchase_daily 인입). "오늘 주문장 만들어/배포" → order-agent.
- **best-\*-agent** = 리포트 보기 내 **베스트 3종 서브탭**(통합베스트/KA·TB/초특급볼륨) 화면·점수.
- **md-agent**(기획) = 소매 리오더 결과를 *입력 축*으로 쓰는 주문추천·포트폴리오 결정.
- "탭 화면/리포트/조회 API 수정" → 이 스킬. "주문장 생성·배포" → order-agent. "베스트 서브탭" → best-*. "무엇을 넣을지" → md-agent.
