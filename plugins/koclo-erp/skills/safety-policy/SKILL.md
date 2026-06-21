---
name: safety-policy
description: NAS·원격 시스템, Docker, Git 게시, 파괴적 명령의 승인 경계를 정의하는 KOCLO 안전 정책. 인프라 접근이나 commit/push 전에 사용한다.
---

# KOCLO Safety Policy

## Required boundaries

- NAS and remote access is closed by default. In Claude Code, the user must run `/nas on [minutes]` first.
- Every Docker command, including read-only inspection, requires approval immediately before execution.
- Every `git commit` and `git push` requires explicit user approval immediately before execution.
- Destructive commands remain blocked until the user deliberately opens the danger gate with `/danger on [minutes]` in Claude Code.
- An open gate permits evaluation of the operation; it does not pre-approve Git publication, Docker access, or NAS mutation.

## Runtime enforcement

- Claude Code: `PreToolUse` applies `deny` or `ask` decisions to Bash commands. `/nas` and `/danger` control short-lived, per-project gates.
- Codex: this skill is policy guidance. The Codex sandbox and host approval policy are the enforcement layer; never treat plugin installation as permission.
- Never embed credentials, host addresses, production endpoints, or unlock state in this plugin or project instructions.

Before a sensitive operation, show the exact command, target, expected effect, and rollback or recovery path. Execute only after the required approval is received.
