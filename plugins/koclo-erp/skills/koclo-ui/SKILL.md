---
name: koclo-ui
description: KOCLO ERP 작업을 Codex 스타일 메뉴로 시작하는 UI 진입점. "KOCLO 메뉴", "UI 모드", "무슨 작업을 할까", "탭 작업 시작" 요청에 사용한다.
---

# KOCLO ERP Work Menu

When called without a target, show this menu and wait for the user's selection:

| # | Mode | Action |
|---|---|---|
| 1 | Development rules | Load `team-development-rules` and review the task boundary |
| 2 | New or separated tab | Use `dev-blueprint` |
| 3 | VMD dashboard | Use `vmd` and route the affected subtabs |
| 4 | Payrate dashboard | Use `payrate` and route frontend/data ownership |
| 5 | Build a tab agent system | Use `agent-blueprint` |
| 6 | Verify current changes | Use `verification-harness` |
| 7 | Project setup | Use `koclo-project-setup` |
| 8 | Safety gates | Use `safety-policy`; in Claude Code use `/nas` or `/danger` |

Accept a menu number, mode name, tab name, or natural-language task. When a target is supplied, select the matching skill immediately. Do not invent a target when the request is ambiguous.

For implementation modes, load `team-development-rules` first and finish with `verification-harness`. Load `safety-policy` before NAS, Docker, destructive, commit, or push operations.
