# Security Model

- This plugin never grants infrastructure or publication permission.
- Claude Code `PreToolUse` denies NAS/remote access until `/nas on`, denies destructive commands until `/danger on`, and returns `ask` for every Docker command, NAS mutations, and every Git commit/push.
- Gates expire after 30 minutes by default, accept 1-120 minutes, are scoped to the current project, and are kept in machine-local temporary state.
- Opening a gate is not approval for a later mutation or Git publication.
- Opening either gate also produces an approval prompt, so an agent cannot use the packaged gate command silently.
- Claude project hooks and permission rules still apply; the strictest result wins.
- Codex sandbox and approval policy still apply independently.
- Installation must not be treated as approval for deployment, migration, production data mutation, Git publication, or destructive commands.
- Keep operational credentials and infrastructure configuration outside the plugin repository.

Command classification is intentionally conservative but cannot understand every shell wrapper or alias. Keep host-level deny/ask policies for critical environments; the hook is defense in depth, not a security boundary against a malicious user who can modify or bypass the plugin.
