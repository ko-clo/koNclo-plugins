#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';

let input = {};
try {
  input = JSON.parse(await new Promise((resolveInput) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (chunk) => { data += chunk; });
    process.stdin.on('end', () => resolveInput(data || '{}'));
  }));
} catch {
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'deny',
      permissionDecisionReason: '안전 훅이 도구 입력을 해석하지 못해 명령을 중단했습니다.'
    }
  }));
  process.exit(0);
}

const command = String(input?.tool_input?.command || '').trim();
if (!command) {
  process.stdout.write('{}');
  process.exit(0);
}

const cwd = resolve(input?.cwd || process.env.CLAUDE_PROJECT_DIR || process.cwd());
const projectKey = createHash('sha256').update(cwd).digest('hex').slice(0, 20);
const stateDir = join(tmpdir(), 'koclo-erp-safety', projectKey);

async function isGateOpen(name) {
  try {
    const expiry = Number((await readFile(join(stateDir, `${name}.unlock`), 'utf8')).trim());
    return Number.isFinite(expiry) && expiry > Date.now();
  } catch {
    return false;
  }
}

function decide(permissionDecision, permissionDecisionReason) {
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision,
      permissionDecisionReason
    }
  }));
  process.exit(0);
}

const gitPublish = /\bgit\b[^\n;&|]*\b(?:commit|push)\b/i.test(command);
const gitDestructive = /\bgit\b[^\n;&|]*\b(?:reset\s+--hard|clean\s+-[^\s]*f|checkout\s+--|restore\b[^\n;&|]*--(?:source|staged|worktree)|commit\b[^\n;&|]*--amend|push\b[^\n;&|]*(?:--force|-f\b))/i.test(command);
const filesystemDestructive = /(?:^|[;&|\n]\s*|\bsudo\s+|\bcommand\s+)rm\s+(?:-[^\s]*[rf][^\s]*\s+)+|\b(?:DROP\s+(?:DATABASE|SCHEMA|TABLE)|TRUNCATE\s+TABLE|DELETE\s+FROM)\b/i.test(command);
const dockerDestructive = /\bdocker\b[^\n;&|]*\b(?:system\s+prune|container\s+prune|volume\s+prune|image\s+prune|network\s+prune|compose\s+down\b[^\n;&|]*\s-v\b|rm\b|rmi\b)/i.test(command);
const destructive = gitDestructive || filesystemDestructive || dockerDestructive;

const remoteAccess = /\b(?:ssh|scp|sftp|smbclient|mount_smbfs|mount_nfs)\b/i.test(command)
  || /\brsync\b[^\n;&|]*(?:\w+@[^\s:]+:|[^\s:]+:\/)/i.test(command)
  || /(?:^|[\s'\"])(?:\/Volumes\/[^\s'\"]+|\/volume\d+\/[^\s'\"]*)/i.test(command)
  || /\b(?:DOCKER_HOST|docker\s+(?:--host|-H))\s*(?:=|\s)\s*(?:ssh|tcp):\/\//i.test(command);
const remoteMutation = remoteAccess && (
  /\b(?:rm|mv|cp|mkdir|rmdir|touch|chmod|chown|install|tee|truncate|dd|docker|kubectl|git\s+(?:pull|fetch|commit|push))\b/i.test(command)
  || /\bsed\b[^\n;&|]*\s-i(?:\s|$)/i.test(command)
  || /(?:^|[^<])>{1,2}(?!>)/.test(command)
  || /\bcurl\b[^\n;&|]*(?:-X|--request)\s*(?:POST|PUT|PATCH|DELETE)\b/i.test(command)
);

const gateOpenCommand = /\bgate-control\.mjs[\"']?\s+(?:nas|danger)\s+on(?:\s|$)/i.test(command);
if (gateOpenCommand) {
  decide('ask', '안전 gate를 여는 작업은 사용자의 명시적 승인이 필요합니다.');
}

if (remoteAccess && !(await isGateOpen('nas'))) {
  decide('deny', 'NAS/원격 접속 gate가 닫혀 있습니다. 먼저 /nas on [minutes]을 명시적으로 실행하세요.');
}

if (destructive && !(await isGateOpen('danger'))) {
  decide('deny', '파괴적 작업 gate가 닫혀 있습니다. 작업 내용을 검토한 뒤 /danger on [minutes]을 명시적으로 실행하세요.');
}

if (gitPublish) {
  decide('ask', '팀 정책에 따라 모든 git commit/push는 매번 사용자 승인이 필요합니다.');
}

if (remoteMutation) {
  decide('ask', 'NAS/원격 시스템을 변경하는 명령은 gate가 열려 있어도 매번 사용자 승인이 필요합니다.');
}

const hasDocker = /\bdocker\b/i.test(command);
if (hasDocker) {
  decide('ask', '팀 정책에 따라 읽기 전용 조회를 포함한 모든 Docker 접속은 매번 사용자 승인이 필요합니다.');
}

process.stdout.write('{}');
