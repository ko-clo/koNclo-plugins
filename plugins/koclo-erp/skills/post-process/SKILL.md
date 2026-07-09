---
name: post-process
description: 후처리마스터 탭 작업 라우팅. "후처리마스터", "후처리 상품마스터", "post-process", "/post-process", "상품등급", "상품마스터 워크북", "마스터시트", "샘플집계", "증가주문", "차감주문", "post_process_products" 등 후처리마스터 탭/영역의 수정·조회·기능추가 요청 시 호출. 요청 영역을 식별해 전담 에이전트로 위임하고 전체 탭 회귀를 검증한다.
---

# 후처리마스터 탭 작업 — 라우팅 스킬

> 후처리마스터는 `ProductMasterView.js`(`/post-process`)의 **상품등급 그리드 · 서버 워크북/시트 편집 · 증가/차감 주문 · 후처리 데이터/캐시 파이프라인**으로 구성된다.
> 이 스킬은 영역 식별 → 전담 에이전트 위임 → 결과 통합 → 전체 회귀 검증 순서로 쓴다.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다.

## 0. 영역 ↔ 에이전트 ↔ 파일 매핑

| # | 영역 | 에이전트 | 프론트 | API | DB/service |
|---|---|---|---|---|---|
| 0 | 상품등급 그리드·매입차감 | `post-process-grid-agent` | `ProductMasterView.js`, `PostProcessMainGrid.js`, `PostProcessMaleGrade.js`, `PostProcessPurchaseCut.js`, `postProcessShared.js`, `post-process.css` | `GET /api/post-process/grid`, `api.getPostProcessGrid` | 응답 `meta/products` 소비. 계산·캐시 변경은 data-agent |
| 1 | 워크북·시트·모달 편집 | `post-process-workbook-agent` | `postProcessStore.js`, `PostProcessSheetBar.js`, `PostProcessSelectionBar.js`, `PostProcessAddModal.js`, `PostProcessAggModal.js`, `PostProcessServerModal.js` | `/api/master-sheets*`, `GET /api/post-process/aggs` | `master_sheet_router.py`, `product_master_sheets`, `product_master_sheet_rows` |
| 2 | 증가주문·차감주문 | `post-process-order-agent` | `PostProcessBoostGrid.js`, `PostProcessCutGrid.js`, `postProcessStore.js`의 `boostData/cutData/tierConfig` | `POST /api/master-sheets/{id}/sheets` | append source=`boost_order`/`cut_order`, 로컬스토리지 `pm_boost_data`/`pm_cut_data`/`pm_tier_config` |
| 3 | 데이터 파이프라인·프리컴퓨트·캐시 | `post-process-data-agent` | `api.js` 계약 영향, 그리드/모달 응답 키 영향 | `post_process_router.py` `GET /grid`, `GET /aggs`, `POST /cache/clear` | `post_process_service.py`, `post_process_products`, `rebuild_post_process_products_db.py`, `post_process_db_direct.py`, `post_process_data.py` |

공통 셸: `frontend/js/views/ProductMasterView.js`, `frontend/js/stores/postProcessStore.js`, `frontend/js/api.js`.
공통 백엔드: `backend/app/routers/post_process_router.py`, `backend/app/services/post_process_service.py`, `backend/app/routers/master_sheet_router.py`.
앱 라우트와 커맨드는 `/post-process`, 탭 id는 `analytics-post`, API prefix는 `/api/post-process`다.

## 1. 작업 흐름

1. **요청 영역 식별** — 사용자 요청이 어느 영역인지 §0 표로 판별한다. 모호하면 한 번만 질문한다.
2. **단일 영역** → 해당 에이전트 1개에 위임한다.
3. **여러 영역** → 영향 에이전트를 함께 위임한다. 특히 `postProcessStore.js`, `/api/master-sheets*`, `post_process_service` 응답 키는 교차 영향이다.
4. **결과 통합** — 각 에이전트 변경/리스크를 메인이 취합한다.
5. **전체 탭 회귀 검증** — §3.

## 2. 위임 규칙 (공유 자산 주의)

- **`/api/post-process/grid` 응답 계약**: `meta.pkl_date`, `meta.gen_time`, `products[]`는 `toRows()`와 `postProcessStore.init()`가 직접 소비한다. `gen_time`은 하이라이트/버전 캐시 키라 요청마다 바뀌면 안 된다.
- **기본 시트 원칙**: `기본` 시트는 `post_process_products`에서 재생성되는 읽기전용 원본이며 서버 워크북에 저장하지 않는다. 서버에는 추가 시트만 저장한다.
- **스토어 싱글턴**: `postProcessStore.js`는 그리드, 시트, 샘플, 증가/차감이 공유한다. 상태 키·저장 함수 변경은 grid/workbook/order 회귀가 필요하다.
- **마스터시트 공용 API**: `/api/master-sheets*`는 후처리마스터뿐 아니라 스코어랭킹, 소매 리오더 등도 소비한다. 라우터/스키마 변경은 공용 회귀 대상이다.
- **샘플집계 지연 로드**: `/grid`는 `agg_list: []`를 반환하고, `PostProcessAggModal`만 `/aggs`를 호출한다. `/aggs`는 무거운 `build_master_data` 경로라 운영 게이트를 확인한다.
- **프리컴퓨트/캐시**: `post_process_products`는 야간 배치 스냅샷이다. `POST /cache/clear`는 in-process cache뿐 아니라 스냅샷 테이블을 비우는 운영성 동작이므로 신중히 다룬다.
- **DB direct 경량 경로**: 비운영 스택은 `use_db_direct()` 경로로 `/grid`를 볼 수 있다. 운영 골든 경로와 산출 shape가 같아야 한다.
- **레거시 정본**: `rebuild_post_process_db.py`는 이식 기준/대조 경로다. 신규 화면은 HTML을 굽지 않고 Vue + JSON 경로를 쓴다.

## 3. 회귀 검증

- **import 스모크**(백엔드 변경 시 필수): `python -c "from app.routers import post_process_router, master_sheet_router"` 무에러, 또는 배포 후 `Application startup complete` + `/docs` 200.
- **탭 셸**: `/post-process` 라우트, 로딩/에러/토스트, 5탭 전환, 날짜 조회, 새로고침/재생성이 정상.
- **그리드**: 여자/남자 성별 필터, 검색/품번/등급/정렬/페이지네이션, 행 펼침, 이미지, 메모, 하이라이트 드래그, 행/색상 삭제, Excel/JSON 내보내기·불러오기.
- **시트/워크북**: 시트 추가/삭제/이름변경/전환, 선택 이동/복사, 서버저장/불러오기/삭제, `기본` 시트 미저장, 추가 시트 보존.
- **샘플/상품추가**: 상품 검색·색상 선택, 샘플집계 지연 로드, 선택 상품의 현재 시트 추가, 신규/매칭 row shape 유지.
- **증가/차감**: `+추가`, 티어 자동산정/일괄적용, 하위컬러 자동선택, Excel export, 서버 워크북 append source=`boost_order`/`cut_order`.
- **데이터 계약**: `from > to`는 프론트에서 차단, `/grid` payload가 `toRows()` 필드(`supplier/product/stores/variants/avg_pp/sell_through/sales_val/stock_val`)를 유지.
- **공유 회귀**: `/api/master-sheets*`, `product_master_sheet_rows`, `score-ranking` 마스터시트 전송, 소매 리오더 상품마스터 소비 경로를 건드렸으면 함께 확인.
- **빌드리스 유지**: CDN Vue + ES모듈, 번들러 도입 없음. 다른 탭 라우팅 무손상, 콘솔 에러 0.

## 4. 작업 전 필독

- `.claude/memory/domain/post-process.md` — 업무 규칙·용어·영역 관계·경계
- `.claude/memory/domain/post-process-feedback.md` — 누적 피드백(F1~)
- `.claude/memory/service/post-process-architecture.md` — Vue/API/DB/데이터 흐름
- `dev-blueprint` 스킬 — 탭 개발 표준(상위 규범)

## 경계 — score-ranking / retail-reorder / order-agent / best-* 와 혼동 금지

- **post-process-\*-agent** = `/post-process` 탭 자체의 그리드, 워크북, 샘플, 증가/차감, 데이터/캐시 경로.
- **score-ranking-\*-agent** = 스코어랭킹 탭과 후처리 워크북으로 보내는 선택 UI. `/api/master-sheets*` 소비는 공유지만 소관은 다르다.
- **retail-reorder-\*-agent** = 소매 리오더 화면에서 상품마스터/주문장 결과를 소비하는 경로.
- **best-\*-agent** = 베스트상품 탭 정본 계산·화면.
- **order-agent** = 실제 주문장 생성 산식·xls 생성·검수·배포 운영. 후처리 증가/차감 시트 append가 곧 실제 발주는 아니다.
