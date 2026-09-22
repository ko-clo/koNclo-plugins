---
name: post-verification
description: Use when 기능 구현, 버그 수정, 리팩터링, API/DB/UI/설정 변경을 마친 뒤 최종 보고 전에 사후 검증이 필요할 때. 입력값, 출력값, 예외 처리, 로깅, 테스트, 회귀, dev 서버 확인, code-review 필요 여부를 증거 기반으로 정리해야 할 때 호출한다.
---

# Post Verification

> 구현 완료 직후 "동작할 것 같다"를 "검증했다"로 바꾸는 마감 게이트다.
> 변경을 새로 설계하지 않는다. 이미 만든 변경이 요청 의도, 입력/출력 계약, 예외 처리, 로깅, 회귀 위험을 통과했는지 증거로 확인한다.

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/post-verification/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/checks.md` | §2 ~ §5 | 각 체크를 수행할 때 |
| `references/execution.md` | §6 · §7 | 실제로 돌려 볼 때 |
| `references/plan.md` | §1 | 검증을 설계할 때 |
| `forms/report.md` | §9 | 최종 보고를 쓸 때 |

## 0. 시작 전 확인

1. `CLAUDE.md`와 관련 skill을 따른다.
   - 탭 개발/Vue/API 분리: `dev-blueprint`
   - 브랜치/PR 리뷰: `code-review` 또는 `/pr-review`
   - 인입 포맷: `ingest-guard`
   - 도메인 탭: `vmd`, `payrate`, `best-products`, `auto-payment-cycle`, `order-audit`, `order-cycle`
2. `git status`와 변경 파일 목록을 확인해 이번 작업 범위와 기존 더티 파일을 분리한다.
3. 사용자의 원요청과 수용 기준을 1-2문장으로 복원한다.

## 1. 검증 계획

→ `references/plan.md`.

## 2. 입력 체크

→ `references/checks.md`.

## 3. 출력 체크

→ `references/checks.md`.

## 4. 예외 처리 체크

→ `references/checks.md`.

## 5. 로깅 체크

→ `references/checks.md`.

## 6. 실행 검증

→ `references/execution.md`.

## 7. 반례 루프

→ `references/execution.md`.

## 8. 최종 판정

판정은 셋 중 하나만 사용한다.

- `PASS`: 수용 기준과 핵심 반례가 증거로 통과.
- `FAIL`: 구현 결함 또는 회귀가 확인됨.
- `INCOMPLETE`: 환경/승인/데이터 부족으로 핵심 검증이 남음.

## 9. 보고 형식

→ `forms/report.md`.
