# order-audit — 시스템 구분 (혼동 주의)

> 본체 `SKILL.md` 에서 분리. 어느 산출물인지 가릴 때에 읽는다.

## 시스템 구분 (혼동 주의)

`order_paper/old` 같은 비교 대상이 **현재 시스템의 이전 빌드가 아닐 수 있음**.

| | 현재 (koclo-erp) | 레거시 (koclo-erp-legacy) |
|---|---|---|
| DB | `KOCLO_ERP_DB_DSN` (testerp/_dev, **pm_suppliers 정규화**) | `TESTERP_DB_DSN`(5434, `products.supplier_name` 직접) |
| 사입처 조회 | `LEFT JOIN pm_suppliers s ON s.id=p.supplier_id`, `GROUP BY s.name` | `p.supplier_name` 직접 |
| 미송 병합 | xls write 직전 병합 있음 | 없음 |
| 안전재고·기본주문·상위5% 강화 코드 | **두 시스템 동일** | **동일** |

→ 두 산출물 비교 시 **어느 시스템/DB 산출인지 먼저 확정**. 코드가 같아도 DB가 다르면
모집단·점수 분포가 달라 `gc`·강화 결과가 갈린다.

---
