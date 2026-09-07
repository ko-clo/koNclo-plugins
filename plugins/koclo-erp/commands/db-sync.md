---
description: testerp_dev 를 운영 testerp 의 지정 테이블로 수동 동기화 (preview | go) — koclo-vm 앱 컨테이너에서 실행. 정기 동기화는 db-sync 배치(매일 09:00)가 담당
argument-hint: "[status] | go | go all | go 테이블,.. | go --exclude 테이블,.."
---
사용자가 `/db-sync $ARGUMENTS` 를 실행했다. 운영 DB(`testerp`)를 원천으로 개발 DB
(`testerp_dev`)의 **지정된 테이블만** 동기화한다. 엔진은 `backend/scripts/sync_dev_from_prod.py`
(postgres_fdw 서버측 INSERT...SELECT, FK 일시무시, 시퀀스 리셋, FDW 객체 자동정리).

## 실행 위치 — koclo-vm 의 운영 앱 컨테이너 (로컬 아님)
로컬에는 postgres 자격증명이 없다. 스크립트는 **koclo-vm 의 앱 컨테이너 안에서** 실행한다.

**dev 앱 컨테이너를 찾지 마라.** 스크립트가 필요로 하는 것은 컨테이너가 아니라 **dev DSN** 이다
(스크립트는 dev DB 에만 접속하고 prod 는 postgres_fdw 외부테이블로 읽기만 한다). 그래서 항상
떠 있는 운영 앱 `koclo_erp-app` 에서 돌리고, 그 컨테이너 env `KOCLO_ERP_DB_DSN`(=`dbname=testerp`)을
`SYNC_PROD_DSN` 으로 그대로 쓰고 dbname 만 `testerp_dev` 로 바꾼 값을 `SYNC_DEV_DSN` 으로 준다.
안전 가드는 컨테이너가 아니라 **접속한 DB 이름**으로 판정하므로(이름에 'dev' 가 없으면 즉시 중단)
실행 위치가 안전성을 바꾸지 않는다.
비밀번호는 컨테이너 내부에서만 펼쳐지며 SSH 세션/로그로 출력되지 않는다.

- 접속: `ssh koclo-vm` (docker 는 sudo 불필요)
- 스크립트 경로(컨테이너 내부): `/app/scripts/sync_dev_from_prod.py` (`./backend/scripts:/app/scripts:ro` 바인드)
- prod=`testerp` · dev=`testerp_dev` 는 **같은 클러스터**(`koclo_erp-db`, 호스트 5434)의 별개 DB다.
- FDW 호스트는 강제 지정 불필요 — 스크립트가 `localhost:5432` 부터 자동 후보 시도(같은 클러스터).

> 2026-09-05 수정: 옛 절차는 NAS(`100.99.51.88`)의 `docker ps | grep "dev-app"` 으로 컨테이너를
> 해석했는데, ⑴ 실서비스 호스트가 koclo-vm 으로 옮겨졌고 ⑵ 거기 dev 앱 이름이
> `koclo_erp-feature-app` 이라 그 grep 이 아무것도 잡지 못해 절차가 "결과가 비면 중단"에 걸렸다.
> 이름 해석 단계 자체를 없앴다.

## 자동 배치와의 관계
같은 엔진을 하루 1회 자동으로 돌리는 배치가 있다(`backend/scripts/nas_db_sync.sh`, 매일 09:00).
평소 동기화는 그쪽이 담당하므로 이 명령은 **급히 지금 맞춰야 할 때만** 쓴다. 배치는
`--yes --auto`(테이블별 전량/증분 자동 판정)로 돌고, 일요일만 `--yes`(전량)로 돈다.
판정 결과만 보고 싶으면 파괴적 실행 없이 `--dry-run --auto` 를 쓴다.

## 동기화 대상 — 프리셋(PRESET)
기본 동작은 **아래 10개 테이블만** 동기화한다. 전체 미러가 아니다.

```
stores,pm_suppliers,products,sales_daily,purchase_daily,missed_orders,trade_ledger,inventory_snapshot,daily_trade_ledger,backorder_products
```
- preview·go 모두 이 프리셋을 `--tables` 로 넘긴다. 전체 미러는 `go all`.

## 전제 — 서버 게이트
- `ssh koclo-vm` 접속이므로 **서버 게이트가 열려 있어야** 한다. 닫혀 있으면 PreToolUse 훅
  (`.claude/hooks/server-gate.sh`)이 막는다 → 사용자에게 **`/server on 30`** 먼저 실행하라고
  안내하고 중단. (`docker exec ... koclo_erp-db` 형태를 쓰면 `nas-guard.sh` 도 함께 걸리므로
  그때는 `/nas on 30` 도 필요하다.)

## ⚠ 부분 동기화 CASCADE 주의
부분 동기화는 `TRUNCATE ... CASCADE` 로 대상 테이블을 비운다. 프리셋의 부모 테이블
(`stores`, `products`, `pm_suppliers` 등)을 FK 로 참조하는 **범위 밖 dev 자식 테이블도
함께 비워질 수 있다.** go 실행 전 이 점을 1줄로 경고한다.

## 실행 절차

### 1) 동작별 실행
컨테이너 이름 해석 단계는 없다 — `koclo_erp-app` 고정이다.
스크립트가 받는 인자(`MODE`)만 동작별로 다르다. 공통 래퍼:
```
ssh koclo-vm "docker exec koclo_erp-app sh -c '
   export SYNC_PROD_DSN=\"\$KOCLO_ERP_DB_DSN\"
   export SYNC_DEV_DSN=\"\$(echo \"\$KOCLO_ERP_DB_DSN\" | sed \"s/dbname=testerp/dbname=testerp_dev/\")\"
   python3 /app/scripts/sync_dev_from_prod.py MODE
'"
```
`KOCLO_ERP_DB_DSN`/파생 DSN 은 컨테이너 내부에서만 펼쳐진다(비번 미출력).
실행 로그 첫머리의 `dev 접속: ... (current_database=testerp_dev)` 로 **대상이 dev 인지 반드시 확인**한다.

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
- 끝나면 추가 서버 작업이 없을 경우 `/server off`(열었다면 `/nas off` 도) 로 잠그도록 안내한다.
