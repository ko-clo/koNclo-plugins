---
name: store-tab
description: Use when 본사용 기존 탭의 매장(현장)용 간소화 버전을 [매장관리] 그룹에 새로 만들거나 기존 매장탭을 고칠 때. 트리거 — "매장관리탭 생성", "매장관리탭 수정", "/store-tab", "매장용 간단 버전", "현장에서 쓸 탭", "매장 화면 간소화".
---

# store-tab — 매장(현장)용 간소화 탭 생성기

> **새 기능을 만드는 스킬이 아니다.** 이미 있는 본사용 탭에서 **매장이 실제로 쓰는 것만 남긴**
> 별도 뷰를 조립해 `[매장관리]` 그룹에 붙인다. 데이터·판정·API 는 전부 원본과 공유한다.
> 탭 개발 표준은 `dev-blueprint`(§1 불변규칙·§4 UX·§6 검증게이트를 그대로 상속), 병행 뷰 선례는 `mobile-blueprint`.
> 원본 탭의 판정 규칙을 바꾸는 것은 **이 스킬의 범위 밖** — 그 탭 전담 에이전트 소관이다.

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/store-tab/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/exclusions.md` | §1 · §2 | 매장탭 범위를 정할 때 |
| `references/gaps.md` | §8 | 착수 전 1회 |
| `references/principles.md` | §0 · §9 | 범위·판단이 갈릴 때 · 금지 항목 확인 |
| `references/procedure.md` | §4 · §6 | 작업을 진행하는 동안 |
| `references/registration.md` | §3 | 파일을 만들고 등록하기 전 |
| `references/status.md` | §7 | 4-0 에서 기존 매장탭 유무를 확인할 때 · 4-5 마무리에서 행을 추가할 때 |
| `references/verification.md` | §5 | 구현 후 검증할 때 |

## 0. 탭 원칙 (이 스킬의 존재 이유 — 모든 결정의 상위 기준)

→ `references/principles.md`.

## 1. 기본 제외 목록 (요청자가 범위를 지정하지 않았을 때의 기본값)

→ `references/exclusions.md`.

## 2. 남길 것 (판단 기준)

→ `references/exclusions.md`.

## 3. 산출물 (매장탭 1개당)

→ `references/registration.md`.

## 4. 절차

→ `references/procedure.md`.

## 5. 검증 게이트 (통과 못하면 미완료)

→ `references/verification.md`.

## 6. 결정 포인트 (plan 단계에서 AskUserQuestion)

→ `references/procedure.md`.

## 7. 현황

현황 표는 `references/status.md` 에 있다. 매장탭을 만들거나 고치면 거기에 행을 추가·갱신한다.

> 사이드바 탭 정본은 `frontend/js/navTabs.js` `STORE_TABS`, 업무 화면 라우트 정본은 `frontend/js/app.js` 다. 현황 표와 어긋나면 **정본이 옳다.**

## 8. 알려진 갭 — 매장 스코프 (반드시 인지하고 작업할 것)

→ `references/gaps.md`.

## 9. 금지

→ `references/principles.md`.
