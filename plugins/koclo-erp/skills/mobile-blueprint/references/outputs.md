# mobile-blueprint — 산출물과 금지

> 본체 `SKILL.md` 에서 분리. 파일을 만들기 전 · 경계를 확인할 때에 읽는다.

## 산출물 (탭 1개당)

```
frontend/
├── js/views/mobile/<Tab>Mobile.js     ← 신규 (표현만 — 판정·API 는 데스크톱과 공유)
├── css/mobile/<tab>.css               ← 신규 (.mv-<tab> 변수 + 탭 고유 규칙만, ~30줄)
├── js/app.js                          ← 수정 (해당 라우트 component 를 responsive() 로 래핑 — 1줄)
├── index.html                         ← 수정 (델타 CSS <link> 1줄 + 캐시버스터)
└── js/widgets/<tab>Logic.js           ← 필요 시 (데스크톱 위젯에 갇힌 계산을 공유 모듈로 추출)

.claude/memory/service/mobile-architecture.md  ← 수정 (§5 현황 표에 행 추가)
```

**`responsive.js` · `mobile.css` 의 `.mv-*` 베이스 · 앱 셸(상단바·드로어)은 이미 완성 — 신규 탭에서 수정하지 않는다.**

## 금지

- **plan 제시·승인 전 파일 생성·수정** (이 스킬의 1순위 규칙).
- **판정·계산 로직을 모바일 뷰에 복사** — 정본 이중화. 반드시 공유 모듈 import.
- **모바일 전용 API 신설** — 데스크톱과 동일 엔드포인트를 쓴다.
- **데스크톱 뷰 동작 변경** — 라우트는 감싸기만, 위젯 수정은 무동작 추출에 한정.
- `responsive.js` · `.mv-*` 베이스 · `.srm-*`(운영 중) 수정.
- 새 팔레트 발명 — 값은 탭 정본 CSS 에서 가져온다.
- `mobile-architecture.md` 내용 중복 서술(참조만).
- 미승인 커밋 · 미승인 `/server-test`.
