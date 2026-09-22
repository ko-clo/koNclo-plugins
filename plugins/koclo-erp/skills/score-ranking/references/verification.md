# score-ranking — 회귀 검증 (§3)

> 본체 `SKILL.md` §3 의 상세다. 공통 게이트는 `dev-blueprint` 스킬 §6 에 있고,
> 여기에는 **이 탭 고유의 확인 항목**만 있다.

## 3. 회귀 검증

- **import 스모크**(백엔드 변경 시 필수): `python3 .claude/skills/dev-blueprint/scripts/import_smoke.py score_ranking_router` → **PASS** 여야 한다.
  SKIP(로컬 의존성 없음)이면 컨테이너에서 재실행하거나 배포 후 `/docs` 200 으로 대체한다.
- **오버뷰 셸**: `/score` 라우트, 헤더, stale warning, `종합 TOP`/`주문장 베스트`/매장 칩, 기간·날짜·정렬·필터, KPI 5종이 정상.
- **리스트/상세**: 상품 펼침, 색상 행, 점수/주간판매/현재고/상태/깔교 표시, 이미지 placeholder, 선택/해제가 정상.
- **마스터시트 전송**: 기존 워크북 새 시트, 기존 시트 병합, 새 워크북 생성, 중복명 확인, source=`score-ranking` row가 정상.
- **데이터 계약**: `from_date > to_date`는 400, `limit`은 1~200, `store`는 매장 id만(미존재/비대상 400), 빈 결과 payload가 프론트에서 깨지지 않음.
- **공유 회귀**: `color_trend_service` 재사용 helper 변경, `/api/master-sheets*`, `/api/order/product-image`, 레거시 리포트 링크를 건드렸으면 해당 소비 화면까지 확인.
- **빌드리스 유지**: CDN Vue + ES모듈, 번들러 도입 없음. 다른 탭 라우팅 무손상, 콘솔 에러 0.
