---
name: dev-blueprint
description: Use when 새 탭을 활성화하거나, iframe(baked-HTML) 탭을 Vue 로 분리하거나, 데이터 화면(리포트·대시보드)을 신규로 만들 때. 트리거 — "dev-blueprint", "blueprint", "탭 분리", "프론트백 분리", "새 탭 활성화", "iframe 제거", "Vue화", "탭 표준", 특정 탭(지급율·마진·VMD 등) 분리 요청.
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

## 읽을 파일

절 번호는 다른 스킬이 참조하는 고정 ID 다. 해당 작업 **전에** 그 파일을 읽는다.
경로 기준은 `.claude/skills/dev-blueprint/` 다.

| 절 | 파일 | 읽는 시점 |
|---|---|---|
| §2 · §3 · §3-2b · §3-3 · §3-4 · §3-5 | `references/backend.md` | service·router 작성, `main.py` 등록 전 |
| §4-1 ~ §4-6 | `references/frontend.md` | View·위젯·CSS 작성 전 |
| §4-7 | `references/style.md` | 색·글꼴·공용 컴포넌트를 정할 때 |
| §4-8 | `references/style.md` | iframe·가안 등 **정본 화면을 옮기는 이관**에서 CSS·마크업을 쓰기 전 |

§7(금지 사항)은 §1·§6 에 통합됐다.

## 1. 불변 규칙 (MUST — 협상 불가)

| 항목 | 표준 |
|---|---|
| **분리 범위** | 본문 전체 Vue화. **iframe 금지.** `*_latest.html`을 화면 본문으로 임베드하지 않는다. |
| **데이터 소스** | **DB 직접 쿼리 신규 엔드포인트** (앱 async 엔진 `engine.connect()` + `text()`). HTML 생성기와 분리 — 라우터·서비스는 HTML 을 만들지 않는다. 새 `psycopg2`/별도 DSN 경로를 만들지 말고 앱 엔진으로 일원화. |
| **데이터 로더** | **공유 monolith `master_data` 금지.** 각 탭은 자기가 실제로 소비하는 컬럼/섹션만 만드는 **고유 경량 loader**를 갖는다. 골든 산식/함수는 그대로 재사용(새 산식 금지). 근거·선례 = §3-4. |
| **차트** | **CDN Chart.js를 Vue 컴포넌트 `onMounted`에서 init.** 서버 HTML에 차트를 굽지 않는다. |
| **빌드리스** | CDN Vue3 + ES모듈만. 번들러·node_modules·빌드 단계 도입 금지. |
| **책임 분리** | 계산(service) / 입출력(router) / 표현(Vue) 3계층 분리. (CLAUDE.md 1·4항) |
| **컴포넌트 분리** | 탭/섹션 1개 = 컴포넌트 1개. `View`는 **셸**(툴바·탭바·fetch·공유상태)만 담고, 표현은 `widgets/<Feature><Part>.js`로 분리한다. View가 비대해지면(≈300줄+) 반드시 쪼갠다. (CLAUDE.md 4·6항) |
| **CSS 분리** | 인라인 CSS 지양. 피처 전용 스타일은 `frontend/css/<feature>.css`에 **`.<feature>` 루트로 스코프**해 분리하고(전역 `theme.css` 무충돌), `index.html`에 `?v=` 캐시버스팅 `<link>`로 1회 로드한다. 컴포넌트 템플릿은 클래스명을 쓰고, 인라인 style은 **동적 값**(밴딩 색상 등)만 허용. |
| **UI 보존** | 이관은 데이터소스 현대화이지 리디자인이 아니다. 정본 화면(iframe HTML·가안)을 옮길 때 콘텐츠 영역은 정본의 색·글꼴·간격과 마크업 구조를 **그대로** 옮긴다. KO&CLO 스타일은 셸 크롬(빌드이력 바·탭바·새로고침 라인)에만. "정본을 보존했다"는 서술은 정본을 열어 대조한 뒤에만 쓴다. 절차 = §4-8. |
| **스타일 정본** | 정본 없이 새로 만드는 탭과 셸 크롬에 적용한다(정본을 옮기는 콘텐츠 영역은 위 **UI 보존**이 우선). 색·글꼴·모서리는 **§4-7**을 따른다. 색은 `var(--koclo-*)`(정의 = `theme.css` `:root`), 글꼴은 **DM Sans · Instrument Serif · JetBrains Mono** 3종만. 토큰에 없는 hex·미로드 글꼴·다크모드·좁은 고정 폭·`position:fixed` 금지. |
| **커밋** | 명시적 승인 전 `git commit` 금지. |

## 5. 작업 순서 (Phase)

1. **Phase 1 — 백엔드** (`references/backend.md`): 정본 식별(§3-3) → service(SQL 이식+계산) → router(입력검증 포함) → main.py 등록 → **import 스모크 테스트**(§3-2b) → API JSON을 기존 `<feature>_latest.html` 수치와 **대조 검증**. *운영 DB가 로컬에 없으면 이 수치대조는 **배포 후로 분리**하고, 그 전엔 SQL 논리동등성으로 대체한다.*
2. **Phase 2 — 프론트** (`references/frontend.md` · `references/style.md`): index.html(차트 CDN) → api.js → View 재작성(iframe 제거) → widgets → CSS. onMounted fetch로 렌더.
3. **Phase 3 — 검증·정리**: 정합성/반응형 수동 검증 → §6 게이트 → **독립 code-reviewer 승인 패스**(자기승인 금지; SQL 논리동등성·계약일치·런타임에러 중심, 지적 반영 후 재검증) → 기존 생성기·`*_latest.html`은 **삭제하지 않고 기준 정답/폴백 유지** → §8 결과 보고.

## 6. 검증 게이트 (통과 못하면 미완료)

**먼저 기계 판정 항목을 돌린다. FAIL 이 0 이어야 한다.** 파일명이 규칙(§2)과 다른 탭은 `--help` 의 경로 옵션으로 직접 지정한다.

```bash
python3 .claude/skills/dev-blueprint/scripts/check_blueprint.py <feature>               # 새로 만든 탭
python3 .claude/skills/dev-blueprint/scripts/check_blueprint.py <feature> --preserve-ui  # 정본을 옮긴 이관 탭(§4-8)
```

스크립트가 보는 것: 토큰 밖 hex · 토큰 밖 글꼴 · 미로드 글꼴 · 다크모드 블록 · `position:fixed` · 좁은 고정 폭(WARN — FAIL 로 세지 않으니 직접 열어 보고 고치거나 사유를 남긴다) · iframe · View 비대 · CSS 링크 · 라우터 등록 · 모델 심볼 실존 · 금지 API(`session.exec`·`build_master_data`·`psycopg2`) · 스피너 · 빌드리스. `--preserve-ui` 에서는 토큰 밖 hex·토큰 밖 글꼴·`position:fixed` 가 WARN 이 된다 — 그 목록이 정본 값과 대조할 대상이다. **정본이 없는 탭이나 정본과 대조하지 않은 탭에 `--preserve-ui` 를 쓰는 것은 게이트 우회다.**

스크립트가 못 보는 아래 항목은 직접 확인한다.

- [ ] **import 스모크 통과**: 라우터/앱 모듈 실제 import 무에러 (§3-2b) — 또는 배포 후 `Application startup complete` + `/docs` 200 확인. *`py_compile` 통과만으론 미충족*
- [ ] 라우터에 딸린 **부속 엔드포인트**(temp-log 등)도 등록 후 정상 — 500/크래시 없음
- [ ] 동일 날짜에서 Vue 화면 수치 == 기존 `<feature>_latest.html` 수치 (합계·매장별·세부) — *로컬에 운영 DB 없으면 **배포 후 확인**으로 분리하고 완료 보고에 명시*
- [ ] 색상/등급 밴딩이 정본 임계와 일치
- [ ] **UI 보존(이관 탭)**: 정본 `<style>` 값과 대조 — 배경·글자·표 헤더 3색 스팟체크, 스크린샷이 가능하면 `visual-verdict` 로 정본 화면과 비교(§4-8). 보고에 **정본 파일 경로와 대조한 값**을 적는다
- [ ] 잘못된/역전 기간 입력 → 400 (조용한 전체범위 폴백 없음)
- [ ] 날짜/탭/토글/차트 갱신 등 인터랙션 정상
- [ ] 로딩 문구가 **무슨 작업인지** 드러낸다(막연한 "불러오는 중…" 금지, §4-5) — 지연/부분 로드 경로 포함
- [ ] 긴 리스트 내부 스크롤·sticky 헤더 동작
- [ ] 다른 탭 무손상 (라우팅 독립 확인)
- [ ] **고유 데이터 로더**: 탭 전용 경량 loader 로 소비 컬럼만 로드(파리티 유지)
- [ ] 콘솔 에러 0, API 예외 처리 존재
- [ ] 독립 리뷰어 승인 (자기승인 아님) — `--preserve-ui` 로 통과한 탭은 리뷰어가 정본 대조 근거를 직접 확인한다

## 8. 최종 보고 형식 (CLAUDE.md 9항)

변경 파일 / 검증 결과(수치 대조 포함) / 남은 리스크 를 3줄 요약.
