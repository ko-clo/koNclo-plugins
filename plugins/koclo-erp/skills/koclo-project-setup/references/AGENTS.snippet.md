## KOCLO Team Workflow

- Apply the `team-development-rules` skill before implementation or review.
- Apply `safety-policy` before NAS, remote, Docker, destructive, commit, or push operations.
- Use `koclo-ui` to select tab-oriented workflows.
- For VMD and payrate changes, load the matching skill and its packaged references.
- Run `verification-harness` before claiming code or configuration work complete.
- Never publish credentials, local paths, production endpoints, or runtime state.
- Never access or mutate NAS/remote systems, access Docker, or run destructive commands without explicit approval.
- Always obtain a fresh explicit approval immediately before every `git commit` and `git push`.
