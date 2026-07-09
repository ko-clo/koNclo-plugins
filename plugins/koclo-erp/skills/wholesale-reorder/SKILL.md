---
name: wholesale-reorder
description: 도매 리오더 탭 작업 라우팅. "도매리오더", "도매 리오더", "wholesale-reorder", "도매 탭", "리오더 카드", "분배", "이고", "회수", "실행지시 엑셀", "풀 재계산", "워크북 인입", "원천점검", "도매외부", "코스/본사 소스탭", "기주문 추적" 등 도매 리오더 탭/영역의 수정·조회·기능추가 요청 시 호출. 요청 영역을 식별해 전담 에이전트로 위임하고 전체 탭 회귀를 검증한다. (batch CSV *인입·cron 운영*은 batch-ingest, _vendor 빌더 *산식*은 PRD 정본 — §경계)
---

# 도매 리오더 탭 작업 — 라우팅 스킬

> 도매 리오더(`WholesaleView.js`)는 **단일 탭**(서브탭 없음)이며 **리포트·카드 표시 · 액션·재계산 · 데이터 파이프라인** 세 영역으로 본다.
> 이 스킬은 **메인 Claude가 따르는 절차서**다: 영역 식별 → 전담 에이전트 위임(Agent 도구) → 결과 통합 → 전체 탭 회귀 검증.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다(중복 서술 금지).

## 0. 영역 ↔ 에이전트 ↔ 파일 매핑

| # | 영역 | 에이전트 | 프론트 | API | DB/service |
|---|---|---|---|---|---|
| 0 | 리포트·카드 | `wholesale-reorder-report-agent` | `WholesaleView.js`·`WholesaleCard.js`(소스필터·키워드섹션·KPI·기주문추적·도매외부·원천점검) | `GET /api/wholesale/overview`·`/image` | `filter_overview`(소스필터) / `card_public`·`variant_public`·`order_public` |
| 1 | 액션·재계산 | `wholesale-reorder-action-agent` | `WholesaleView.js`(매장 이동·정리 섹션·다운로드·재계산 버튼·발주확정) | `POST /api/wholesale/refresh`·`GET /api/wholesale/action-plan.xlsx`·`POST /api/wholesale/reorder` | `refresh_snapshot`·`_ingest_then_compute`·`ingest_workbook` / `action_public`·`build_actions` |
| 2 | 데이터 파이프라인 | `wholesale-reorder-data-agent` | — (백엔드 owner) | `wholesale_router` 전체 | `wholesale_service`·`wholesale/compute_data`·`db_adapters`·`ingest`·`serialize`·`_vendor` 빌더·스냅샷 스키마 |

공통 셸: `frontend/js/views/WholesaleView.js`(소스탭·키워드섹션·액션·원천점검) · `frontend/js/widgets/WholesaleCard.js` · `frontend/js/api.js`(wholesale 메서드).
공통 백엔드: `backend/app/routers/wholesale_router.py` · `backend/app/services/wholesale_service.py` · `backend/app/services/wholesale/`(compute_data·db_adapters·ingest·serialize·_vendor).
`_vendor/`(build_reorder_fresh 등)은 **PRD 빌더 100% 원본** — 산식 변경은 재복사 동기화이며 임의 수정 금지(§경계).

## 1. 작업 흐름

1. **요청 영역 식별** — 사용자 요청이 어느 영역(들)인지 §0 표로 판별. 불명확하면 AskUserQuestion.
2. **단일 영역** → 해당 에이전트 1개에 위임.
3. **여러 영역** → **병렬 위임**(단일 메시지에 다중 Agent 호출).
4. **결과 통합** — 각 에이전트 변경/리스크를 메인이 취합.
5. **전체 탭 회귀 검증** — §3.

## 2. 위임 규칙 (공유 자산 주의)

영역은 독립이 아니다. 아래 **공유 자산**을 건드리는 작업은 영향받는 에이전트를 **모두** 위임하거나 메인이 직접 조정한다(`service/wholesale-reorder-architecture.md`로 영향 범위 확인):

- **`compute_data` payload 키**(`cards`/`variants`·`orders`·`actions`·`action_plan`·`kpis`·`source_audit{coverage,self_check}`·`external`) — report/action 이 소비, data-agent 가 owner. 키 추가/변경은 양쪽 회귀.
- **`wholesale_report_snapshots` 스키마**(payload JSON) — refresh 가 쓰고 overview 가 읽음. compute_data 출력 변경은 refresh·overview·프론트 동시 영향.
- **`db_adapters.enable_db_adapters` 스왑 + `ingest`** — batch(2-A)·워크북(2-B)을 DB-읽기로 교체. 어댑터/인입 변경은 산식 파리티(`_vendor` 원본과 1:1) 유지 확인.
- **`_vendor` 빌더**(`build_reorder_fresh`·`build_wholesale_reorder_latest`·`build_frontend_locked`·`self_check`) — PRD 정본. 산식 변경은 빌더 재복사이며 data-agent가 파리티 검증. 임의 수정 금지.
- **`WholesaleView.js` 공통 셸**(소스필터·키워드섹션·visibleSections·actionsOf) — report/action 공유. 섹션 구조·필터 변경은 둘 다 확인.

단일 영역에 갇힌 작업(예: 카드 셀 라벨만 변경)은 해당 에이전트 단독.

## 3. 회귀 검증 (dev-blueprint 스킬 §6 게이트 재사용)

- **import 스모크**(필수): `python -c "from app.routers import wholesale_router"` 무에러 — 또는 배포 후 `Application startup complete` + `/docs` 200. (`py_compile`만으론 미충족) · compute 검증은 `compute_report_data(False)` 직접 호출(dev DB는 `TESTERP_DB_NAME=testerp_dev` 오버라이드 — prod 미접근).
- **탭 렌더**: 소스탭(ALL/코스/본사)·키워드섹션(리오더/후보/확장/소진/정상)·매장 이동·정리·기주문추적·도매외부·원천점검(coverage/self_check) 전부 정상, **콘솔 에러 0**.
- **인터랙션**: 풀 재계산 폴링·스피너·발주확정·실행지시 엑셀 다운로드·소스필터·키워드 KPI 필터·섹션 스크롤·이미지 로드.
- **빌드리스 유지**(CDN Vue + ES모듈), **다른 탭 무손상**(라우팅 독립).
- 공유 자산 변경 시 §2의 교차 영향 영역을 실제로 다시 확인. `_vendor` 산식 변경 시 self_check PASS·golden 대조.

## 4. 작업 전 필독

- `.claude/memory/domain/wholesale-reorder.md` — 업무 규칙·용어·영역 관계·경계
- `.claude/memory/domain/wholesale-reorder-feedback.md` — 누적 피드백(F1~)
- `.claude/memory/service/wholesale-reorder-architecture.md` — Vue/API/DB/데이터 흐름
- `dev-blueprint` 스킬 — 탭 개발 표준(상위 규범)

## 경계 — batch-ingest / _vendor / order-agent 와 혼동 금지

- **이 스킬/wholesale-reorder-\*-agent** = 도매 리오더 **탭 자체**의 화면(WholesaleView.js)·조회 API·compute/serialize·어댑터 개발.
- **batch-ingest 스킬 / 운영** = batch CSV(2-A) → DB 인입 **배치·cron 운영**(`rebuild_wholesale_*_db.py` + `nas_*_ingest.sh`). "도매 batch 인입/cron" → batch-ingest.
- **`_vendor` 빌더 산식** = PRD 정본(`build_reorder_fresh`). 산식 자체 변경은 빌더 재복사·파리티 검증 — 임의 수정 금지.
- **vmd-data / payrate-data** = 본사/매장 데이터의 정본 집계 service(이 탭은 `collect_bonsa_db`로 testerp DB 직접 쿼리 — 그 service 미사용).
- "탭 화면/조회 API/어댑터 수정" → 이 스킬. "batch 인입·cron" → batch-ingest. "빌더 산식 정본" → _vendor 재복사.
