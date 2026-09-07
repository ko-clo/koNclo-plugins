#!/usr/bin/env node

import { execFileSync } from 'node:child_process';
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

const gateOpenCommand = /\bgate-control\.mjs[\"']?\s+(?:nas|danger|testfile)\s+on(?:\s|$)/i.test(command);
if (gateOpenCommand) {
  decide('ask', '안전 gate를 여는 작업은 사용자의 명시적 승인이 필요합니다.');
}

if (remoteAccess && !(await isGateOpen('nas'))) {
  decide('deny', 'NAS/원격 접속 gate가 닫혀 있습니다. 먼저 /nas on [minutes]을 명시적으로 실행하세요.');
}

if (destructive && !(await isGateOpen('danger'))) {
  decide('deny', '파괴적 작업 gate가 닫혀 있습니다. 작업 내용을 검토한 뒤 /danger on [minutes]을 명시적으로 실행하세요.');
}

// ── 테스트 파일 커밋 차단 ────────────────────────────────────────────
// 테스트 파일을 만드는 것은 자유다. 막는 것은 그것이 커밋에 들어가는 것 하나다.
// (2026-08-02 사고: 지시받지 않은 회귀 테스트 859줄이 기능 커밋에 함께 들어갔다.
//  CLAUDE.md §완료 기준은 "검증 스크립트가 없으면 없다고 보고한다"이지 "만들어라"가 아니다.)
const TEST_PATH_RE = /(^|\/)(test_[^/\s]+\.py|[^/\s]+_test\.py|[^/\s]+_scenarios\.py|[^/\s]+\.(?:test|spec)\.[cm]?[jt]sx?)$|(^|\/)tests?\//i;

function stagedTestFiles() {
  // 커밋 직전 staged 전수 검사 — 어떤 경로로 스테이징됐든 최종 방어선에서 잡힌다.
  const collected = [];
  // --name-status 로 읽어 삭제(D)를 제외한다 — 테스트를 커밋에서 **빼는** 정리 작업은
  // 이 가드가 장려하는 방향이라 절대 막지 않는다(막으면 잘못 커밋된 테스트를 정리조차 못 한다).
  const probes = [['diff', '--cached', '--name-status']];
  if (/\bcommit\b[^\n;&|]*\s-[A-Za-z]*a|\bcommit\b[^\n;&|]*--all\b/i.test(command)) {
    probes.push(['diff', '--name-status']);         // commit -a 는 추적 중 수정분까지 커밋한다
  }
  if (/\badd\b\s+(?:-[A-Za-z]*[Au][A-Za-z]*|--all|\.|:\/|\*)(?:\s|$)/i.test(command)) {
    probes.push(['status', '--porcelain']);         // git add -A / . 로 쓸려 들어가는 경로
  }
  for (const args of probes) {
    try {
      const out = execFileSync('git', ['-C', cwd, ...args], { encoding: 'utf8', timeout: 3000 });
      for (const raw of out.split('\n')) {
        if (!raw.trim()) continue;
        let status, path;
        if (args[0] === 'status') { status = raw.slice(0, 2); path = raw.slice(3); }
        else { const parts = raw.split('\t'); status = parts[0]; path = parts[parts.length - 1]; }
        if (/D/.test(status)) continue;             // 삭제분은 차단 대상이 아니다
        if (path.trim() && TEST_PATH_RE.test(path.trim())) collected.push(path.trim());
      }
    } catch {
      // git 조회 실패는 판정 근거로 삼지 않는다(레포 밖 실행 등). 명시 경로 검사는 그대로 동작.
    }
  }
  return [...new Set(collected)];
}

const gitStages = /\bgit\b[^\n;&|]*\b(?:add|commit)\b/i.test(command);
if (gitStages && !(await isGateOpen('testfile'))) {
  const explicit = command.split(/[\s'"]+/).filter((token) => TEST_PATH_RE.test(token));
  const hits = [...new Set([...explicit, ...stagedTestFiles()])];
  if (hits.length) {
    decide('deny',
      `테스트 파일을 커밋에 넣으려 합니다 — 기본 차단 (${hits.length}개: ${hits.slice(0, 5).join(', ')}). `
      + '테스트 파일 생성은 자유지만 커밋 포함은 사고입니다. 지시받지 않은 검증 스크립트라면 '
      + 'scratchpad 에서 확인을 끝내고 커밋에서 빼세요. 기존 테스트를 고쳐야만 통과하는 변경은 '
      + '설계를 되짚을 신호입니다. 정말 필요하면 파일·줄수·이유를 보고하고 사용자가 '
      + '/testfile on [minutes] 을 실행해야 합니다.');
  }
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
