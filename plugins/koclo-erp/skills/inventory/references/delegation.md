# inventory — 위임 규칙·경계 (§2 · §경계)

> 본체 `SKILL.md` 에서 분리. 위임 대상을 정하거나 인접 스킬과의 경계를 판단할 때 읽는다.
> 영역 매핑(§0)과 작업 흐름(§1)은 본체에 있다.

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
