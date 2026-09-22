---
name: color-trend
description: Use when 인기컬러 탭/영역의 수정·조회·기능추가 요청을 받았을 때. 트리거 — "인기컬러", "인기 컬러", "컬러트렌드", "컬러 트렌드", "color-trend", "/color-trend", "전체 칼라", "포인트 칼라", "VMD 팔레트", "인기종합순", "부진칼라", "외부 트렌드", "마스터시트 전송"
---

# 인기컬러 탭 작업 — 라우팅 스킬

> 인기컬러는 `ColorTrendView.js`(`/color-trend`)의 **전체 칼라 · 포인트 칼라 · VMD 팔레트 · 인기종합순 · 부진칼라 경고 · 외부 트렌드 · 상세 모달/마스터시트 전송 · source DB 집계 파이프라인**으로 구성된다.
> 이 스킬은 영역 식별 → 전담 에이전트 위임 → 결과 통합 → 전체 회귀 검증 순서로 쓴다.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다.

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/color-trend/`.

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
3. **여러 영역** → 영향 에이전트를 함께 위임한다. 특히 `color_trend_service.py`, `/api/color-trend/overview` 응답 키, `ColorTrendDetailModal.js`, `/api/master-sheets*`는 교차 영향이다.
4. **결과 통합** — 각 에이전트 변경/리스크를 메인이 취합한다.
5. **전체 탭 회귀 검증** — §3.

## 2. 위임 규칙 (공유 자산 주의)

→ 위임 대상을 정하거나 공유 자산(응답 계약·공용 API·산식)을 건드릴 때 `references/delegation.md` 를 읽는다.

## 3. 회귀 검증

→ `dev-blueprint` 스킬 §6 게이트를 따른다. 이 탭 고유 항목은 `references/verification.md` 에 있다.

## 4. 작업 전 필독

- `.claude/memory/domain/color-trend.md` — 업무 규칙·용어·영역 관계·경계
- `.claude/memory/domain/color-trend-feedback.md` — 누적 피드백(F1~)
- `.claude/memory/service/color-trend-architecture.md` — Vue/API/DB/데이터 흐름
- `dev-blueprint` 스킬 — 탭 개발 표준(상위 규범)
