---
name: agent-blueprint
description: 임의의 ERP 탭에 대해 메인 Skill, 서브탭 담당 범위, domain/architecture references, 명령 메뉴를 설계하는 메타 스킬.
---

# Tab Agent Blueprint

Create a tab-oriented work system that remains useful in both Claude Code and Codex.

## Output model

```text
skills/<tab>/SKILL.md
├── references/domain.md
├── references/architecture.md
└── references/feedback.md

Claude adapter (when requested)
├── agents/<tab>-<subtab>-agent.md
└── commands/<tab>.md

Codex adapter
└── plugin UI routes to skills/<tab>/SKILL.md
```

The Skill is the canonical router. Named subtab agents are optional runtime adapters, not the source of truth.

## Workflow

1. Identify the exact target View and list its visible subtabs.
2. Inspect frontend shell/widgets, API client, router, service, scripts, and database tables.
3. Map shared assets consumed by multiple subtabs.
4. Check neighboring tabs and keyword collisions.
5. Before writing files, present:
   - output tree
   - subtab/owner/file/API/DB table
   - shared-file ownership
   - verification plan
6. Ask for approval before generating project instruction, agent, command, or memory files.
7. Create the canonical Skill and references first.
8. Create Claude named agents only when the project uses Claude Code.
9. Add a menu route for Codex/Claude without duplicating domain rules.

## Agent rules

- One agent corresponds to one stable ownership boundary, not merely one visual panel.
- The agent definition stays small: role, owned files, shared boundaries, required references, output contract.
- A subagent cannot be relied on to spawn another subagent. The main Skill coordinates all delegation.
- If named agents are unavailable, the main runtime performs the same scope directly.

## Verification

- Frontmatter names are unique and descriptions do not collide.
- Every referenced file, endpoint, response key, and DB table is confirmed against code.
- Shared assets have one explicit coordinator.
- All subtabs render and their primary interactions work.
- Run `verification-harness` before completion.

## Prohibitions

- Do not generate files before approval.
- Do not modify production code or data merely to create the work system.
- Do not add host addresses, credentials, local paths, or runtime state.
- Do not duplicate `team-development-rules` or `dev-blueprint`; reference them.
