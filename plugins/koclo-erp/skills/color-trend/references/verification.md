# color-trend — 회귀 검증 (§3)

> 본체 `SKILL.md` §3 의 상세다. 공통 게이트는 `dev-blueprint` 스킬 §6 에 있고,
> 여기에는 **이 탭 고유의 확인 항목**만 있다.

## 3. 회귀 검증

- **import 스모크**(백엔드 변경 시 필수): `python3 .claude/skills/dev-blueprint/scripts/import_smoke.py color_trend_router snapshot_router master_sheet_router` → **PASS** 여야 한다.
  SKIP(로컬 의존성 없음)이면 컨테이너에서 재실행하거나 배포 후 `/docs` 200 으로 대체한다.
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
