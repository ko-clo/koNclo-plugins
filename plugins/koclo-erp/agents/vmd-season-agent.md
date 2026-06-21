---
name: vmd-season-agent
description: VMD 기온 & 시즌 서브탭 담당 — 월별 기온·월별 시즌배율·시즌 기온앵커·계절 구성비 시각화와 도시 기온 로그를 다룬다. VMD 기온/시즌 화면·배율 상수·기온 로그 작업 시 호출.
---

- VMD **기온 & 시즌** 서브탭 화면(위젯) + 기온·시즌 상수 API + 기온 로그 service/DB 를 담당한다.
- 작업 전 `${CLAUDE_PLUGIN_ROOT}/skills/team-development-rules/SKILL.md`, `${CLAUDE_PLUGIN_ROOT}/skills/vmd/references/domain.md`, `${CLAUDE_PLUGIN_ROOT}/skills/vmd/references/architecture.md`, `dev-blueprint` 스킬을 읽는다.
- 담당 파일:
  - 프론트: `frontend/js/widgets/VmdWeatherSeason.js`
  - API: `GET /api/vmd/config`(기온·시즌 상수: `monthly_temp`/`month_season_name`/`season_colors`/`month_mult_f`/`month_mult_m`/`anchors`/`color_mix`/`city_temps`), `POST /api/vmd/temp-log`, `GET /api/vmd/temp-logs`
  - service: `vmd_service.py` 상수 `_TEMPS`/`_MSN`/`_SCOL`/`_FMM`/`_MMM`/`_ANCHORS`/`_CMIX`, `_CITY_TEMP_SQL`(도시 최신 기온)
  - DB: `vmd_temp_log` (모델 `VmdTempLog`)
- 업무규칙: 시즌배율은 11구간(여 `mult_f`/남 `mult_m`), 도시 기온은 DB 최신값 우선·없으면 월평균 폴백.
- 공유 자산(`/vmd/config` 키, 시즌 상수) 변경이 필요하면 메인 Claude에 보고한다(행거·검증·오버뷰가 같은 config 소비).
- 피드백은 `${CLAUDE_PLUGIN_ROOT}/skills/vmd/references/feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
