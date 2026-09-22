# order-cycle — 실패-해결 매핑

> 본체 `SKILL.md` 에서 분리. 빌드가 실패했을 때에 읽는다.

## 실패-해결 매핑 (이번 세션 겪은 것만)

| 증상 | 원인 | 해결 |
|---|---|---|
| 누락주문분 0건 | detect_missed_orders 버그 | 두 CSV 직접 비교 복구 스크립트 (F9, F12) |
| 경로 안 보임 | backend/reports 버그 (F10) | CACHE_DIR=`Z:/자동주문/cache` 설정 |
| xlwt ModuleNotFoundError | pip 경로 | `python3 -m pip install xlwt` |
| Supabase 500 에러 | date filter 금지 | 전체 페이징 + client filter (reference_supabase_koclo.md) |
| 증분 파일 DB 안 들어감 | 크론 대기 | 수동 `ingest_incremental.py` |
| 04-12 누락분 섞임 | 쿼리 범위 잘못 (F8) | `txn_date = TO_DATE-1`만 |
| 샘플 반품완료분 포함 | sample_ledger만 조회 (F15) | `sample_products.notes ~ '반\s*\d'` 제외 |
| 09 홍대 xls Permission | 엑셀 열려있음 | 파일 닫기, 다시 실행 |
| **CSV vs DB SKU 차이 (F17)** | products size/color NULL 매칭 실패 | `(size IS NULL OR size='' OR size=%s)` fallback 적용 + processed list에서 파일 제거 후 재인입 |
| 매장별 판매 SKU 수가 CSV보다 적음 | 동일 NULL 버그 | 각 매장 CSV와 sales_daily count 비교 검증 필수 |
| **미송 전부 0 (파일은 있는데)** | 통합주문 CSV에 `참조재고` 등 컬럼 삽입(col8) → 수량컬럼 col14→col15 밀림 → `validate_layout`이 전매장 스킵(F18) | 통합주문 헤더 첫 `수량` 컬럼이 col14인지 사전점검(`/order-manual`이 자동검사). 밀렸으면 삽입컬럼 제거(24컬럼 복원) 후 `nas_manual_order.sh {date}` 재실행. 근본대책=`backorder_merge.py`를 `수량`블록 상대오프셋으로 수정 |
