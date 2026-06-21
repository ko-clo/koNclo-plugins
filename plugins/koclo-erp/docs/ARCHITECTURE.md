# Plugin Architecture

```text
Codex plugin card / Claude slash command
                  |
              koclo-ui
                  |
   +--------------+----------------+-------------+
   |              |                |             |
dev-blueprint    vmd            payrate    safety-policy
                  |                |
          subtab agents     area/data agents
   \______________|________________/
                  |
        verification-harness
```

- Skills are the cross-runtime workflow layer.
- Claude Code discovers the packaged agents and commands.
- Codex exposes skills through the plugin card and starter prompts.
- Codex and Claude Code discover the packaged `SessionStart` hook. It injects the mandatory KOCLO development and verification policy when a new session starts.
- Codex requires users to review and trust a new or changed non-managed hook through `/hooks` before it runs.
- Persistent repository-specific policy belongs in project `AGENTS.md` or `CLAUDE.md`; use `koclo-project-setup` to propose that integration and obtain approval before editing it.
- Claude `PreToolUse` runs `safety-guard.mjs`; `/nas` and `/danger` run `gate-control.mjs` against short-lived per-project state.
- Codex hard controls remain the Codex sandbox and approval configuration. Plugin installation does not grant permissions or modify project instruction files.
- Packaged references are read on demand and are not global memory.
