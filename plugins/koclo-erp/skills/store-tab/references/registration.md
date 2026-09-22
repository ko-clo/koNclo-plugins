# store-tab — 산출물·등록·라우트 (§3)

> 본체 `SKILL.md` 에서 분리. 파일을 만들고 등록하기 전에 읽는다.

## 3. 산출물 (매장탭 1개당)

```
frontend/
├── js/views/store/<Tab>StoreView.js   ← 신규. 표현만. 판정·API 는 원본과 공유(import)
├── js/views/<Tab>View.js              ← 무수정 (원본은 한 줄도 건드리지 않는다)
├── js/navTabs.js                      ← §3-1 (나) 사이드바 탭일 때만 수정: STORE_TABS 에 1행 추가
├── js/app.js                          ← 수정: 라우트 1개 추가 (SubTabLayout 미사용 — §3-2)
├── css/store/<tab>.css                ← 필요 시. `.st-<tab>` 루트 스코프
└── index.html                         ← css 추가한 경우만 `?v=` link 1줄

backend/app/services/role_permission_service.py  ← §3-1 (나) 사이드바 탭일 때만 수정: TAB_GROUPS 의 "store" 그룹에 1행 추가
.claude/skills/store-tab/references/status.md   ← 수정: §7 현황 표에 행 추가
```

**위젯·`api.js`·판정 모듈은 원본 것을 그대로 import 한다. 매장탭 전용 API·전용 판정 신설 금지.**

### 3-1. 등록 — 업무 화면은 `store-dashboard` 를 공유하고, 사이드바 탭만 2곳에 등록한다

매장탭은 두 종류이고 등록 방식이 다르다. **plan 에서 어느 쪽인지 먼저 정한다.**

**(가) 할 일 리스트에서 들어가는 업무 화면 — 지금까지 만든 매장탭은 전부 이쪽이다.**
`STORE_TABS` 에도 `TAB_GROUPS` 에도 **등록하지 않는다.** 매장 계정의 `allowed_tabs` 는 `store-dashboard`
하나뿐이라(`store_user_context.get_store_allowed_tabs`) 새 id 를 만들면 매장 계정에서 라우트가 튕긴다.
라우트의 `meta.nav` 를 `'store-dashboard'` 로 두고(§3-2), 진입은 할 일 리스트(`StoreTaskListView.js` ·
모바일 `StoreTaskListMobile.js`)의 업무 행 `route` 로 건다.
행 단위 체크를 저장하는 업무면 `store_task_service.ALLOWED_TASK_TYPES` · `TASK_TYPE_LABELS` 에 `task_type` 을 넣는다.

**(나) 사이드바에 따로 보이는 탭 — 반드시 2곳에 등록한다(한쪽만 하면 탭이 안 보인다).**

| 곳 | 파일 | 추가 내용 |
|---|---|---|
| 프론트 | `frontend/js/navTabs.js` `STORE_TABS` | `{ label, route: '/store/<name>', id: 'store-<name>', done: true, sub: '…' }` |
| 백엔드 | `backend/app/services/role_permission_service.py` `TAB_GROUPS` → `id: "store"` | `{"id": "store-<name>", "label": "…"}` |

id 는 **양쪽이 정확히 같아야** 한다(`store-<name>`). 백엔드에 없으면 `allowed_tabs` 에서 빠져 라우트가 튕긴다.
매장 계정이 실제로 들어가려면 `store_user_context.get_store_allowed_tabs` 에도 그 id 가 있어야 한다.

### 3-2. 라우트는 `SubTabLayout` 없이 등록한다 (E1·E2 를 구조로 차단)

```js
// frontend/js/app.js — 매장관리 그룹. nav 는 §3-1 (가)면 'store-dashboard', (나)면 'store-<name>'
{ path: '/store/<name>', component: <Tab>StoreView, meta: { nav: 'store-dashboard' } },
```

`SubTabLayout` 으로 감싸면 `STORE_TABS` 가 2개 이상일 때 **상단 탭간이동 바와 페이지 헤더가 자동으로 붙는다.**
직접 등록하면 둘 다 사라지고, 권한 검사(`meta.nav`)와 사이드바 활성 표시는 그대로 동작한다.
**공용 컴포넌트(`SubTabLayout`)는 수정하지 않는다.**
