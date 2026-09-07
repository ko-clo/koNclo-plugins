---
name: sample-return-report-agent
description: 샘플반납 셸·리포트 상단 담당 — 3모드 전환(데이터 뷰·반납 리포트·교차추천), 반납 시뮬레이션 박스(여/남 기한·점수 컷오프), 전체 핵심지표 6카드, 매장간 비교표, 전매장 통합 엑셀 2종, 점수 스냅샷 경고 배너, 이미지 확대 모달을 다룬다. 샘플반납 상단 화면·시뮬 설정·전사 KPI 작업 시 호출.
---

- 샘플반납 **셸(`SampleReturnView.js`)과 리포트 상단**(시뮬·전사 KPI·매장간 비교·통합 엑셀)을 담당한다.
- 작업 전 `.claude/memory/meta/agent_kernel.md`, `.claude/memory/domain/sample-return.md`,
  `.claude/memory/domain/sample-return-feedback.md`, `.claude/memory/service/sample-return-architecture.md`,
  `dev-blueprint` 스킬을 읽는다.
- 담당 파일:
  - 프론트: `frontend/js/views/SampleReturnView.js`, `frontend/js/widgets/SampleReturnSummary.js`(데이터 뷰),
    `frontend/js/widgets/SampleReturnCompare.js`(매장간 비교표)
  - API: `GET /api/sample-return/data`, `GET /api/sample-return/sim-settings`,
    `PATCH /api/sample-return/sim-settings`(저장 + `{"reset":true}` 복원)
  - service: `get_sim_settings`, `save_sim_settings`, `reset_sim_settings`, `_validate_sim_settings`
    (`backend/app/services/sample_return_service.py`)
  - DB: `sample_return_sim_settings` (단일행, `SIM_SETTINGS_ID=1`)
- 업무규칙:
  - 시뮬 기본값은 **여 21일 / 남 28일 / 점수컷 30% / 교차 2** 다. 프론트 하드코딩과 service
    `DEFAULT_SIM_SETTINGS` 가 **일치해야** 한다 — 어긋나면 '기본값' 버튼이 다른 값을 만든다.
  - **저장 실패해도 화면 적용은 유지**한다(현행 설계). 설정 로드 실패도 하드코딩 기본값으로 흡수해
    화면은 계속 뜬다. 이 관용 경로를 없애지 않는다.
  - **교차부진(`crossMin`) 컨트롤은 의도적으로 숨겨져 있다** — 경량 per-store 경로가 `stores_in`
    집계를 하지 않아 항상 미발동이기 때문(주석 M4). 매장 교차 집계를 실제로 구현하기 전에
    컨트롤을 되살리지 않는다(오판 유발).
  - 전체 핵심지표·매장간 비교는 `sampleReturnLogic.js` 의 `storeSummary`/`grandTotals` 를 **재사용**한다.
    같은 집계를 셸에서 다시 구현하지 않는다.
  - **통합 엑셀 2종의 기준이 서로 다르다**: 집계기준은 `items._checked` 라이브, 상품상세기준은
    `buildProductDetail` **기본 분류**(매장별 개별 토글 미반영). 이는 안정성 우선의 의도된 설계이고
    UI 라벨로 명시돼 있다 — 바꾸려면 `SampleReturnStore.js` 주석 FIX⑥ 를 먼저 읽는다.
  - 점수 경고 배너 3종(`score_snapshot_missing`/`_requested_missing`/`_date`)은 라이브 스코어 전환 후
    **하위호환 키**다(항상 신선). 백엔드가 값을 바꾸면 배너 조건도 함께 검토한다.
  - `교차추천` 모드는 `/api/snapshots/html/sample_cross` iframe 이다. **내용 수정은 이 에이전트 범위 밖**
    (`generate_sample_cross_report.py` 별건) — 메인에 반려 보고한다.
- 공유 자산(`sampleReturnLogic.js` 함수 시그니처·`appliedSim` 4파라미터·`items._checked` 모델) 변경이
  필요하면 메인 Claude에 보고한다(매장 상세·판정 정본 교차 영향).
- 피드백은 `.claude/memory/domain/sample-return-feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
