---
name: best-products
description: Use when 베스트상품 탭/서브탭의 수정·조회·기능추가 요청을 받았을 때. 트리거 — "베스트상품", "베스트탭", "통합베스트", "KA·TB 마스터", "KA TB 마스터", "초특급볼륨", "베스트 오버뷰", "베스트 서브탭" (베스트 데이터를 활용한 주문추천/기획은 md-agent 소관 — §경계)
---

# 베스트상품 탭 작업 — 라우팅 스킬

> 베스트상품 탭(`BestProductView.js`)은 **읽기전용 3 서브탭**으로 구성된다. 통합베스트/KA·TB는 주문장 생성(`order_v8_2_rebuild_FULL.py`) 적재본을 읽고, 초특급볼륨은 최신 `best_volume` batch를 anchor로 삼아 선택기간 판매합을 조회 시점에 재계산한다. 이 스킬은 **메인 Claude가 따르는 절차서**다.
> 서브탭 식별 → 전담 에이전트 위임(Agent 도구) → 결과 통합 → 전체 탭 회귀 검증.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다(중복 서술 금지).

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/best-products/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/delegation.md` | §2 · §경계 | 위임 대상·경계를 정하기 전 |
| `references/routing.md` | §0 | 어느 에이전트에 맡길지 고를 때 |
| `references/verification.md` | §3 | 변경 후 회귀 검증할 때 |

## 0. 서브탭 ↔ 에이전트 ↔ 파일 매핑

→ `references/routing.md`.

## 1. 작업 흐름

1. **요청 서브탭 식별** — 어느 서브탭(들)인지 §0 표로 판별. 불명확하면 AskUserQuestion.
2. **단일 서브탭** → 해당 에이전트 1개에 위임.
3. **여러 서브탭** → **병렬 위임**(단일 메시지에 다중 Agent 호출).
4. **결과 통합** — 각 에이전트 변경/리스크를 메인이 취합.
5. **전체 탭 회귀 검증** — §3.

## 2. 위임 규칙 (공유 자산 주의 — VMD보다 결합도 높음)

→ 위임 대상을 정하거나 공유 자산(응답 계약·공용 API·산식)을 건드릴 때 `references/delegation.md` 를 읽는다.

## 3. 회귀 검증 (dev-blueprint 스킬 §6 게이트 재사용)

→ `dev-blueprint` 스킬 §6 게이트를 따른다. 이 탭 고유 항목은 `references/verification.md` 에 있다.

## 4. 작업 전 필독

- `.claude/memory/domain/best-products.md` — 업무 규칙·용어·서브탭 관계·공유 의존
- `.claude/memory/service/best-products-architecture.md` — Vue/API/DB/적재 파이프라인/데이터 흐름
- `dev-blueprint` 스킬 — 탭 개발 표준(상위 규범)
