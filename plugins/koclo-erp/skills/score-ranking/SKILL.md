---
name: score-ranking
description: Use when 스코어랭킹 탭/영역의 수정·조회·기능추가 요청을 받았을 때. 트리거 — "스코어랭킹", "스코어 랭킹", "score-ranking", "score ranking", "/score-ranking", "종합 TOP", "주문장 베스트", "깔교대상", "색상 아코디언", "마스터시트 전송", "점수 산식", "랭킹 필터"
---

# 스코어랭킹 탭 작업 — 라우팅 스킬

> 스코어랭킹은 `ScoreView.js`(`/score`)의 **오버뷰 셸 · 상품/색상 리스트 · DB 직접 점수 파이프라인**으로 구성된다.
> 이 스킬은 영역 식별 → 전담 에이전트 위임 → 결과 통합 → 전체 회귀 검증 순서로 쓴다.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다.

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/score-ranking/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/delegation.md` | §2 · §경계 | 위임 대상·경계를 정하기 전 |
| `references/routing.md` | §0 | 어느 에이전트에 맡길지 고를 때 |
| `references/verification.md` | §3 | 변경 후 회귀 검증할 때 |

## 0. 영역 ↔ 에이전트 ↔ 파일 매핑

→ `references/routing.md`.

## 1. 작업 흐름

1. **요청 영역 식별** — 사용자 요청이 어느 영역인지 §0 표로 판별한다. 모호하면 한 번만 질문한다.
2. **단일 영역** → 해당 에이전트 1개에 위임한다.
3. **여러 영역** → 영향 에이전트를 함께 위임한다. 특히 `ScoreView.js`, `ScoreRankingProductList.js`, `score_ranking_service` 응답 키, master-sheet 전송 계약은 교차 영향이다.
4. **결과 통합** — 각 에이전트 변경/리스크를 메인이 취합한다.
5. **전체 탭 회귀 검증** — §3.

## 2. 위임 규칙 (공유 자산 주의)

→ 위임 대상을 정하거나 공유 자산(응답 계약·공용 API·산식)을 건드릴 때 `references/delegation.md` 를 읽는다.

## 3. 회귀 검증

→ `dev-blueprint` 스킬 §6 게이트를 따른다. 이 탭 고유 항목은 `references/verification.md` 에 있다.

## 4. 작업 전 필독

- `.claude/memory/domain/score-ranking.md` — 업무 규칙·용어·영역 관계·경계
- `.claude/memory/domain/score-ranking-feedback.md` — 누적 피드백(F1~)
- `.claude/memory/service/score-ranking-architecture.md` — Vue/API/DB/데이터 흐름
- `dev-blueprint` 스킬 — 탭 개발 표준(상위 규범)
