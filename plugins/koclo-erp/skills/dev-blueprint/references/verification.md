# dev-blueprint — 검증 게이트 (§6)

> 본체 `SKILL.md` 에서 분리. 구현 후 · 완료 보고 전에 읽는다.

## 6. 검증 게이트 (통과 못하면 미완료)

**먼저 기계 판정 항목을 돌린다. FAIL 이 0 이어야 한다.** 파일명이 규칙(§2)과 다른 탭은 `--help` 의 경로 옵션으로 직접 지정한다.

```bash
python3 .claude/skills/dev-blueprint/scripts/check_blueprint.py <feature>               # 새로 만든 탭
python3 .claude/skills/dev-blueprint/scripts/check_blueprint.py <feature> --preserve-ui  # 정본을 옮긴 이관 탭(§4-8)
```

스크립트가 보는 것: 토큰 밖 hex · 토큰 밖 글꼴 · 미로드 글꼴 · 다크모드 블록 · `position:fixed` · 좁은 고정 폭(WARN — FAIL 로 세지 않으니 직접 열어 보고 고치거나 사유를 남긴다) · iframe · View 비대 · CSS 링크 · 라우터 등록 · 모델 심볼 실존 · 금지 API(`session.exec`·`build_master_data`·`psycopg2`) · 스피너 · 빌드리스. `--preserve-ui` 에서는 토큰 밖 hex·토큰 밖 글꼴·`position:fixed` 가 WARN 이 된다 — 그 목록이 정본 값과 대조할 대상이다. **정본이 없는 탭이나 정본과 대조하지 않은 탭에 `--preserve-ui` 를 쓰는 것은 게이트 우회다.**

스크립트가 못 보는 아래 항목은 직접 확인한다.

- [ ] **import 스모크 통과** (§3-2b): `python3 .claude/skills/dev-blueprint/scripts/import_smoke.py <라우터...>` → **PASS**.
      SKIP(로컬 의존성 없음)이면 컨테이너에서 재실행하거나 배포 후 `Application startup complete` + `/docs` 200 으로 대체한다. *`py_compile` 통과만으론 미충족*
- [ ] 라우터에 딸린 **부속 엔드포인트**(temp-log 등)도 등록 후 정상 — 500/크래시 없음
- [ ] 동일 날짜에서 Vue 화면 수치 == 기존 `<feature>_latest.html` 수치 (합계·매장별·세부) — *로컬에 운영 DB 없으면 **배포 후 확인**으로 분리하고 완료 보고에 명시*
- [ ] 색상/등급 밴딩이 정본 임계와 일치
- [ ] **UI 보존(이관 탭)**: 정본 `<style>` 값과 대조 — 배경·글자·표 헤더 3색 스팟체크, 스크린샷이 가능하면 `visual-verdict` 로 정본 화면과 비교(§4-8). 보고에 **정본 파일 경로와 대조한 값**을 적는다
- [ ] 잘못된/역전 기간 입력 → 400 (조용한 전체범위 폴백 없음)
- [ ] 날짜/탭/토글/차트 갱신 등 인터랙션 정상
- [ ] 로딩 문구가 **무슨 작업인지** 드러낸다(막연한 "불러오는 중…" 금지, §4-5) — 지연/부분 로드 경로 포함
- [ ] 긴 리스트 내부 스크롤·sticky 헤더 동작
- [ ] 다른 탭 무손상 (라우팅 독립 확인)
- [ ] **고유 데이터 로더**: 탭 전용 경량 loader 로 소비 컬럼만 로드(파리티 유지)
- [ ] 콘솔 에러 0, API 예외 처리 존재
- [ ] 독립 리뷰어 승인 (자기승인 아님) — `--preserve-ui` 로 통과한 탭은 리뷰어가 정본 대조 근거를 직접 확인한다
