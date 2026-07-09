---
description: testerp_dev 를 운영 testerp 의 지정 테이블로 동기화 (preview | go) — NAS dev 컨테이너서 실행
argument-hint: "[status] | go | go all | go 테이블,.. | go --exclude 테이블,.."
---
사용자가 `/db-sync $ARGUMENTS` 를 실행했다. 운영 DB(`testerp`)를 원천으로 개발 DB
(`testerp_dev`)의 **지정된 테이블만** 동기화한다. 엔진은 `backend/scripts/sync_dev_from_prod.py`
(postgres_fdw 서버측 INSERT...SELECT, FK 일시무시, 시퀀스 리셋, FDW 객체 자동정리).

## 실행 위치 — NAS dev 컨테이너 (로컬 아님)
로컬에는 postgres 자격증명이 없다. 스크립트는 **NAS 의 dev 앱 컨테이너 안에서** 실행한다.
그 컨테이너의 기존 env `KOCLO_ERP_DB_DSN`(=`dbname=testerp_dev`)을 그대로 `SYNC_DEV_DSN` 으로,
dbname 만 `testerp` 로 바꾼 값을 `SYNC_PROD_DSN` 으로 주입한다(같은 클러스터·같은 계정).
비밀번호는 컨테이너 내부에서만 펼쳐지며 SSH 세션/로그로 출력되지 않는다.

- 접속: `ssh -p 2323 -i ~/.ssh/id_rsa saykim4195@100.99.51.88` (SSH 경고줄은 `2>/dev/null` 필터)
- docker: PATH 에 없음 → `sudo -n /usr/local/bin/docker`
- 스크립트 경로(컨테이너 내부): `/app/scripts/sync_dev_from_prod.py` (`./backend/scripts:/app/scripts:ro` 바인드)
- dev 컨테이너 이름은 환경에 따라 다름(`testerp-dev-app` 또는 `koclo_erp-dev-app`) → **하드코딩 말고 `docker ps` 로 해석**.
- FDW 호스트는 강제 지정 불필요 — 스크립트가 `localhost:5432` 부터 자동 후보 시도(같은 클러스터).

## 동기화 대상 — 프리셋(PRESET)
기본 동작은 **아래 10개 테이블만** 동기화한다. 전체 미러가 아니다.

```
stores,pm_suppliers,products,sales_daily,purchase_daily,missed_orders,trade_ledger,inventory_snapshot,daily_trade_ledger,backorder_products
```
- preview·go 모두 이 프리셋을 `--tables` 로 넘긴다. 전체 미러는 `go all`.

## 전제 — NAS 게이트
- `100.99.51.88` 접속이므로 **NAS 게이트가 열려 있어야** 한다. 닫혀 있으면 PreToolUse 훅이 막는다
  → 사용자에게 **`/nas on 30`** 먼저 실행하라고 안내하고 중단.

## ⚠ 부분 동기화 CASCADE 주의
부분 동기화는 `TRUNCATE ... CASCADE` 로 대상 테이블을 비운다. 프리셋의 부모 테이블
(`stores`, `products`, `pm_suppliers` 등)을 FK 로 참조하는 **범위 밖 dev 자식 테이블도
함께 비워질 수 있다.** go 실행 전 이 점을 1줄로 경고한다.

## 실행 절차

### 1) dev 컨테이너 이름 해석 (모든 동작 공통, 먼저)
```
ssh -p 2323 -i ~/.ssh/id_rsa saykim4195@100.99.51.88 2>/dev/null \
  'sudo -n /usr/local/bin/docker ps --format "{{.Names}}" | grep -E "dev-app" | grep -v legacy | head -1'
```
결과가 비면 중단하고 사용자에게 알린다. 이하 명령의 `<DEV_CT>` 에 이 이름을 넣는다.

### 2) 동작별 실행
스크립트가 받는 인자(`MODE`)만 동작별로 다르다. 공통 래퍼:
```
ssh -p 2323 -i ~/.ssh/id_rsa saykim4195@100.99.51.88 2>/dev/null \
  "sudo -n /usr/local/bin/docker exec <DEV_CT> sh -c '
     export SYNC_DEV_DSN=\"\$KOCLO_ERP_DB_DSN\"
     export SYNC_PROD_DSN=\"\$(echo \"\$KOCLO_ERP_DB_DSN\" | sed s/dbname=testerp_dev/dbname=testerp/)\"
     python3 /app/scripts/sync_dev_from_prod.py MODE
  '"
```
`KOCLO_ERP_DB_DSN`/파생 DSN 은 컨테이너 내부에서만 펼쳐진다(비번 미출력).

- **status** 또는 **인자 없음** → 미리보기(읽기전용, 변경 없음). **여기서 멈춘다.**
  `MODE` = `--dry-run --tables stores,pm_suppliers,products,sales_daily,purchase_daily,missed_orders,trade_ledger,inventory_snapshot,daily_trade_ledger,backorder_products`

- **go** → 프리셋 10개 동기화(파괴적). 순서:
  1. 먼저 위 `--dry-run` 으로 행수 차이를 요약해 보여주고, **해당 dev 테이블이 prod 스냅샷으로
     덮어써짐** + **CASCADE 로 범위 밖 자식 테이블이 비워질 수 있음**을 1줄씩 경고한 뒤 확인을
     받는다(이미 'go' 친 것을 승인으로 간주하되, dev-only 데이터(daily_trade_ledger,
     trade_ledger 초과분)가 사라짐을 명시).
  2. 확인되면 `MODE` = `--yes --tables stores,pm_suppliers,products,sales_daily,purchase_daily,missed_orders,trade_ledger,inventory_snapshot,daily_trade_ledger,backorder_products`
  3. 검증 섹션(행수 불일치 개수)을 그대로 보고한다.

- **go all** → 전체 미러(프리셋 무시, 모든 dev-only 데이터 소실). 강한 경고 후:
  `MODE` = `--yes`

- **go 테이블1,테이블2** → 지정 테이블만: `MODE` = `--yes --tables 테이블1,테이블2`

- **go --exclude 테이블1,테이블2** → 프리셋에서 제외 대상을 뺀 목록으로 `--yes --tables ...`

## 규칙
- PROD(`testerp`)는 **읽기 전용** — 절대 쓰지 않는다(스크립트가 readonly 세션 + dbname 'dev' 가드).
- 동기화 방향은 **prod → dev 단방향**. 반대 방향은 하지 않는다.
- 비밀번호·토큰을 출력하지 않는다(DSN 은 컨테이너 내부에서만 펼침).
- `StrictHostKeyChecking=no` 등 우회 옵션 사용 금지.
- 끝나면 추가 NAS 작업이 없을 경우 `/nas off` 로 잠그도록 안내한다.
