---
name: inventory
description: 통합재고관리 탭 작업 라우팅. "통합재고", "통합재고관리", "inventory", "/inventory", "반품관리 탭", "이고관리", "깔교관리 탭", "진행중샘플", "60%무판매", "주간플랜", "로직표", "반품검수장", "inventory_action_items", "판정 스냅샷" 등 통합재고관리 탭/서브탭의 수정·조회·기능추가 요청 시 호출. 요청 서브탭을 식별해 전담 에이전트로 위임하고 전체 탭 회귀를 검증한다. (무엇을 반품·이고·깔교할지 결정·실행하는 업무판단은 returns-agent 소관 — §경계)
---

# 통합재고관리 탭 작업 — 라우팅 스킬

> 통합재고관리(`InventoryReportView.js`)는 9개 서브탭으로 구성된다. 이 스킬은 **메인 Claude가 따르는 절차서**다.
> 서브탭을 식별 → 전담 에이전트로 위임(Agent 도구) → 결과 통합 → 전체 탭 회귀 검증.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다(중복 서술 금지).

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

## 1. 작업 흐름

1. **요청 서브탭 식별** — 사용자 요청이 어느 서브탭(들)인지 §0 표로 판별. 불명확하면 AskUserQuestion.
2. **단일 서브탭** → 해당 에이전트 1개에 위임.
3. **여러 서브탭** → **병렬 위임**(단일 메시지에 다중 Agent 호출).
4. **결과 통합** — 각 에이전트 변경/리스크를 메인이 취합.
5. **전체 탭 회귀 검증** — §3.

## 2. 위임 규칙 (공유 자산 주의)

서브탭은 독립이 아니다. 아래 **공유 자산**을 건드리는 작업은 영향받는 서브탭 에이전트를 **모두**
위임하거나 메인이 직접 조정한다(`service/inventory-architecture.md`로 영향 범위 확인):

- **`/api/inventory/overview` 단일 응답** — 9탭 전부가 이 한 번의 fetch 로 렌더된다. 키 추가/변경/삭제는
  소비 서브탭 전부 회귀. 셸이 `meta`/`kpi`/`stores`/`returns`/`transfers`/`kkalgyo`/`samples`/`pct60`/`params`
  9키를 props 로 쪼개 내려주므로, 셸 수정은 곧 전탭 영향이다.
- **`inventoryShared.js`** — `STORE_LIST`·`useStoreTabs`·`useKeyword`·`fmtScore`·`exportRowsXlsx` 를
  반품·이고·깔교·샘플·60%·주간플랜 6탭이 공유. 수정 시 6탭 회귀.
- **`inventory_action_items.detail_json` 스키마** — 판정 5유형이 한 테이블·한 컬럼을 공유한다.
  야간 배치(`rebuild_inventory_db.judge_unified`)가 쓰고 프론트가 그대로 읽는 **무계약 JSON** 이라,
  키를 바꾸면 배치·service·위젯 3곳을 동시에 고쳐야 한다.
- **`inventory_service.LOGIC_PARAMS` 13상수** — 야간 배치 산식의 **표시용 사본**이다. 로직표 탭이 그대로
  보여주므로 배치 상수만 바꾸고 여기를 안 바꾸면 **화면이 거짓말을 한다**. 반드시 동시 수정.
- **`_TRANSFER_TYPES` 5종** — 새 이고 유형 추가 시 service 분기·`InventoryTransfers.TYPE_META`·
  kpi 카운트 3곳을 동시에. (`igo_sw` 누락 사고 이력 있음)
- **`STORES` 8매장** — service 와 `inventoryShared.STORE_LIST` 에 이중 정의. 순서까지 일치해야 한다.

단일 서브탭에 갇힌 작업(예: 60%무판매 표 컬럼 정렬만 변경)은 해당 에이전트 단독.

## 3. 회귀 검증 (dev-blueprint 스킬 §6 게이트 재사용)

- **import 스모크**(필수): `python -c "from app.routers import inventory_router"` 무에러 — 또는 배포 후
  `Application startup complete` + `/docs` 200. (`py_compile`만으론 미충족)
- **9탭 렌더**: 종합/반품관리/이고관리/깔교관리/진행중샘플/60%무판매/주간플랜/로직표/반품검수장
  전부 정상 표시, **콘솔 에러 0**.
- **인터랙션**: 날짜선택(SnapshotHistoryBar)·매장 서브탭 전환·검색·이고 유형필터·Excel 내보내기·
  주간플랜 예산 조정·반품검수장 추가/삭제 동작.
- **탭 카운트 배지**: `return_count`·`igo_count`·`kkalgyo_count`·`sample_count`·`pct60_count` 가
  각 탭 실제 행수와 일치(과거 `kkalgyo_count` 불일치 버그).
- **스냅샷 없음 경로**: 테이블 부재/빌드 전에도 500 아닌 빈 페이로드 + '스냅샷 없음' 표시 유지.
- **빌드리스 유지**(CDN Vue + ES모듈), **다른 탭 무손상**(라우팅 독립).
- 공유 자산 변경 시 §2의 교차 영향 서브탭을 실제로 다시 확인.

## 4. 작업 전 필독

- `.claude/memory/domain/inventory.md` — 업무 규칙·용어·서브탭 관계
- `.claude/memory/domain/inventory-feedback.md` — 과거 지적 누적(F1~)
- `.claude/memory/service/inventory-architecture.md` — Vue/API/DB/데이터 흐름
- `dev-blueprint` 스킬 — 탭 개발 표준(상위 규범)

## 경계 — returns-agent / sample-return / md-agent 와 혼동 금지

트리거 키워드(반품·깔교·이고·재고정리·샘플)가 정면으로 겹친다. **"탭개발 vs 업무실행"** 으로 가른다.

- **이 스킬/inventory-\*-agent** = 통합재고관리 **탭 자체**의 화면·API·DB 개발/수정.
  「탭이 안 뜬다 / 컬럼 추가 / API 응답이 틀리다 / 카운트가 안 맞는다」
- **returns-agent**(업무실행) = 무엇을 반품·이고·깔교할지 **결정하고 실행**. 사입처 반품 수용 판단,
  반품처리원장 기록, 기획→반품 이관.
- **`sample-return` 스킬** = 별개 탭(`/sample-return`). 단 **진행중샘플 판정 규칙은 두 탭이 공유**한다
  (커밋 d67ae46 에서 통합재고 판정을 샘플반납 정본 규칙에 동기화). 판정 규칙을 건드리면
  `inventory-sample-agent` 와 `sample-return-logic-agent` 를 **함께** 위임한다.
- **`.claude/memory/domain/sample-judgment-rule.md`** = 샘플 진행/종결 판정 **공용 정본**. 양쪽이 참조.
- **md-agent**(기획) = 재고 3분류를 *입력 축*으로 쓰는 주문추천·포트폴리오 결정.
