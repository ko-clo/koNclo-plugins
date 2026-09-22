# post-process — 회귀 검증 (§3)

> 본체 `SKILL.md` §3 의 상세다. 공통 게이트는 `dev-blueprint` 스킬 §6 에 있고,
> 여기에는 **이 탭 고유의 확인 항목**만 있다.

## 3. 회귀 검증

- **import 스모크**(백엔드 변경 시 필수): `python3 .claude/skills/dev-blueprint/scripts/import_smoke.py post_process_router master_sheet_router` → **PASS** 여야 한다.
  SKIP(로컬 의존성 없음)이면 컨테이너에서 재실행하거나 배포 후 `/docs` 200 으로 대체한다.
- **탭 셸**: `/post-process` 라우트, 로딩/에러/토스트, 5탭 전환, 날짜 조회, 새로고침/재생성이 정상.
- **그리드**: 여자/남자 성별 필터, 검색/품번/등급/정렬/페이지네이션, 행 펼침, 이미지, 메모, 하이라이트 드래그, 행/색상 삭제, Excel/JSON 내보내기·불러오기.
- **시트/워크북**: 시트 추가/삭제/이름변경/전환, 선택 이동/복사, 서버저장/불러오기/삭제, `기본` 시트 미저장, 추가 시트 보존.
- **샘플/상품추가**: 상품 검색·색상 선택, 샘플집계 지연 로드, 선택 상품의 현재 시트 추가, 신규/매칭 row shape 유지.
- **증가/차감**: `+추가`, 티어 자동산정/일괄적용, 하위컬러 자동선택, Excel export, 서버 워크북 append source=`boost_order`/`cut_order`.
- **데이터 계약**: `from > to`는 프론트에서 차단, `/grid` payload가 `toRows()` 필드(`supplier/product/stores/variants/avg_pp/sell_through/sales_val/stock_val`)를 유지.
- **공유 회귀**: `/api/master-sheets*`, `product_master_sheet_rows`, `score-ranking` 마스터시트 전송, 소매 리오더 상품마스터 소비 경로를 건드렸으면 함께 확인.
- **빌드리스 유지**: CDN Vue + ES모듈, 번들러 도입 없음. 다른 탭 라우팅 무손상, 콘솔 에러 0.
