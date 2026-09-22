# auto-payment-cycle — 7단계 사이클 상세

> 본체 `SKILL.md` 에서 분리. 사이클을 실제로 돌릴 때에 읽는다.

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
