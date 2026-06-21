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
- SessionStart injection is Claude-only; persistent Codex policy belongs in project `AGENTS.md`.
- Claude `PreToolUse` runs `safety-guard.mjs`; `/nas` and `/danger` run `gate-control.mjs` against short-lived per-project state.
- Codex does not consume Claude hooks. Its hard controls are the Codex sandbox and approval configuration.
- Packaged references are read on demand and are not global memory.
