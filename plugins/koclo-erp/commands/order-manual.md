---
description: 날짜 지정 수동 주문장+미송 재생성 (nas_manual_order.sh 래퍼)
argument-hint: "YYYYMMDD [--reuse-html PATTERN]"
---
사용자가 `/order-manual $ARGUMENTS` 를 실행했다. 지정한 날짜의 **주문장 + 미송장**을 운영
NAS(testerp-app 컨테이너)에서 **수동 재생성**한다. 엔진은 NAS에 배포된
`/volume1/docker/testerp/backend/scripts/nas_manual_order.sh`(→ `manual_order_run.py`,
통합주문 경로를 `batch/integrated_order/{date}` 언더스코어로 고정한 미송 정본판).

산출: `/volume1/자동주문/cache/주문장_업로드/주문장_{date}/` (컨테이너 `/app/order_upload`).

## 인자 파싱
- 첫 토큰 = **기준일 YYYYMMDD**(필수). 없거나 형식이 틀리면 사용법만 안내하고 중단.
- 나머지 = 그대로 sh 뒤에 전달(예: `--reuse-html '/app/reports/order_analytics_v8.2_{date}*.html'`
  → 본체 재빌드 생략, 미송만 빠르게 재반영).

## 전제 — NAS 게이트
- `100.99.51.88` 에 SSH 접속하므로 **NAS 게이트가 열려 있어야** 한다(닫혀 있으면 PreToolUse 훅이 차단).
  닫혀 있으면 사용자에게 **`/nas on 30`** 먼저 실행하라고 안내하고 중단.
- 무인 키 인증이 되는 계정은 **`saykim4195`**(`-i ~/.ssh/id_rsa`)다. `orderhead1` 은 비밀번호
  인증이라 BatchMode 무인 실행에서 거부되므로 쓰지 않는다.

## 사전 점검 (읽기 전용, 로컬 마운트 `/Volumes/자동주문/cache`)
실행 전 **반드시** 통합주문 CSV 레이아웃을 검사한다. (참조재고 등 컬럼 삽입으로 수량 컬럼이
밀리면 `validate_layout`이 전매장을 스킵해 **미송이 0**이 되는 알려진 실패 모드가 있다.)
- `batch/integrated_order/{date}/` 폴더와 `data-fetch/증분사입흐름_{date}_오늘.csv` 존재 확인.
- 통합주문 CSV 헤더에서 첫 `수량` 컬럼이 **col14(0-기준)**인지 확인.
  - col14가 아니면(예: `참조재고` 삽입으로 col15) → **경고하고 중단**: "통합주문 CSV 컬럼 밀림 →
    이대로 돌리면 미송 0. CSV에서 추가 컬럼 제거(24컬럼 복원) 또는 backorder_merge 수정 후 재시도."
  - 정상이면 계속.

## 실행
1. 운영 `backorder_products` 누적원장이 갱신됨(운영 데이터 변경)을 1줄로 알리고 사용자 확인을 받는다
   (`/order-manual` 호출 자체를 승인으로 간주하되, 대상 날짜·운영DB 갱신을 명시).
2. 확인되면 SSH로 배포된 래퍼 실행. **`saykim4195` 는 docker.sock 직접 접근 권한이 없으므로**
   래퍼의 `DOCKER` 변수를 `sudo -n /usr/local/bin/docker` 로 오버라이드해야 한다(안 하면
   `permission denied ... docker.sock` 로 rc=1):
   ```
   ssh -o BatchMode=yes -o ConnectTimeout=10 -i "$HOME/.ssh/id_rsa" -p 2323 saykim4195@100.99.51.88 \
     "DOCKER='sudo -n /usr/local/bin/docker' bash /volume1/docker/testerp/backend/scripts/nas_manual_order.sh <date> <extra>"
   ```
   - 래퍼가 없다(배포 안 됨)는 오류면: 먼저 NAS에서 `git pull`(승인 필요)로 배포하라고 안내하거나,
     `SCRIPT_PATH`/inline `docker exec ... manual_order_run.py --date <date>` 대안을 제시한다.
3. 출력에서 `[미송] ...` / `[미송][DB] backorder_products 신규 N행 / 도착삭제 M행` 라인과
   매장별 미송 라인수를 그대로 보고한다.

## 검증 후 보고
- 결과 폴더 xls 개수 확인(읽기 전용):
  `ls /Volumes/자동주문/cache/주문장_업로드/주문장_{date}/*.xls | wc -l` → **8매장**인지.
- 미송 신규행이 0이면 사전 점검(컬럼 밀림)·사입흐름 과다도착을 의심해 원인을 한 줄로 보고.
- 끝나면 추가 NAS 작업이 없으면 `/nas off` 로 잠그도록 안내.

## 규칙
- 운영 코드/CSV는 임의 수정하지 않는다(읽기 점검만). 변경이 필요하면 승인 요청.
- 비밀번호·토큰·DSN을 출력하지 않는다.
- NAS Safety / Dangerous Action 규칙(CLAUDE.md)을 따른다.
