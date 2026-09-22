# agent-blueprint — 산출물과 금지

> 본체 `SKILL.md` 에서 분리. 파일을 만들기 전 · 경계를 확인할 때에 읽는다.

## 산출물 (탭 1개당)

```
.claude/
├── skills/<tab>/SKILL.md                    ← 서브탭 식별→위임→회귀검증 라우팅
├── agents/<tab>-<subtab>-agent.md           ← 서브탭 1개당 1 에이전트
│   └── … (서브탭 수만큼)
├── commands/<tab>.md                        ← 인자 없으면 에이전트 목록, 있으면 직접 위임
└── memory/
    ├── domain/<tab>.md                      ← 용어·서브탭 관계·업무규칙·공유의존
    ├── domain/<tab>-feedback.md             ← 피드백 누적(F1~)  ※포함 결정 시
    ├── service/<tab>-architecture.md        ← 화면파일·API·DB·데이터 흐름
    ├── MEMORY.md  (수정)                     ← 인덱스 섹션 추가
    └── meta/agent_kernel.md  (수정)          ← §1 피드백 표에 <tab>-* 행 추가
```

복제 원본(그대로 모방할 파일): `skills/vmd/SKILL.md`, `agents/vmd-*.md`, `commands/vmd.md`, `memory/domain/vmd.md`, `memory/domain/vmd-feedback.md`, `memory/service/vmd-architecture.md`.

## 금지
앞 절에 이미 적힌 금지는 되풀이하지 않는다(§2 · §3 · 도입부). 그중 **plan 제시·승인 전 파일 생성 금지(§2)가 이 스킬의 1순위 규칙**이다.

- VMD와 다른 임의 구조 신설(정본 모방 — 벗어나려면 plan에 사유 명시).
