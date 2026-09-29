# 카카오 채널 — 검증

카카오 전용 검증 스크립트는 **없다**(`backend/scripts/test_*`·`tests/` 에 kakao 없음). 없다고 보고한다.

## 로컬 (승인 불필요)

```bash
python3 -m py_compile backend/app/routers/kakao*.py backend/app/services/kakao*.py backend/app/services/agent/registries/kakao.py
node --check frontend/js/views/KakaoChatView.js   # 프론트 변경 시 해당 파일
```

`kakao_reply_engine`·`is_sendable_codex_reply`·`build_codex_user_message` 는 순수 함수 — scratchpad 스크립트로 입력별 결과를 확인한다(레포에 남기지 않는다).

## dev / prod (사용자 승인 후)

| 확인 | 방법 | 기대 |
|---|---|---|
| 토큰 가드 | `/api/kakao/skill` 무토큰·틀린 토큰 curl | 401 |
| 스킬 즉답 | 토큰 + 인사 발화 payload | 200, textCard |
| 인입 멱등 | 같은 JSON 2회 ingest | 2회차 삽입 0 |
| MCP 도구 | koclo-vm `agent.log` 에서 `koclo-erp-kakao` 등록·호출 | `registered N tool(s)` |
| 격리 | 앱 컨테이너 env `HERMES_SEND_MODE` | `1` |
| 실기기 | 테스트채널에 발화(봇테스트는 콜백 불가) | 답 도착 · `kakao_chat_logs` 저장 |

프론트 렌더는 로컬이 아니라 dev 에서 확인한다(`/server-test`, 승인 필요).
