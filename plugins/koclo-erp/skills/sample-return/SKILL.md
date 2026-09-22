---
name: sample-return
description: Use when 샘플반납 탭/영역의 수정·조회·기능추가 요청을 받았을 때. 트리거 — "샘플반납", "샘플 반납", "sample-return", "/sample-return", "반납 리포트", "반납대상", "집계샘플", "샘플집계명", "상품 상세", "반품집계", "반납 시뮬레이션", "기한초과", "과락", "무판매", "교차부진", "배치 폴더 저장", "sample_ledger" (실제 반납 실행 판단은 returns-agent, 샘플 진행/종결 판정 정본은 sample-judgment-rule 메모리 — §경계)
---

# 샘플반납 탭 작업 — 라우팅 스킬

> 샘플반납(`SampleReturnView.js`)은 3모드(데이터 뷰 · 반납 리포트 · 교차추천) + 매장 상세 5서브탭으로 구성된다.
> 이 스킬은 **메인 Claude가 따르는 절차서**다.
> 영역을 식별 → 전담 에이전트로 위임(Agent 도구) → 결과 통합 → 전체 탭 회귀 검증.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다(중복 서술 금지).

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/sample-return/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/delegation.md` | §2 · §경계 | 위임 대상·경계를 정하기 전 |
| `references/routing.md` | §0 | 어느 에이전트에 맡길지 고를 때 |
| `references/verification.md` | §3 | 변경 후 회귀 검증할 때 |

## 0. 영역 ↔ 에이전트 ↔ 파일 매핑

→ `references/routing.md`.

## 1. 작업 흐름

1. **요청 영역 식별** — 사용자 요청이 어느 영역(들)인지 §0 표로 판별. 불명확하면 AskUserQuestion.
2. **단일 영역** → 해당 에이전트 1개에 위임.
3. **여러 영역** → **병렬 위임**(단일 메시지에 다중 Agent 호출).
4. **결과 통합** — 각 에이전트 변경/리스크를 메인이 취합.
5. **전체 탭 회귀 검증** — §3.

## 2. 위임 규칙 (공유 자산 주의)

→ 위임 대상을 정하거나 공유 자산(응답 계약·공용 API·산식)을 건드릴 때 `references/delegation.md` 를 읽는다.

## 3. 회귀 검증 (dev-blueprint 스킬 §6 게이트 재사용)

→ `dev-blueprint` 스킬 §6 게이트를 따른다. 이 탭 고유 항목은 `references/verification.md` 에 있다.

## 4. 작업 전 필독

- `.claude/memory/domain/sample-return.md` — 업무 규칙·용어·영역 관계
- `.claude/memory/domain/sample-return-feedback.md` — 과거 지적 누적(F1~)
- `.claude/memory/service/sample-return-architecture.md` — Vue/API/DB/데이터 흐름
- `.claude/memory/domain/sample-judgment-rule.md` — 샘플 진행/종결 판정 **공용 정본**
- `dev-blueprint` 스킬 — 탭 개발 표준(상위 규범)
