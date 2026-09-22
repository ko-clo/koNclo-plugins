# best-products — 회귀 검증 (§3)

> 본체 `SKILL.md` §3 의 상세다. 공통 게이트는 `dev-blueprint` 스킬 §6 에 있고,
> 여기에는 **이 탭 고유의 확인 항목**만 있다.

## 3. 회귀 검증 (dev-blueprint 스킬 §6 게이트 재사용)

- **import 스모크**(백엔드 변경 시 필수): `python3 .claude/skills/dev-blueprint/scripts/import_smoke.py best_v2_router` → **PASS** 여야 한다.
  SKIP(로컬 의존성 없음)이면 컨테이너에서 재실행하거나 배포 후 `/docs` 200 으로 대체한다.
- **적재 검증**: order_v8_2 `USE_DB=1` 실행 → `[베스트 DB저장] batch=… integrated/ka_tb/volume` 건수 + 3테이블 행수 일치. (persist 로직 변경 시)
- **3탭 렌더**: 통합베스트/KA·TB마스터/초특급볼륨 전부 정상 표시, **이미지·품번 노출**, **콘솔 에러 0**.
- **인터랙션**: 성별 필터(통합)·매장 필터(KA·TB/볼륨)·초특급볼륨 판매기간(1~8주)·7,000원 필터·이미지 호버 프리뷰·클릭 모달 동작.
- **초특급볼륨 재계산**: `/api/best/volume?weeks=1..8`이 latest `best_volume.batch_date`를 기준으로 `sales_daily` 기간판매를 재집계하고, `include_all_top=True` 합집합 후보(KA/TB Top17 ∪ 전체 실판매 Top17)를 반환.
- **JOIN 복원**: API 응답에 사입처·품명·색·사이즈 빈 행 0(전 행 product_id 매핑).
- **빌드리스 유지**(CDN Vue + ES모듈), **다른 탭 무손상**(라우팅 독립).
- 공유 자산 변경 시 §2의 교차 영향 서브탭을 실제로 다시 확인.
