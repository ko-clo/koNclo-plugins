# color-trend — 위임 규칙·경계 (§2 · §경계)

> 본체 `SKILL.md` 에서 분리. 위임 대상을 정하거나 인접 스킬과의 경계를 판단할 때 읽는다.
> 영역 매핑(§0)과 작업 흐름(§1)은 본체에 있다.

## 2. 위임 규칙 (공유 자산 주의)

- **overview 응답 계약**: `meta`, `all_colors`, `point_colors`, `efficiency_colors`, `denim_colors`, `trend_colors`, `bad_colors`, `vmd_palette`, `products_by_color`, `color_css`, `external_trends`는 `ColorTrendView.js`와 위젯들이 직접 소비한다.
- **점수 원천**: 인기컬러는 `score_ranking_service`의 source DB 직접 집계 경로를 재사용한다. 별도 HTML 생성기나 MASTER_DATA/emaster 파일을 화면 본문 원천으로 되살리지 않는다.
- **색상 정규화**: `COLOR_GROUPS`, `NOT_COLOR`, `BASIC_GROUPS`, `DENIM_GROUPS`, `COLOR_CSS`는 업무 규칙이다. 단순 UI 라벨처럼 임의 변경하지 않는다.
- **포인트/부진/VMD 산식**: 포인트는 비기본색 `trend_score > 0` 상위 30개, 부진은 비기본색 `dead_count > 3` 상위 15개, VMD 팔레트는 매장별 비기본·비데님 판매순 TOP 10이다. 변경 시 data-agent와 화면 에이전트 회귀가 필요하다.
- **외부 트렌드**: 현재 `/overview`는 `EXTERNAL_TREND_SOURCES`와 `GLOBAL_TREND_PALETTE` 상수 기반 캐시 응답이다. 실시간 웹 수집을 추가하려면 장애/타임아웃/캐시/출처 표기 정책을 먼저 정한다.
- **상세 모달 전송**: `ColorTrendDetailModal.js`는 공용 `/api/master-sheets*`에 `source='color_trend'`로 append/create한다. master-sheet 스키마 변경은 후처리마스터·스코어랭킹·소매 리오더까지 공유 회귀 대상이다.
- **SnapshotHistoryBar**: `report-type="color_trend"`는 `snapshot_router.TYPE_MAP`의 `report_snapshots`/`color_trend_latest.html` 매핑과 연결된다. 날짜 선택은 overview의 `to_date`로만 전달된다.

## 경계 — vmd / score-ranking / post-process / retail-reorder 와 혼동 금지

- **color-trend-\*-agent** = `/color-trend` 인기컬러 탭 자체의 컬러 그룹 추천·상세·전송·데이터 경로.
- **vmd-\*-agent** = `/vmd` 행거 대시보드의 행거 수량·시즌·월별·검증 조정. 인기컬러의 `VMD 팔레트`는 색상 후보 표시일 뿐 VMD 행거 산식이 아니다.
- **score-ranking-\*-agent** = 상품/색상 점수 랭킹의 원천 점수와 리스트/전송 UI. 인기컬러는 그 helper를 읽지만 화면 소관은 다르다.
- **post-process-\*-agent** = 후처리마스터 워크북/그리드 자체. 인기컬러 상세 모달은 공용 master-sheet API 소비자다.
- **retail-reorder-\*-agent / order-agent** = 주문장 추천·실제 xls 생성·검수·운영. 인기컬러 컨펌/전송은 실제 주문장 생성이 아니다.
