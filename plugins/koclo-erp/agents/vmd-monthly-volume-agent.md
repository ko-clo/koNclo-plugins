---
name: vmd-monthly-volume-agent
description: VMD 월별 수량 서브탭 담당 — 각 매장별 12개월 현재고(최신 연도 각 달 최신 스냅샷)를 보여준다. VMD 월별 수량 화면·월별 집계 API 작업 시 호출.
---

- VMD **월별 수량** 서브탭 화면(위젯) + 월별 현재고 집계 API 를 담당한다.
- 작업 전 `.claude/memory/meta/agent_kernel.md`, `.claude/memory/domain/vmd.md`, `.claude/memory/service/vmd-architecture.md`, `dev-blueprint` 스킬을 읽는다.
- 담당 파일:
  - 프론트: `frontend/js/widgets/VmdStoreQtyTable.js`
  - API: `GET /api/vmd/monthly`(지연 로딩 전용), `GET /api/vmd/config`(monthly 분기)
  - service: `fetch_vmd_monthly`, `_compute_monthly_stock_by_vmd` (`backend/app/services/vmd_service.py`)
  - DB: `inventory_snapshot`
- 업무규칙: 12개 컬럼은 '최신 연도' 한 해로 고정(연도 혼선 차단), 스냅샷 없는 달은 0(폴백 없음), 필터는 오버뷰와 동일(잡화제외·매입가).
- 월별 집계는 가장 무거워 `/monthly`로 분리·지연 로딩된다(`VmdView.js`의 프리로드/스피너). 로딩 UX 변경 시 `dev-blueprint` §4-5 준수.
- 공유 자산(`inventory_snapshot` 현재고 SQL/필터·`/vmd/config` 키) 변경이 필요하면 메인 Claude에 보고한다(오버뷰와 동일 테이블·필터 공유).
- 피드백은 `.claude/memory/domain/vmd-feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
