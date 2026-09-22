# payrate — 위임 규칙·경계 (§2 · §5)

> 본체 `SKILL.md` 에서 분리. 위임 대상을 정하거나 인접 스킬과의 경계를 판단할 때 읽는다.
> 영역 매핑(§0)과 작업 흐름(§1)은 본체에 있다.

## 2. 위임 규칙 (공유 자산 — 이 탭은 결합도가 높다)
아래를 건드리면 영향 영역을 **모두** 위임하거나 메인이 직접 조정한다(`service/payrate-architecture.md`로 범위 확인):
- **`/api/payrate/overview` 응답**(`meta`/`grand`/`stores[]`/`weekly_trend`) — payrate-data가 형태 소유, 3 서브탭이 소비. **스키마 변경 = data + 소비 서브탭 전부 회귀**.
- **`PayrateOverviewView.js` 단일 파일** — 3 프론트 에이전트가 서로 다른 `v-show` 섹션·computed 그룹만 소유. 공통부(toolbar·tab bar·`setup()` return·날짜 fetch·포맷터 `fmtPr`/`fmtWon`/`fmtAmt`) 변경은 **메인이 조정**(충돌 방지).
- **`PayrateTrendChart.js`** — 오버뷰·지급관리 공유.
- **밴딩 임계**(정본 `rebuild_payrate_db.py`) — 업무 규칙. 임의 단순화 금지.

## 5. 경계 — '지급' 3중 충돌 주의 (반드시 구분)
- **이 스킬/payrate-\*-agent** = **지급율**(`/payrate`, `PayrateOverviewView`) 탭 개발. *이 탭 안의 '지급관리' 서브탭(management)도 여기 포함*.
- **`auto-payment-agent`** = 별개 최상위 탭 **지급관리**(`/payment`, `PayrateView`) — 영수증OCR·사입처매칭·자동지급. **건드리지 않음**.
- **`md-agent`** = 지급율을 *기획 입력 축*으로 사용(주문추천·포트폴리오). 탭 개발 아님.
→ "지급율 화면/오버뷰/본사물류/역마진" → payrate · "영수증/매칭/자동지급" → auto-payment · "주문추천/무엇을 넣을지" → md-agent.
