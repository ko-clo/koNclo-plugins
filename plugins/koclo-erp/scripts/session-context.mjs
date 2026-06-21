#!/usr/bin/env node

const context = [
  '[KOCLO ERP Team plugin active]',
  'Before editing, inspect the existing code and ownership boundaries.',
  'Keep changes scoped; separate calculation, I/O, and presentation.',
  'NAS/remote access is locked until /nas on. Destructive commands are locked until /danger on.',
  'Every Docker command and every git commit or push require explicit approval even while a gate is open.',
  'Do not deploy, migrate, modify production data, or run destructive commands without explicit approval.',
  'For code changes, use the verification-harness skill before claiming completion.',
  'Use koclo-ui for the interactive workflow menu.'
].join('\n');

process.stdout.write(JSON.stringify({
  hookSpecificOutput: {
    hookEventName: 'SessionStart',
    additionalContext: context
  }
}));
