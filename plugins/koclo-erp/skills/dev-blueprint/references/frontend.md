# dev-blueprint — 프론트 표준 (§4-1 ~ §4-6)

> 본체 `SKILL.md` §1 불변 규칙이 우선한다. 색·글꼴은 `references/style.md`(§4-7).

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
- 선례: `wholesale-golden.css`.
