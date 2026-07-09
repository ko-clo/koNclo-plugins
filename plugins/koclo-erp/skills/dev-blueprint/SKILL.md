---
name: dev-blueprint
description: KOCLO 프론트백 분리 개발 표준. "dev-blueprint", "blueprint", "탭 분리", "프론트백 분리", "새 탭 활성화", "iframe 제거", "Vue화", "탭 표준", 또는 특정 탭(지급율/마진/VMD 등) 분리 요청 시 호출. 이 문서의 표준대로 신규 코드를 작성한다.
---

# dev-blueprint — KOCLO 탭 개발 표준

> **이 스킬은 "기존 구조를 뜯어고치는 것"이 아니라, "모든 탭을 이 표준대로 작성한다"는 개발 규범이다.**
> 새 탭을 활성화하거나 iframe 탭을 분리할 때, 아래 구조·명명·템플릿을 **그대로** 따른다. 표준에서 벗어나려면 명시적 사유와 승인이 필요하다.

## 0. 적용 시점
- 새 탭을 처음 활성화할 때
- 기존 `iframe`(baked-HTML) 탭을 분리할 때
- 데이터 화면(리포트/대시보드)을 신규로 만들 때

> **시작 전 확인** — 분리 대상 View를 **정확히 식별**한다. 이름이 비슷한 인접 기능과 혼동하지 않는다
> (예: `PayrateView`=지급**관리**/자동지급 vs `PayrateOverviewView`=지급**율** 오버뷰).
> 운영이 실제 서빙하는 컨테이너/코드베이스도 확인한다(여러 스택이 공존할 수 있음).

## 1. 불변 규칙 (MUST — 협상 불가)

| 항목 | 표준 |
|---|---|
| **분리 범위** | 본문 전체 Vue화. **iframe 금지.** `*_latest.html`을 화면 본문으로 임베드하지 않는다. |
| **데이터 소스** | **DB 직접 쿼리 신규 엔드포인트** (앱 async 엔진 `engine.connect()` + `text()`). HTML 생성기와 분리. 새 `psycopg2`/별도 DSN 경로를 만들지 말고 앱 엔진으로 일원화. |
| **차트** | **CDN Chart.js를 Vue 컴포넌트 `onMounted`에서 init.** 서버 HTML에 차트를 굽지 않는다. |
| **빌드리스** | CDN Vue3 + ES모듈만. 번들러·node_modules·빌드 단계 도입 금지. |
| **책임 분리** | 계산(service) / 입출력(router) / 표현(Vue) 3계층 분리. (CLAUDE.md 1·4항) |
| **컴포넌트 분리** | 탭/섹션 1개 = 컴포넌트 1개. `View`는 **셸**(툴바·탭바·fetch·공유상태)만 담고, 표현은 `widgets/<Feature><Part>.js`로 분리한다. View가 비대해지면(≈300줄+) 반드시 쪼갠다. 한 파일이 여러 탭 렌더를 다 품지 않는다. (CLAUDE.md 4·6항) |
| **CSS 분리** | 인라인 CSS 지양. 피처 전용 스타일은 `frontend/css/<feature>.css`에 **`.<feature>` 루트로 스코프**해 분리하고(전역 `theme.css` 무충돌), `index.html`에 `?v=` 캐시버스팅 `<link>`로 1회 로드한다. 컴포넌트 템플릿은 클래스명을 쓰고, 인라인 style은 **동적 값**(밴딩 색상 등)만 허용. 선례: `wholesale-golden.css`. |
| **커밋** | 명시적 승인 전 `git commit` 금지. |

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

## 4. 프론트 표준 템플릿

### 4-1. index.html — Chart.js CDN (차트 쓰는 탭만, 1회)
```html
<!-- app.js 보다 먼저 -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
```

### 4-2. api.js — 메서드 추가
```js
get<Feature>Overview: (from, to) =>
  request(`/<feature>/overview${from || to ? `?from_date=${from||''}&to_date=${to||''}` : ''}`),
```

### 4-3. View (Vue 셸 — iframe 없음, JSON fetch)
```js
// frontend/js/views/<Feature>View.js
import { api } from '../api.js';
export default {
  name: '<Feature>View',
  template: `
    <div>
      <div class="view-toolbar"><!-- 날짜/탭/새로고침 --></div>
      <div class="page-body">
        <!-- 로딩 스피너(MUST, §4-5): 시간 걸리는 fetch 동안 빈 화면 금지 -->
        <div v-if="loading" class="loading-box"><div class="spinner"></div><div style="color:#9C9A97;font-size:13px">불러오는 중…</div></div>
        <template v-else>
          <component-cards :stores="data.stores"></component-cards>
          <!-- 위젯 조립. iframe 절대 금지 -->
        </template>
      </div>
    </div>`,
  setup() {
    const { ref, onMounted } = Vue;
    const data = ref({ stores: [], weekly_trend: {} });
    const loading = ref(true);
    async function load() {
      loading.value = true;
      try { data.value = await api.get<Feature>Overview(); }
      catch (e) { console.error('[<feature>] 로드 실패', e); }
      finally { loading.value = false; }
    }
    onMounted(load);
    return { data, loading, load };
  },
};
```

### 4-4. 차트 위젯 (Chart.js를 onMounted에서 init)
```js
// frontend/js/widgets/<Feature>TrendChart.js
export default {
  name: '<Feature>TrendChart',
  props: { series: { type: Array, default: () => [] } },
  template: `<canvas ref="cv" style="max-height:280px"></canvas>`,
  setup(props) {
    const { ref, onMounted, watch, onUnmounted } = Vue;
    const cv = ref(null); let chart = null;
    function render() {
      if (chart) { chart.destroy(); chart = null; }
      if (!props.series.length) return;   // 빈 시리즈: 차트 미생성(이전 차트도 파괴 → stale 방지)
      chart = new Chart(cv.value, { type: 'bar', data: {...}, options: {...} });
    }
    onMounted(render);
    watch(() => props.series, render, { deep: true });   // 빈↔데이터 전환 모두 재처리
    onUnmounted(() => { if (chart) chart.destroy(); });
    return { cv };
  },
};
```

### 4-5. 데이터 테이블·입력 UX 표준
- **로딩 스피너 (MUST — 시간 걸리는 작업엔 항상 표시)**: fetch/집계 등 **눈에 띄는 지연(체감 0.5초+)이 있는 모든 비동기 작업**은 진행 중임을 시각적으로 알린다. 빈 화면·정지된 화면을 그대로 노출하지 않는다.
  - **재사용 자산**: 전역 `frontend/css/theme.css`에 `.loading-box` + `.spinner`(+`@keyframes spin`)가 정의돼 있다. 새로 만들지 말고 그대로 쓴다:
    ```html
    <div v-if="loading" class="loading-box"><div class="spinner"></div><div style="color:#9C9A97;font-size:13px">불러오는 중…</div></div>
    ```
    (라이트 테마 뷰에서도 동일 클래스 사용 가능 — 색만 인라인으로 조정.) 텍스트만(`불러오는 중...`) 두지 말고 **반드시 `.spinner` 요소를 포함**한다.
  - **작업명 표기 (MUST)**: 문구는 막연한 "불러오는 중…"이 아니라 **무슨 작업인지** 드러낸다(예: `행거 현재고 불러오는 중…`, `월별 수량 불러오는 중…`, `지급율 집계 불러오는 중…`). 조회 파라미터(기간·매장 등)가 이미 정해져 있으면 함께 보여 사용자가 무엇을 기다리는지 알게 한다(예: `지급율 집계 불러오는 중… (2026-05-01 ~ 2026-06-01)`).
  - **초기 로드**: `loading=true`로 시작 → 본문 대신 스피너 → 완료 시 `false`. (§4-3 템플릿 참조)
  - **부분/지연 로드**: 오버뷰를 먼저 보여주고 무거운 부분을 뒤늦게 가져오는 경우(예: VMD 월별 지연 로딩), 그 영역에 **별도 로딩 플래그**(`xxxLoading`)로 스피너를 띄운다. 백그라운드 프리로드 + 스피너 폴백을 함께 둔다.
  - **항상 점검**: dev-blueprint 작업(신규/분리/수정) 시 시간이 걸리는 경로마다 스피너 유무를 확인하고, **없으면 추가**한다(이 표준의 상시 점검 항목, §6 게이트).
- **긴 리스트는 내부 스크롤**: 데이터 테이블/리스트(상세 펼침·알림 리스트 등)는 `max-height` + `overflow-y:auto` 컨테이너로 감싸고 `thead`를 `position:sticky;top:0`로 고정한다. 길어져도 페이지가 무한정 늘어나지 않게 한다.
- **다크 네이티브 컨트롤**: `<input type="date">` 등 네이티브 입력엔 `color-scheme:dark`를 줘 다크 테마에서 달력 아이콘 등이 보이게 한다.
- **`v-for` 키**: 안정적 식별자(`store+'|'+supplier` 등)를 쓰고 인덱스 키는 지양한다(정렬/필터 시 DOM 재사용 오류 방지).

### 4-6. 컴포넌트 분리 & CSS 추출 (MUST — §1)
- **탭 = 컴포넌트**: 탭/섹션마다 `frontend/js/widgets/<Feature><Part>.js` 하나. View 는 탭바·툴바·fetch·`loading` 만 갖는 셸. 활성 탭 컴포넌트에 데이터를 props 로 내려주고, 컴포넌트는 순수 표현(검색/정렬/스크롤/Excel 자기완결).
  ```js
  // View 셸 — 어느 탭을 그릴지만 결정
  template: `
    <div class="<feature>">
      <div class="view-toolbar">...탭바...</div>
      <div class="page-body">
        <div v-if="loading" class="loading-box"><div class="spinner"></div><div><작업명> 불러오는 중…</div></div>
        <template v-else>
          <feature-main-grid   v-show="tab===0" :products="data.products"></feature-main-grid>
          <feature-male-grade  v-show="tab===1" :rows="data.male_grades"></feature-male-grade>
          <feature-purchase-cut v-show="tab===2" :rows="data.purchase_cut"></feature-purchase-cut>
        </template>
      </div>
    </div>`,
  ```
- **CSS 추출**: 컴포넌트 템플릿에 대량 인라인 style 을 박지 않는다. 피처 CSS 는 `frontend/css/<feature>.css` 로 빼고 **`.<feature>` 루트로 스코프**(전역 무충돌), `index.html` 에 `?v=` link 1줄. 서버 HTML 생성기의 `<style>` 을 이식할 때는 **해당 스코프의 3탭 관련 규칙만 선별**한다(편집탭 등 iframe 잔존 영역 규칙은 남긴다). 동적 값(밴딩 색상 등)만 인라인 허용.

## 5. 작업 순서 (Phase)

1. **Phase 1 — 백엔드**: 정본 식별(§3-3) → service(SQL 이식+계산) → router(입력검증 포함) → main.py 등록 → **import 스모크 테스트**(아래) → API JSON을 기존 `<feature>_latest.html` 수치와 **대조 검증**. *운영 DB가 로컬에 없으면(예: NAS 전용) 이 수치대조는 **배포 후로 분리**하고, 그 전엔 SQL 논리동등성으로 대체한다.*
   - **import 스모크(필수, §3-2b)**: `py_compile` 만으로 끝내지 않는다(컴파일은 import 미실행). 라우터/앱 모듈을 **실제 import**해 누락 모델·잘못된 ORM API 등 import-time 크래시를 잡는다. 런타임 의존성이 깔린 환경에서:
     `python -c "import app.main"` 또는 `python -c "from app.routers import <feature>_router"` → 에러 없이 통과해야 한다.
     로컬에 런타임이 없으면(예: `ModuleNotFoundError: sqlmodel`) **배포 직후 컨테이너 로그에서 `Application startup complete` 와 `/docs` 200 응답을 반드시 확인**(import 크래시 시 `--reload` 자식이 죽어 전 엔드포인트 무응답).
2. **Phase 2 — 프론트**: index.html(차트 CDN) → api.js → View 재작성(iframe 제거) → widgets. onMounted fetch로 렌더.
3. **Phase 3 — 검증·정리**: 정합성/반응형 수동 검증 → **독립 code-reviewer 승인 패스**(자기승인 금지; SQL 논리동등성·계약일치·런타임에러 중심, 지적 반영 후 재검증) → 기존 생성기·`*_latest.html`은 **삭제하지 않고 오라클/폴백 유지** → 결과 보고(변경·검증·리스크).

## 6. 검증 게이트 (통과 못하면 미완료)
- [ ] **import 스모크 통과**: 라우터/앱 모듈 실제 import 무에러 (§3-2b) — 또는 배포 후 `Application startup complete` + `/docs` 200 확인. *`py_compile` 통과만으론 미충족*
- [ ] 라우터에 딸린 **부속 엔드포인트**(temp-log 등)도 등록 후 정상(참조 모델 실존, ORM API 규약 일치) — 500/크래시 없음
- [ ] 동일 날짜에서 Vue 화면 수치 == 기존 `<feature>_latest.html` 수치 (합계·매장별·세부) — *로컬에 운영 DB 없으면 **배포 후 확인**으로 분리하고 완료 보고에 명시*
- [ ] 색상/등급 밴딩이 정본 임계와 일치
- [ ] 잘못된/역전 기간 입력 → 400 (조용한 전체범위 폴백 없음)
- [ ] 날짜/탭/토글/차트 갱신 등 인터랙션 정상
- [ ] **로딩 스피너 표시 + 작업명**: 시간 걸리는 모든 비동기 경로(초기 로드·지연/부분 로드)에 `.spinner`가 보이고, 문구가 **무슨 작업인지** 드러낸다(막연한 "불러오는 중…" 금지, §4-5) — 빈/정지 화면·텍스트 단독은 미충족
- [ ] 긴 리스트 내부 스크롤·sticky 헤더 동작
- [ ] 다른 탭 무손상 (라우팅 독립 확인)
- [ ] 빌드리스 유지 (CDN Vue + ES모듈, 번들러 미도입)
- [ ] **탭별 컴포넌트 분리**: 각 탭이 독립 `widgets/` 컴포넌트, View 는 셸(탭 렌더 로직 미포함, 비대하지 않음)
- [ ] **CSS 분리**: 인라인 CSS 최소, 피처 CSS 는 `.<feature>` 스코프 파일로 추출·`index.html` 링크
- [ ] 콘솔 에러 0, API 예외 처리 존재
- [ ] 독립 리뷰어 승인 (자기승인 아님)

## 7. 금지 사항
- 화면 본문 iframe 임베드
- 탭 렌더 로직을 `View` 한 파일에 몰아넣기(탭별 컴포넌트 미분리)
- 컴포넌트 템플릿에 대량 인라인 CSS(피처 CSS 파일 미추출)
- 라우터/서비스에서 HTML 문자열 생성·반환
- 정본 미확인 이식(파일모드/DB모드 혼동), 임의 SQL 신작
- 분모를 기간필터로 0 만들기 / 밴딩·임계값 임의 단순화
- 잘못된 입력을 검증 없이 조용히 폴백
- 시간 걸리는 작업에 스피너 없이 빈/정지 화면 노출 (텍스트만 두는 것도 미흡 — `.spinner` 필수)
- 별도 DB 접근 경로(`psycopg2`/DSN) 신설
- 번들러·node_modules·빌드 스텝 추가
- 기존 생성기·`*_latest.html` 성급한 삭제 (오라클 유지)
- 미승인 커밋

## 8. 최종 보고 형식 (CLAUDE.md 9항)
변경 파일 / 검증 결과(수치 대조 포함) / 남은 리스크 를 3줄 요약.
