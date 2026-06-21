#!/usr/bin/env node

const context = [
  '[KOCLO ERP Team plugin active]',
  'For every KOCLO implementation, bug fix, refactor, API/DB/UI change, or review, load and follow the team-development-rules skill before editing.',
  'Before editing, inspect repository instructions, the existing code, tests, and ownership boundaries.',
  'Keep changes scoped; separate calculation, I/O, and presentation.',
  'NAS/remote access is locked until /nas on. Destructive commands are locked until /danger on.',
  'Every Docker command and every git commit or push require explicit approval even while a gate is open.',
  'Do not deploy, migrate, modify production data, or run destructive commands without explicit approval.',
  'For code or configuration changes, load and run the verification-harness skill before claiming completion.',
  'If a KOCLO repository does not yet contain the KOCLO workflow block in AGENTS.md or CLAUDE.md, use koclo-project-setup to propose the smallest integration and wait for explicit approval before editing it.',
  'Use koclo-ui for the interactive workflow menu.'
].join('\n');

process.stdout.write(JSON.stringify({
  hookSpecificOutput: {
    hookEventName: 'SessionStart',
    additionalContext: context
  }
}));
