# wholesale-reorder — 위임 규칙·경계 (§2 · §경계)

> 본체 `SKILL.md` 에서 분리. 위임 대상을 정하거나 인접 스킬과의 경계를 판단할 때 읽는다.
> 영역 매핑(§0)과 작업 흐름(§1)은 본체에 있다.

## 2. 위임 규칙 (공유 자산 주의)

영역은 독립이 아니다. 아래 **공유 자산**을 건드리는 작업은 영향받는 에이전트를 **모두** 위임하거나 메인이 직접 조정한다(`service/wholesale-reorder-architecture.md`로 영향 범위 확인):

- **`compute_data` payload 키**(`cards`/`variants`·`orders`·`actions`·`action_plan`·`kpis`·`source_audit{coverage,self_check}`·`external`) — report/action 이 소비, data-agent 가 owner. 키 추가/변경은 양쪽 회귀.
- **`wholesale_report_snapshots` 스키마**(payload JSON) — refresh 가 쓰고 overview 가 읽음. compute_data 출력 변경은 refresh·overview·프론트 동시 영향.
- **`db_adapters.enable_db_adapters` 스왑 + `ingest`** — batch(2-A)·워크북(2-B)을 DB-읽기로 교체. 어댑터/인입 변경은 산식 파리티(`_vendor` 원본과 1:1) 유지 확인.
- **`_vendor` 빌더**(`build_reorder_fresh`·`build_wholesale_reorder_latest`·`build_frontend_locked`·`self_check`) — PRD 정본. 산식 변경은 빌더 재복사이며 data-agent가 파리티 검증. 임의 수정 금지.
- **`WholesaleView.js` 공통 셸**(소스필터·키워드섹션·visibleSections·actionsOf) — report/action 공유. 섹션 구조·필터 변경은 둘 다 확인.

단일 영역에 갇힌 작업(예: 카드 셀 라벨만 변경)은 해당 에이전트 단독.

## 경계 — batch-ingest / _vendor / order-agent 와 혼동 금지

- **이 스킬/wholesale-reorder-\*-agent** = 도매 리오더 **탭 자체**의 화면(WholesaleView.js)·조회 API·compute/serialize·어댑터 개발.
- **batch-ingest 스킬 / 운영** = batch CSV(2-A) → DB 인입 **배치·cron 운영**(`rebuild_wholesale_*_db.py` + `nas_*_ingest.sh`). "도매 batch 인입/cron" → batch-ingest.
- **`_vendor` 빌더 산식** = PRD 정본(`build_reorder_fresh`). 산식 자체 변경은 빌더 재복사·파리티 검증 — 임의 수정 금지.
- **vmd-data / payrate-data** = 본사/매장 데이터의 정본 집계 service(이 탭은 `collect_bonsa_db`로 testerp DB 직접 쿼리 — 그 service 미사용).
- "탭 화면/조회 API/어댑터 수정" → 이 스킬. "batch 인입·cron" → batch-ingest. "빌더 산식 정본" → _vendor 재복사.
