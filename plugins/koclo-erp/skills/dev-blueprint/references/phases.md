# dev-blueprint — 작업 순서 (§5)

> 본체 `SKILL.md` 에서 분리. 어느 단계인지 확인할 때에 읽는다.

## 5. 작업 순서 (Phase)

1. **Phase 1 — 백엔드** (`references/backend.md`): 정본 식별(§3-3) → service(SQL 이식+계산) → router(입력검증 포함) → main.py 등록 → **import 스모크 테스트**(§3-2b) → API JSON을 기존 `<feature>_latest.html` 수치와 **대조 검증**. *운영 DB가 로컬에 없으면 이 수치대조는 **배포 후로 분리**하고, 그 전엔 SQL 논리동등성으로 대체한다.*
2. **Phase 2 — 프론트** (`references/frontend.md` · `references/style.md`): index.html(차트 CDN) → api.js → View 재작성(iframe 제거) → widgets → CSS. onMounted fetch로 렌더.
3. **Phase 3 — 검증·정리**: 정합성/반응형 수동 검증 → §6 게이트 → **독립 code-reviewer 승인 패스**(자기승인 금지; SQL 논리동등성·계약일치·런타임에러 중심, 지적 반영 후 재검증) → 기존 생성기·`*_latest.html`은 **삭제하지 않고 기준 정답/폴백 유지** → §8 결과 보고.
