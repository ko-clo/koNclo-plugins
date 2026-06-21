---
name: team-development-rules
description: KOCLO ERP 코드 작성·리뷰·검증에 항상 적용할 팀 개발 규칙. 구현, 버그 수정, 리팩터링, API·DB·UI 변경 전에 사용한다.
---

# KOCLO ERP Team Development Rules

## Before editing

1. Read the repository instructions (`AGENTS.md`, `CLAUDE.md`, nested rules).
2. Inspect the existing implementation, tests, and ownership boundaries.
3. Identify affected public APIs, schemas, shared components, and runtime configuration.
4. Preserve unrelated user changes and keep the requested scope explicit.

## Design

- Prefer existing project patterns over new abstractions.
- Keep one clear responsibility per module, class, and function.
- Separate business calculation, database/API I/O, and presentation.
- Avoid circular dependencies, hidden globals, and hard-to-test coupling.
- Inject external dependencies or wrap them behind small adapters.
- Do not add speculative layers, dependencies, or unrelated refactors.

## Naming and errors

- Functions start with verbs; classes and components use descriptive nouns.
- Boolean names communicate state or capability (`is*`, `has*`, `can*`).
- Handle external API, file, DB, and network failures explicitly.
- Do not swallow exceptions. Preserve actionable context without exposing secrets.
- Separate user-facing errors from internal diagnostic details.

## Logging and security

- Log meaningful state transitions and failures at an appropriate level.
- Never log credentials, tokens, personal data, environment secrets, or raw production records.
- Do not weaken authentication, authorization, TLS, host checking, or validation to make a task pass.

## Change safety

- Apply `safety-policy` before infrastructure, Docker, destructive, or Git publication operations.
- Every `git commit` and `git push` requires explicit approval immediately before execution. Earlier task approval is not publication approval.
- NAS/remote access requires an open NAS gate in Claude Code; any NAS mutation still requires approval every time.
- Every Docker command, including read-only inspection, requires approval immediately before execution.
- Never merge, rebase, deploy, migrate, seed, delete data, restart shared services, or alter production configuration without explicit approval.
- Inspect status and diffs before any Git operation.
- Treat `.env`, secrets, credentials, production data, and infrastructure endpoints as non-publishable.
- Prefer reversible changes and describe rollback for high-risk work.

## Completion gate

For code or configuration changes, invoke `verification-harness` before completion. Report changed files, checks run, failures or omissions, and remaining risk. Evidence is required; “should work” is not a passing result.
