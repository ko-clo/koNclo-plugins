---
name: order-cycle
description: TESTERP 주문장 일일 생성 — "주문장 만들어" "오늘 주문장" "auto_order" 키워드 매칭. 명령어 템플릿 + 실패-해결 매핑 + 점검 SQL
---

# 주문 사이클 스킬

**필독**: `domain/order.md` + `domain/order-feedback.md` + `service/order-architecture.md`

## 명령어 템플릿

### 증분 수동 인입
```bash
docker exec -e APP_BASE=/app -e TESTERP_DB_DSN='host=localhost port=5434 dbname=testerp user=testerp password=testerp2026' testerp-app python3 /app/scripts/ingest_incremental.py
```

### 주문장 빌드 + xls 추출
```bash
docker exec -e APP_BASE=/app -e USE_DB=1 -e TESTERP_DB_DSN='host=localhost port=5434 dbname=testerp user=testerp password=testerp2026' testerp-app python3 /app/scripts/auto_order_db.py --date $(date +%Y%m%d)
```

### 강제 재빌드 (기존 HTML 무시)
```bash
docker exec -e APP_BASE=/app -e USE_DB=1 -e TESTERP_DB_DSN='...' testerp-app python3 /app/scripts/order_v8_2_rebuild_FULL.py --from $(date +%Y-%m-%d) --to $(date +%Y-%m-%d)
```

## 점검 SQL 3개

```sql
-- 오늘 매출 8매장
SELECT store_id, count(*), sum(quantity) FROM sales_daily WHERE txn_date=CURRENT_DATE GROUP BY store_id ORDER BY store_id;

-- 현재고 최신 mtime
SELECT store_id, max(imported_at) FROM purchase_data GROUP BY store_id;

-- 어제 누락주문분
SELECT count(*), sum(delta) FROM missed_orders WHERE txn_date=CURRENT_DATE-1;
```

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

## 절대 원칙

1. ERP v4 6열 양식 (`사입처명/품명/칼라/사이즈/수량/비고`)
2. 출력 경로 `Z:\자동주문\cache\주문장_업로드\주문장_YYYYMMDD\` (F14)
   - 완료/업로드 판정은 `*_order.xls` 8개 기준
   - MCP 다운로드 요청은 `ensure_order_file`로 이 산출 경로의 `.xls` 파일을 생성/갱신한다
3. 누락주문분 TO_DATE-1일만 (F8)
4. 반품 완료 샘플 제외 (F15)
5. 새 피드백은 F번호 즉시 추가 (domain/order-feedback.md)
