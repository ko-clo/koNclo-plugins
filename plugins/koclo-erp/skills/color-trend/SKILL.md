---
name: color-trend
description: 인기컬러 탭 작업 라우팅. "인기컬러", "인기 컬러", "컬러트렌드", "컬러 트렌드", "color-trend", "/color-trend", "전체 칼라", "포인트 칼라", "VMD 팔레트", "인기종합순", "부진칼라", "외부 트렌드", "마스터시트 전송" 등 인기컬러 탭/영역의 수정·조회·기능추가 요청 시 호출. 요청 영역을 식별해 전담 에이전트로 위임하고 전체 탭 회귀를 검증한다.
---

# 인기컬러 탭 작업 — 라우팅 스킬

> 인기컬러는 `ColorTrendView.js`(`/color-trend`)의 **전체 칼라 · 포인트 칼라 · VMD 팔레트 · 인기종합순 · 부진칼라 경고 · 외부 트렌드 · 상세 모달/마스터시트 전송 · source DB 집계 파이프라인**으로 구성된다.
> 이 스킬은 영역 식별 → 전담 에이전트 위임 → 결과 통합 → 전체 회귀 검증 순서로 쓴다.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다.

## 0. 영역 ↔ 에이전트 ↔ 파일 매핑

| # | 영역 | 에이전트 | 프론트 | API | DB/service |
|---|---|---|---|---|---|
| 0 | 전체 칼라·데님 사이드 | `color-trend-all-agent` | `ColorTrendView.js`, `ColorTrendAllColorsTab.js`, `color-trend.css` | `api.getColorTrendOverview`, `GET /api/color-trend/overview` | 응답 `all_colors/denim_colors/color_css` 소비. 계산 변경은 data-agent |
| 1 | 포인트 칼라·효율·선택 컨펌 | `color-trend-point-agent` | `ColorTrendPointColorsTab.js`, `ColorTrendConfirmBar.js`, `ColorTrendView.js` 선택/복사 메서드 | 동일 overview API | 응답 `point_colors/efficiency_colors` 소비. 포인트 산식은 data-agent |
| 2 | VMD 팔레트 | `color-trend-vmd-agent` | `ColorTrendVmdPaletteTab.js`, `ColorTrendView.js` | 동일 overview API | 응답 `vmd_palette` 소비. VMD 탭 자체가 아니라 인기컬러 내부 팔레트 |
| 3 | 인기종합순 | `color-trend-ranking-agent` | `ColorTrendRankingTab.js`, `ColorTrendView.js` | 동일 overview API | 응답 `trend_colors/denim_colors`, `trend_score` 소비 |
| 4 | 부진칼라 경고 | `color-trend-bad-agent` | `ColorTrendBadColorsTab.js`, `ColorTrendView.js` | 동일 overview API | 응답 `bad_colors`, `dead_count/bad_count` 소비 |
| 5 | 외부 트렌드 | `color-trend-external-agent` | `ColorTrendExternalTrendsTab.js`, `ColorTrendView.js` | 동일 overview API | 응답 `external_trends`. 현재는 service 상수 기반 캐시 소스 |
| 6 | 상세 모달·마스터시트 전송 | `color-trend-transfer-agent` | `ColorTrendDetailModal.js`, `api.js`, `ColorTrendView.js` detail state | `/api/master-sheets*`, `api.productImageUrl` | `master_sheet_router.py`, `product_master_sheets`, `product_master_sheet_rows` |
| 7 | 데이터 파이프라인·정규화·API | `color-trend-data-agent` | `api.js` 계약, 모든 위젯 응답 키 영향 | `color_trend_router.py`, `snapshot_router.py` | `color_trend_service.py`, `score_ranking_service.py`, `sales_daily/purchase_daily/inventory_snapshot/products/pm_suppliers`, 레거시 생성기 |

공통 셸: `frontend/js/views/ColorTrendView.js`, `frontend/js/api.js`, `frontend/css/color-trend.css`.
공통 백엔드: `backend/app/routers/color_trend_router.py`, `backend/app/services/color_trend_service.py`, `backend/app/routers/snapshot_router.py`.
앱 라우트와 커맨드는 `/color-trend`, 탭 id는 `order-color`, API prefix는 `/api/color-trend`, snapshot report type은 `color_trend`다.

## 1. 작업 흐름

1. **요청 영역 식별** — 사용자 요청이 어느 영역인지 §0 표로 판별한다. 모호하면 한 번만 질문한다.
2. **단일 영역** → 해당 에이전트 1개에 위임한다.
3. **여러 영역** → 영향 에이전트를 함께 위임한다. 특히 `color_trend_service.py`, `/api/color-trend/overview` 응답 키, `ColorTrendDetailModal.js`, `/api/master-sheets*`는 교차 영향이다.
4. **결과 통합** — 각 에이전트 변경/리스크를 메인이 취합한다.
5. **전체 탭 회귀 검증** — §3.

## 2. 위임 규칙 (공유 자산 주의)

- **overview 응답 계약**: `meta`, `all_colors`, `point_colors`, `efficiency_colors`, `denim_colors`, `trend_colors`, `bad_colors`, `vmd_palette`, `products_by_color`, `color_css`, `external_trends`는 `ColorTrendView.js`와 위젯들이 직접 소비한다.
- **점수 원천**: 인기컬러는 `score_ranking_service`의 source DB 직접 집계 경로를 재사용한다. 별도 HTML 생성기나 MASTER_DATA/emaster 파일을 화면 본문 원천으로 되살리지 않는다.
- **색상 정규화**: `COLOR_GROUPS`, `NOT_COLOR`, `BASIC_GROUPS`, `DENIM_GROUPS`, `COLOR_CSS`는 업무 규칙이다. 단순 UI 라벨처럼 임의 변경하지 않는다.
- **포인트/부진/VMD 산식**: 포인트는 비기본색 `trend_score > 0` 상위 30개, 부진은 비기본색 `dead_count > 3` 상위 15개, VMD 팔레트는 매장별 비기본·비데님 판매순 TOP 10이다. 변경 시 data-agent와 화면 에이전트 회귀가 필요하다.
- **외부 트렌드**: 현재 `/overview`는 `EXTERNAL_TREND_SOURCES`와 `GLOBAL_TREND_PALETTE` 상수 기반 캐시 응답이다. 실시간 웹 수집을 추가하려면 장애/타임아웃/캐시/출처 표기 정책을 먼저 정한다.
- **상세 모달 전송**: `ColorTrendDetailModal.js`는 공용 `/api/master-sheets*`에 `source='color_trend'`로 append/create한다. master-sheet 스키마 변경은 후처리마스터·스코어랭킹·소매 리오더까지 공유 회귀 대상이다.
- **SnapshotHistoryBar**: `report-type="color_trend"`는 `snapshot_router.TYPE_MAP`의 `report_snapshots`/`color_trend_latest.html` 매핑과 연결된다. 날짜 선택은 overview의 `to_date`로만 전달된다.

## 3. 회귀 검증

- **import 스모크**(백엔드 변경 시 필수): `python -c "from app.routers import color_trend_router, snapshot_router, master_sheet_router"` 무에러, 또는 배포 후 `Application startup complete` + `/docs` 200.
- **탭 셸**: `/color-trend` 라우트, `SnapshotHistoryBar`, 로딩 스피너, 에러/다시시도, 6탭 전환, 날짜 선택 후 재조회가 정상.
- **전체 칼라**: 상의 칼라 표, 검색, 기본/포인트 필터, 판매/효율 정렬, 데님 사이드 패널, 상세 모달 오픈.
- **포인트 칼라**: 카드 정렬, HOT/급상승/효율 badge, VMD 컨펌 체크박스, 하단 선택바, 선택 목록 복사.
- **VMD 팔레트**: 매장별 팔레트 TOP 10, 빈 매장 표시, 색상 클릭 상세 오픈.
- **인기종합순**: `trend_score` 바/순위, 데님 사이드, 상세 오픈.
- **부진칼라**: `dead_count`, `stock`, `s2w`, `efficiency`, 사입처/매장 수, 평균점수 표시.
- **외부 트렌드**: 캐시 팔레트와 source 성공/실패 표시, 링크/출처/연도 표기.
- **상세·전송**: 검색/매장/정렬/원색 필터, 다중선택, 이미지 URL, 워크북 목록/시트 로드, 신규 워크북 생성, 기존 워크북 append, `source='color_trend'` 유지.
- **데이터 계약**: `from > to`는 400, 빈 데이터는 `_empty_payload` shape 유지, 기본색/데님/포인트/부진 산식 변경 시 레거시 스크립트와 대조.
- **공유 회귀**: `/api/master-sheets*`, `SnapshotHistoryBar`, `score-ranking` 점수 helper, 다른 order subtabs 라우팅을 건드렸으면 함께 확인.
- **빌드리스 유지**: CDN Vue + ES모듈, 번들러 도입 없음. 다른 탭 라우팅 무손상, 콘솔 에러 0.

## 4. 작업 전 필독

- `.claude/memory/domain/color-trend.md` — 업무 규칙·용어·영역 관계·경계
- `.claude/memory/domain/color-trend-feedback.md` — 누적 피드백(F1~)
- `.claude/memory/service/color-trend-architecture.md` — Vue/API/DB/데이터 흐름
- `dev-blueprint` 스킬 — 탭 개발 표준(상위 규범)

## 경계 — vmd / score-ranking / post-process / retail-reorder 와 혼동 금지

- **color-trend-\*-agent** = `/color-trend` 인기컬러 탭 자체의 컬러 그룹 추천·상세·전송·데이터 경로.
- **vmd-\*-agent** = `/vmd` 행거 대시보드의 행거 수량·시즌·월별·검증 조정. 인기컬러의 `VMD 팔레트`는 색상 후보 표시일 뿐 VMD 행거 산식이 아니다.
- **score-ranking-\*-agent** = 상품/색상 점수 랭킹의 원천 점수와 리스트/전송 UI. 인기컬러는 그 helper를 읽지만 화면 소관은 다르다.
- **post-process-\*-agent** = 후처리마스터 워크북/그리드 자체. 인기컬러 상세 모달은 공용 master-sheet API 소비자다.
- **retail-reorder-\*-agent / order-agent** = 주문장 추천·실제 xls 생성·검수·운영. 인기컬러 컨펌/전송은 실제 주문장 생성이 아니다.
