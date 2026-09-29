# 카카오 채널 — 구조 지도

## 흐름

```
[수집] 파트너센터(운영채널) → Mac 브라우저 수집 JSON → scripts/kakao_history_push.py
        → POST /api/kakao/history/ingest (멱등) → kakao_chat_rooms · kakao_chat_logs
[봇]   오픈빌더(테스트채널) → POST /api/kakao/skill
        ├ 규칙 분류(인사·수령확인) → 즉답
        └ 그 외 → useCallback → 백그라운드: 최근 대화 + 메시지 → run_via_hermes(domain="kakao")
             → Hermes(mode=kakao, 기억 없음) → Codex → /mcp/kakao/ get_reply_policy
             → 안전 필터 → callbackUrl POST (실패 시 규칙 답) → 대화 저장
[조회] 관리자 탭 /kakao-chat → /api/kakao-chat/* (방 목록·타임라인·사입처 매핑·답장 초안)
```

## 파일

| 계층 | 파일 | 역할 |
|---|---|---|
| 웹훅 | `backend/app/routers/kakao_router.py` | `/api/kakao/` — skill · history/ingest · history/watermark. Bearer `KAKAO_SKILL_TOKEN` |
| 조회 API | `backend/app/routers/kakao_chat_router.py` | `/api/kakao-chat/` — rooms · logs · supplier-candidates · suppliers(PUT) · reply-draft. 관리자 전용 |
| 스킬 응답 | `services/kakao_chat_service.py` | textCard 조립·기본 안내 |
| 규칙 엔진 | `services/kakao_reply_engine.py` | `classify_message`·템플릿·금액 패턴. 순수 함수 |
| 콜백 | `services/kakao_callback_service.py` | Codex 호출·안전 필터·callbackUrl POST·킬스위치 |
| 원장 | `services/kakao_chat_log_service.py` | 인입·스킬 대화 저장·최근 대화 조회 |
| 매핑 | `services/kakao_room_supplier_service.py` | 방↔사입처 후보·확정 |
| 초안 컨텍스트 | `services/kakao_reply_context_service.py` | 답장 초안에 넘길 방 정보 |
| 상수 | `services/kakao_chat_constants.py` | sender 값·메시지 타입 |
| MCP 도메인 | `services/agent/registries/kakao.py` + `mcp_server/catalog.py` `EXPOSED` | SYSTEM_PROMPT·`get_reply_policy` |
| 브리지 | `services/agent/hermes_bridge.py` | `run_via_hermes` — `HERMES_SEND_MODE=1` 일 때만 `mode` 전송 |
| 수집 스크립트 | `backend/scripts/kakao_history_push.py` | JSON → ingest API |
| 프론트 | `frontend/js/views/KakaoChatView.js` · `widgets/KakaoChat*.js` · `KakaoRoomSupplierPicker.js` · `css/kakao-chat.css` | 관리자 탭 |
| 탭 등록 | `frontend/js/navTabs.js`(`admin-kakao-chat`) · `role_permission_service.py` | |
| 라우터 등록 | `backend/app/main.py` | include_router · `AUTH_PUBLIC_PREFIXES` 에 `/api/kakao/` |

## 테이블

`kakao_chat_rooms` · `kakao_chat_logs` · `kakao_room_suppliers` — `models.py` + `init.sql`, `create_all` 자동 생성.

## env (compose `environment` 에 있어야 컨테이너에 들어간다)

`KAKAO_SKILL_TOKEN` · `KAKAO_BOT_CHANNEL`(현재 test) · `KAKAO_CODEX_REPLY`(0=Codex 끔) · `HERMES_SEND_MODE`(1 필수)

## 외부 시스템

| 시스템 | 위치 |
|---|---|
| 오픈빌더 봇 | 테스트채널 Ko&Clo Test · 폴백 블록 Callback API 켜짐 · 스킬 URL `https://erp.koandclo.com/api/kakao/skill` |
| Hermes | koclo-vm 컨테이너 `hermes` · `/home/konclo/hermes/data/config.yaml`(`koclo-erp-kakao`, `memoryless_modes: [kakao]`) · 로그 `…/logs/agent.log` |
| 파트너센터 | 내부 API `chats/search`·`chatlogs` — 로그인된 Chrome 세션에서만 |
