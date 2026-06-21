---
name: verification-harness
description: 코드·설정 변경 완료 전 실행하는 KOCLO 검증 하네스. 테스트, lint, typecheck, build, diff/API/schema 검토와 반례 검증을 수행한다.
---

# Verification Harness

## 1. Define scope

- Capture `git status`, staged/unstaged diff, and changed-file list.
- Restate the behavior and acceptance criteria that must be proven.
- Separate pre-existing failures and user changes from this task.

## 2. Automated checks

Discover commands from repository configuration instead of guessing. Run the narrowest relevant checks first, then broader checks justified by the change:

- unit tests
- integration or end-to-end tests
- lint and formatting checks
- typecheck or static analysis
- build or import/compile smoke checks

Record command, exit status, and meaningful result. Do not conceal failures.

## 3. Diff review

Review the complete diff for:

- unrelated files or unnecessary refactoring
- accidental generated files, secrets, debug output, and local paths
- public API, route, response, event, or CLI contract changes
- database schema, migration, seed, or persistent-data changes
- configuration and production-only behavior changes
- missing tests, docs, compatibility handling, or rollback notes

## 4. Counterexample loop

Try to disprove the implementation with relevant cases:

- empty, zero, null, missing, malformed, and boundary inputs
- duplicate requests, partial failures, timeouts, and retries
- concurrent access, stale state, and race conditions
- production configuration differences and unavailable dependencies
- adjacent-feature regression scenarios

If a counterexample fails, fix the issue and restart the affected checks and diff review. Stop after the same blocker repeats three times and report the blocker rather than looping indefinitely.

## 5. Verdict

Return `PASS`, `FAIL`, or `INCOMPLETE` with:

- acceptance criterion and evidence
- checks run and results
- API/schema/config impact
- counterexamples attempted
- remaining unverified risk

Do not claim completion without fresh evidence.
