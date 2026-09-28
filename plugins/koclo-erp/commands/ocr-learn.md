---
description: 자동판정 PaddleOCR 학습 — 오늘(또는 지정일) 메인(claude 비전)·테스트(PaddleOCR) 결과로 채점·파서 보정
argument-hint: "[YYYY-MM-DD] (기본 오늘)"
---
사용자가 `/ocr-learn $ARGUMENTS` 를 실행했다. `ocr-learn` 스킬을 로드해 그 절차를 따른다.
날짜 인자가 있으면 `--date $ARGUMENTS` 로 넘기고, 없으면 오늘 날짜로 수집한다.
결과가 없으면 에러로 끝내지 말고 스크립트가 알려 준 상황(매장별 메인/테스트 유무·큐 상태)을 그대로 전한다.
사용자 지적을 교훈으로 쌓는 `/learn` 과 다른 명령이다.
