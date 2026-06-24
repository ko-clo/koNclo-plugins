---
description: 새 CSV→DB 인입 배치 생성 표준 (ingest_all 단계 + nas_*_ingest.sh + DDL). 질문 먼저 → 정본 패턴대로 구현·테스트
argument-hint: "[자유서술 요구사항 | 비우면 질문부터]"
---
사용자가 `/batch-ingest $ARGUMENTS` 를 실행했다. **새 CSV→DB 인입 배치**를 이 레포의 정본
패턴대로 만든다. 정본 구현 = `backend/scripts/ingest_all.py::ingest_returns_ledger` +
`backend/scripts/nas_returns_ingest.sh` + `backend/scripts/sql/create_returns_ledger.sql`
(반품처리원장 배치). 이 셋을 항상 본보기로 재사용한다.

## 0. 절대 원칙
- **구현 전 반드시 아래 질문을 먼저** 한다(인자에 답이 없으면). 모호한 채로 코드 쓰지 않는다.
- `.claude/` 수정이므로 **koNclo-plugins 미러**(CLAUDE.md §10)도 함께 본다.
- 운영(prod) DB 쓰기·NAS 실행·git commit·cron 등록은 **각각 명시 승인 후에만**. cron 은 기본 수동.
- 변경 파일은 dev 에서 먼저 검증(`/server-test`)한다. prod 직접 수행은 사용자가 명시 지시할 때만,
  그 경우에도 `INGEST_STAGES=<name>` 로 **대상 테이블 외 미접촉**을 보장한다.

## 1. 요구사항 질문 (인자에 없으면 AskUserQuestion 으로 먼저 수집)
1. **단계/배치 이름** `<name>` (예: `returns_ledger`). 이걸로 결정됨:
   함수 `ingest_<name>`, 배치 `nas_<name>_ingest.sh`, 환경변수 `INGEST_STAGES=<name>`.
2. **대상 테이블**: 이름 + **생성 여부**.
   - 신규 → `backend/scripts/sql/create_<table>.sql` (CREATE TABLE IF NOT EXISTS) 작성.
   - 기존 → 운영/ dev 에서 실제 스키마(컬럼·UNIQUE 제약)를 **먼저 조회**해 코드와 맞춘다.
     (returns_ledger 처럼 레포에 DDL 없이 운영에만 있는 테이블 주의 — 컬럼·`uq_*` 제약 실측 필수.)
3. **소스 파일 위치/패턴**: 예 `cache/batch/YYYYMMDD/<prefix>_*.csv` 또는 `cache/data-fetch/<prefix>_*`.
   컨테이너 기준 `CACHE_DIR=/app/.cache` 하위. 파일명에 날짜 토큰이 있으면 그 의미(범위 시작/종료/거래일).
4. **저장 방식**(덮어쓰기 전략) — 하나 선택:
   - **sliding-window-overwrite** (returns 정본): 매일 같은 윈도우가 시작일만 밀려 들어옴.
     최신 파일 1개 선택(mtime) → 파일명 시작일 `range_start` 이상 DELETE → 전량 INSERT.
     윈도우 밖(이전) history 보존. 비교는 `regexp_replace(날짜,'[^0-9]','','g') >= 'YYYYMMDD'` (형식무관).
   - **replace-by-date** (`ingest_daily_trade_ledger` 정본): 파일=날짜 1개 → `DELETE WHERE date=%s` 후 INSERT.
   - **upsert**: `ON CONFLICT (...) DO UPDATE` (행이 갱신되는 누적 마스터).
   - **append-idempotent**: `ON CONFLICT DO NOTHING` + `is_imported(import_log)` 스킵 (단순 누적).
5. **CSV 컬럼 → DB 컬럼 매핑**: 컬럼 순서(iloc 인덱스), 날짜 정규화 대상(→ `YYYY-MM-DD`),
   숫자 컬럼(`safe_int`/`safe_float`), **UNIQUE 키 구성 컬럼**(멱등·중복흡수 기준).
6. **FK 해석**: store/supplier/product 매칭 필요 여부 → 있으면 `resolve_fks` 재사용
   (미매칭 행은 스킵 카운트). store만이면 `resolve_store_id`, 사입처는 `get_supplier_id`.
7. **배치 시각**(cron): sh 헤더 주석에 예시만 기재, **등록은 수동**(crontab 손관리).

## 2. 구현 (정본 패턴 그대로)
**(a) `ingest_all.py` 에 `ingest_<name>(conn, force=False)` 추가 + 단계 등록**
- `ingest_all_csvs` 의 `stages` 리스트(`("<name>", ingest_<name>)`)에 추가 → `INGEST_STAGES` 로 격리됨.
- 날짜 정규화는 모듈 헬퍼 `_normalize_ymd` 재사용(없으면 추가). 비교 키는 정규화·digits 비교로.
- INSERT 는 테이블 UNIQUE 제약 대상으로 `ON CONFLICT ON CONSTRAINT <uq> DO NOTHING` (CSV 내 중복 흡수).
  적재 건수는 `cur.rowcount` 합으로 센다(DO NOTHING 스킵 분리 로깅).
- 헬퍼: `read_file_auto`(파일읽기), `safe_str/safe_int/safe_float`, `log_import`(감사).
- ⚠ **id 가 1부터 안 나옴은 정상**: `get_conn()` 이 연결마다 시퀀스를 `MAX(id)+10000` 으로 점프
  시키고(동시성 가드), PostgreSQL 시퀀스는 롤백돼도 안 돌아온다(실패런·ON CONFLICT 스킵이 구멍 남김).
  id 는 대리키라 값·구멍 무해 — 행수/내용으로 검증한다.

**(b) `nas_<name>_ingest.sh` 작성** (`nas_returns_ingest.sh` 미러)
- 락(`/tmp/nas_<name>_ingest.lock`), 로그(`/volume1/docker/testerp/data/<name>_ingest.log`).
- `CONTAINER=koclo_erp-app`(운영), dev 테스트는 `koclo_erp-dev-app`.
- 핵심 호출:
  `$DOCKER exec -e APP_BASE=/app -e CACHE_DIR=/app/.cache -e USE_DB=1 -e INGEST_STAGES=<name> "$C" python3 /app/scripts/ingest_all.py --skip-pkl --skip-supabase`
- `chmod +x`. cron 등록은 헤더 주석 예시만.

**(c) `create_<table>.sql`** (신규 테이블일 때)
- `CREATE TABLE IF NOT EXISTS` + 컬럼 + FK(stores(store_id)/pm_suppliers(id)/products(id)) +
  멱등용 `CONSTRAINT uq_<table>_key UNIQUE (...)` + 비교 키 인덱스. 기존 운영 테이블은 불간섭.

## 3. 검증 (정본 절차)
1. 로컬 구문: `python3 -c "import ast; ast.parse(open('backend/scripts/ingest_all.py').read())"` + `bash -n` sh.
2. **dev 검증**(`/server-test` → dev 오버레이): `INGEST_STAGES=<name>` 로 dev 컨테이너 실행 →
   적재 건수·날짜범위·중복흡수 확인. **재실행 멱등성**(삭제 N→재적재 N, count 불변) 확인.
3. **sliding-window 2일 테스트**(어제·오늘 파일): 운영코드/실캐시 변경 없이 **임시 CACHE_DIR로 입력 통제**:
   - `$DOCKER exec "$C" sh -lc "mkdir -p /tmp/<name>_y/batch/<어제> && cp -f <어제파일> /tmp/<name>_y/batch/<어제>/"`
     → `-e CACHE_DIR=/tmp/<name>_y` 로 인입(어제분). (⚠ `rm -rf` 는 danger-guard 차단 → `mkdir -p`만)
   - 오늘 파일도 `/tmp/<name>_t` 로 동일 → 인입. 검증: **직전 시작일 이전 행이 보존**(min_date·해당일 건수
     유지)되고 윈도우 구간만 갱신, 건수 합 정합, `batch_date` 로 출처 분리되는지.
4. prod 직접 수행은 사용자 명시 지시 시: 위 임시 CACHE_DIR 방식으로 동일하게(대상 테이블만).

## 4. 마무리
- 변경 파일·검증결과(적재/삭제/중복/멱등)·남은 것(cron 수동등록·운영배포)을 요약.
- 운영 배포는 `git pull`(바인드마운트라 재빌드 불필요), 커밋·푸시는 명시 승인 후.
- `.claude/commands/` 수정분은 koNclo-plugins 미러 커밋도 안내.
