---
description: NAS 부하 상태 상세 점검 (CPU·메모리·디스크·로드·도커)
argument-hint: "(인자 없음)"
---
사용자가 `/nas-stat` 를 실행했다. NAS(`100.99.51.88`, SSH 포트 2323, 계정 `saykim4195`)의
시스템 부하를 **읽기 전용**으로 상세 점검한다. 모두 조회 명령뿐이라 안전하다.

## 전제 (둘 다 필요)
1. **NAS 게이트 열림** — Bash 도구가 `100.99.51.88` 마커 명령을 통과하려면 `/nas on` 필요.
2. **SSH 공개키 등록(무인 접속)** — 이 세션의 `!` 와 비대화 Bash 도구는 TTY가 없어
   **비밀번호 입력이 불가능**하다. 따라서 키 기반 접속이 전제다. (비밀번호 평문 전달·저장 금지)

## 절차
1. **게이트 확인**: `.claude/.nas-unlock` 의 epoch가 현재보다 큰지 확인. 닫혀 있으면
   "`/nas on 10` 먼저 실행하세요"라고 안내하고 중단.
2. **Bash 도구로 조회 1회 실행** (키 기반이라 비번 없이):
   ```
   ssh -o BatchMode=yes -o ConnectTimeout=8 -p 2323 saykim4195@100.99.51.88 'echo "===== UPTIME/LOAD ====="; uptime; echo "코어수: $(nproc)"; echo "===== LOADAVG ====="; cat /proc/loadavg; echo "===== MEMORY ====="; free -h 2>/dev/null || free; echo "===== DISK ====="; df -h | grep -vE "tmpfs|devtmpfs"; echo "===== CPU/MEM TOP ====="; top -bn1 2>/dev/null | head -15; echo "===== TOP MEM PROCS ====="; (ps -eo pid,pcpu,pmem,rss,comm --sort=-pmem 2>/dev/null | head -8) || ps w 2>/dev/null | head -8; echo "===== DOCKER ====="; (docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>/dev/null) || echo "(docker 미접근 — sudo 필요할 수 있음)"'
   ```
3. **`Permission denied (publickey...)` 로 실패하면** → 키 미등록 상태다. 사용자에게
   **자신의 터미널(Terminal.app 등, 이 세션의 `!` 아님)** 에서 1회만 실행하라고 안내:
   `ssh-copy-id -p 2323 saykim4195@100.99.51.88` (비밀번호 1회 입력) → 이후 무인 접속.
4. **출력 해석** — 자원별 판정 + 상위 소비자를 표로 정리:
   - **CPU 로드**: loadavg(1분) ÷ 코어수 → <0.7 🟢 / 0.7~1.0 🟡 / >1.0 🔴
   - **메모리**: 실사용률(buff/cache 제외) → <80% 🟢 / 80~90% 🟡 / >90% 🔴
   - **디스크**: 볼륨별 use% → <80% 🟢 / 80~90% 🟡 / >90% 🔴 (특히 `/volume1`)
   - **상위 프로세스/도커 컨테이너**: CPU·MEM 상위, testerp 관련 컨테이너 부하를 짚는다.
   - 끝에 **한 줄 종합 판정**(전반 여유/주의/위험 + 최대 병목). 일부 실패 시 그 항목만 "확인 불가".

## 참고
- 호스트 메트릭이라 SSH 필요. Postgres(5434)만으론 호스트 부하를 알 수 없다.
- 키 미등록 시 대안: 사용자가 자기 터미널에서 위 stat 한 줄을 직접 실행(비번 입력) 후 출력을
  붙여넣으면, 그 출력을 4번 기준으로 해석한다.
