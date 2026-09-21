# dev-blueprint — 백엔드 표준 (§2 · §3)

> 본체 `SKILL.md` §1 불변 규칙이 우선한다. 이 파일은 그 규칙의 구조·템플릿·근거다.

## 2. 표준 파일 구조 & 명명

탭 1개 = 아래 5종 파일. `<feature>`는 탭 식별자(예: `payrate`, `margin`, `vmd`).

```
backend/app/services/<feature>_service.py   ← 순수 계산: (session, 파라미터) → dict.  DB 쿼리·집계만. HTML/IO 없음.
backend/app/routers/<feature>_router.py      ← APIRouter(prefix="/api/<feature>"). service 호출 → JSON 반환.
                                                 main.py 에 include_router 1줄 등록.
frontend/js/views/<Feature>View.js           ← Vue 셸(탭/툴바/상태)만. onMounted 에서 fetch, 활성 탭 컴포넌트에 props 전달. iframe 없음.
frontend/js/widgets/<Feature><Part>.js       ← 탭/섹션 1개 = 컴포넌트 1개. 카드/표/차트 등 표현 단위(자기완결: 검색·정렬·스크롤·Excel 등).
frontend/css/<feature>.css                    ← 피처 전용 CSS. `.<feature>` 루트 스코프. index.html 에 `?v=` link 1줄.
frontend/js/api.js                            ← get<Feature>(...) 메서드 1개 추가.
```

- 서비스 함수: 동사 시작 (`fetch_*`, `compute_*`, `build_*`).
- 라우터 클래스/엔드포인트: 명사 prefix + 동작.
- Vue 컴포넌트: `PascalCase`, 위젯은 `<Feature>` 접두.
- **탭별 컴포넌트**: 탭(또는 논리 섹션)마다 별도 `widgets/` 파일로 분리한다. View 는 어느 탭을 그릴지 고르고 데이터를 내려주는 셸에 그친다 — 탭 렌더 로직을 View 안에 쌓지 않는다.
- **데이터 fetch 위치**: 여러 탭이 같은 파이프라인 산출을 쓰면 셸이 **1회 fetch** 후 각 컴포넌트에 슬라이스를 props 로 넘긴다(비싼 재호출 방지). 탭별로 소스가 완전히 다르면 컴포넌트가 각자 fetch 한다.

## 3. 백엔드 표준 템플릿

### 3-1. service (순수 계산 — IO/HTML 없음)
```python
# backend/app/services/<feature>_service.py
"""<feature> 지표 계산 — DB in, dict out. 비즈니스 로직 전담(표현/HTML 없음)."""
from sqlalchemy import text


async def fetch_<feature>_overview(conn, from_date=None, to_date=None) -> dict:
    # SQL은 기존 진실원천(rebuild_<feature>_db.py / generate_*_report.py)에서 '그대로' 이식한다.
    rows = (await conn.execute(text("""
        SELECT ...
        FROM ...
        WHERE (:from_date IS NULL OR txn_date >= :from_date)
          AND (:to_date   IS NULL OR txn_date <= :to_date)
    """), {"from_date": from_date, "to_date": to_date})).fetchall()
    # 집계/지표 계산만. 예외는 상위로 전달하거나 의미있는 메시지로 변환.
    return {"meta": {...}, "grand": {...}, "stores": [...], "weekly_trend": {...}}
```

### 3-2. router (JSON 반환 — 계산 위임)
```python
# backend/app/routers/<feature>_router.py
from fastapi import APIRouter, HTTPException
from app.db.database import engine
from app.services import <feature>_service

router = APIRouter(prefix="/api/<feature>", tags=["<feature>"])


@router.get("/overview")
async def get_<feature>_overview(from_date: str = None, to_date: str = None):
    # 입력 검증: 잘못된 형식·역전(from>to)은 400. 조용히 전체범위로 폴백하지 않는다
    #   (역전→빈 기간→분모 0→'지급율 0%' 사고 변형 방지). 정규화 값(nf,nt)을 service에 전달.
    try:
        nf, nt = <feature>_service.validate_period(from_date, to_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        async with engine.connect() as conn:
            return await <feature>_service.fetch_<feature>_overview(conn, nf, nt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"<feature> 집계 실패: {e}")
```
```python
# backend/app/main.py — import + 등록 (다른 라우터와 동일 위치)
from app.routers import <feature>_router
_app.include_router(<feature>_router.router)
```

### 3-2b. 라우터 등록 = 모듈 전체 import (MUST — 앱 전체 크래시 방지)
> **사고 이력(VMD)**: 미등록이던 `vmd_router`를 `main.py`에 등록하자 그 안에 잠겨 있던 부속 코드
> (`temp-log` 엔드포인트)가 같이 깨어나 `from app.db.models import VmdTempLog` (존재하지 않는 모델)에서
> **import 단계에 앱 전체가 크래시**. `--reload` 자식 프로세스가 죽어 `/docs` 포함 **모든 엔드포인트가 무응답**.
> `py_compile`은 통과했었다 — 컴파일은 import를 **실행하지 않기** 때문.

- **`include_router` 는 그 모듈의 top-level import를 전부 실행시킨다.** 신규 작성이든, 이미 있던 라우터를 처음 등록하는 것이든, 그 파일이 참조하는 **모든 모델·심볼·세컨더리 엔드포인트**가 즉시 로드된다. 잠재 버그(없는 모델 import, 오타, 잘못된 API)가 그 순간 앱 전체를 죽인다.
- **등록 전 점검**: 라우터 파일의 import·참조가 전부 실존하는지 확인한다. 특히 `from app.db.models import X` 의 `X` 가 `models.py`에 **정의돼 있는지**, 본문에서 쓰는 ORM API가 이 앱 규약과 맞는지(아래) 확인. 내가 만든 `/overview` 외에 **파일에 딸려 있던 다른 엔드포인트**도 함께 활성화됨을 잊지 말 것.
- **ORM API 규약**: 이 앱의 세션은 `sqlalchemy.ext.asyncio.AsyncSession` — `await session.execute(stmt)` 후 `result.scalars().all()` 를 쓴다. **`session.exec()` 는 없다**(sqlmodel 동기 Session 전용 → `AttributeError` 500). 기존 정상 라우터(`best_product_router` 등)의 패턴을 그대로 따른다.
- **신규 모델이 필요하면**: `models.py`에 `SQLModel, table=True`로 정의하면 startup `database.py`의 `SQLModel.metadata.create_all`이 테이블을 **추가 생성**(비파괴)한다. 모델 없이 import만 하면 크래시.
- **검증은 `py_compile` 로 끝내지 않는다 — import 스모크가 필수**. §5 Phase 1 마지막에 실행한다.

### 3-3. 데이터 소스 규칙 (필수)
- **정본 식별 (먼저)**: SQL은 기존 검증 쿼리를 그대로 이식한다(새로 짜지 않음). 단 한 피처에 생성기가 **여럿**일 수 있다 — `generate_*_report.py`(파일모드)와 `rebuild_<feature>_db.py`(DB모드)는 **로직이 다를 수 있고**, 파일모드는 폐기·버그(예: 분모 기간 0%)일 수 있다. **운영이 실제 실행하는 DB모드를 정본으로 확정**하고, 과거 회귀(0% 사건 등)의 수정이 어느 파일에 들어갔는지 git/커밋/주석으로 확인한 뒤 그 파일을 이식한다.
- **분모 기간 정합**: 분모(매출 등)를 분자와 **다른 기간**으로 좁혀 0이 되게 만들지 않는다(지급율 0% 사건 근본원인). 분자·분모를 **항상 동일 기간**으로 집계하거나 누적 기준을 유지.
- **수치 동등성**: 정본이 Python에서 **행단위로 절사/반올림/형변환**(예: `int(float(x))`) 후 합산했다면, 순진한 SQL `SUM()`은 numeric 컬럼에서 결과가 달라질 수 있다. `SUM(TRUNC(...))`/`ROUND` 등으로 **동일 결과를 보장**한다. 대상 금액 컬럼 타입(numeric/int)을 먼저 확인.
- **밴딩·임계값도 이식**: 색상/등급 밴딩(역마진·미달 기준 등)은 표현처럼 보여도 **업무 규칙**이다. 정본 임계를 그대로 옮긴다(예: 매장 40~45 초록·<40 미달, 합계 ≤45, 사입처 >100 역마진). 단일 목표값 초과=빨강 식의 **임의 단순화 금지**.
- **엔진 도달성**: 신규 service는 앱 async 엔진(`engine`/`DATABASE_URL`)을 쓴다. 그 엔진이 **대상 테이블에 실제로 닿는지** 같은 테이블을 읽는 기존 라우터로 확인한다. 별도 `psycopg2`/DSN 2차 경로를 새로 만들지 않는다.
- DB가 Single Source. PKL은 신선도 라벨 등 보조에만.

### 3-4. 데이터 로더 (§1 데이터 로더 상세)

**공유 monolith `master_data` 금지.** `db_master_loader.build_master_data()` 처럼 전 매장·전 섹션을 담은 무거운 객체를 웹 워커에 상주시켜 여러 탭이 공유하지 않는다(워커 RSS 선형증가·수백 MB 직렬화 → **2026-07-05 host OOM 사고**의 근본원인). 각 탭은 **자기가 실제로 소비하는 컬럼/섹션만** 만드는 **고유 경량 loader**를 갖는다. 미소비 섹션(예: daily 시계열)은 애초에 만들지 않고, 필요하면 매장 단위 임시 생성 후 즉시 폐기한다. **파리티**: 골든 산식/함수는 그대로 재사용(새 산식 금지). 선례: `backend/scripts/post_process_db_direct.py` `build_post_process_md_direct`(후처리 /grid 전용 DB 직독 경량 빌더) + 야간배치 프리컴퓨트 테이블 직독.

### 3-5. Phase 1 상세 (§5)

1. **Phase 1 — 백엔드**: 정본 식별(§3-3) → service(SQL 이식+계산) → router(입력검증 포함) → main.py 등록 → **import 스모크 테스트**(아래) → API JSON을 기존 `<feature>_latest.html` 수치와 **대조 검증**. *운영 DB가 로컬에 없으면(예: NAS 전용) 이 수치대조는 **배포 후로 분리**하고, 그 전엔 SQL 논리동등성으로 대체한다.*
   - **import 스모크(필수, §3-2b)**: `py_compile` 만으로 끝내지 않는다(컴파일은 import 미실행). 라우터/앱 모듈을 **실제 import**해 누락 모델·잘못된 ORM API 등 import-time 크래시를 잡는다. 런타임 의존성이 깔린 환경에서:
     `python -c "import app.main"` 또는 `python -c "from app.routers import <feature>_router"` → 에러 없이 통과해야 한다.
     로컬에 런타임이 없으면(예: `ModuleNotFoundError: sqlmodel`) **배포 직후 컨테이너 로그에서 `Application startup complete` 와 `/docs` 200 응답을 반드시 확인**(import 크래시 시 `--reload` 자식이 죽어 전 엔드포인트 무응답).
