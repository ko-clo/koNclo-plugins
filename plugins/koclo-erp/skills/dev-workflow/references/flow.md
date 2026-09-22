# dev-workflow — 작업 흐름과 구현 위임 (§1 · §5)

> 본체 `SKILL.md` 에서 분리. 스텝을 진행할 때 · 구현을 넘길 때에 읽는다.

## 1. 작업 흐름과 스텝 배너

```
요청
 └─▶ ① 모드 분류 ──────────── §2  (코드 읽기만, 편집 금지)
     └─▶ ② 조사 ──────────── dev-investigator-agent (읽기전용)
         └─▶ ③ 설계 ──────── 모드별 설계 에이전트 (읽기전용)
             └─▶ ④ 승인 ──── §3 템플릿 출력 → **정지** → 승인 시에만 §4 게이트 개방
                 └─▶ ⑤ 구현 ─ 기존 탭 에이전트 (§5)
                     └─▶ ⑥ 검증 ─ dev-verify-agent + post-verification
                         └─▶ ⑦ 완료 보고 §6 → 게이트 잠금
```

②③ 은 **단일 메시지로 병렬 위임**할 수 있다(조사 결과가 설계의 입력이면 순차).
요청이 작아 조사가 파일 2~3개로 끝나면 ② 를 메인이 직접 해도 된다 — **④ 게이트만은 생략 금지.**

### 스텝 배너 — 모든 스텝은 이 머리를 달고 나온다

→ `references/templates.md`.

## 5. 구현 위임 (새 구현 에이전트를 만들지 않는다 — DRY)

| 변경 영역 | 위임 대상 |
|---|---|
| 탭 화면·서브탭 | 해당 탭 스킬/에이전트 (`vmd`·`payrate`·`inventory`·`sample-return`·`best-products`·`retail-reorder`·`wholesale-reorder`·`score-ranking`·`post-process`·`color-trend`) |
| 백엔드 구조·DB 스키마·이관 | `backend-agent` |
| 주문장 생성·배치 | `order-agent` / `batch-ingest` 스킬 |
| 새 탭 신설·iframe 제거 | `dev-blueprint` 스킬 |
| 모바일 뷰 | `mobile-view-agent` |
| 인입 포맷 방어 | `ingest-guard` 스킬 |

해당 없는 영역(공통 셸·`backend/scripts/**`·훅)만 메인이 직접 구현한다.
공유 자산(공통 계산식·config 키·공유 테이블)을 건드리면 **소비하는 쪽 에이전트도 함께** 위임한다.
