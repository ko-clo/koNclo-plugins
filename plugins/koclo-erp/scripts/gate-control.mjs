#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';

const gateNames = new Set(['nas', 'danger', 'testfile']);
const actions = new Set(['on', 'off', 'status']);
const gate = process.argv[2];
const action = process.argv[3] || 'status';

if (!gateNames.has(gate) || !actions.has(action)) {
  console.error('Usage: gate-control.mjs <nas|danger|testfile> <on [minutes]|off|status>');
  process.exit(2);
}

const projectDir = resolve(process.env.CLAUDE_PROJECT_DIR || process.cwd());
const projectKey = createHash('sha256').update(projectDir).digest('hex').slice(0, 20);
const stateDir = join(tmpdir(), 'koclo-erp-safety', projectKey);
const stateFile = join(stateDir, `${gate}.unlock`);

async function readExpiry() {
  try {
    const value = Number((await readFile(stateFile, 'utf8')).trim());
    return Number.isFinite(value) ? value : 0;
  } catch (error) {
    if (error?.code === 'ENOENT') return 0;
    throw error;
  }
}

if (action === 'on') {
  const requestedMinutes = Number(process.argv[4] || 30);
  if (!Number.isFinite(requestedMinutes)) {
    console.error('minutes는 숫자여야 합니다.');
    process.exit(2);
  }

  const minutes = Math.min(120, Math.max(1, Math.floor(requestedMinutes)));
  const expiresAt = Date.now() + minutes * 60_000;
  await mkdir(stateDir, { recursive: true, mode: 0o700 });
  await writeFile(stateFile, String(expiresAt), { mode: 0o600 });
  console.log(`${gate.toUpperCase()} gate가 ${minutes}분 동안 열렸습니다.`);
} else if (action === 'off') {
  await rm(stateFile, { force: true });
  console.log(`${gate.toUpperCase()} gate를 닫았습니다.`);
} else {
  const expiresAt = await readExpiry();
  const remainingMs = expiresAt - Date.now();
  if (remainingMs > 0) {
    console.log(`${gate.toUpperCase()} gate가 열려 있습니다. 약 ${Math.ceil(remainingMs / 60_000)}분 남았습니다.`);
  } else {
    await rm(stateFile, { force: true });
    console.log(`${gate.toUpperCase()} gate가 닫혀 있습니다.`);
  }
}
