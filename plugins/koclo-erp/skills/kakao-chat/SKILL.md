---
name: kakao-chat
description: Use when 카카오 채널(사입처 대화) 로직의 조사·수정·기능추가 요청을 받았을 때. 트리거 — "/kakao-chat", "카카오", "카톡", "카카오 대화", "카카오 봇", "오픈빌더", "스킬 서버", "콜백", "파트너센터 수집", "대화 원장", "방↔사입처 매핑", "답장 초안", "kakao MCP", "mode=kakao"
---

# 카카오 채널 작업 — 절차 스킬

> 카카오 비즈니스 채널의 사입처 대화를 **수집·저장·답장**하는 로직 전체(백엔드 웹훅·원장·답장 엔진·
> Hermes/MCP 격리·관리자 탭). 전담 에이전트가 없으므로 **메인 Claude 가 직접** 조사·구현한다.

## 읽을 파일

경로 기준 `.claude/skills/kakao-chat/`.

| 파일 | 읽는 시점 |
|---|---|
| `references/map.md` | 항상 먼저 — 파일·API·테이블·env·외부 시스템 지도 |
| `references/invariants.md` | 수정·기능추가 설계 전 — 어기면 사고 나는 규칙 |
| `references/verification.md` | 변경 후 검증할 때 |

프로젝트 이력(결정·실측·미결)은 auto memory `project_kakao_channel_chatbot.md`, 에이전트/MCP 규칙은
`.claude/memory/service/rules-agent-mcp.md`.

## 1. 작업 흐름

1. **요청 분류** — 조사 / 수정 / 기능추가.
2. **조사** — 읽기 전용. `map.md` 로 범위를 좁히고 코드를 읽는다. 운영 확인은 koclo-vm(`/server on` 필요).
   결론은 표 + 판정 한 문장으로 보고.
3. **수정·기능추가** — `dev-workflow` 스킬로 모드(기능수정/버그해결/기능추가)를 정하고 승인 게이트를 거친다.
   설계안에 `invariants.md` 의 해당 항목을 명시한다.
4. **검증** — `verification.md`. dev 반영·실기기 테스트는 사용자 승인 후.

## 2. 경계

- 사입처 결제·지급·영수증 판단 자체는 `auto-payment-agent` 소관. 이 스킬은 그 데이터를 **읽어 답장에 쓰는 통로**만 다룬다.
- Hermes 설정·재기동은 운영 작업 — 승인 후에만.
