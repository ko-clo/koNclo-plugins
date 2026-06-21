#!/usr/bin/env node

import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const script = fileURLToPath(new URL('./session-context.mjs', import.meta.url));

test('injects mandatory KOCLO development and verification policy', () => {
  const result = spawnSync(process.execPath, [script], { encoding: 'utf8' });

  assert.equal(result.status, 0, result.stderr);
  const output = JSON.parse(result.stdout);
  assert.equal(output.hookSpecificOutput.hookEventName, 'SessionStart');

  const context = output.hookSpecificOutput.additionalContext;
  assert.match(context, /team-development-rules/);
  assert.match(context, /verification-harness/);
  assert.match(context, /koclo-project-setup/);
  assert.match(context, /explicit approval before editing/);
});
