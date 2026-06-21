#!/usr/bin/env node

import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdirSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const script = fileURLToPath(new URL('./safety-guard.mjs', import.meta.url));
const testRoot = join(tmpdir(), `koclo-safety-test-${process.pid}`);
const cwd = join(testRoot, 'project');

function run(command) {
  const result = spawnSync(process.execPath, [script], {
    input: JSON.stringify({ tool_input: { command }, cwd }),
    encoding: 'utf8',
    env: { ...process.env, TMPDIR: testRoot }
  });
  assert.equal(result.status, 0, result.stderr);
  return JSON.parse(result.stdout || '{}')?.hookSpecificOutput?.permissionDecision;
}

function openGate(name) {
  const key = createHash('sha256').update(cwd).digest('hex').slice(0, 20);
  const dir = join(testRoot, 'koclo-erp-safety', key);
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, `${name}.unlock`), String(Date.now() + 60_000));
}

test('git commit and push always ask', () => {
  assert.equal(run('git commit -m test'), 'ask');
  assert.equal(run('git -C repo push origin main'), 'ask');
});

test('all Docker access asks', () => {
  assert.equal(run('docker ps'), 'ask');
  assert.equal(run('docker compose logs api'), 'ask');
  assert.equal(run('docker restart api'), 'ask');
  assert.equal(run('sudo docker inspect api'), 'ask');
});

test('remote access needs NAS gate and remote mutation still asks', () => {
  assert.equal(run('ssh user@example.invalid uptime'), 'deny');
  assert.equal(run('sudo ssh user@example.invalid uptime'), 'deny');
  openGate('nas');
  assert.equal(run('ssh user@example.invalid uptime'), undefined);
  assert.equal(run("ssh user@example.invalid 'rm old.log'"), 'ask');
});

test('destructive command needs danger gate', () => {
  assert.equal(run('rm -rf build-cache'), 'deny');
  assert.equal(run('sudo rm -rf build-cache'), 'deny');
  openGate('danger');
  assert.equal(run('rm -rf build-cache'), undefined);
});

test('opening a gate asks for user approval', () => {
  assert.equal(run('node "/plugin/scripts/gate-control.mjs" nas on 30'), 'ask');
  assert.equal(run('node "/plugin/scripts/gate-control.mjs" danger on 10'), 'ask');
});
