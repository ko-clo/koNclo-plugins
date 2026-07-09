---
name: best-products
description: 베스트상품 탭 작업 라우팅. "베스트상품", "베스트탭", "통합베스트", "KA·TB 마스터", "KA TB 마스터", "초특급볼륨", "베스트 오버뷰", "베스트 서브탭" 등 베스트상품 탭/서브탭의 수정·조회·기능추가 요청 시 호출. 요청 서브탭을 식별해 전담 에이전트로 위임하고 전체 탭 회귀를 검증한다. (베스트 데이터를 활용한 주문추천/기획은 md-agent 소관 — §경계)
---

# 베스트상품 탭 작업 — 라우팅 스킬

> 베스트상품 탭(`BestProductView.js`)은 **읽기전용 3 서브탭**으로 구성된다. 통합베스트/KA·TB는 주문장 생성(`order_v8_2_rebuild_FULL.py`) 적재본을 읽고, 초특급볼륨은 최신 `best_volume` batch를 anchor로 삼아 선택기간 판매합을 조회 시점에 재계산한다. 이 스킬은 **메인 Claude가 따르는 절차서**다.
> 서브탭 식별 → 전담 에이전트 위임(Agent 도구) → 결과 통합 → 전체 탭 회귀 검증.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다(중복 서술 금지).

## 0. 서브탭 ↔ 에이전트 ↔ 파일 매핑

| # | 서브탭 | 에이전트 | 프론트 | API | 생성/계산 | DB |
|---|---|---|---|---|---|---|
| 0 | 통합베스트 | `best-integrated-agent` | `BestProductView.js`(integrated 탭·TAB_COLS) | `GET /api/best/integrated` | order_v8_2 `best_candidates`(점수 가중치)+`persist_best_products` | `best_integrated` |
| 1 | KA·TB 마스터 | `best-ka-tb-agent` | `BestProductView.js`(ka_tb 탭) | `GET /api/best/ka-tb` | order_v8_2 KA/TB 코드 추출+persist | `best_ka_tb` |
| 2 | 초특급볼륨 | `best-volume-agent` | `BestProductView.js`(volume 탭·판매기간·7천원 필터) | `GET /api/best/volume?weeks=1..8` | `best_volume_service.fetch_best_volume_items` — 최신 `best_volume` batch anchor + `sales_daily` 기간판매 Top17 재계산 | `best_volume`(anchor), `sales_daily`, `products`, `pm_suppliers`, `stores` |

공통 셸: `frontend/js/views/BestProductView.js`(3탭 라우팅·이미지/프리뷰/모달·컬럼 렌더).
공통 백엔드: `backend/app/routers/best_v2_router.py`(읽기 API) · `backend/app/services/best_volume_service.py`(초특급볼륨 기간 재계산) · `backend/scripts/order_v8_2_rebuild_FULL.py`(`persist_best_products` 적재) · `backend/app/db/models.py`(Best* 모델).
메타: `GET /api/best/meta`(3탭 최신 batch_date·건수).

## 1. 작업 흐름

1. **요청 서브탭 식별** — 어느 서브탭(들)인지 §0 표로 판별. 불명확하면 AskUserQuestion.
2. **단일 서브탭** → 해당 에이전트 1개에 위임.
3. **여러 서브탭** → **병렬 위임**(단일 메시지에 다중 Agent 호출).
4. **결과 통합** — 각 에이전트 변경/리스크를 메인이 취합.
5. **전체 탭 회귀 검증** — §3.

## 2. 위임 규칙 (공유 자산 주의 — VMD보다 결합도 높음)

3 서브탭은 **단일 파이프라인**을 공유한다. 아래 **공유 자산**을 건드리는 작업은 영향받는 서브탭 에이전트를 **모두** 위임하거나 메인이 직접 조정한다(`service/best-products-architecture.md`로 영향 범위 확인):

- **`persist_best_products`**(order_v8_2) — 3테이블을 **한 함수**에서 batch_date 단위로 적재. 컬럼/스키마/적재 로직 변경은 3탭 전부 회귀.
- **`best_v2_router.py`** — 4 엔드포인트 한 파일. JOIN(products/pm_suppliers/stores) 변경은 소비 서브탭 전부.
- **`best_volume_service.py`** — 초특급볼륨 탭과 소매 리오더 마스터주문 후보가 공유하는 기간판매 Top 계산. `weeks`/`include_all_top`/가격 조회 변경은 양쪽 회귀.
- **`BestProductView.js`** — 3탭 한 파일. 공유 이미지/프리뷰/모달·`fmt`·필터 변경은 3탭 전부.
- **`sales_daily` 가격 소스**(regular/purchase 최신 non-null) — 초특급볼륨 가격 + 주문장 전체 매출/발주 금액에 동시 영향. 적재본 가격은 `db_master_loader`, 조회 재계산 가격은 `best_volume_service` LATERAL 조회 패턴.
- **점수 상수**(`BEST_SCORE_WEIGHTS`·`BEST_MIN_AVG_SCORE`·`VOLUME_TOP_N` 등) — 통합·볼륨 선정에 영향.
- **batch_date 스냅샷 모델**(Best* 3테이블 공통 키).

단일 서브탭에 갇힌 작업(예: KA·TB탭 표시 컬럼만 변경)은 해당 에이전트 단독.

## 3. 회귀 검증 (dev-blueprint 스킬 §6 게이트 재사용)

- **import 스모크**(필수): `python -c "from app.routers import best_v2_router"` 무에러 — 또는 배포 후 `Application startup complete` + `/docs` 200. (`py_compile`만으론 미충족)
- **적재 검증**: order_v8_2 `USE_DB=1` 실행 → `[베스트 DB저장] batch=… integrated/ka_tb/volume` 건수 + 3테이블 행수 일치. (persist 로직 변경 시)
- **3탭 렌더**: 통합베스트/KA·TB마스터/초특급볼륨 전부 정상 표시, **이미지·품번 노출**, **콘솔 에러 0**.
- **인터랙션**: 성별 필터(통합)·매장 필터(KA·TB/볼륨)·초특급볼륨 판매기간(1~8주)·7,000원 필터·이미지 호버 프리뷰·클릭 모달 동작.
- **초특급볼륨 재계산**: `/api/best/volume?weeks=1..8`이 latest `best_volume.batch_date`를 기준으로 `sales_daily` 기간판매를 재집계하고, `include_all_top=True` 합집합 후보(KA/TB Top17 ∪ 전체 실판매 Top17)를 반환.
- **JOIN 복원**: API 응답에 사입처·품명·색·사이즈 빈 행 0(전 행 product_id 매핑).
- **빌드리스 유지**(CDN Vue + ES모듈), **다른 탭 무손상**(라우팅 독립).
- 공유 자산 변경 시 §2의 교차 영향 서브탭을 실제로 다시 확인.

## 4. 작업 전 필독

- `.claude/memory/domain/best-products.md` — 업무 규칙·용어·서브탭 관계·공유 의존
- `.claude/memory/service/best-products-architecture.md` — Vue/API/DB/적재 파이프라인/데이터 흐름
- `dev-blueprint` 스킬 — 탭 개발 표준(상위 규범)

## 경계 — md-agent 와 혼동 금지

- **이 스킬/best-\*-agent** = 베스트상품 **탭 자체**의 계산·저장(DB)·API·화면 표시 개발/수정.
- **md-agent**(기획) = 베스트 데이터를 *입력 축*으로 쓰는 주문추천·포트폴리오 결정('무엇을 넣을지').
- "탭 수정/기능추가/조회 화면/적재 로직" → 이 스킬. "베스트 활용 주문추천/적중률 기획" → md-agent.
