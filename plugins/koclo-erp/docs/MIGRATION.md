# Migration Notes

Source reviewed: the KOCLO ERP project's `.claude/` directory.

## Included

- `dev-blueprint` and `agent-blueprint`
- VMD and payrate routing skills
- VMD and payrate subtab/area agents for Claude Code
- VMD and payrate domain, feedback, and architecture references
- portable development and verification policy

## Excluded intentionally

- `settings.local.json`, local permission history, and machine-specific approvals
- NAS/server/database operational commands, host addresses, and persisted guard unlock files
- credentials, secret-location references, production endpoints, and absolute user paths
- OMC session state, locks, archived notes, and generated runtime files
- order and automatic-payment workflows containing environment-specific connection details

The portable safety hook includes no endpoint or credential. Its unlock state is generated at runtime in machine-local temporary storage and expires automatically. Add environment integrations through a separate private operations plugin after a dedicated secret and permission review.
