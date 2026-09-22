# dev-workflow — 스텝 배너 실물 예시

> 양식은 `forms/step-banner.md`. 이건 채워진 결과 예시다.

## 스텝 배너 예시

````markdown
---

### ② 조사 요약 — stacking context 가둠
`① 분류 ▸ 【② 조사】 ▸ ③ 설계 ▸ ④ 승인 ▸ ⑤ 구현 ▸ ⑥ 검증 ▸ ⑦ 완료`

> 근본 원인은 z-index 값이 아니라 `.tab-body` 의 transform 이 새 stacking context 를 만든 것.

- `frontend/css/layout.css:88` — transform 진원지
- `frontend/views/InventoryView.js:412` — 모달 마운트 위치
````
