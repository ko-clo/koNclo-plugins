---
description: order 주문장 cron 실시간 모니터링 — 로그 tail -F 스트리밍 + 빌드 시작/8·8 완료 자동 감지·종료
argument-hint: "[order|all] [감시분, 기본 90]"
---
사용자가 `/cron-watch` 를 실행했다. NAS(`100.99.51.88`, SSH 2323, 계정 `saykim4195`)에서
crontab이 돌리는 스크립트의 로그를 **`tail -F` 로 백그라운드 스트리밍**해 **새 줄이 찍히는 즉시**
진행 이벤트를 사용자에게 보고하고, **완료를 감지하면 자동으로 모니터링을 끝낸다**. 모두 읽기 전용이다.
**대기 중에도 "지금 돌고 있다"는 신호(heartbeat)를 끊김 없이 보여준다** — 아무 줄도 안 나오는 침묵 구간을 만들지 않는다.

`$ARGUMENTS` 첫 토큰 = 대상(`order`=주문장 메인+legacy, `all`=거기에 trade/analysis 로그 추가, 기본 `order`),
둘째 토큰 = 감시 분(기본 90). 정시 한 번 찍고 끝나는 `/cron-check` 과 달리, 이건 **켜놓고 지켜보는** 용도다.

## 전제
1. **NAS 게이트 열림** — 백그라운드 `tail` 을 **시작할 때** 게이트가 열려 있어야 한다(한 번 뜬 백그라운드
   프로세스는 이후 게이트가 만료돼도 계속 돈다 — 훅은 *새* Bash 호출만 검사하기 때문). 그래도 만료되면
   중간에 추가 조회(8/8 확인 등)가 막히니, 감시 분만큼 `/nas on <분>` 을 먼저 충분히 열어두도록 안내.
2. **SSH 공개키 등록(무인 접속)** — 비대화 Bash는 비번 입력 불가. 키 기반 전제(`/cron-check` 와 동일).

## 감시 대상 로그
- order 메인: `/volume1/docker/testerp/data/auto_ingest.log` (`[order]`)
- order legacy: `/volume1/docker/testerp-legacy/data/auto_ingest.log` (아직 없을 수 있음 → `tail -F` 가 생성 시 자동 추적)
- (`all`일 때만) trade: `/volume1/docker/testerp/data/trade_ingest.log`, analysis: `/volume1/docker/testerp/data/analysis_ingest.log`

## 절차
1. **게이트 확인**: `.claude/.nas-unlock` epoch > 현재? 닫혔으면 "`/nas on 90` 먼저" 안내 후 중단.
2. **시작 스냅샷 1회** — 현재 상태부터 보여준다(시각/오늘 로그 줄수/XLS n/8). `/cron-check` 의 [1][2][3] 만 가볍게.
3. **백그라운드 tail 스트리밍 시작** — `run_in_background: true` 로 아래를 띄운다. `-F` 는 파일 미존재 시
   재시도하므로 legacy 로그가 아직 없어도 안전하다. `--max-unchanged-stats` 로 회전 감지를 빠르게.
   ```
   ssh -o BatchMode=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=6 -p 2323 saykim4195@100.99.51.88 'tail -F -n3 /volume1/docker/testerp/data/auto_ingest.log /volume1/docker/testerp-legacy/data/auto_ingest.log 2>/dev/null'
   ```
   (`all` 이면 tail 인자에 trade_ingest.log analysis_ingest.log 도 추가.) `==> 파일 <==` 헤더로 어느 로그인지 구분된다.
4. **스트림 해석 — 새 줄이 올 때마다** 사용자에게 핵심 이벤트만 한 줄로 중계한다(원문 덤프 말고 요약):
   - `대기중 - 필수 미도착:…` → "⏳ (메인/legacy) 입력 CSV 대기 중"
   - `필수 파일 도착 - 빌드 시작` / `증분 인입 시작` → "▶️ 빌드 진입"
   - `완료 - XLS 8/8매장 생성` → "✅ (메인/legacy) 8/8 완료"
   - `오류 - XLS n/8` 또는 `[ERROR]`/`rc!=0` → "🔴 오류" + 줄 인용
   - `이미 완료. skip` → 무시(노이즈)
4-b. **진행 표시(heartbeat) — 침묵 금지**: 백그라운드 tail 은 새 줄이 찍히기 전까지 **아무 출력이 없다**.
   그 빈 구간 동안 사용자가 "멈춘 거 아냐?" 하지 않도록, **일정 주기(기본 30초)마다 살아있다는 한 줄을 찍는다**.
   - 형식: `⏳ HH:MM 감시중 (메인 로그 N줄·XLS n/8 / legacy m줄·k/8) ····` — **점 1개씩 늘려가며** 진행 누적을 표현.
     (즉 매 사이클 새 줄을 추가; 같은 줄을 덮어쓰는 게 아니라 줄을 쌓아 "계속 돌고 있음"을 시각화.)
   - 구현: 백그라운드 tail 의 새 출력이 한 주기 동안 없으면 `/cron-check` 의 [2][3] 만 가볍게 1회 폴링해 카운트(로그 줄수·XLS n/8)를 갱신해 heartbeat 줄에 싣는다. 카운트가 바뀌면 그 자체가 진행 이벤트이므로 점 대신 변화를 강조.
   - 페이싱은 `ScheduleWakeup`(기본 30~60초; 캐시 유지 위해 270초 이하 권장)으로 다음 heartbeat 를 예약하고, 그 사이 백그라운드 tail 이 이벤트를 던지면 즉시 중계(4번)한다.
5. **자동 종료 조건** — 다음 중 하나면 백그라운드 tail 을 `TaskStop`(또는 해당 background Bash kill)으로 끄고
   최종 요약을 낸다:
   - 감시 대상 **모두 `8/8 완료`** 를 봤을 때 (order면 메인+legacy 둘 다; 단 legacy가 그날 비대상 요일이면 메인만).
   - 또는 **감시 분 경과**. (Bash `timeout <분*60>` 로 tail 자체에 상한을 걸어도 된다.)
   - 또는 사용자가 중단 요청.
6. **종료 시**: `/cron-check` 산출물 확인(XLS n/8)으로 교차검증 후 "메인 ✅ 8/8 / legacy ✅ 8/8 (HH:MM 완료)" 식 한 줄 결론.

## 페이싱(대안) — 가벼운 주기 점검
스트리밍이 과하면 **주기 스냅샷**으로 대체 가능: `/loop 5m /cron-check` → 5분마다 `/cron-check` 재실행.
windows(20:10~21:00)만 돌고 8/8 완료 보이면 사용자가 `/loop` 을 멈춘다. 무인·장시간이면 이쪽이 안전.
이 모드는 **매 사이클이 곧 heartbeat** 라서(주기마다 스냅샷 한 줄이 찍힘) "돌고 있음"이 자연히 보인다 — 위 4-b 의 점 누적 대신 이 방식을 써도 된다.

## 참고
- 시작 타이밍: order는 20:10(legacy)~20:55(메인) 창. 18~19시에 켜면 한참 `대기중`만 나오니, **20:00 직전에 켜는 것**을 권장.
- `tail -F` 백그라운드는 게이트 만료와 무관하게 계속 살아있다 → 다 봤으면 **반드시 종료**(TaskStop)하고 `/nas off`.
- legacy 로그파일이 끝까지 안 생기면 = 그 줄이 미발화(요일/`/etc/crontab` 스페이스 구분자 의심) → `/cron-check [0]` 와 `/etc/crontab` 원문으로 추적.
