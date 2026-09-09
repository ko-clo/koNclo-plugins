# KONCLO DB 조회 플러그인

기획팀이 **한국어로 물어보면 회사 DB 를 조회해 표로 보여 주는** 플러그인이다.
Claude Code(CLI·GUI)와 Codex(CLI·GUI) 어디서든 같은 방식으로 동작한다.

- **조회(SELECT)만 가능하다.** 데이터가 바뀌거나 지워질 수 없다.
- 30초 · 5,000행 상한이 걸려 있어 서버에 부담을 주지 않는다.
- 접속정보는 **각자 PC 의 홈 폴더 한 곳**(`~/.koandclo/konclo-db.env`, 권한 0600)에만 저장된다.
  공유 폴더·저장소·플러그인 코드 어디에도 비밀번호가 들어가지 않는다.

## 접속 대상 (개발팀용 메모)

기본 접속처는 **NAS** 이고, 이는 의도된 선택이다(2026-09-09 결정).
운영 서빙은 koclo-vm 이지만 기획팀 조회는 NAS 로 받아 운영 DB 에 조회 부하를 얹지 않는다.

NAS 는 koclo-vm 의 실시간 복제본이 아니라 **자체 배치로 채워지는 별도 DB** 이므로,
값이 운영과 어긋날 수 있다. 운영 기준 수치가 필요한 분석이라면 이 통로를 쓰지 않는다.
접속처를 바꿔야 할 이유가 생기면 `konclo_db/config.py` 를 임의로 고치지 말고
**먼저 확인을 받는다.**

## 어느 화면을 쓰느냐에 따라 설치 방법이 다르다

| 사용 화면 | 설치물 | 설치 방법 |
|---|---|---|
| **Claude 데스크톱 앱의 채팅** (기획팀) | `konclo-db-<버전>.mcpb` | 파일 더블클릭 → 칸 3개 입력 |
| Claude Code · Codex (개발팀) | 마켓플레이스 플러그인 | `/plugin marketplace add` 후 설치 |

같은 폴더 하나로 둘 다 만든다 — 코드(`konclo_db/`)와 `pyproject.toml` 을 공유하고,
`manifest.json` 은 데스크톱 확장이, `.claude-plugin/`·`skills/`·`commands/` 는 플러그인이 쓴다.

---

# A. 기획팀 — Claude 데스크톱 앱

## 설치 (2단계)

1. **`konclo-db-<버전>.mcpb` 파일을 더블클릭**한다.
   (또는 Claude 데스크톱 앱 → 설정 → 확장 → 파일 선택)
2. 설치 화면에 뜨는 칸 **3개**를 채운다 — DB 이름 · 아이디 · 비밀번호.
   개발팀에서 받은 값을 그대로 넣으면 된다.

끝이다. 파이썬 설치도, 명령 입력도, 접속정보 파일 만들기도 없다.
필요한 파이썬과 부품은 앱이 알아서 준비한다(`server.type: "uv"`).

**비밀번호는 이 PC 의 보안 저장소(키체인 / 자격증명 관리자)에 암호화 저장된다.**
파일로 남지 않고, 번들 안에도 들어 있지 않다.

## 접속정보를 바꾸려면

설정 → 확장 → **KONCLO DB 조회** → 값 수정. 다시 설치할 필요 없다.

## 번들 만들기 (배포 담당자용)

```bash
npx @anthropic-ai/mcpb pack plugins/konclo-db konclo-db.mcpb
```

`.mcpbignore` 가 플러그인 전용 자산과 빌드 부산물을 걸러 낸다.
패킹 전 `npx @anthropic-ai/mcpb validate plugins/konclo-db/manifest.json` 으로 확인한다.

---

# B. 개발팀 — Claude Code · Codex

## 설치 (기획팀용 — 한 번만, 3단계)

> 사용자가 직접 명령을 칠 일은 없다. 2단계에서 Claude / Codex 가 알아서 설치까지 해 준다.

### 사전 준비 — 파이썬 (PC 당 1회)

python.org 에서 Python 3 설치. Windows 는 설치 첫 화면에서
**"Add python.exe to PATH" 를 반드시 체크**한다. (이미 돼 있으면 넘어간다.)

### 1. 플러그인 설치

**Claude Code**

```text
/plugin marketplace add https://github.com/<team>/koNclo-plugins
/plugin install konclo-db@koclo-team
```

**Codex**

```bash
codex plugin marketplace add /absolute/path/to/koNclo-plugins
codex plugin add konclo-db@koclo-team
```

### 2. 설정 — `/konclo-db-setup` 한 번 실행

Claude / Codex 프롬프트에 `/konclo-db-setup` 이라고 입력하거나
**"DB 연결 설정해줘"** 라고 말하면 된다. 그러면 도우미가:

1. 조회 통로가 깔려 있는지 확인하고, 없으면 **대신 설치해 준다**
   (`pip install` — 사용자가 칠 필요 없다),
2. DB 이름·아이디·비밀번호를 물어보고,
3. 실제로 연결되는지 확인해 준다.

비밀번호를 대화에 남기고 싶지 않으면 터미널에서 `konclo-db-setup` 을 직접 실행해도 된다
(입력해도 화면에 보이지 않고 명령 기록에도 남지 않는다).
서버 주소·포트는 기본값이 들어 있어 **묻지 않는다**.

### 3. Claude / Codex 재시작

껐다 켜면 도구가 잡힌다. 이후로는 **아무것도 하지 않아도 자동 연결**된다.

## 쓰는 법

그냥 한국어로 물어보면 된다.

- "이번 달 매장별 매출 보여줘"
- "홍대 매장 최근 일주일 매출 흐름 알려줘"
- "지난달에 제일 많이 팔린 상품 20개 뽑아줘"
- "삼산이랑 서면 매출 비교해줘"
- "이거 엑셀로 저장해줘" → 바탕화면 `KONCLO-DB조회` 폴더에 CSV 로 저장된다

## 구성

```text
konclo_db/config.py    접속정보 로드·저장 (0600)
konclo_db/guard.py     무엇을 실행해도 되는지 판정 (SELECT 전용·상한·금지 테이블)
konclo_db/db.py        읽기전용 실행 (psycopg2)
konclo_db/render.py    결과를 표·CSV 로
konclo_db/server.py    MCP 도구 노출
konclo_db/setup.py     접속정보 등록 CLI
skills/konclo-db-query 매장 번호표·컬럼 안내 등 도메인 지식
commands/              /konclo-db-setup 슬래시 명령
```

## 문제 해결

| 증상 | 조치 |
|---|---|
| 도구가 안 보임 | Claude / Codex 를 껐다 켠다 |
| `konclo-db-setup: command not found` | `/konclo-db-setup` 을 다시 실행 (설치까지 알아서 한다) |
| 아이디/비밀번호 오류 | `/konclo-db-setup` 재실행 |
| 연결 시간 초과 | 회사망(Tailscale)이 켜져 있는지 확인 |
| 파이썬이 없다는 안내 | python.org 에서 Python 3 설치 후 다시 시도 (개발팀 문의) |

수동으로 조회 통로만 다시 깔아야 하면 `pip install <플러그인 폴더 경로>` 다.
`pip` 이 없다는 오류가 나면 `python -m pip` 또는 `py -m pip` 로 시도한다.

## 접속정보를 바꾸려면

```bash
konclo-db-setup            # 다시 등록
konclo-db-setup --check    # 지금 설정으로 연결되는지 확인만
```

다른 서버를 봐야 할 때만 `--host` · `--port` 를 붙인다.
