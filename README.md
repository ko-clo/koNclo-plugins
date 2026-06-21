# KOCLO ERP Team Marketplace

Team marketplace for both Codex and Claude Code. The packaged plugin provides shared engineering rules, a menu-oriented UI workflow, VMD/payrate subtab routing, and a verification harness.

## Repository layout

```text
.agents/plugins/marketplace.json     Codex team marketplace
.claude-plugin/marketplace.json      Claude Code marketplace
plugins/koclo-erp/              Cross-compatible plugin
```

## Codex installation

```bash
codex plugin marketplace add /absolute/path/to/koNclo-plugins
codex plugin add koclo-erp@koclo-team
```

Start a new Codex thread, select **KOCLO ERP Team**, or ask `KOCLO 개발 메뉴를 열어줘`.

Open `/hooks` once after installation, review the plugin's `SessionStart` hook, and trust it. New Codex threads then receive the KOCLO development and verification policy automatically.

## Claude Code installation

Inside Claude Code, run the two commands separately:

```text
/plugin marketplace add https://github.com/<team>/koNclo-plugins
/plugin install koclo-erp@koclo-team
```

Then use `/koclo`, `/vmd`, `/payrate`, or `/team-verify`.

## Project activation

Plugin installation makes workflows available, and the trusted `SessionStart` hook injects the common development policy into new sessions. Codex plugin installation does not modify repository files. For persistent repository-specific rules, run `koclo-project-setup` and review the proposed `AGENTS.md` or `CLAUDE.md` integration before accepting edits.

## Deliberate exclusions

The source project's local permissions, NAS/server commands, unlock files, OMC state, archived notes, and secret-location references are not packaged. See `plugins/koclo-erp/docs/MIGRATION.md`.
