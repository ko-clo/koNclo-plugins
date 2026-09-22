# sample-return — 위임 규칙·경계 (§2 · §경계)

> 본체 `SKILL.md` 에서 분리. 위임 대상을 정하거나 인접 스킬과의 경계를 판단할 때 읽는다.
> 영역 매핑(§0)과 작업 흐름(§1)은 본체에 있다.

## 2. 위임 규칙 (공유 자산 주의)

영역은 독립이 아니다. 아래 **공유 자산**을 건드리는 작업은 영향받는 에이전트를 **모두** 위임하거나
메인이 직접 조정한다(`service/sample-return-architecture.md`로 영향 범위 확인):

- **판정 정본 이중화(JS ↔ py)** — 반납 판정은 `sampleReturnLogic.js`(프론트 라이브 재계산)와
  `sample_return_service.py`(원자재 산출·경과일·점수)에 **2곳으로 나뉘어 있다**. 기한·과락·무판매·교차
  규칙을 바꾸면 **양쪽을 동시에** 고쳐야 한다(커밋 347bfe6 기한초과 게이트 개정 = 이 사고 지점).
  → 반드시 `sample-return-logic-agent` + `sample-return-data-agent` 동시 위임.
- **`sampleReturnLogic.js` 순수함수** — `classifyStore`는 셸이, `storeSummary`/`grandTotals`는 셸+Compare가,
  `buildProductDetail`은 셸(통합엑셀)+Store(상품상세)가 소비한다. 시그니처·반환키 변경은 4파일 회귀.
- **`appliedSim` 4파라미터**(`fWeeks`/`mWeeks`/`scoreCut`/`crossMin`, 기본 여21·남28·컷30·교차2) —
  셸이 소유하고 Store·Compare 에 props 로 내려간다. DB(`sample_return_sim_settings`)에도 영속된다.
  파라미터 추가는 프론트 3곳 + service `_SIM_FIELDS`/`_SIM_BOUNDS` + DDL 을 동시에.
- **`items._checked` 라이브 상태** — 매장별 체크가 `report` 배열의 원본 item 에 직접 붙는다.
  전체 핵심지표·매장간 비교·집계기준 통합엑셀이 전부 이걸 읽는다. 체크 모델 변경은 전 영역 회귀.
  (⚠ 상품상세 개별 토글은 `SampleReturnStore` **로컬 휘발성** — 통합엑셀은 기본 분류 기준 산출.
   의도된 설계이며 UI 라벨로 명시돼 있다. 승격 시도 전 `SampleReturnStore.js` 주석 FIX⑥ 필독.)
- **`sample_ledger` + `sample_products` LATERAL 매칭** — `sample_products` 는 period 마다 누적 INSERT 라
  **최신 1건만** 취해야 한다. 정본 규칙 = `.claude/memory/domain/sample-judgment-rule.md`.
- **`_RESULT_CACHE` 데이터 버전 스탬프** — 라이브 스코어가 무거워(매장별 수십초) 입력 테이블 최신도로
  캐시한다. 새 입력 테이블을 참조하면 `_data_version_stamp` 에도 추가해야 stale 이 안 난다.

단일 영역에 갇힌 작업(예: 매장간 비교표 색상만 변경)은 해당 에이전트 단독.

## 경계 — returns-agent / inventory / md-agent 와 혼동 금지

트리거 키워드(반납·반품·샘플)가 겹친다. **"탭개발 vs 업무실행"** 으로 가른다.

- **이 스킬/sample-return-\*-agent** = 샘플반납 **탭 자체**의 화면·API·DB 개발/수정.
  「탭이 안 뜬다 / 컬럼 추가 / 반납대상이 0건이다 / 엑셀이 틀리다」
- **returns-agent**(업무실행) = 실제로 무엇을 반납·반품할지 **결정하고 실행**, 반품처리원장 기록.
- **`inventory` 스킬** = 별개 탭(`/inventory`) 통합재고관리. 단 **`진행중샘플` 판정 규칙은 공유** —
  판정을 건드리면 `inventory-sample-agent` 를 **함께** 위임한다.
- **`샘플교차추천`·`샘플오버뷰`** 는 별개 탭이다. 이 탭의 `교차추천` 모드는 그 스냅샷 HTML 을
  iframe 으로 얹은 것뿐이라, 내용 수정 요청은 `generate_sample_cross_report.py` 쪽 별건이다.
- **md-agent**(기획) = 샘플을 *입력 축*으로 쓰는 주문추천·포트폴리오 결정.
