# sample-return — 영역 ↔ 에이전트 ↔ 파일 매핑 (§0)

> 본체 `SKILL.md` 에서 분리. 어느 에이전트에 맡길지 고를 때에 읽는다.

## 0. 영역 ↔ 에이전트 ↔ 파일 매핑

| # | 영역 | 에이전트 | 프론트 | API | DB |
|---|---|---|---|---|---|
| 0 | 셸 · 리포트 상단 | `sample-return-report-agent` | `SampleReturnView.js`(3모드·시뮬박스·전체핵심지표·통합엑셀 2종·이미지모달), `SampleReturnSummary.js`(데이터 뷰), `SampleReturnCompare.js`(매장간 비교) | `GET /api/sample-return/data`, `GET`·`PATCH /sim-settings` | `sample_return_sim_settings` |
| 1 | 매장 상세 | `sample-return-store-agent` | `SampleReturnStore.js` — 매장 KPI + 5서브탭(샘플집계명 상세 / 반납대상 / 집계샘플 / 상품 상세 / 반품집계) + 정렬 + 엑셀 2종 + 배치 폴더 저장 | `POST /api/sample-return/export-batch` | — (`.cache/batch/sample_return/<YYYYMMDD>/<매장명>/`) |
| 2 | 판정 정본 | `sample-return-logic-agent` | `sampleReturnLogic.js` — `classifyItem`/`classifyStore`/`computeCutoff`/`storeSummary`/`buildProductDetail`/`grandTotals`/컬러규칙 | — | — |
| 3 | 백엔드 파이프라인 | `sample-return-data-agent` | — | `/api/sample-return` 4엔드포인트 전체 | 11테이블(§아키텍처) + `rebuild_sample_return_db.py`·`run_sample_return_batch.py` |

공통 셸: `frontend/js/views/SampleReturnView.js` · `frontend/js/views/SnapshotHistoryBar.js`(교차추천 모드) ·
`frontend/js/api.js`(sample-return 메서드 4개).
공통 백엔드: `backend/app/routers/sample_return_router.py` · `backend/app/services/sample_return_service.py`(1544L) ·
`backend/app/services/sample_return_export_service.py`.
