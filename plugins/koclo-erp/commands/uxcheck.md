---
description: QA 검사 실행 — 고친 기능과 관련된 흐름을 자동으로 돌려보고 결과를 표로 본다
argument-hint: "(인자 없음=변경 기반 자동) | <도메인…> | --all | --smoke | --write | --coverage | --history | --report [run_id] | --prod"
---
사용자가 `/uxcheck $ARGUMENTS` 를 실행했다. `backend/scripts/uxcheck/runner.py` 로
**사용자 흐름(API 호출 순서)을 재생해 기능이 실제로 도는지** 확인한다.

검사 정본은 러너와 `scenarios/*.json` 이다. 이 명령은 **어디서 어떻게 실행할지**만 정한다.

## 🚫 금지
- 시나리오 단정을 "통과시키려고" 고치지 않는다. 실패하면 실패로 보고한다.
  (기대값이 실제로 틀렸다고 판단되면 근거를 대고 사용자에게 물은 뒤 고친다.)
- **prod 쓰기 금지.** `--prod` 와 `--write` 를 함께 쓰지 않는다(러너도 하드 차단한다).
- 결과를 요약하며 실패를 숨기지 않는다. FAIL 은 건별로 원문을 남긴다.

## 게이트
NAS 접속·컨테이너 실행이 필요하면 이 명령이 **NAS 게이트를 20분 연다**:
```
EXP=$(( $(date +%s) + 1200 )); echo "$EXP" > .claude/.nas-unlock
```
게이트 **없이** 되는 것: `--coverage` · `--history` · `--report` · `--dry-run` · `--list`
(전부 로컬 실행. 네트워크를 쓰지 않는다.)

## 실행 위치 결정

| 상황 | 어디서 |
|---|---|
| 배포된 코드를 확인 | 컨테이너 (`docker exec`) — 인증 불필요 |
| 로컬 미커밋 변경을 확인 | 먼저 `/server-test` 로 dev 반영 후 컨테이너 |
| 목록·이력·커버리지만 | 로컬 (`python3 backend/scripts/uxcheck/runner.py …`) |

컨테이너: dev = `koclo_erp-dev-app`(9001) · prod = `koclo_erp-app`(9000).
`--prod` 인자가 있으면 prod, 없으면 **dev 가 기본**이다.

## 절차

### 1) 인자 해석
- 인자 없음 → **변경 파일 기반 자동 선택**. 로컬에서 대상을 먼저 뽑는다:
  ```
  python3 backend/scripts/uxcheck/runner.py --print-domains
  ```
  출력이 비면 "변경 파일에 매칭된 도메인이 없다"고 보고하고 **끝낸다**(억지로 `--all` 하지 않는다).
- 도메인 이름들 → 그대로 전달.
- `--all` / `--smoke` / `--write` / `--slow` → 러너에 그대로 전달.
- `--coverage` / `--history` / `--report [run_id]` → **로컬에서 바로 실행하고 끝**(2~4 단계 생략).

### 2) 게이트 열기 (원격 실행이 필요할 때만)
위 게이트 명령을 실행하고 "✅ NAS 게이트 20분 오픈" 한 줄 출력.

### 3) 실행
`backend/app/**` 을 안 건드리므로 **컨테이너 재시작은 필요 없다**(러너는 매 실행 새 프로세스).

```
ssh -p 2323 -i "$HOME/.ssh/id_rsa" saykim4195@100.99.51.88 2>/dev/null \
  "sudo -n /usr/local/bin/docker exec \
     -e UXCHECK_COMMIT=$(git rev-parse --short HEAD) \
     -e UXCHECK_BRANCH=$(git branch --show-current) \
     <컨테이너> python3 /app/scripts/uxcheck/runner.py <인자들> --target <dev|prod>"
```

- **`UXCHECK_COMMIT`/`UXCHECK_BRANCH` 를 반드시 넘긴다.** 컨테이너엔 git 이 없어
  안 넘기면 기록에 "어떤 코드 상태를 검사했는지"가 빈다.
- `--target` 을 생략하지 않는다. prod 컨테이너에서 기본값(dev)으로 도는 사고를 막는다.
- 무거운 도메인은 콜드 스타트가 길다(sample-return ~36s, color-trend ~10s). 타임아웃을
  넉넉히 잡고, 스모크(`--smoke`)는 116개 순회라 더 길다.

### 4) 보고
- 도메인별 PASS/FAIL/SKIP, step 통과 수, 단정 수를 표로.
- **FAIL 은 건별로 원문(`→ …`)을 그대로** 싣는다. 요약하지 않는다.
- `⚠ 매칭 시나리오 없음` 이 떴으면 그 파일 목록을 함께 보고한다(커버리지 갭).
- 마지막에 `--report <run_id>` 로 다시 볼 수 있음을 알린다.

## 결과 기록
실행마다 `/app/data/uxcheck/<run_id>.run.json` 에 남는다(prod=`data/`, dev=`data_dev/`).
`--history` 로 목록, `--report <run_id>` 로 재출력. 컨테이너 재시작해도 보존된다.

## 화면에서도 된다
관리자 → **QA 검사** 탭(`/uxcheck`)에서 클릭으로 실행·조회할 수 있다.
CLI 가 막히거나 사용자가 화면을 선호하면 그쪽을 안내한다.

## 규칙
- 비밀번호·토큰 출력 금지. `StrictHostKeyChecking=no` 등 우회 금지.
- CLAUDE.md 의 NAS / Dangerous Action 규칙을 따른다. 게이트는 짧게 열고, 끝나면 `/nas off`.
