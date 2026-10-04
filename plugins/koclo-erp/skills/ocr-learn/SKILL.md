---
name: ocr-learn
description: Use when 자동판정 테스트서버(PaddleOCR) 결과를 메인서버(claude 비전) 결과와 비교해 파서를 보정(학습)할 때. 트리거 — "/ocr-learn", "학습", "OCR 학습", "paddle 학습", "테스트서버 결과 반영", "오늘 결과로 학습". 사용자 지적을 교훈으로 쌓는 /learn 과 다르다.
---

# 자동판정 PaddleOCR 학습 루프

테스트서버(koclo-vm `autojudge-test`, `AJ_OCR_ENGINE=paddle`)의 결과를 메인서버(claude 비전) 결과를 정답으로 삼아
채점하고, 오답을 원인별로 나눠 `receipt-autojudge/auto_judge_paddle.py` 파서·분리 규칙을 고친다.
날짜가 쌓일수록 **회귀 세트 전체**로 재채점해 한 날짜에 과적합하지 않게 한다.

## 전제
- **서버 게이트**: `/server on [분]` 이 서버·NAS·플러그인 원격 가드를 함께 연다. 닫혀 있으면 안내하고 멈춘다.
- **실행은 사용자가 한다**: 메인서버·테스트서버 잡 실행·재실행은 사용자가 ERP 에서 한다. 큐 JSON 을 되돌리지 않는다.
- **작업 폴더**: koclo-vm `~/paddle_dev/ocr_learn/` (저장소 밖). 큐·게시·DB 에 쓰지 않는다.
- **도구**: 이 폴더의 `ocr_learn.py` — 저장소(receipt-autojudge)에 넣지 않는다.

## 절차

1. **게이트 확인** — `.claude/hooks/gate.sh server status`. 닫혀 있으면 "`/server on 60` 을 실행해 주세요" 안내 후 중단.
2. **스크립트 올리기·수집** (인자로 날짜를 주면 `--date YYYY-MM-DD`, 없으면 오늘):
   ```bash
   ssh koclo-vm 'mkdir -p ~/paddle_dev/ocr_learn'
   scp -q .claude/skills/ocr-learn/ocr_learn.py koclo-vm:paddle_dev/ocr_learn/
   ssh koclo-vm '/home/konclo/autojudge/.venv/bin/python ~/paddle_dev/ocr_learn/ocr_learn.py collect [--date …]'
   ```
   - **대상 없음**이면 스크립트가 매장별 메인/테스트 유무와 큐 상태를 알려 준다 → 그대로 전하고 끝낸다(에러 아님).
   - 테스트 결과가 claude 비전으로 돈 것(엔진 전환 전)이면 건너뛴다고 알려 준다.
3. **오답 분석** — `~/paddle_dev/ocr_learn/reports/<날짜>.json` 의 `mismatches`·`split_diff` 를 원인별로 나눈다:
   | 원인 | 판단 근거 | 대응 |
   |---|---|---|
   | OCR 글자 오독 | 원시 OCR 텍스트부터 틀림(드랍→드립) | 파서로 못 고침 — 사입처 목록 대조 등 후처리 검토 |
   | 파서 규칙 | 원시 OCR 은 맞는데 필드가 틀림 | `auto_judge_paddle.py` 규칙 보정 |
   | 분리 | `split_diff` (조각 수 차이) | 사진을 직접 확인(썸네일) 후 분리 임계값 보정 |
   | **claude 비전 오답** | 사진 확인 결과 claude 비전이 틀림 | 보정하지 않는다 — 보고에 명시 |
   분리 차이는 **반드시 사진으로 확인**한다(2026-09-28: 34장 중 1장은 claude 비전이 틀렸다).
4. **보정 설계·승인** — 무엇을 왜 고치는지, 예상 효과를 보여주고 승인받은 뒤 로컬 `receipt-autojudge` 에서 고친다.
5. **회귀 재채점** — 고친 `auto_judge_paddle.py` 를 올려 쌓인 모든 날짜를 재파싱:
   ```bash
   ssh koclo-vm 'mkdir -p ~/paddle_dev/ocr_learn/code'
   scp -q <receipt-autojudge>/auto_judge_paddle.py <receipt-autojudge>/auto_judge_layout.py koclo-vm:paddle_dev/ocr_learn/code/
   ssh koclo-vm '/home/konclo/autojudge/.venv/bin/python ~/paddle_dev/ocr_learn/ocr_learn.py reparse --code ~/paddle_dev/ocr_learn/code'
   ```
   "저장된 결과(수정 전)" 대비 **전체 수치가 떨어지면 반영하지 않는다**(날짜별 수치도 함께 본다).
   분리 규칙 변경은 재OCR 이 필요해 reparse 로 채점되지 않는다 — 사진 확인 결과로 판단한다.
6. **반영** — 커밋·push·PR(base develop)·테스트서버 폴더 갱신·서비스 재시작은 **각각 승인** 후.
   PR 을 올린 뒤 후속 커밋 전에는 `gh pr view <번호> --json state` 로 머지 여부를 먼저 확인한다.
7. **보고** — 수치(전/후), 고친 규칙, claude 비전 오답으로 판정한 건, 남은 한계.

## 경계
- 메인서버(`autojudge.service`)·운영 폴더(`/home/konclo/autojudge`)는 읽기만 한다.
- 검증·비교 스크립트를 receipt-autojudge 저장소에 커밋하지 않는다(2026-09-28 사용자 지시).
- 원시 OCR 은 테스트 실행의 `vision/_paddle_raw/` 에 남는다(엔진 PR 이후 실행분부터).
