# wholesale-reorder — 회귀 검증 (§3)

> 본체 `SKILL.md` §3 의 상세다. 공통 게이트는 `dev-blueprint` 스킬 §6 에 있고,
> 여기에는 **이 탭 고유의 확인 항목**만 있다.

## 3. 회귀 검증 (dev-blueprint 스킬 §6 게이트 재사용)

- **import 스모크**(백엔드 변경 시 필수): `python3 .claude/skills/dev-blueprint/scripts/import_smoke.py wholesale_router` → **PASS** 여야 한다.
  SKIP(로컬 의존성 없음)이면 컨테이너에서 재실행하거나 배포 후 `/docs` 200 으로 대체한다.
  compute 검증은 `compute_report_data(False)` 직접 호출(dev DB는 `TESTERP_DB_NAME=testerp_dev` 오버라이드 — prod 미접근).
- **탭 렌더**: 소스탭(ALL/코스/본사)·키워드섹션(리오더/후보/확장/소진/정상)·매장 이동·정리·기주문추적·도매외부·원천점검(coverage/self_check) 전부 정상, **콘솔 에러 0**.
- **인터랙션**: 풀 재계산 폴링·스피너·발주확정·실행지시 엑셀 다운로드·소스필터·키워드 KPI 필터·섹션 스크롤·이미지 로드.
- **빌드리스 유지**(CDN Vue + ES모듈), **다른 탭 무손상**(라우팅 독립).
- 공유 자산 변경 시 §2의 교차 영향 영역을 실제로 다시 확인. `_vendor` 산식 변경 시 self_check PASS·golden 대조.
