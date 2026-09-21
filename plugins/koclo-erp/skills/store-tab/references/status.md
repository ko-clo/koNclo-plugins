# store-tab — 매장탭 현황 (§7)

> 본체 `SKILL.md` §7 의 표다. 매장탭을 만들거나 고치면 여기에 행을 추가·갱신한다.

| 매장탭 | 원본 탭 | 라우트 | 상태 |
|---|---|---|---|
| 태그매치 | (없음 — 매장 전용으로 신설된 탭) | `/tag-match` | **사이드바 미노출**(2026-08-04 지시 — `STORE_TABS` 에서 주석 처리, 라우트·뷰는 남아 있다). 이 스킬 이전에 생성, `SubTabLayout` 경유 |
| 매장 대시보드 | (허브 — 원본 없음) | `/store` | 오늘 할 일 리스트. 기본업무 3종(샘플반납·재고조사·영수증(장끼) 확인)이 실데이터이고 업무 전용 화면으로 보낸다 |
| 샘플반납 | 샘플반납 `/sample-return` | `/store/sample-return` | 구현 완료·**dev 미검증**. 범위=본사 chrome 만 제거(매장 선택 아래 원본 그대로). 진입은 할 일 리스트 경유 |
| 재고조사 | MD 내부관리 > 재고 점검 `/md-inventory` 의 '조사 리스트' 섹션 | `/store/inventory-survey` | 구현 완료·**dev 미검증**. 범위="리스트만"(파라미터 조절·전매장 요약·실사 집계·다운로드 제외). 행 단위 체크가 완료이고 할일 집계에 들어간다. 저장은 `store_task_product_checks` 에 `task_type='inventory-survey'` — **DDL 없음**. 데스크톱+모바일 |
| 영수증(장끼) 확인 | (없음 — 매장 기본업무. 행 원천 = 그날 자동판정 산출물) | `/store/receipt-check` | 구현 완료. 행은 DB 에 없고 서버 `store_receipt_check_service` 가 산출물을 읽어 준다(`/api/store-basic-tasks/receipt-check`). 행 단위 확인 체크만 `store_task_product_checks` 에 `task_type='receipt-check'` 로 저장 — **DDL 없음**. 데스크톱+모바일 |

> 사이드바 탭 정본은 `frontend/js/navTabs.js` `STORE_TABS`, 업무 화면 라우트 정본은 `frontend/js/app.js` 다. 위 표와 어긋나면 **정본이 옳다.**
