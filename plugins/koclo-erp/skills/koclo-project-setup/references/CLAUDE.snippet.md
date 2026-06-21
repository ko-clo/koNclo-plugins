## KOCLO Team Workflow

- Load `team-development-rules` before implementation or review.
- Load `safety-policy` before NAS, remote, Docker, destructive, commit, or push operations.
- Use `/koclo` for the work menu and `/vmd` or `/payrate` for tab routing.
- Run `/team-verify` before claiming code or configuration work complete.
- Use `/nas on [minutes]` before NAS/remote access and `/danger on [minutes]` before destructive commands.
- Always obtain a fresh explicit approval immediately before every Docker command and every `git commit` or `git push`.
- Never publish credentials, local paths, production endpoints, or runtime state.
