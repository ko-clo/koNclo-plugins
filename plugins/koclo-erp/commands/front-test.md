---
description: 프론트 View 하나를 백엔드·dev서버 없이 로컬에서 stub 데이터로 띄워 UI만 확인 (기능테스트 아님)
argument-hint: "<탭이름|View파일|route>  예: 상품관리 · ProductAdminView · /product-admin"
---
사용자가 `/front-test $ARGUMENTS` 를 실행했다. 지정한 **프론트 View 컴포넌트 하나**를
백엔드·dev서버·NAS 없이 **로컬에서 실제 Vue 컴포넌트 그대로** 브라우저에 띄워, 사용자가
직접 눌러보게 한다. 이건 **UI 확인(화면·레이아웃·상호작용)** 전용이고 **기능 테스트가 아니다** —
데이터는 stub 이라 실제 API·판정·산식은 돌지 않는다.

> 정본 사례: 2026-09-02 상품 관리(ProductAdminView) 를 이 방식으로 띄워 로그인 폼 UI 를 확인했다.
> 실제 컴포넌트+CSS 를 복사하고 `api.js` 만 stub 으로 바꿔 마운트한다 — 스크린샷 목업이 아니다.

## 이 명령이 하는 것 / 안 하는 것
- **한다**: 실제 View `.js` + 그것이 import 하는 위젯·공용 모듈 + 관련 CSS 를 scratch 로 복사,
  `api.js` 를 stub 으로 교체, 전역 Vue 로 마운트, 로컬 http 서버로 서빙, 사용자 Chrome 에 띄움.
- **안 한다**: 원본 `frontend/` 수정(복사본만 씀) · 백엔드 기동 · dev/NAS 반영 · 실제 네트워크 호출
  · 기능/회귀 검증(그건 `/server-test`). CDN Vue 를 쓰지만 **UI 확인 한정**이라 "CDN Vue 우회 금지"
  (기능검증은 dev 에서) 규칙과 충돌하지 않는다 — 이 명령은 검증이 아니라 미리보기다.

## 🚫 안전
- 원본 `frontend/**` 를 **읽기만** 한다. 절대 편집하지 않는다(복사본만 조작).
- scratch 는 **세션 scratchpad 하위**에 만든다. `rm -rf` 는 danger-guard 하드 차단이므로 쓰지 말고,
  **매번 새 디렉터리명**(`uilive-<타임스탬프>`)을 써서 충돌을 피한다. 정리는 서버 종료로 끝낸다.
- 로컬 전용. NAS·dev·prod 를 건드리지 않으므로 게이트 불필요.

## 실행 절차

### 1) 대상 View 해석
`$ARGUMENTS` 로 View 파일을 특정한다. 우선순위:
1. 인자가 파일 경로면(`frontend/js/views/*.js`) 그대로 사용.
2. 인자가 route(`/product-admin`)면 `frontend/js/app.js` 에서 그 path 의 `component` 를 찾는다.
3. 인자가 탭 이름/컴포넌트명(`상품관리`·`ProductAdminView`)이면:
   - `frontend/js/navTabs.js` 의 label/route 로 매칭 → route → app.js → View,
   - 또는 `frontend/js/views/` 에서 이름 유사 파일 검색.
4. **인자가 없거나 후보가 여러 개면 `AskUserQuestion` 으로 어떤 View 인지 먼저 묻는다.**
   엉뚱한 View 를 띄우는 것보다 한 번 묻는 게 낫다.

### 2) 로컬 의존 모듈 수집(transitive) + 복사
대상 View 의 `import ... from '...'` 를 파싱해 **로컬 상대경로 import 를 재귀로** 따라간다.
```bash
SRC=frontend
SC="<세션 scratchpad>/uilive-$(date +%s)"       # 새 디렉터리명
mkdir -p "$SC/js/views" "$SC/js/widgets" "$SC/css"
# 시작 View 복사
cp "$SRC/js/views/<View>.js" "$SC/js/views/"
```
- View 와 각 의존 파일에서 `^import .* from ['"](\.\.?/[^'"]+)['"]` 를 뽑아, `.js` 로컬 파일이면
  **원본과 같은 상대구조로 복사**(`js/widgets/...`, `js/views/...`, `js/*.js` 공용 모듈 등).
- **`api.js` 는 복사하지 않는다**(3에서 stub 으로 대체). `https://`·`http://` 외부 import 는 무시.
- 방문한 파일을 집합에 넣어 순환/중복을 막고, 새로 나온 로컬 import 가 없을 때까지 반복한다.
- 팁: `grep -oE "from ['\"](\.\.?/[^'\"]+)['\"]" <파일>` 로 한 단계씩 뽑아 큐로 처리한다.

### 3) 관련 CSS 복사
- `frontend/css/theme.css` 는 **항상** 복사(버튼·배지·공용 토큰).
- 탭 전용 CSS 를 찾는다: `index.html` 의 `<link>` 목록 또는 이름 매칭
  (`ProductAdminView`→`product-admin.css`). 확신이 안 서면 `frontend/css/` 전체를 복사해도 된다(작다).
- 어떤 CSS 를 넣었는지 보고에 남긴다.

### 4) stub `js/api.js` 작성
기본은 **관용 stub** — 어떤 메서드를 불러도 안 깨지게 한다:
```js
// UI 미리보기용 stub — 네트워크 없이 화면만. 실제 api.js 아님.
const ok = async () => ({});
export const api = new Proxy({}, {
  get: (_t, prop) => {
    // URL 빌더류(동기 문자열 반환)는 문자열을, 그 외는 async ()=>({}) 를 준다.
    if (String(prop).endsWith('Url')) return () => '';
    return ok;
  },
});
```
- **렌더가 비거나 콘솔 에러가 나면**(예: 컴포넌트가 `overview.targets.targets` 같은 중첩 필드를
  읽어 터짐), 그 View 의 **빈 상태 기본값**(대개 `emptyXxx()`/`ref({...})` 초기값)을 코드에서 읽어
  그 모양대로 반환하는 **맞춤 stub** 으로 교체한다. 정본 사례(ProductAdminView)는 `emptyOverview()`
  모양(token/targets/sources/runs…)을 그대로 돌려줬고, 로그인 성공까지 시뮬레이션했다.
- 상호작용을 보여주려면 상태 변수를 stub 안에 둬서 호출 시 바꾼다(로그인→`connected=true`).

### 5) host `index.html` 작성
```html
<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>&lt;View&gt; UI 미리보기</title>
<link rel="stylesheet" href="css/theme.css">
<link rel="stylesheet" href="css/<탭>.css">
<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
<!-- View 가 vue-router(useRoute/useRouter)를 쓰면 아래도 추가 -->
<!-- <script src="https://unpkg.com/vue-router@4/dist/vue-router.global.prod.js"></script> -->
<style>body{margin:0;background:#FAFAF8}
  .ft-hint{max-width:1100px;margin:12px auto;font-size:12px;color:#6B6A67;line-height:1.6}
  .ft-frame{max-width:1100px;margin:0 auto;border:1px solid #E8E6E3;border-radius:10px;overflow:hidden;background:#fff}</style>
</head><body>
  <p class="ft-hint"><strong>&lt;탭&gt;</strong> 실제 컴포넌트를 stub 데이터로 띄운 UI 미리보기(기능 없음).</p>
  <div class="ft-frame"><div id="app"></div></div>
  <script type="module">
    import View from './js/views/<View>.js';
    const { createApp } = Vue;
    const app = createApp(View);
    // View 가 router 를 쓰면: app.use(VueRouter.createRouter({history:VueRouter.createWebHashHistory(),routes:[{path:'/:x(.*)*',component:View}]}));
    app.mount('#app');
  </script>
</body></html>
```
- 앱은 전역 Vue(`vue.global.prod.js`)를 쓴다 — 컴포넌트가 `const {ref,...}=Vue` 로 접근하므로 그대로 동작.
- View 가 `Vue.useRoute`/`useRouter` 를 참조하면 vue-router 전역을 로드하고 catch-all 라우트로 감싼다.

### 6) 서빙 + 사용자 Chrome 에 띄우기
```bash
cd "$SC" && python3 -m http.server <PORT> >/dev/null 2>&1 &   # 예: 8901~8999 중 빈 포트
sleep 1; curl -s -o /dev/null -w "%{http_code}\n" http://localhost:<PORT>/index.html   # 200 확인
```
- 이전 `/front-test` 서버가 떠 있으면 그 포트만 `pkill -f "http.server <PORT>"` 로 정리(광범위 kill 금지).
- claude-in-chrome 으로 `http://localhost:<PORT>/index.html` 을 **사용자 Chrome 새 탭**에 열고,
  스크린샷 1장으로 렌더를 확인한다(빈 화면/에러면 4로 돌아가 stub 을 맞춤화).
- 이 탭은 **사용자 브라우저에 실제로 떠 있으므로**, 사용자가 직접 클릭·입력할 수 있다고 안내한다.

### 7) 보고
- 띄운 View·route, 복사한 파일 수, 넣은 CSS, stub 방식(관용/맞춤), 접속 URL(`http://localhost:<PORT>`).
- 원본 `frontend/` 무수정 · 백엔드/dev 미사용 · 기능 아닌 UI 확인임을 명시.
- 서버를 켜둘지/끌지 사용자에게 묻는다. 끌 때는 해당 포트만 `pkill -f "http.server <PORT>"`.

## 한계(미리 알린다)
- 데이터가 stub 이라 **실제 값·판정·목록은 진짜가 아니다.** 값·산식·회귀 확인은 `/server-test`(dev).
- 자식 컴포넌트가 `resolveComponent`(전역 등록 의존)나 무거운 외부 라이브러리를 요구하면 일부가
  안 뜰 수 있다 — 그 경우 해당 위젯만 최소 stub 컴포넌트로 대체하거나, 확인 대상 패널만 남긴다.
- route 파라미터·전역 store 강결합 View 는 맞춤 stub 손이 더 든다. 안 되면 그 사실을 보고한다.
