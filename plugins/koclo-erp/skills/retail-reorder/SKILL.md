---
name: retail-reorder
description: 소매 리오더 탭 작업 라우팅. "소매리오더", "소매 리오더", "retail-reorder", "retail-order", "리오더 탭", "주문장 탭", "리포트 보기", "전체핵심", "마스터주문", "상품 마스터", "매장별 요약", "행거 컬럼", "지급율 컬럼", "샘플건", "주문표 모달", "빌드 이력", "안전재고 설정", "데이터 상태", "생성 취소", "store-metrics" 등 소매 리오더 탭/영역의 수정·조회·기능추가 요청 시 호출. 주문장 생성·배포 운영은 order-agent, 베스트상품 정본 화면은 best-* 소관.
---

# 소매 리오더 탭 작업 — 라우팅 스킬

> 소매 리오더는 `OrderView.js`(`/order`)의 **실행 · 리포트 보기(전체핵심 + 베스트3종 + 상품 마스터) · 빌드 이력**과, 분리된 `OrderSheetView.js`(`/order-sheet`)의 **주문장 상세**로 구성된다.
> 이 스킬은 영역 식별 → 전담 에이전트 위임 → 결과 통합 → 전체 회귀 검증 순서로 쓴다.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다.

## 0. 영역 ↔ 에이전트 ↔ 파일 매핑

| # | 영역 | 에이전트 | 프론트 | API | DB/service |
|---|---|---|---|---|---|
| 0 | 리포트·전체핵심·주문장 상세 | `retail-reorder-report-agent` | `OrderView.js`(core: KPI·상단 재계산바·매장별요약·주요상품·주문표 모달·기존 탭 토글), `OrderSheetView.js`, `orderDetailShared.js` | `GET /api/order/build/latest`·`/build/detail/{id}`·`/build/runs`·`/store-metrics`·`/product-image` | `fetch_order_build_*`·`fetch_store_extra_metrics` / `order_build_*`·`backorder_products`·`sample_products`·`sample_ledger` |
| 1 | 마스터주문·상품 마스터 | `retail-reorder-report-agent` + 스키마/계산 변경 시 `retail-reorder-data-agent` | `OrderView.js`(마스터주문 후보/예산/선택반영, 상품 마스터 서브탭), `api.js` | `GET /api/order/build/master-order`·`POST /api/order/build/master-add`·`/api/master-sheets*`·`/api/best/integrated` | `fetch_master_order_candidates`·`add_master_order_items`·`volume_capacity_service`·best_*·master_sheets·inventory_snapshot·purchase_daily |
| 2 | 실행·생성 UI | `retail-reorder-run-agent` | `OrderView.js`(주문 파라미터·안전재고·데이터 상태·생성/취소·진행 폴링) | 현재 UI: `POST /api/reports/regenerate`·`GET /api/reports/task/{id}`·`POST /api/order/cancel/{id}`·`GET /api/order/data-status`; 직접 실행 API: `/api/order/run`·`/status/{id}`·`/history`; 보조: `/api/reports/cache-status`·`/api/config/safety_stock_config` | `task_runner`, `order_progress`, `fetch_order_data_status`; 실제 생성 산식은 order-agent 경계 |
| 3 | 데이터 파이프라인·응답 계약 | `retail-reorder-data-agent` | `api.js` 계약 영향 | `order_router` 전체 + report/config/master-sheet/best API 의존 | `order_service` 전체 + `vmd_service`/`payrate_service`/`best_volume_service`/`volume_capacity_service` 재사용·`order_build_*` 스냅샷 스키마 |

공통 셸: `frontend/js/views/OrderView.js`, `frontend/js/api.js`.
공통 백엔드: `backend/app/routers/order_router.py`, `backend/app/services/order_service.py`.
분리 상세 탭: `frontend/js/views/OrderSheetView.js`, `frontend/js/orderDetailShared.js`.

## 1. 작업 흐름

1. **요청 영역 식별** — 사용자 요청이 어느 영역인지 §0 표로 판별. 모호하면 한 번만 질문한다.
2. **단일 영역** → 해당 에이전트 1개에 위임한다.
3. **여러 영역** → 영향 에이전트를 함께 위임한다. 특히 `OrderView.js`, `order_service` 응답 키, `order_build_*` 스키마, 마스터주문 반영은 교차 영향이다.
4. **결과 통합** — 각 에이전트 변경/리스크를 메인이 취합한다.
5. **전체 탭 회귀 검증** — §3.

## 2. 위임 규칙 (공유 자산 주의)

- **`order_service` 응답 dict 키**: `fetch_order_build_detail`의 `meta/stores/items/gd/master_items/report_section`, `fetch_store_extra_metrics`의 `hanger/payrate/sample/*_ok`, `fetch_master_order_candidates`의 예산·후보 키는 프론트가 직접 소비한다. 키 추가/변경은 report+data 회귀.
- **`order_build_*` 스냅샷 스키마**: 생성기 `order_v8_2_rebuild_FULL.py`가 쓰고 리포트/주문장/마스터주문이 읽는다. 컬럼 변경은 생성기(order-agent 경계)와 조회를 함께 맞춘다.
- **마스터주문 반영**: `POST /build/master-add`는 실제 발주·xls 재생성이 아니라 `order_build_store_payload.excel_data` 스냅샷만 갱신한다. 이 경로를 바꾸면 리포트 요약·주문표 모달·`OrderSheetView`·후보 재조회가 모두 영향받는다.
- **`/store-metrics` 재사용 의존**: VMD 행거, 지급율, 진행샘플을 병렬 집계한다. `vmd_service`/`payrate_service` 자체 수정은 각 소관 에이전트로 넘기고, 소매 리오더는 응답 계약과 회귀를 본다.
- **`OrderView.js` 공통 셸**: run/report/history, `reportTabs`, `summaryRows`, 마스터주문 상태가 한 파일에 공존한다. 모드·탭·선택 매장 상태 변경은 report+run 회귀.
- **베스트3종**: `BestProductView` forced-tab 연결부는 소매 리오더 소관, 통합베스트/KA·TB/초특급볼륨 정본 계산과 화면은 best-* 소관.
- **레거시 HTML**: `기존 탭` iframe(`order_analytics_latest.html`)은 폴백/대조용이다. 신규 기능을 이 경로에 추가하지 않는다.

## 3. 회귀 검증

- **import 스모크**(필수): `python -c "from app.routers import order_router"` 무에러, 또는 배포 후 `Application startup complete` + `/docs` 200. `py_compile`만으로는 미충족.
- **실행 화면**: 데이터 상태 패널(`/data-status`), 안전재고 조회/저장, 생성 요청(`/reports/regenerate`), 진행 폴링(`/reports/task`), 멈추기(`/order/cancel`)가 정상.
- **리포트 전체핵심**: `build/latest|detail`, KPI, 상단 재계산바, 매장별 요약, 행거/지급율/샘플 lazy, 남여토글, 미송 포함 토글, 주문표 모달 필터/정렬/미송이 정상.
- **마스터주문**: 매장 전환별 후보 로드, 목표 지급율 조절, 초특급볼륨 주차/가격/매장 필터, 수량 조절, 예산 제한, 선택분 주문장 반영 후 요약·주문표·후보 재조회가 정상.
- **상품 마스터**: 워크북/시트/매장/검색/페이징, 숨김 시트(`기본`) 제외, 이미지 placeholder가 정상.
- **주문장 탭**: `/order-sheet`가 최신/선택 빌드의 상세 주문표를 렌더하고, 서브탭·필터·정렬·CSV 다운로드가 정상.
- **빌드 이력/베스트3종/기존 탭**: 이력 보기, 베스트 forced-tab, 레거시 iframe 토글이 기존 동작을 유지.
- **빌드리스 유지**: CDN Vue + ES모듈, 번들러 도입 없음. 다른 탭 라우팅 무손상, 콘솔 에러 0.

## 4. 작업 전 필독

- `.claude/memory/domain/retail-reorder.md` — 업무 규칙·용어·영역 관계·경계
- `.claude/memory/domain/retail-reorder-feedback.md` — 누적 피드백(F1~)
- `.claude/memory/service/retail-reorder-architecture.md` — Vue/API/DB/데이터 흐름
- `dev-blueprint` 스킬 — 탭 개발 표준(상위 규범)

## 경계 — order-agent / best-* / md-agent 와 혼동 금지

- **retail-reorder-\*-agent** = 소매 리오더 탭 화면, 조회 API, 스냅샷 기반 마스터주문 반영, 주문장 상세 탭.
- **order-agent** = 주문장 생성 산식·검증·배포 운영(testerp NAS, auto_order_db, order_v8_2, 증분 인입, xls 생성/발송).
- **best-\*-agent** = 베스트상품 정본 화면·점수·후보 계산. 소매 리오더는 forced-tab/후보 소비만 담당.
- **md-agent** = 리오더 결과를 입력으로 쓰는 주문추천·포트폴리오 기획.
