---
name: auto-payment-cycle
description: Use when 자동지급 일일 검증 사이클 요청을 받았을 때. 트리거 — "자동지급", "지급관리", "영수증 OCR", "매칭 돌려", "자가검수", "검증 실행", "신규주문장 검증", "K5 체크".
---

# 자동지급 일일 검증 사이클

## 읽을 파일

절 번호는 고정 ID(다른 스킬이 인용). 경로 기준 `.claude/skills/auto-payment-cycle/`.

| 파일 | 절 | 읽는 시점 |
|---|---|---|
| `references/cycle.md` |  | 사이클을 실제로 돌릴 때 |

## 언제 사용
사용자가 다음 같은 요청을 할 때:
- "자동지급 돌려"
- "4/9 홍대 검증해"
- "매칭 돌려봐"
- "자가검수 실행"
- "신규주문장 체크"

## 시작 전 필독
1. `.claude/memory/domain/auto-payment.md`
2. `.claude/memory/domain/auto-payment-feedback.md` (F1~ 전부 숙지 — 계속 늘어난다)
3. `.claude/memory/service/auto-payment-architecture.md`

## 절대 원칙
- **일자 기준** — 사용자가 명시한 일자로만 작업 (F1)
- **장기거래원장 = 정답** — OCR이 다르면 OCR이 틀린 것 (F2)
- **사입+빈비고+양수 필터** — (F3)
- **batch xls 자동 인입 X** — (F4)
- **한국어 소통** — 기술 중간과정 노출 금지 (KERNEL 7번)

## 7단계 사이클

→ `references/cycle.md`.

## 사이클 후 학습

이번 사이클에서:
- 실패한 단계가 있었는가?
- 사용자 피드백이 있었는가?
- 새로 발견한 데이터 이슈가 있는가?

있으면 **즉시** `domain/auto-payment-feedback.md`에 새 항목 추가 (F번호 증가).

## 빠른 실행
```bash
# 한 줄로 전체 사이클 (4/9 홍대):
curl -s "http://100.99.51.88:9000/api/payment/agent/cross-verify?store=%ED%99%8D%EB%8C%80&txn_date=2026-04-09" | python3 -c "import sys,json;d=json.load(sys.stdin);s=d['summary'];print(f'사입처:{s[\"sup_match_rate\"]}% 금액:{s[\"amount_coverage\"]}% 미매칭:{s[\"ocr_only\"]+s[\"janggi_only\"]}곳')"
```
