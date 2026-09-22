# post-verification — 실행 검증과 반례 루프 (§6 · §7)

> 본체 `SKILL.md` 에서 분리. 실제로 돌려 볼 때에 읽는다.

## 6. 실행 검증

가장 좁은 검증부터 실행하고, 변경 위험에 따라 넓힌다.

1. 정적/구문 확인: import smoke, `ast.parse`, `bash -n`, 타입/린트 중 해당되는 것.
2. 단위 검증: 계산 함수, format guard, helper, edge case.
3. API 검증: 정상/오류 요청, 응답 shape, 400/500 여부.
4. UI 검증: 렌더, 상호작용, 콘솔 에러 0.
5. dev 서버 검증: 필요하면 `/server-test`로 dev 오버레이 후 확인하고 `/server-clear`로 원복한다.
6. 리뷰 검증: merge 전 또는 영향 범위가 넓으면 `/pr-review <브랜치>`로 독립 리뷰를 받는다.

Docker, NAS, DB 쓰기, 배포, 마이그레이션, git commit/push는 `CLAUDE.md` 승인 규칙을 따른다.

## 7. 반례 루프

아래 중 관련 있는 반례를 최소 1개 이상 시도한다.

- 빈 데이터, 데이터 1건, 대량 데이터.
- 날짜 역전, 범위 밖 날짜, 미래 날짜.
- 중복 실행, 재시도, 이미 처리된 파일/행.
- product/store/supplier 매칭 실패.
- 네트워크/DB/파일 없음.
- 공유 자산 변경 후 인접 탭 회귀.

반례가 실패하면 수정 후 영향받은 검증을 다시 실행한다. 같은 blocker가 3회 반복되면 완료가 아니라 blocker로 보고한다.
