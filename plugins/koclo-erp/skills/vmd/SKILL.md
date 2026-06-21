---
name: vmd
description: VMD 행거 대시보드 탭 작업 라우팅. "VMD", "행거탭", "행거 대시보드", "행거 조정", "기온 시즌", "월별 수량", "검증 조정", "VMD 오버뷰", "VMD 서브탭" 등 VMD 탭/서브탭의 수정·조회·기능추가 요청 시 호출. 요청 서브탭을 식별해 전담 에이전트로 위임하고 전체 탭 회귀를 검증한다.
---

# VMD 탭 작업 — 라우팅 스킬

> VMD 행거 대시보드(`VmdView.js`)는 5개 서브탭으로 구성된다. 이 스킬은 **메인 Claude가 따르는 절차서**다.
> 서브탭을 식별 → 전담 범위 위임 또는 직접 수행 → 결과 통합 → 전체 탭 회귀 검증.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다(중복 서술 금지).

작업 전에 `references/domain.md`, `references/architecture.md`, `references/feedback.md`를 읽는다.
Claude Code에서 named agent가 사용 가능하면 §0의 에이전트에 위임한다. Codex 등 named agent가
없는 런타임에서는 동일한 담당 범위를 메인 에이전트가 수행하되 파일 소유 경계를 그대로 지킨다.

## 0. 서브탭 ↔ 에이전트 ↔ 파일 매핑

| # | 서브탭 | 에이전트 | 프론트 | API | DB |
|---|---|---|---|---|---|
| 0 | 오버뷰 | `vmd-overview-agent` | `VmdStoreTable.js`, `VmdDatePicker.js` | `GET /vmd/overview`, `/config`(stock), `PATCH /vmd/store-const` | `inventory_snapshot`, `products`, `pm_suppliers`, `stores` |
| 1 | 기온 & 시즌 | `vmd-season-agent` | `VmdWeatherSeason.js` | `GET /vmd/config`(기온·시즌상수), `POST/GET /vmd/temp-log(s)` | `vmd_temp_log` |
| 2 | 월별 수량 | `vmd-monthly-volume-agent` | `VmdStoreQtyTable.js` | `GET /vmd/monthly`, `/config`(monthly) | `inventory_snapshot` |
| 3 | 행거 조정 | `vmd-hanger-agent` | `VmdHangerAdjust.js`, `vmdCompute.js`(wb/sq/cpH/lowerMultApplies) | `GET /vmd/config`(행거상수), `PATCH /vmd/hanger` | `hangers`, `hanger_sizes`, `hanger_capacities`, `hanger_seasons`, `stores` |
| 4 | 검증 & 조정 | `vmd-verification-agent` | `VmdVerifyAdjust.js`, `vmdCompute.js`(mq/iqm) | `GET /vmd/config`(tf/lower_fixed/color_mix/seasonal) | 읽기전용 |

공통 셸: `frontend/js/views/VmdView.js`(탭 라우팅·로딩·프리로드) · `frontend/js/api.js`(VMD 메서드).
공통 백엔드: `backend/app/routers/vmd_router.py` · `backend/app/services/vmd_service.py`.

## 1. 작업 흐름

1. **요청 서브탭 식별** — 사용자 요청이 어느 서브탭(들)인지 §0 표로 판별. 불명확하면 사용자에게 한 번 확인한다.
2. **단일 서브탭** → named agent 지원 시 해당 에이전트에 위임하고, 아니면 그 범위를 직접 수행한다.
3. **여러 서브탭** → 충돌 없는 범위만 병렬화하고 공유 파일은 메인이 단독 조정한다.
4. **결과 통합** — 각 에이전트 변경/리스크를 메인이 취합.
5. **전체 탭 회귀 검증** — §3.

## 2. 위임 규칙 (공유 자산 주의)

서브탭은 독립이 아니다. 아래 **공유 자산**을 건드리는 작업은 영향받는 서브탭을 **모두** 검토하거나 메인이 직접 조정한다(`references/architecture.md`로 영향 범위 확인):

- **`/vmd/config` 응답 키** — 5탭 전부가 단일 소스로 읽음. 키 추가/변경/삭제는 소비 서브탭 전부 회귀.
- **`vmdCompute.js` 계산식** — `wb`/`sq`는 오버뷰·행거 공유, `mq`/`iqm`은 검증·오버뷰 헤더(`mq`) 공유, `lowerMultApplies`는 행거·검증 공유.
- **DB 공유테이블 `inventory_snapshot`** — 오버뷰·월별수량 공유(현재고 SQL/필터 변경 시 둘 다).
- **`vmd_service.py` 상수**(`VMD_STORE_MAP`/`_HANGER_*_SEASONAL` 등) — 다수 서브탭 동시 의존.

단일 서브탭에 갇힌 작업(예: 검증탭 표시 색만 변경)은 해당 에이전트 단독.

## 3. 회귀 검증 (dev-blueprint 스킬 §6 게이트 재사용)

- **import 스모크**(필수): `python -c "from app.routers import vmd_router"` 무에러 — 또는 배포 후 `Application startup complete` + `/docs` 200. (`py_compile`만으론 미충족)
- **5탭 렌더**: 오버뷰/기온&시즌/월별수량/행거조정/검증&조정 전부 정상 표시, **콘솔 에러 0**.
- **인터랙션**: 날짜선택·남여분리·필터·계수저장·행거저장·월별 지연로딩 스피너 동작.
- **빌드리스 유지**(CDN Vue + ES모듈), **다른 탭 무손상**(라우팅 독립).
- 공유 자산 변경 시 §2의 교차 영향 서브탭을 실제로 다시 확인.

## 4. 작업 전 필독

- `references/domain.md` — 업무 규칙·용어·서브탭 관계
- `references/architecture.md` — Vue/API/DB/데이터 흐름
- `references/feedback.md` — 누적 피드백과 반복 방지 규칙
- `dev-blueprint` 스킬 — 탭 개발 표준(상위 규범)

## 경계 — md-agent 와 혼동 금지

- **이 스킬/vmd-\*-agent** = VMD **탭 자체**의 화면·API·DB 개발/수정.
- **md-agent**(기획) = VMD를 *입력 축*으로 쓰는 주문추천·포트폴리오 결정.
- "탭 수정/기능추가/조회 화면" → 이 스킬. "무엇을 넣을지/주문추천" → md-agent.
