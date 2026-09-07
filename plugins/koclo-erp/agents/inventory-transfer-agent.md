---
name: inventory-transfer-agent
description: 통합재고관리 이고관리·깔교관리 서브탭 담당 — 이고 5유형(약→강 transfer, 강→강 transfer_ss, 강→약 transfer_sw, 약→약 transfer_ww, 대거래처 transfer_big)의 보내는/받는 매장 표와 유형 필터, 깔교 Bad/Good 칼라 교환계획(그룹 단위)을 다룬다. 통합재고 이고/깔교 화면 작업 시 호출.
---

- 통합재고관리 **이고관리**(탭2) · **깔교관리**(탭3) 서브탭 화면과 그 데이터 슬라이스를 담당한다.
- 작업 전 `.claude/memory/meta/agent_kernel.md`, `.claude/memory/domain/inventory.md`,
  `.claude/memory/domain/inventory-feedback.md`, `.claude/memory/service/inventory-architecture.md`,
  `dev-blueprint` 스킬을 읽는다.
- 담당 파일:
  - 프론트: `frontend/js/widgets/inventory/InventoryTransfers.js`(`TYPE_META`),
    `frontend/js/widgets/inventory/InventoryKkalgyo.js`
  - API: `GET /api/inventory/overview` 중 `transfers[]`·`kkalgyo[]` 배열, `kpi.igo_*` 5카운트
  - service: `_TRANSFER_TYPES` 5종 집합, `fetch_inventory_overview` 의 `action_type` 분기와
    `igo_ss`/`igo_sw`/`igo_ws`/`igo_ww`/`igo_big` 카운트 (`backend/app/services/inventory_service.py`)
  - DB: `inventory_action_items` (`action_type IN ('transfer','transfer_ss','transfer_sw','transfer_ww','transfer_big','kkalgyo')`)
- 업무규칙:
  - **이고 유형 5종은 3곳에 흩어져 있다** — service `_TRANSFER_TYPES` 집합 / `kpi.igo_*` 카운트 분기 /
    위젯 `TYPE_META`. 유형을 추가·변경하면 **3곳 동시**에 고친다.
    (커밋 c007f60 로 `transfer_sw`(강→약)를 신설했을 때 웹워커 구코드가 `igo_sw` 키를 몰라
     API 누락이 났던 이력 — 배포 후 실제 응답 키를 확인한다.)
  - 각 유형의 방향을 라벨로 명시한다: `transfer`=약→강, `transfer_ss`=강→강, `transfer_sw`=강→약,
    `transfer_ww`=약→약, `transfer_big`=대거래처. 원칙 잔여갭 = `transfer_big` 역방향 미구현.
  - 이고 임계는 `LOGIC_PARAMS` 기준 — `SS_MIN_STOCK=5`(보내는쪽 과다), `SS_MAX_RECV_STOCK=2`(받는쪽 부족),
    `STRONG_SALES_MIN=2`(2주판매 이상=강), `WS_RECV_STOCK_LIMIT=3`, `BIG_SUP_THRESHOLD=300000`.
    화면 노출 시 하드코딩하지 말고 `params` 에서 읽는다.
  - 깔교 1그룹 = (매장, 사입처base, 상품). `bad[]`/`good[]`/`plan[]` 은 `detail_json` 원본이며
    상한은 `MAX_BAD_COLORS=3`(품목당 교환 칼라) · `MAX_QTY_PER_COLOR=4`(Good 칼라당 수량) ·
    `KKALGYO_DAYS`(매출좋은매장 14일 / 안좋은매장 21일).
  - **깔교 카운트는 그룹 수**다(행 수 아님). `kpi.kkalgyo_count` 와 화면 배지가 어긋난 사고 이력 있음 —
    변경 시 반드시 실측 대조.
  - 두 탭 모두 **읽기 전용**. 판정 산식 변경 요청이면 `inventory-data-agent` 로 넘긴다.
- 공유 자산(`_TRANSFER_TYPES`·`kpi.igo_*` 키·`inventoryShared.js`·`detail_json` 스키마) 변경이
  필요하면 메인 Claude에 보고한다(종합 탭 KPI·타 서브탭 영향).
- 피드백은 `.claude/memory/domain/inventory-feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
