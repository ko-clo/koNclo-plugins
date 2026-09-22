# inventory — 회귀 검증 (§3)

> 본체 `SKILL.md` §3 의 상세다. 공통 게이트는 `dev-blueprint` 스킬 §6 에 있고,
> 여기에는 **이 탭 고유의 확인 항목**만 있다.

## 3. 회귀 검증 (dev-blueprint 스킬 §6 게이트 재사용)

- **import 스모크**(백엔드 변경 시 필수): `python3 .claude/skills/dev-blueprint/scripts/import_smoke.py inventory_router` → **PASS** 여야 한다.
  SKIP(로컬 의존성 없음)이면 컨테이너에서 재실행하거나 배포 후 `/docs` 200 으로 대체한다.
- **9탭 렌더**: 종합/반품관리/이고관리/깔교관리/진행중샘플/60%무판매/주간플랜/로직표/반품검수장
  전부 정상 표시, **콘솔 에러 0**.
- **인터랙션**: 날짜선택(SnapshotHistoryBar)·매장 서브탭 전환·검색·이고 유형필터·Excel 내보내기·
  주간플랜 예산 조정·반품검수장 추가/삭제 동작.
- **탭 카운트 배지**: `return_count`·`igo_count`·`kkalgyo_count`·`sample_count`·`pct60_count` 가
  각 탭 실제 행수와 일치(과거 `kkalgyo_count` 불일치 버그).
- **스냅샷 없음 경로**: 테이블 부재/빌드 전에도 500 아닌 빈 페이로드 + '스냅샷 없음' 표시 유지.
- **빌드리스 유지**(CDN Vue + ES모듈), **다른 탭 무손상**(라우팅 독립).
- 공유 자산 변경 시 §2의 교차 영향 서브탭을 실제로 다시 확인.
