# post-process — 위임 규칙·경계 (§2 · §경계)

> 본체 `SKILL.md` 에서 분리. 위임 대상을 정하거나 인접 스킬과의 경계를 판단할 때 읽는다.
> 영역 매핑(§0)과 작업 흐름(§1)은 본체에 있다.

## 2. 위임 규칙 (공유 자산 주의)

- **`/api/post-process/grid` 응답 계약**: `meta.pkl_date`, `meta.gen_time`, `products[]`는 `toRows()`와 `postProcessStore.init()`가 직접 소비한다. `gen_time`은 하이라이트/버전 캐시 키라 요청마다 바뀌면 안 된다.
- **기본 시트 원칙**: `기본` 시트는 `post_process_products`에서 재생성되는 읽기전용 원본이며 서버 워크북에 저장하지 않는다. 서버에는 추가 시트만 저장한다.
- **스토어 싱글턴**: `postProcessStore.js`는 그리드, 시트, 샘플, 증가/차감이 공유한다. 상태 키·저장 함수 변경은 grid/workbook/order 회귀가 필요하다.
- **마스터시트 공용 API**: `/api/master-sheets*`는 후처리마스터뿐 아니라 스코어랭킹, 소매 리오더 등도 소비한다. 라우터/스키마 변경은 공용 회귀 대상이다.
- **샘플집계 지연 로드**: `/grid`는 `agg_list: []`를 반환하고, `PostProcessAggModal`만 `/aggs`를 호출한다. `/aggs`는 무거운 `build_master_data` 경로라 운영 게이트를 확인한다.
- **프리컴퓨트/캐시**: `post_process_products`는 야간 배치 스냅샷이다. `POST /cache/clear`는 in-process cache뿐 아니라 스냅샷 테이블을 비우는 운영성 동작이므로 신중히 다룬다.
- **DB direct 경량 경로**: 비운영 스택은 `use_db_direct()` 경로로 `/grid`를 볼 수 있다. 운영 골든 경로와 산출 shape가 같아야 한다.
- **레거시 정본**: `rebuild_post_process_db.py`는 이식 기준/대조 경로다. 신규 화면은 HTML을 굽지 않고 Vue + JSON 경로를 쓴다.

## 경계 — score-ranking / retail-reorder / order-agent / best-* 와 혼동 금지

- **post-process-\*-agent** = `/post-process` 탭 자체의 그리드, 워크북, 샘플, 증가/차감, 데이터/캐시 경로.
- **score-ranking-\*-agent** = 스코어랭킹 탭과 후처리 워크북으로 보내는 선택 UI. `/api/master-sheets*` 소비는 공유지만 소관은 다르다.
- **retail-reorder-\*-agent** = 소매 리오더 화면에서 상품마스터/주문장 결과를 소비하는 경로.
- **best-\*-agent** = 베스트상품 탭 정본 계산·화면.
- **order-agent** = 실제 주문장 생성 산식·xls 생성·검수·배포 운영. 후처리 증가/차감 시트 append가 곧 실제 발주는 아니다.
