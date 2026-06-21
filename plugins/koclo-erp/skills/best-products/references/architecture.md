---
name: 베스트상품 대시보드 아키텍처
description: 베스트상품 탭의 Vue 파일·API 엔드포인트·DB 테이블·적재 파이프라인·데이터 흐름 매핑. 베스트상품 탭 작업 시 무엇을 어디서 고칠지 판단하는 구조도. 새 베스트상품 작업 전 항상 참조.
type: reference
---

# 베스트상품 대시보드 — 아키텍처

dev-blueprint 표준 탭(iframe 제거, DB 직접 쿼리). **읽기전용**: 화면은 DB API만 소비, 데이터는 주문장 생성(`order_v8_2`)이 적재. 표시값(사입처/품명/색/사이즈)은 router가 JOIN으로 복원.

## 파일 매핑

### 프론트엔드 (`frontend/js/`)
| 파일 | 역할 |
|---|---|
| `views/BestProductView.js` | 공통 셸 — 3내부탭(통합/KA·TB/볼륨) 라우팅 + `TAB_COLS`(탭별 컬럼) + 이미지/호버프리뷰/모달 + `fmt`(가격/날짜) + 성별·매장 필터. 단일 파일 |
| (별도 위젯 없음) | 3탭이 한 컴포넌트의 `activeTab`/`cols`로 분기 |

이미지 URL: `/reports/images/{사입처}_VL_%25_VL_{품명}.png` (StaticFiles `/reports/images` 마운트, main.py).

### 백엔드 (`backend/app/`)
| 파일 | 역할 |
|---|---|
| `routers/best_v2_router.py` | `APIRouter(prefix="/api/best")` — 4 엔드포인트. 최신 batch 조회 + raw SQL JOIN(products/pm_suppliers/stores)으로 표시값 복원. 쓰기 없음 |
| `db/models.py` | `BestIntegrated`/`BestKaTb`/`BestVolume`(SQLModel, create_all 자동생성 + ORM 미러). FK는 DB DDL 제약 |

> 폐기 대기(구 워크북): `best_product_router.py` + `best_product_sheets` 테이블 + `_build_best_products.py`(HTML 파싱 빌더). 신규 검증 후 제거.

### 스크립트 (`backend/scripts/`)
| 파일 | 역할 |
|---|---|
| `order_v8_2_rebuild_FULL.py` | **적재 정본**. `persist_best_products(batch_date, all_best_js, all_results, volume_top)` 가 3테이블을 batch 단위 DELETE→INSERT. `best_candidates`(통합 점수)·KA/TB 추출·`_volume_top`(볼륨) 계산. `get_or_create_product`로 product_id 해소 |
| `db_master_loader.py` | MASTER_DATA 가격 소스 — `regular_price`/`purchase_price`를 `sales_daily` 최신 non-null에서 조회(`reg_price_map`/`pur_price_map`). 초특급볼륨 가격 + 전체 매출/발주 금액 출처 |
| `sql/create_best_products.sql` | 3테이블 DDL 정본(FK product_id→products, store_id→stores, batch_date UNIQUE) |

## API 4엔드포인트 → 소스

| 메서드 · 경로 | 소스 테이블 + JOIN | 용도 |
|---|---|---|
| `GET /api/best/meta` | Best* 3테이블 max(batch_date)+count | 3탭 최신 batch_date·건수(헤더) |
| `GET /api/best/integrated` | `best_integrated` ⋈ products ⋈ pm_suppliers | 통합베스트(성별 필터, rank순) |
| `GET /api/best/ka-tb` | `best_ka_tb` ⋈ products ⋈ pm_suppliers ⋈ stores | KA·TB 마스터(score순, store/ka_tb 필터) |
| `GET /api/best/volume` | `best_volume` ⋈ products ⋈ pm_suppliers ⋈ stores | 초특급볼륨(sold_qty순, store 필터) |

## DB 테이블

| 테이블 | 역할 | R/W |
|---|---|---|
| `best_integrated` | 통합베스트 — batch_date, product_id FK, gender, rank, avg_score, sold_2w, store_count, replenish_qty. UNIQUE(batch_date,product_id) | W(persist) / R(router) |
| `best_ka_tb` | KA·TB 마스터 — batch_date, store_id FK, product_id FK, ka_tb, score, sold_2w, current_stock. UNIQUE(batch_date,store_id,product_id) | W/R |
| `best_volume` | 초특급볼륨 — batch_date, store_id FK, product_id FK, ka_tb, sold_qty(=total_sales 누적), purchase_price, sale_price, registration_date | W/R |
| `products` | 상품 정본(id, supplier_id, product_code, product_name, color, size). FK 대상 + JOIN 표시값 | R |
| `pm_suppliers` | 공급사(name `M)%`=남성 판정) | R |
| `stores` | 매장(store_id, store_name) | R |
| `sales_daily` | 가격 소스(regular_price/purchase_price, db_master_loader 경유) | R |

## 적재 파이프라인 (데이터 흐름)

```
order_v8_2 (계산):
  best_candidates  ← 점수 6요소 가중합(BEST_SCORE_WEIGHTS) + 매장수임계·momentum + 여30/남20
  KA/TB 추출       ← product_code KA/TB (TB 우선) 전수
  _volume_top      ← KA/TB total_sales 매장별 Top VOLUME_TOP_N
  가격             ← db_master_loader (sales_daily 최신 non-null)
        │
        ▼  persist_best_products(batch_date)  — get_or_create_product로 product_id/store_id 해소, DELETE→INSERT(ON CONFLICT DO NOTHING)
        ▼  best_integrated / best_ka_tb / best_volume  (3테이블)
        ▼  best_v2_router  (최신 batch + JOIN으로 사입처/품명/색/사이즈 복원)
        ▼  BestProductView.js  → 3탭 표시(이미지·품번·가격)
```

## 운영 주의

- **적재 트리거**: 주문장 재빌드(`order_v8_2` `USE_DB=1`, `nas_auto_order.sh` 매일·`/order-manual` 수동)에서만 채워짐. `--reuse-html`(재빌드 생략)이면 persist 미발동.
- **가격 반영**: db_master_loader 변경 후 **MASTER_DATA 캐시 1회 삭제** 필요(`DELETE FROM cache_summary WHERE key IN ('master_data_v1','master_data_dirty')`) — 안 하면 구 캐시.
- **에러 격리**: persist는 try/except/finally + 별도 커넥션 → 실패해도 주문장 생성 무영향(원자적 롤백).
- **가격 0 가능**: 미판매(sales_daily 가격 없음) 상품은 0(레거시 폴백 제거).

상세 업무규칙·용어는 [[베스트상품 대시보드 도메인 규칙]] 참조.
