# retail-reorder — 위임 규칙·경계 (§2 · §경계)

> 본체 `SKILL.md` 에서 분리. 위임 대상을 정하거나 인접 스킬과의 경계를 판단할 때 읽는다.
> 영역 매핑(§0)과 작업 흐름(§1)은 본체에 있다.

## 2. 위임 규칙 (공유 자산 주의)

- **`order_service` 응답 dict 키**: `fetch_order_build_detail`의 `meta/stores/items/gd/master_items/report_section`, `fetch_store_extra_metrics`의 `hanger/payrate/sample/*_ok`, `fetch_master_order_candidates`의 예산·후보 키는 프론트가 직접 소비한다. 키 추가/변경은 report+data 회귀.
- **`order_build_*` 스냅샷 스키마**: 생성기 `order_v8_2_rebuild_FULL.py`가 쓰고 리포트/주문장/마스터주문이 읽는다. 컬럼 변경은 생성기(order-agent 경계)와 조회를 함께 맞춘다.
- **마스터주문 반영**: `POST /build/master-add`는 실제 발주·xls 재생성이 아니라 `order_build_store_payload.excel_data` 스냅샷만 갱신한다. 이 경로를 바꾸면 리포트 요약·주문표 모달·`OrderSheetView`·후보 재조회가 모두 영향받는다.
- **`/store-metrics` 재사용 의존**: VMD 행거, 지급율, 진행샘플을 병렬 집계한다. `vmd_service`/`payrate_service` 자체 수정은 각 소관 에이전트로 넘기고, 소매 리오더는 응답 계약과 회귀를 본다.
- **`OrderView.js` 공통 셸**: run/report/history, `reportTabs`, `summaryRows`, 마스터주문 상태가 한 파일에 공존한다. 모드·탭·선택 매장 상태 변경은 report+run 회귀.
- **베스트3종**: `BestProductView` forced-tab 연결부는 소매 리오더 소관, 통합베스트/KA·TB/초특급볼륨 정본 계산과 화면은 best-* 소관.
- **레거시 HTML**: `기존 탭` iframe(`order_analytics_latest.html`)은 폴백/대조용이다. 신규 기능을 이 경로에 추가하지 않는다.

## 경계 — order-agent / best-* / md-agent 와 혼동 금지

- **retail-reorder-\*-agent** = 소매 리오더 탭 화면, 조회 API, 스냅샷 기반 마스터주문 반영, 주문장 상세 탭.
- **order-agent** = 주문장 생성 산식·검증·배포 운영(testerp NAS, auto_order_db, order_v8_2, 증분 인입, xls 생성/발송).
- **best-\*-agent** = 베스트상품 정본 화면·점수·후보 계산. 소매 리오더는 forced-tab/후보 소비만 담당.
- **md-agent** = 리오더 결과를 입력으로 쓰는 주문추천·포트폴리오 기획.
