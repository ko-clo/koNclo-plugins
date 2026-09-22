# inventory — 영역 ↔ 에이전트 ↔ 파일 매핑 (§0)

> 본체 `SKILL.md` 에서 분리. 어느 에이전트에 맡길지 고를 때에 읽는다.

## 0. 서브탭 ↔ 에이전트 ↔ 파일 매핑

| # | 서브탭 | 에이전트 | 프론트 | API | DB |
|---|---|---|---|---|---|
| 0·7 | 종합 · 로직표 | `inventory-summary-agent` | `InventorySummary.js`, `InventoryLogicTable.js` | `GET /api/inventory/overview` → `kpi`·`stores`·`params` | `inventory_snapshots`(`meta_json`: stats/store_tiers/store_cutoffs) |
| 1·5 | 반품관리 · 60%무판매 | `inventory-returns-agent` | `InventoryReturns.js`, `InventoryPct60.js` | overview → `returns[]`·`pct60[]` | `inventory_action_items` (`action_type='return'`·`'pct60'`) |
| 2·3 | 이고관리 · 깔교관리 | `inventory-transfer-agent` | `InventoryTransfers.js`, `InventoryKkalgyo.js` | overview → `transfers[]`·`kkalgyo[]` | `inventory_action_items` (`transfer`/`_ss`/`_sw`/`_ww`/`_big`, `kkalgyo`) |
| 4 | 진행중샘플 | `inventory-sample-agent` | `InventorySamples.js` | overview → `samples[]` | `inventory_action_items` (`sample`) |
| 6·8 | 주간플랜 · 반품검수장 | `inventory-plan-agent` | `InventoryWeeklyPlan.js`, `InventoryInspection.js` | `GET`·`POST`·`DELETE /api/inventory/inspection` (**탭 유일 쓰기**) | `returns_blocked_suppliers`, `returns_rejected_items`, `returns_shipped` |
| — | 백엔드 파이프라인 | `inventory-data-agent` | — | 4엔드포인트 전체 | 위 5테이블 + 야간 빌드 `rebuild_inventory_db.py` |

공통 셸: `frontend/js/views/InventoryReportView.js`(탭 라우팅·단일 fetch·loading) ·
`frontend/js/views/SnapshotHistoryBar.js`(날짜 선택) · `frontend/js/widgets/inventory/inventoryShared.js`(공용 헬퍼) ·
`frontend/js/api.js`(inventory 메서드 4개).
공통 백엔드: `backend/app/routers/inventory_router.py` · `backend/app/services/inventory_service.py`.
