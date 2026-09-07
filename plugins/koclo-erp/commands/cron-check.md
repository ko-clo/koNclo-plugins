---
description: crontab이 돌리는 스크립트가 오늘 실제로 시작/실행됐는지 점검 (order·trade·analysis 로그·락·산출물)
argument-hint: "[order|trade|analysis|all] (기본 all)"
---
사용자가 `/cron-check` 를 실행했다. NAS(`100.99.51.88`, SSH 2323, 계정 `saykim4195`)에서
**crontab이 돌리는 각 스크립트가 오늘 실제로 시작/실행됐는지**를 **읽기 전용**으로 점검한다.
핵심은 "crond 데몬이 떴나"가 아니라 **스크립트가 발화했는가**다 — 근거는 각 스크립트의
**로그 줄(오늘 날짜) · 락파일 · 산출물(XLS)** 이다. 인자(`$ARGUMENTS`)로 특정 잡만 볼 수 있다(기본 all).

## 전제 (둘 다 필요)
1. **NAS 게이트 열림** — `100.99.51.88` 마커 명령이 PreToolUse 훅을 통과하려면 `/nas on` 필요.
2. **SSH 공개키 등록(무인 접속)** — 비대화 Bash 도구는 TTY가 없어 비밀번호 입력 불가. 키 기반 전제.

## 점검 대상 (crontab 등록 스크립트)
| 잡 | 스케줄 | 로그 | 락파일 | 산출물 |
|---|---|---|---|---|
| order 메인 | 20:15~20:55 일~목 | `/volume1/docker/testerp/data/auto_ingest.log` `[order]` | `/tmp/nas_order_ingest.lock` | `주문장_업로드/주문장_<날짜>/*.xls` ==8 |
| order legacy | 20:10~20:55 일~목 | `/volume1/docker/testerp-legacy/data/auto_ingest.log` | `/tmp/nas_order_ingest_legacy.lock` | `주문장_업로드/주문장_<날짜>/*.xls` ==8 |
| trade bundle | 23:00 매일 | `/volume1/docker/testerp/data/trade_ingest.log` `[trade:bundle]` | `/tmp/nas_trade_ingest_bundle.lock` | 로그 "인입 완료" |
| trade daily | 02:00 매일 | (동일 trade_ingest.log) `[trade:daily]` | `/tmp/nas_trade_ingest_daily.lock` | 로그 줄 |
| analysis 현재고 | 06:00 매일 | `/volume1/docker/testerp/data/analysis_ingest.log` | `/tmp/nas_analysis_ingest.lock` | 로그 줄 |

## 절차
1. **게이트 확인**: `.claude/.nas-unlock` 의 epoch가 현재보다 큰지 확인. 닫혀 있으면
   "`/nas on 10` 먼저 실행하세요"라고 안내하고 중단.
2. **Bash 도구로 점검 1회 실행** (키 기반, 비번 없이). `$ARGUMENTS` 가 `order`/`trade`/`analysis`면
   해당 섹션만 봐도 되지만, 아래 한 줄로 전체를 받아 필요한 부분만 해석해도 된다:
   ```
   ssh -o BatchMode=yes -o ConnectTimeout=8 -p 2323 saykim4195@100.99.51.88 'D=$(date +%Y-%m-%d); T=$(date +%Y%m%d); echo "##### CRON 스크립트 실행 점검 — $(date "+%Y-%m-%d %H:%M %a") #####"; echo; echo "=== [0] crond 데몬 ==="; ps -ef | grep -E "[c]rond" | head -3 || echo "(crond 프로세스 안보임 — 죽었으면 어떤 스케줄도 안 돔)"; echo; echo "=== [1] 지금 실행 중? (락파일 + 프로세스) ==="; ls -la /tmp/nas_order_ingest.lock /tmp/nas_order_ingest_legacy.lock /tmp/nas_trade_ingest_*.lock /tmp/nas_analysis_ingest.lock 2>/dev/null || echo "(락파일 없음 = 현재 실행 중인 스크립트 없음)"; ps -ef | grep -E "[n]as_order_ingest|[n]as_trade_ingest|[n]as_analysis|[i]ngest_incremental|[a]uto_order_db" | grep -vF "date +%Y" | head || echo "(실행 중인 스크립트 프로세스 없음)"; echo; echo "=== [2] ORDER 메인 (20:15~20:55 일~목) ==="; LOG=/volume1/docker/testerp/data/auto_ingest.log; echo "오늘 order 로그 줄수: $(grep -c "\[$D.*\[order\]" $LOG 2>/dev/null || echo 0)"; grep "\[$D" $LOG 2>/dev/null | grep "\[order\]" | tail -4; echo "산출 XLS: $(ls /volume1/자동주문/cache/주문장_업로드/주문장_$T/*.xls 2>/dev/null | wc -l)/8"; echo; echo "=== [3] ORDER legacy (20:10~20:55 일~목) ==="; LLOG=/volume1/docker/testerp-legacy/data/auto_ingest.log; if [ -f "$LLOG" ]; then echo "오늘 legacy 로그 줄수: $(grep -c "\[$D" $LLOG)"; grep "\[$D" $LLOG | tail -4; else echo "!! 로그파일 자체가 없음 → 한 번도 실행 안 됨(미발화). cron 줄 요일/구분자(스페이스) 의심"; fi; echo "산출 XLS: $(ls /volume1/자동주문/cache/주문장_업로드/주문장_$T/*.xls 2>/dev/null | wc -l)/8"; echo; echo "=== [4] TRADE (23:00 bundle / 02:00 daily) ==="; TLOG=/volume1/docker/testerp/data/trade_ingest.log; grep "\[$D" $TLOG 2>/dev/null | tail -5 || echo "오늘 trade 로그 없음(아직 23:00/02:00 전이면 정상)"; echo; echo "=== [5] ANALYSIS 현재고 (06:00) ==="; ALOG=/volume1/docker/testerp/data/analysis_ingest.log; grep "\[$D" $ALOG 2>/dev/null | tail -3 || echo "오늘 analysis 로그 없음(아직 06:00 전이면 정상)"'
   ```
3. **`Permission denied (publickey...)` 로 실패하면** → 키 미등록. 사용자가 **자기 터미널**(이 세션의 `!` 아님)에서
   `ssh-copy-id -p 2323 saykim4195@100.99.51.88` 1회 실행하도록 안내(비밀번호 1회). 비번 평문 전달·저장 금지.

## 출력 해석 (잡별 판정)
각 잡을 아래 3상태 중 하나로 판정해 표로 요약한다. **"스케줄 시각이 지났는데 오늘 로그 줄이 0" 이 가장 중요한 적신호.**
- 🟢 **완료**: 오늘 로그에 종료 마커(order=`완료 - XLS 8/8`, trade=`인입 완료`) + (order면) 산출 XLS 8/8.
- 🔵 **실행 중/대기**: 락파일 존재 또는 프로세스 보임 / 오늘 로그에 `대기중 - 필수 미도착` (cron은 발화했고 입력 CSV 기다리는 중 = 정상).
- 🔴 **미발화**: 스케줄 시각이 지났는데 **오늘 날짜 로그 줄이 0**(legacy는 로그파일 자체가 없음). → crond 죽음/요일 불일치/`/etc/crontab` 구분자(legacy 줄은 탭 아닌 스페이스)/경로 오타를 의심하고 `[0]` 와 `/etc/crontab` 원문으로 추적.
- ⚪ **시각 전**: 아직 스케줄 시각 전(예: 18시에 점검 → order 20시·trade 23시는 당연히 안 돎). 정상이며 "미발화"로 오판하지 말 것.

판정 시 **현재 시각과 스케줄 시각을 반드시 비교**한다. 끝에 한 줄 종합(예: "order 메인 🟢 8/8, legacy 🔴 미발화 — 로그파일 없음, 점검 필요").

## 참고
- 입력 CSV(증분매출/사입) 도착 시각: 최근 기준 매출 ~20:05~20:15, 사입 ~18~19시. order 메인이 `대기중`이면 매출 CSV가 아직 안 온 것.
- order 스크립트는 멱등(8 XLS 있으면 `이미 완료. skip`) → 같은 날 여러 폴링 로그가 보이는 게 정상.
- 호스트/로그 접근은 SSH 필요. crond 데몬이 죽어 있으면 mtime 자동 리로드도 안 되므로 `[0]` 을 먼저 본다.
