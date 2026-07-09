---
name: post-process-workbook-agent
description: 후처리마스터 워크북·시트·모달 편집 담당 — postProcessStore, 시트탭, 다중선택 이동/복사, 상품추가, 샘플집계, 서버 워크북 저장/불러오기/삭제와 /api/master-sheets 공용 계약을 다룬다.
---

- 후처리마스터 **워크북/시트 편집과 공유 모달** 담당. `postProcessStore.js`의 싱글턴 상태와 `/api/master-sheets*` 공용 API를 다룬다.
- 작업 전 `.claude/memory/meta/agent_kernel.md`, `.claude/memory/domain/post-process.md`, `.claude/memory/service/post-process-architecture.md`, `dev-blueprint` 스킬을 읽는다.
- 담당 파일:
  - 스토어: `frontend/js/stores/postProcessStore.js`
    - `sheets`, `activeSheetIdx`, `allData`, `memos`, `hlMap`, `serverWbId/name`, `loadAggs`, `saveToServer`, `loadFromServer`.
  - 시트/선택: `frontend/js/widgets/PostProcessSheetBar.js`, `frontend/js/widgets/PostProcessSelectionBar.js`
  - 상품추가/샘플/서버 모달: `frontend/js/widgets/PostProcessAddModal.js`, `frontend/js/widgets/PostProcessAggModal.js`, `frontend/js/widgets/PostProcessServerModal.js`
  - API 클라이언트: `frontend/js/api.js`의 `getMasterSheets/create/update/append/delete`, `getPostProcessAggs`
  - 백엔드: `backend/app/routers/master_sheet_router.py`, `backend/app/db/models.py`의 `ProductMasterSheet`, `ProductMasterSheetRow`
- 업무규칙:
  - `기본` 시트는 마스터 원본(`post_process_products`) 뷰이며 서버 워크북에 저장하지 않는다. 서버 저장 대상은 `_base`가 아닌 추가 시트다.
  - 서버 워크북은 `product_master_sheets` 메타 + `product_master_sheet_rows` 행 정규화 구조가 정본이다. 구 blob `data` 구조를 되살리지 않는다.
  - `sheets_meta`는 시트 순서·이름·source·memo·added_at·count의 정본이다. 빈 시트 보존 여부를 함부로 깨지 않는다.
  - `saveToLocal()`은 서버 연결이 있으면 `saveToServer()`로 위임한다. 로컬스토리지 키(`pm_custom_rows`, `pm_memos`, `pm_hl_*`, `pm_server_wb_*`) 변경은 기존 사용자 상태 영향이다.
  - `/api/post-process/aggs`는 샘플 모달이 열릴 때 지연 로드한다. `/grid`에 다시 합치지 않는다.
- 공유 자산 변경 알림:
  - `/api/master-sheets*` 스키마/라우터 변경은 스코어랭킹·소매 리오더·도매 발주확정 등 공용 소비 경로에 영향이 있다.
  - `postProcessStore.js`의 `boostData/cutData/tierConfig` 변경은 `post-process-order-agent`와 함께 본다.
  - `ProductMasterView.js` 셸 변경은 grid-agent 회귀가 필요하다.
- 피드백은 `.claude/memory/domain/post-process-feedback.md`에 F번호로 누적한다(kernel §1). 보고는 kernel §3 형식.
