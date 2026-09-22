---
name: order-cycle
description: Use when TESTERP 주문장을 일일 생성할 때. 트리거 — "주문장 만들어", "오늘 주문장", "auto_order".
---

# 주문 사이클 스킬

**필독**: `domain/order.md` + `domain/order-feedback.md` + `service/order-architecture.md`

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/order-cycle/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/troubleshooting.md` |  | 빌드가 실패했을 때 |

## 명령어 템플릿

> DB 접속 문자열은 컨테이너 env `KOCLO_ERP_DB_DSN` 을 상속한다(`docker-compose.yml` 이 주입 — 스크립트가
> `os.environ["KOCLO_ERP_DB_DSN"]` 로 읽는다). **명령줄·문서에 접속 문자열과 비밀번호를 적지 않는다.**

### 증분 수동 인입
```bash
docker exec -e APP_BASE=/app koclo_erp-app python3 /app/scripts/ingest_incremental.py
```

### 주문장 빌드 + xls 추출
```bash
docker exec -e APP_BASE=/app -e USE_DB=1 koclo_erp-app python3 /app/scripts/auto_order_db.py --date $(date +%Y%m%d)
```

### 강제 재빌드 (기존 HTML 무시)
```bash
docker exec -e APP_BASE=/app -e USE_DB=1 koclo_erp-app python3 /app/scripts/order_v8_2_rebuild_FULL.py --from $(date +%Y-%m-%d) --to $(date +%Y-%m-%d)
```

## 점검 SQL 3개

```sql
-- 오늘 매출 8매장 (sales_daily.txn_date 는 varchar 라 date 로 바꿔 비교한다)
SELECT store_id, count(*), sum(quantity) FROM sales_daily WHERE NULLIF(txn_date::text, '')::date = CURRENT_DATE GROUP BY store_id ORDER BY store_id;

-- 현재고 최신 mtime
SELECT store_id, max(imported_at) FROM inventory_snapshot GROUP BY store_id;  -- 현재고 레지스터(구 purchase_data)

-- 어제 누락주문분
SELECT count(*), sum(delta) FROM missed_orders WHERE txn_date=CURRENT_DATE-1;
```

## 실패-해결 매핑 (이번 세션 겪은 것만)

→ `references/troubleshooting.md`.

## 절대 원칙

1. ERP v4 6열 양식 (`사입처명/품명/칼라/사이즈/수량/비고`)
2. 출력 경로 `Z:\자동주문\cache\주문장_업로드\주문장_YYYYMMDD\` (F14)
   - 완료/업로드 판정은 `*_order.xls` 8개 기준
   - MCP 다운로드 요청은 `ensure_order_file`로 이 산출 경로의 `.xls` 파일을 생성/갱신한다
3. 누락주문분 TO_DATE-1일만 (F8)
4. 반품 완료 샘플 제외 (F15)
5. 새 피드백은 F번호 즉시 추가 (domain/order-feedback.md)
