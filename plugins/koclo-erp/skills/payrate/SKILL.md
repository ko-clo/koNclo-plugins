---
name: payrate
description: 지급율 관리 탭 작업 라우팅. "지급율", "지급율 관리", "payrate", "지급율 오버뷰", "본사물류", "역마진", "무매출", "고액외상", "물류거점", "주간추이 지급율" 등 지급율 탭/서브탭의 수정·조회·기능추가 요청 시 호출. 요청 영역을 식별해 전담 에이전트로 위임하고 전체 탭 회귀를 검증한다. (별개 탭 '지급관리'/자동지급은 auto-payment 담당 — §경계)
---

# 지급율 관리 탭 작업 — 라우팅 스킬

> 지급율 관리 대시보드(`PayrateOverviewView.js`, `/payrate`)는 3개 서브탭이 **단일 API 응답 1개를 공유**하는
> 모놀리식 구조다(VMD처럼 서브탭=위젯=API 1:1이 아님). 이 스킬은 **메인 Claude가 따르는 절차서**다.
> 요청 영역 식별 → 전담 범위 위임 또는 직접 수행 → 결과 통합 → 전체 탭 회귀 검증.
> 탭 개발 표준은 `dev-blueprint` 스킬을 상위 규범으로 따른다(중복 서술 금지).

작업 전에 `references/domain.md`, `references/architecture.md`, `references/feedback.md`를 읽는다.
Claude Code에서 named agent가 사용 가능하면 §0의 에이전트에 위임한다. Codex 등 named agent가
없는 런타임에서는 동일한 담당 범위를 메인 에이전트가 수행하되 파일 소유 경계를 그대로 지킨다.

## 0. 영역 ↔ 에이전트 ↔ 담당 매핑

| 영역 | 에이전트 | 담당 |
|---|---|---|
| 오버뷰 서브탭 | `payrate-overview-agent` | KPI·성별 지급율·매장별 표·주간추이·역마진/무매출. `PayrateStoreTable`·`PayrateAlertList`·`PayrateTrendChart`(공유) |
| 지급관리 서브탭 | `payrate-management-agent` | 목표대비실적·주별추이·이동평균·고액외상. `PayrateTrendChart`(공유) |
| 본사물류 서브탭 | `payrate-logistics-agent` | 물류/직거래 6지표·흐름도·본사/M)본사 지급·물류vs직거래. `logi`/`logiKpis` |
| 백엔드/데이터 | `payrate-data-agent` | 지급율 계산·SQL·`/api/payrate/overview` 응답 스키마. `payrate_service.py`·`payrate_router.py`·`rebuild_payrate_db.py`·DB·`api.js` |

공통 셸: `frontend/js/views/PayrateOverviewView.js`(단일 파일, `activeTab` v-show로 3 서브탭 전환 + 공통 toolbar/날짜/포맷터).

## 1. 작업 흐름
1. **요청 영역 식별** — §0 표로 어느 서브탭/백엔드인지 판별. 불명확하면 사용자에게 한 번 확인한다.
2. **단일 영역** → named agent 지원 시 해당 에이전트에 위임하고, 아니면 그 범위를 직접 수행한다.
3. **여러 영역** → 충돌 없는 범위만 병렬화하고 공유 파일은 메인이 단독 조정한다.
4. **결과 통합** → 5. **전체 탭 회귀 검증**(§3).

## 2. 위임 규칙 (공유 자산 — 이 탭은 결합도가 높다)
아래를 건드리면 영향 영역을 **모두** 검토하거나 메인이 직접 조정한다(`references/architecture.md`로 범위 확인):
- **`/api/payrate/overview` 응답**(`meta`/`grand`/`stores[]`/`weekly_trend`) — payrate-data가 형태 소유, 3 서브탭이 소비. **스키마 변경 = data + 소비 서브탭 전부 회귀**.
- **`PayrateOverviewView.js` 단일 파일** — 3 프론트 에이전트가 서로 다른 `v-show` 섹션·computed 그룹만 소유. 공통부(toolbar·tab bar·`setup()` return·날짜 fetch·포맷터 `fmtPr`/`fmtWon`/`fmtAmt`) 변경은 **메인이 조정**(충돌 방지).
- **`PayrateTrendChart.js`** — 오버뷰·지급관리 공유.
- **밴딩 임계**(정본 `rebuild_payrate_db.py`) — 업무 규칙. 임의 단순화 금지.

## 3. 회귀 검증 (dev-blueprint 스킬 §6 게이트 재사용)
- **import 스모크**(필수): `python -c "from app.routers import payrate_router"` 무에러 — 또는 배포 후 `Application startup complete` + `/docs` 200.
- **3 서브탭 렌더**: 오버뷰/지급관리/본사물류 전부 정상, **콘솔 에러 0**.
- **인터랙션**: 기간(From/To·전체기간)·매장 select·탭 전환·차트 갱신.
- **데이터 정합**: 분자(지급)·분모(매출) **동일 기간**(0% 사건 방지), 밴딩 임계가 정본과 일치.
- **빌드리스 유지**·**다른 탭 무손상**.

## 4. 작업 전 필독
- `references/domain.md` — 업무 규칙·용어·서브탭 관계
- `references/architecture.md` — 파일/API/DB/데이터 흐름
- `references/feedback.md` — 누적 피드백과 반복 방지 규칙
- `dev-blueprint` 스킬 — 탭 개발 표준

## 5. 경계 — '지급' 3중 충돌 주의 (반드시 구분)
- **이 스킬/payrate-\*-agent** = **지급율**(`/payrate`, `PayrateOverviewView`) 탭 개발. *이 탭 안의 '지급관리' 서브탭(management)도 여기 포함*.
- **`auto-payment-agent`** = 별개 최상위 탭 **지급관리**(`/payment`, `PayrateView`) — 영수증OCR·사입처매칭·자동지급. **건드리지 않음**.
- **`md-agent`** = 지급율을 *기획 입력 축*으로 사용(주문추천·포트폴리오). 탭 개발 아님.
→ "지급율 화면/오버뷰/본사물류/역마진" → payrate · "영수증/매칭/자동지급" → auto-payment · "주문추천/무엇을 넣을지" → md-agent.
