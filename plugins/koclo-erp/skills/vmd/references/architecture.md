---
name: VMD 행거 대시보드 아키텍처
description: VMD 탭의 Vue 파일·API 엔드포인트·DB 테이블·config 응답 키·데이터 흐름 매핑. VMD 탭 작업 시 무엇을 어디서 고칠지 판단하는 구조도. 새 VMD 작업 전 항상 참조.
type: reference
---

# VMD 행거 대시보드 — 아키텍처

dev-blueprint 표준 탭(iframe 제거, DB 직접 쿼리). 계산은 `vmd_service` 위임, 표현은 Vue, 실시간 재계산은 클라이언트(`vmdCompute.js`).

## 파일 매핑

### 프론트엔드 (`frontend/js/`)
| 파일 | 역할 |
|---|---|
| `views/VmdView.js` | 공통 셸 — 5탭 라우팅·히어로 헤더·로딩·월별 백그라운드 프리로드(`loadMonthly`) |
| `widgets/VmdStoreTable.js` | 오버뷰 — 현재고 vs 목표, 남/여 분리, 계수 편집, 날짜선택. 잡화 전용 테이블도 이 컴포넌트 재사용 |
| `widgets/VmdDatePicker.js` | 데이터 있는 snapshot_date만 활성인 커스텀 캘린더 |
| `widgets/VmdWeatherSeason.js` | 기온 & 시즌 — CSS 바차트(Chart.js 미사용) |
| `widgets/VmdStoreQtyTable.js` | 월별 수량 — 12개월 매장별 현재고 |
| `widgets/VmdHangerAdjust.js` | 행거 조정 — 행거 구성 편집 + 시즌별 필요수량 |
| `widgets/VmdVerifyAdjust.js` | 검증 & 조정 — 고정현황·시즌효율·괴리 |
| `widgets/vmdCompute.js` | 정본 계산식 — `wb`/`sq`/`th`/`cpH`/`mq`/`iqm`/`lowerMultApplies`/`stChip`/`cityTemp`. `generate_vmd_report.py` 임베드 JS에서 이식 |
| `api.js` | `getVmdOverview`/`getVmdConfig`/`getVmdMonthly`/`saveVmdStoreConst`/`saveVmdHanger` |

### 백엔드 (`backend/app/`)
| 파일 | 역할 |
|---|---|
| `routers/vmd_router.py` | `APIRouter(prefix="/api/vmd")` — 7 엔드포인트. service 위임, HTML 생성 없음 |
| `services/vmd_service.py` | 현재고 집계 + 행거/시즌 상수 + DB 행거 정본 로드. DB in, dict out |
| `db/models.py` | `VmdTempLog`(기온 로그 모델) |

### 스크립트 (`backend/scripts/`)
| 파일 | 역할 |
|---|---|
| `rebuild_vmd_db.py` | 행거 정본 4테이블(`hangers`/`hanger_sizes`/`hanger_capacities`/`hanger_seasons`) 빌드/적재 |
| `generate_vmd_report.py` | 구(舊) 정본(iframe HTML 생성기). 임베드 JS가 `vmdCompute.js` 이식 출처 — 오라클/폴백으로 보존(삭제 금지) |

## API 7엔드포인트 → service 함수

| 메서드 · 경로 | service 함수 | 용도 |
|---|---|---|
| `GET /api/vmd/overview` | `fetch_vmd_overview_via_engine` | 매장별 현재고/목표/상태 + 합계(서버 집계) |
| `GET /api/vmd/config` | `fetch_vmd_config` | 5탭 공용 상수 + 현재고 + 도시기온 + 날짜목록 (`monthly=false` 기본=경량) |
| `GET /api/vmd/monthly` | `fetch_vmd_monthly` | 월별 현재고만(지연 로딩 전용 경량) |
| `PATCH /api/vmd/store-const` | `save_store_consts` | 매장 재고 계수 일괄 저장(`stores.inventory_const`, 음수 0 클램프) |
| `PATCH /api/vmd/hanger` | `save_hanger` | 한 VMD 매장 행거 구성 UPSERT(`hangers`) |
| `POST /api/vmd/temp-log` | (라우터 직접, `VmdTempLog`) | 기온 변동 로그 저장 |
| `GET /api/vmd/temp-logs` | (라우터 직접, `VmdTempLog`) | 최근 기온 로그 조회 |

## DB 9테이블

| 테이블 | 역할 | R/W |
|---|---|---|
| `inventory_snapshot` | 현재고(snapshot_date text, current_stock, purchase_price, product_id, store_id) | R |
| `products` | 상품(product_name·style·supplier_id). 부가세/잡화 필터·성별 조인 | R |
| `pm_suppliers` | 공급사(name `M)%`=남성 판정) | R |
| `stores` | 매장 — `inventory_const`(계수), `region`(행거 city), `folder_name` | R/W(const) |
| `hangers` | 행거 구성 정본 — (store_id,gender,size_mm,rack_type) UNIQUE, rack_count | R/W(UPSERT) |
| `hanger_sizes` | 사이즈 — size_mm, `lower_mult_applies`, sort_order | R |
| `hanger_capacities` | 1대당 용량 — gender, size_mm, rack_type, capacity_per_rack | R |
| `hanger_seasons` | 시즌 — name_short, mult_f, mult_m, season_idx | R |
| `vmd_temp_log` | 도시 기온 로그(`VmdTempLog`) — DISTINCT ON(city) 최신값 | R/W |

> 행거 4테이블(`hangers`/`hanger_sizes`/`hanger_capacities`/`hanger_seasons`)이 **미존재·공백이면 `_load_hanger_config`가 None → 코드 상수 폴백**(`_S`/`_PH`/`_SZ`/`_FM`/`_MM`/`_SN`).

## `/vmd/config` 응답 키 (top-level 32개) — 출처

- **DB 우선(없으면 상수 폴백)**: `stores`·`per_hanger`·`sizes`·`size_lower_mult`·`mult_f`·`mult_m`·`season_names` (← `_load_hanger_config`)
- **상수 정본**: `current_month`·`season_idx`·`season_name`·`monthly_temp`·`month_to_season`·`month_season_name`·`month_mult_f`·`month_mult_m`·`anchors`·`season_colors`·`color_mix`·`tf`·`lower_fixed`·`hanger_f_seasonal`·`hanger_m_seasonal`·`store_vmd_map`
- **DB 조회**: `city_temps`(vmd_temp_log)·`vmd_stock`(현재고)·`vmd_stock_misc`(잡화)·`vmd_stock_monthly`+`vmd_stock_monthly_year`(월별, `monthly=true`만)·`store_const`(stores)·`available_dates`·`selected_date`
- **에코**: `filters`(적용된 exclude_misc/price_min)

## 데이터 흐름

```
inventory_snapshot ⋈ products ⋈ pm_suppliers   (현재고)
hangers/hanger_* + stores.region               (행거 정본)
vmd_temp_log                                    (도시 기온)
        │
        ▼  vmd_service (집계·버킷·상수 조립)
        ▼  GET /api/vmd/config  (+ /overview, /monthly)
        ▼  VmdView.js  → 위젯 5종
        ▼  vmdCompute.js (클라이언트 실시간 계산 — 행거 임시편집 재계산)
```

## 월별 분리 로딩 (성능)

월별 집계(`_compute_monthly_stock_by_vmd`)는 **최신 연도 12개 스냅샷을 조인**해 가장 무겁다.
→ `fetch_vmd_config(include_monthly=False)`가 기본이라 오버뷰 첫 로드에서 제외하고, `GET /api/vmd/monthly`로 **지연 로딩**한다.
`VmdView.js`가 오버뷰 표시 직후 백그라운드 프리로드(`loadMonthly`) + '월별 수량' 탭 진입 시 스피너 폴백(`monthlyLoaded`/`monthlyLoading`).

## 현재고 SQL 정합 주의

- `snapshot_date`는 **text(varchar)** — date 캐스팅 없이 문자열 등치 비교(`SUBSTRING`으로 연/월 추출).
- `current_stock <> 0` 으로 0재고 제외(합계 불변·속도↑).
- `purchase_price`는 비숫자/NULL 방어 — 정규식 검증 후 numeric 캐스팅, 변환 불가는 0.

상세 업무규칙·용어는 [[VMD 행거 대시보드 도메인 규칙]] 참조.
