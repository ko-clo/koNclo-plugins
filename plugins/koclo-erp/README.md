# KOCLO ERP Team Plugin

## Entry points

- `koclo-ui`: interactive work menu for Codex and Claude Code
- `team-development-rules`: shared implementation policy
- `safety-policy`: approval boundaries for NAS, Docker, destructive commands, and Git publication
- `dev-blueprint`: KOCLO frontend/backend tab standard
- `agent-blueprint`: creates a tab Skill and subtab Agent structure
- `vmd`: routes five VMD subtabs
- `payrate`: routes payrate frontend and data ownership
- `verification-harness`: automated checks, diff review, and counterexample loop
- `koclo-project-setup`: proposes persistent project integration

Codex and Claude Code discover `hooks/hooks.json`. Its `SessionStart` hook automatically injects the KOCLO development and verification policy into new sessions. Codex requires the user to review and trust the hook with `/hooks` before it can run.

Claude Code additionally discovers `agents/` and `commands/`. Its `PreToolUse` hook blocks closed NAS/danger gates and asks for approval on every Docker command and every `git commit`/`git push`. Use `/nas on [minutes]`, `/danger on [minutes]`, and the corresponding `off`/`status` actions.

Codex uses the common `skills/` packages, plugin interface metadata, and bundled lifecycle hooks. Codex enforcement remains the sandbox and host approval policy; installing this plugin does not alter permissions or write `AGENTS.md` automatically. Run `koclo-project-setup` once per repository when persistent project instructions are required.

This package intentionally contains no credentials, production host addresses, local permissions, or deployment commands.
