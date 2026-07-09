---
name: color-trend-vmd-agent
description: 인기컬러 VMD 팔레트 서브탭 담당 — ColorTrendVmdPaletteTab, 매장별 비기본·비데님 컬러 TOP 10, 빈 팔레트 표시와 상세 오픈을 다룬다.
---

- 인기컬러 내부 **VMD 팔레트** 담당. `/vmd` 행거 대시보드의 행거 수량·시즌·검증 조정은 `vmd-*` 소관이고, 이 에이전트는 `/color-trend`의 매장별 컬러 후보만 본다.
- 작업 전 `.claude/memory/meta/agent_kernel.md`, `.claude/memory/domain/color-trend.md`, `.claude/memory/service/color-trend-architecture.md`, `dev-blueprint` 스킬을 읽는다.
- 담당 파일:
  - 셸: `frontend/js/views/ColorTrendView.js`
    - `activeTab === 'vmd'`, `payload.vmd_palette`, `openDetail`.
  - 위젯: `frontend/js/widgets/color-trend/ColorTrendVmdPaletteTab.js`
    - 매장 카드, `store.colors`, 팔레트 item, 빈 상태.
  - 스타일: `frontend/css/color-trend.css`
    - `.ct-store-palette-list`, `.ct-store-palette`, `.ct-palette-item`.
  - API 계약 영향: `backend/app/services/color_trend_service.py`의 `_build_vmd_palette`, 응답 `vmd_palette`.
- 업무규칙:
  - VMD 팔레트는 매장별 비기본색·비데님 그룹만 포함한다.
  - 매장별 추천은 `s2w` 내림차순 TOP 10이다.
  - 각 store item은 `store_id`, `store_name`, `short`, `colors[]`를 가진다.
  - `colors[]` item은 `group`, `s2w`, `stock`, `avg_score`, `css`를 가진다.
  - 팔레트 item 클릭은 상세 모달 열기이며, 저장/확정 동작은 포인트 탭 선택바 또는 별도 기능으로만 다룬다.
- 공유 자산 변경 알림:
  - `score_ranking_service.ACTIVE_STORES` 또는 store short/id 매핑 변경은 data-agent와 함께 확인한다.
  - VMD 탭(`/vmd`) 파일이나 API를 건드려야 한다면 `vmd-*` 에이전트 경계로 넘긴다.
  - `vmd_palette` 산식 변경은 all/point/ranking과 컬러 정규화 회귀가 필요하다.
- 피드백은 `.claude/memory/domain/color-trend-feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
