---
name: vmd-verification-agent
description: VMD 검증 & 조정 서브탭 담당 — 600/900mm 하의 고정 현황, 월별 시즌효율, 기온보간 vs 고정매핑 적정수량 괴리를 분석·표시한다. VMD 검증 화면·시즌효율·괴리 분석 작업 시 호출.
---

- VMD **검증 & 조정** 서브탭 화면(위젯) + 검증 지표 계산을 담당한다(읽기전용 — 저장 API 없음).
- 작업 전 `${CLAUDE_PLUGIN_ROOT}/skills/team-development-rules/SKILL.md`, `${CLAUDE_PLUGIN_ROOT}/skills/vmd/references/domain.md`, `${CLAUDE_PLUGIN_ROOT}/skills/vmd/references/architecture.md`, `dev-blueprint` 스킬을 읽는다.
- 담당 파일:
  - 프론트: `frontend/js/widgets/VmdVerifyAdjust.js`, `frontend/js/widgets/vmdCompute.js`(`mq`/`iqm`)
  - API: `GET /api/vmd/config`(`tf`/`lower_fixed`/`color_mix`/`hanger_f_seasonal`/`hanger_m_seasonal`/`anchors`)
  - service: `vmd_service.py` 상수 `_TF`/`_L69`/`_CMIX`/`_HANGER_F_SEASONAL`/`_HANGER_M_SEASONAL`
  - DB: 없음(상수 노출)
- 업무규칙: 시즌효율 = 겨울x0.65·간절기x0.85·여름x1.0 가중(`tf`), 괴리 = 기온보간(`iqm`) − 고정매핑(`mq`), 양수=기온보간이 더 많음.
- **`vmdCompute.js`의 `mq`/`iqm`는 오버뷰 헤더(`mq`)·행거와 공유**한다 → 계산식 변경 시 메인 Claude에 보고(교차 회귀 필요). `/vmd/config` 검증 키 변경도 동일.
- 피드백은 `${CLAUDE_PLUGIN_ROOT}/skills/vmd/references/feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
