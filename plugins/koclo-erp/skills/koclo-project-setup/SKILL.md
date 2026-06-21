---
name: koclo-project-setup
description: 현재 저장소에 KOCLO 팀 개발 규칙을 영구 연결하도록 AGENTS.md 또는 CLAUDE.md 변경안을 안전하게 제안하고 적용한다.
---

# KOCLO Project Setup

1. Detect the active runtime and existing instruction files.
2. Read existing `AGENTS.md` and `CLAUDE.md`; never overwrite them wholesale.
3. Propose the smallest integration:
   - Codex: append the contents or an adapted summary from `references/AGENTS.snippet.md`.
   - Claude Code: append the contents or an adapted summary from `references/CLAUDE.snippet.md`.
   - Mixed team: maintain both, sharing the same policy language.
4. Show the exact planned diff and obtain approval before editing instruction or settings files.
5. Do not copy permissions, host addresses, credentials, unlock files, or runtime state.
6. Verify that the resulting instructions point team members to `team-development-rules`, `safety-policy`, `koclo-ui`, and `verification-harness`.
