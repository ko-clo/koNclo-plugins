# vmd — 영역 ↔ 에이전트 ↔ 파일 매핑 (§0)

> 본체 `SKILL.md` 에서 분리. 어느 에이전트에 맡길지 고를 때에 읽는다.

## 0. 서브탭 ↔ 에이전트 ↔ 파일 매핑

| # | 서브탭 | 에이전트 | 프론트 | API | DB |
|---|---|---|---|---|---|
| 0 | 오버뷰 | `vmd-overview-agent` | `VmdStoreTable.js`, `VmdDatePicker.js` | `GET /vmd/overview`, `/config`(stock), `PATCH /vmd/store-const` | `inventory_snapshot`, `products`, `pm_suppliers`, `stores` |
| 1 | 기온 & 시즌 | `vmd-season-agent` | `VmdWeatherSeason.js` | `GET /vmd/config`(기온·시즌상수), `POST/GET /vmd/temp-log(s)` | `vmd_temp_log` |
| 2 | 월별 수량 | `vmd-monthly-volume-agent` | `VmdStoreQtyTable.js`, `vmdCompute.js`(tempInterpQty) | `GET /vmd/config`(seasonal·anchors·temp) | 없음(프론트 기온보간) |
| 3 | 행거 조정 | `vmd-hanger-agent` | `VmdHangerAdjust.js`, `vmdCompute.js`(wb/sq/cpH/lowerMultApplies) | `GET /vmd/config`(행거상수), `PATCH /vmd/hanger` | `hangers`, `hanger_sizes`, `hanger_capacities`, `hanger_seasons`, `stores` |
| 4 | 검증 & 조정 | `vmd-verification-agent` | `VmdVerifyAdjust.js`, `vmdCompute.js`(mq/iqm) | `GET /vmd/config`(tf/lower_fixed/color_mix/seasonal) | 읽기전용 |

공통 셸: `frontend/js/views/VmdView.js`(탭 라우팅·로딩·프리로드) · `frontend/js/api.js`(VMD 메서드).
공통 백엔드: `backend/app/routers/vmd_router.py` · `backend/app/services/vmd_service.py`.
