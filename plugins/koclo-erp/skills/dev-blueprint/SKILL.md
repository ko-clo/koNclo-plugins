---
name: dev-blueprint
description: Use when 새 탭을 활성화하거나, iframe(baked-HTML) 탭을 Vue 로 분리하거나, 데이터 화면(리포트·대시보드)을 신규로 만들 때. 트리거 — "dev-blueprint", "blueprint", "탭 분리", "프론트백 분리", "새 탭 활성화", "iframe 제거", "Vue화", "탭 표준", 특정 탭(지급율·마진·VMD 등) 분리 요청.
---

# dev-blueprint — KOCLO 탭 개발 표준

> **이 스킬은 "기존 구조를 뜯어고치는 것"이 아니라, "모든 탭을 이 표준대로 작성한다"는 개발 규범이다.**
> 새 탭을 활성화하거나 iframe 탭을 분리할 때, 아래 구조·명명·템플릿을 **그대로** 따른다. 표준에서 벗어나려면 명시적 사유와 승인이 필요하다.

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/dev-blueprint/`.
스크립트는 **실행해서 결과만** 본다 — 파일을 읽지 않는다.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/backend.md` | §2 · §3 · §3-2b · §3-3 · §3-4 · §3-5 | service·router 작성, `main.py` 등록 전 |
| `references/frontend.md` | §4-1 ~ §4-6 | View·위젯·CSS 작성 전 |
| `references/phases.md` | §5 | 어느 단계인지 확인할 때 |
| `references/rules.md` | §1 — MUST | 설계·구현 전 전량 확인 |
| `references/style.md` | §4-7 | 색·글꼴·공용 컴포넌트를 정할 때 |
| `references/style.md` | §4-8 | **정본 화면을 옮기는 이관**에서 CSS·마크업을 쓰기 전 |
| `references/verification.md` | §6 | 구현 후 · 완료 보고 전 |
| `scripts/check_blueprint.py` | §6 | 게이트 기계 판정 |
| `scripts/import_smoke.py` | §3-2b | 라우터 import 스모크 (전 탭 스킬 공용) |

§7(금지 사항)은 §1·§6 에 통합됐다.

## 0. 적용 시점

- 새 탭을 처음 활성화할 때
- 기존 `iframe`(baked-HTML) 탭을 분리할 때
- 데이터 화면(리포트/대시보드)을 신규로 만들 때

> **시작 전 확인** — 분리 대상 View를 **정확히 식별**한다. 이름이 비슷한 인접 기능과 혼동하지 않는다
> (예: `PayrateView`=지급**관리**/자동지급 vs `PayrateOverviewView`=지급**율** 오버뷰).
> 운영이 실제 서빙하는 컨테이너/코드베이스도 확인한다(여러 스택이 공존할 수 있음).

## 1. 불변 규칙 (MUST — 협상 불가)

→ `references/rules.md`.

## 5. 작업 순서 (Phase)

→ `references/phases.md`.

## 6. 검증 게이트 (통과 못하면 미완료)

→ `references/verification.md`.

## 8. 최종 보고 형식 (CLAUDE.md 9항)

변경 파일 / 검증 결과(수치 대조 포함) / 남은 리스크 를 3줄 요약.
