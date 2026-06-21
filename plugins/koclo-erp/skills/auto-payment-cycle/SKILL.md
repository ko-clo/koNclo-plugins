---
name: auto-payment-cycle
description: 자동지급 일일 검증 사이클. "자동지급", "지급관리", "영수증 OCR", "매칭 돌려", "자가검수", "검증 실행", "신규주문장 검증", "K5 체크" 같은 요청에 사용.
---

# 자동지급 일일 검증 사이클

## 언제 사용
사용자가 다음 같은 요청을 할 때:
- "자동지급 돌려"
- "4/9 홍대 검증해"
- "매칭 돌려봐"
- "자가검수 실행"
- "신규주문장 체크"

## 시작 전 필독
1. `~/.claude/.../memory/auto-payment.md`
2. `~/.claude/.../memory/auto-payment-feedback.md` (F1~F5 숙지)
3. `~/.claude/.../memory/auto-payment-architecture.md`

## 절대 원칙
- **일자 기준** — 사용자가 명시한 일자로만 작업 (F1)
- **장기거래원장 = 정답** — OCR이 다르면 OCR이 틀린 것 (F2)
- **사입+빈비고+양수 필터** — (F3)
- **batch xls 자동 인입 X** — (F4)
- **한국어 소통** — 기술 중간과정 노출 금지 (KERNEL 7번)

## 7단계 사이클

### 1. 일자 확인
사용자에게 일자를 확인하거나 명시된 일자 사용. 기본값 = 최신 날짜.
```bash
# 최신 거래일 확인
curl http://100.99.51.88:9000/api/payment/longterm?limit=1
```

### 2. 데이터 확인
```bash
# 해당 일자 장기거래원장 건수
# 해당 일자 OCR 결과 존재 여부
# NAS 스캔 폴더 이미지 수
```

### 3. 자가검수 실행
```bash
curl "http://100.99.51.88:9000/api/payment/agent/cross-verify?store=홍대&txn_date=2026-04-XX"
```
- 사입처 매칭률, 금액 커버리지, 자가진단 카테고리 확인
- 미매칭 원인 분류 (강제매칭 필요/영수증 누락/OCR 오인식)

### 4. 자동 매칭 추천 적용 (선택)
```bash
curl -X POST "http://100.99.51.88:9000/api/payment/agent/apply-suggestions" \
  -H "Content-Type: application/json" \
  -d '{"store":"홍대","txn_date":"2026-04-XX","min_score":0.7}'
```

### 5. 신규주문장 빌드 + 검증
```bash
curl -X POST "http://100.99.51.88:9000/api/payment/build-neworder" \
  -H "Content-Type: application/json" \
  -d '{"store":"홍대","txn_date":"2026-04-XX"}'

curl "http://100.99.51.88:9000/api/payment/neworder-verify"
```
- K5 판정, U열 등가, 샘플장기, 면제분류 확인

### 6. 검수 + 보고
형식:
```
[요청] "..." → 결과 요약
- 정답(장기거래): X개 사입처 / Y원
- OCR: X개 사입처 / Y원 / 매칭 Z%
- K5: 정상/오류
- 액션 우선순위: 1) ... 2) ... 3) ...
```

### 7. 슬랙 전송 (선택)
```bash
curl -X POST "http://100.99.51.88:9000/api/payment/neworder-verify-slack"
```

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
