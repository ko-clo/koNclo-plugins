---
name: retail-reorder
description: Use when 소매 리오더 탭/영역의 수정·조회·기능추가 요청을 받았을 때. 트리거 — "소매리오더", "소매 리오더", "retail-reorder", "retail-order", "리오더 탭", "주문장 탭", "리포트 보기", "전체핵심", "마스터주문", "상품 마스터", "매장별 요약", "행거 컬럼", "지급율 컬럼", "샘플건", "주문표 모달", "빌드 이력", "안전재고 설정", "데이터 상태", "생성 취소", "store-metrics". 주문장 생성·배포 운영은 order-agent, 베스트상품 정본 화면은 best-* 소관.
---

# 소매 리오더 탭 작업 — 라우팅 스킬

> 소매 리오더는 `OrderView.js`(`/order`)의 **실행 · 리포트 보기(전체핵심 + 베스트3종 + 상품 마스터) · 빌드 이력**과, 분리된 `OrderSheetView.js`(`/order-sheet`)의 **주문장 상세**로 구성된다.
> 이 스킬은 영역 식별 → 전담 에이전트 위임 → 결과 통합 → 전체 회귀 검증 순서로 쓴다.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다.

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/retail-reorder/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/delegation.md` | §2 · §경계 | 위임 대상·경계를 정하기 전 |
| `references/routing.md` | §0 | 어느 에이전트에 맡길지 고를 때 |
| `references/verification.md` | §3 | 변경 후 회귀 검증할 때 |

## 0. 영역 ↔ 에이전트 ↔ 파일 매핑

→ `references/routing.md`.

## 1. 작업 흐름

1. **요청 영역 식별** — 사용자 요청이 어느 영역인지 §0 표로 판별. 모호하면 한 번만 질문한다.
2. **단일 영역** → 해당 에이전트 1개에 위임한다.
3. **여러 영역** → 영향 에이전트를 함께 위임한다. 특히 `OrderView.js`, `order_service` 응답 키, `order_build_*` 스키마, 마스터주문 반영은 교차 영향이다.
4. **결과 통합** — 각 에이전트 변경/리스크를 메인이 취합한다.
5. **전체 탭 회귀 검증** — §3.

## 2. 위임 규칙 (공유 자산 주의)

→ 위임 대상을 정하거나 공유 자산(응답 계약·공용 API·산식)을 건드릴 때 `references/delegation.md` 를 읽는다.

## 3. 회귀 검증

→ `dev-blueprint` 스킬 §6 게이트를 따른다. 이 탭 고유 항목은 `references/verification.md` 에 있다.

## 4. 작업 전 필독

- `.claude/memory/domain/retail-reorder.md` — 업무 규칙·용어·영역 관계·경계
- `.claude/memory/domain/retail-reorder-feedback.md` — 누적 피드백(F1~)
- `.claude/memory/service/retail-reorder-architecture.md` — Vue/API/DB/데이터 흐름
- `dev-blueprint` 스킬 — 탭 개발 표준(상위 규범)
