---
name: reality-gate
description: >-
  Detect and close the gap between a green test suite and a system that breaks on the real
  database, real config, or real client. Use when tests pass but agent-loop, manual QA, or
  production runs fail; when writing acceptance criteria for a coding-agent packet or PR that
  touches a persistence, config, or response-shape seam; or when auditing a repo's tests for
  tautological mocks, silent integration skips, hand-written schemas, or a regression replay
  suite that lives outside the repo.
user-invocable: true
license: MIT
compatibility: "Stack-agnostic rules; bundled audit script counts Go repos in depth and degrades gracefully elsewhere."
metadata:
  version: "1.1.0"
allowed-tools: Read Edit Write Glob Grep Bash Agent AskUserQuestion
---

# Reality Gate

> **This skill exists to stop:** a coding agent's green test suite from being accepted as proof that the code works against the real database, real configuration, and real client — when the agent wrote the code, the fake, the fixture, and the test in the same turn.

## 🤖 0. HOW TO USE

Choose one mode:

- **Audit** (default when tests are green but real runs fail): run `scripts/audit.sh [repo] --probe`, confirm each RED by opening the cited files, map the last real-run bugs to the ten mechanisms, write the report to `.jimmy/docs/reality-gate-audit.md` (kit default), or to the report location the target repo's AGENTS.md already names.
- **Gate**: write or review acceptance criteria for a packet/PR with `templates/acceptance-criteria.md`. Seam changes get a reality AC; exit code 0 is not evidence.
- **Build**: stand up the in-repo regression replay suite (Workflow C) on the first seam change, then grow it one case per real-run bug.

Outputs: an audit scorecard (mechanism → evidence → bug it caused → fix), an AC block the reviewer reruns and pastes, and a tracked replay suite. Self-contained: copy the directory anywhere; it links to nothing outside itself.

## 1. Core claim

A green suite proves "code matches the agent's assumptions", not "code matches reality".
Bugs live at the seams the agent assumed away. One rule closes the gap:

> **No change touching a persistence, config, or client-facing seam is verified until it
> has been observed against something the agent did not write** — a real schema, a
> container that actually ran, a recorded real request, or a diff against the legacy system.

Two corollaries, each earned by a bug that passed every gate above (2026-09-14):

- **The thing that ran must be the thing that runs.** A real container is not evidence if it
  is a different engine version from the deployed one. A query carrying a 350 KB JSON column
  through `ORDER BY` failed on the deployed MySQL 9.4 (`Error 1038: Out of sort memory`) and
  passed on the mysql:8 container the suite booted — at any payload size.
- **Correct is not the same as affordable.** Every mechanism below asks "does it match
  reality". None asks "what does it cost" — how many queries, rows, bytes or remote calls one
  request now spends. A read that pulls 350 KB to return 30 bytes, or a loop that issues one
  query per item, is green on all of them, and nobody without database experience knows to
  ask. Make the cost a printed number instead of a judgement call, and a reviewer who knows
  nothing about the engine can still see that it is wrong.

Do not demand test-first for its own sake. Ask for tests, then gate on outcome evidence.
Strict TDD-in-the-loop costs tokens and still produces the ten failures below. A rule that
lives in prose or a table, but not in a checklist or an acceptance command, does not exist
for an agent: it optimizes for the AC it is given.

## 2. The ten mechanisms (measured by `scripts/audit.sh`; 7, 8 and 10 are heuristics the AC then proves)

| # | Mechanism | Tell-tale | Fix (details in [REFERENCE.md](REFERENCE.md)) |
|---|---|---|---|
| 1 | Integration tests skip silently | tagged suite exits 0 with 0 tests when Docker is down; AC is `go test ./...` only | loud skip: fail unless `INTEGRATION_SKIP_OK=1`; AC shows `--- PASS` lines |
| 2 | Hand-written test schema, invented fixtures | DDL in a test helper "with only the columns readers need"; no fixture came from a real row | DDL dumped from the real read-only DB; fixtures are sanitized real rows/documents |
| 3 | Tautological fakes at the seam | dozens of `fakeXRepo`; tests assert recorded calls or SQL text | fakes for pure logic only; every DB-owning file gets a container test; ban SQL-text asserts |
| 4 | Replay suite outside the repo | reports name a script git does not contain | tracked `scripts/certify/`, parameterized by base URL and DSN, named in AC |
| 5 | Wiring and config untested | many env keys, few in `.env.example`; composition tests pass empty `Deps{}` | one boot test per process; env-example drift check |
| 6 | No client contract evidence | zero golden responses; many `omitempty`; OpenAPI never validated | golden pairs captured from the real client; response validated against the schema |
| 7 | Test engine is not the real engine | container image pinned to a major (`mysql:8`) while the deployed server reports another version; nobody compares them | pin the image to the deployed version from ONE constant; an `engine-parity` script prints both `VERSION()`s side by side (template in REFERENCE §7) |
| 8 | Cost blindness at the seam | the AC for a seam change states no cost number at all — queries, rows or bytes per request, calls to another service, response size — so a correct-but-expensive change is green on every gate | AC-007: one measured number per seam touched, taken on real-sized data; the reviewer reads a number, not a judgement (REFERENCE §8 lists which number per seam) |
| 9 | Test harness reads the developer's environment | a test fails (or passes) only under the task runner; the Makefile does `-include .env` plus `export`, or test setup loads a dotenv file, so local values reach the suite | the harness clears every key listed in `.env.example` before it builds config; AC-008 runs the suite through the task runner and directly, both green with the same test count |
| 10 | App clock vs database clock | the app stamps a time and the database compares it with its own `now()` (or the reverse); exact `<=` assertions across the two; a test pins a calendar date that will pass | one clock per comparison; tests make a row due on the database clock instead of sleeping; time assertions carry a stated tolerance; dates derive from the clock under test |

For behavior that is proven by driving the running app (UI, API, webhook, consumer), the executable recipe lives in a project-local verify skill built by `verify-app`; this skill decides what that recipe's evidence must contain.

## 3. Workflow A — audit (about 30 minutes)

1. `bash <skill>/scripts/audit.sh [repo-root] --probe`. The probe runs one tagged package to
   catch mechanism 1 and is safe with Docker down.
2. Confirm every RED/AMBER at the cited file. Counts are heuristics, not verdicts.
3. Find the latest real-run bug list (QA notes, handoff, post-mortem). Map each bug to a
   mechanism; a bug that maps to none earns a new row before any recommendation. A test that
   fails only under the task runner, or only on one machine or at one time of day, is a
   mechanism 9 or 10 candidate: read the failing assertion line and what the runner exports
   before forming a timing hypothesis.
4. Check whether the rule that would have caught it exists somewhere un-gated (prose in a
   skill, a table, a README). Report that as the root cause, not the missing test.

## 4. Workflow B — acceptance criteria

Use [templates/acceptance-criteria.md](templates/acceptance-criteria.md). Reviewer rules:

- Classify: **pure logic**, **seam** (SQL, document store, cache, gRPC/HTTP client, config,
  response shape, auth), or **both**. Seam changes get a reality AC. No exceptions.
- A reality AC is one of: (a) a named container-backed test whose `--- PASS` line is pasted;
  (b) replay of recorded real requests against a running server with a field-level diff;
  (c) a diff of the row/document written by the new code vs the legacy system.
- The AC command must fail when evidence is absent. `exit 0`, "integration green", and grep
  gates on prose or whitespace are not evidence.
- Behavior change: name the tests allowed to change and the invariant that must hold.
  Refactor: forbid test edits. Never both in one packet.
- Executor prose is not evidence. The reviewer reruns and pastes.

## 5. Workflow C — in-repo regression replay suite

1. Capture real client traffic (browser devtools, proxy, access log) for the flows in scope
   into `testdata/replay/<flow>/<n>.json`: request, legacy response, identity (token redacted).
2. Normalize volatile fields through one shared allowlist file, never per test.
3. `scripts/certify/run.sh --base <url> --legacy <url>` replays every case, diffs `data`
   field by field, prints one line per case, exits non-zero on any new diff. Accepted
   divergences live in one tracked file, each with a decision reference.
4. Make the run command an AC for every packet touching a listed flow; run it in CI when a
   dev database is reachable.
5. Every real-run bug adds one capture before its fix lands.

## 6. Reject in review

- "Integration green" without `-v` output showing tests ran.
- A fixture that gained a column, enum value, or field so a test could pass.
- A fake written in the same commit as the code it fakes, with no container test for the
  real implementation.
- `strings.Contains(query, ...)` or exact-SQL assertions.
- An expected value changed to match new output without saying why the old one was wrong.
- A report naming a script the repo does not contain.
- An integration run whose engine version was never compared with the deployed one.
- A seam change whose AC states no cost number (queries, rows, bytes or calls per request)
  when the seam is a database, another service, or a list/response path.
- An acceptance harness that builds config from whatever the shell or task runner exported.
- An exact comparison between an app-minted timestamp and the database's `now()`; a `sleep`
  used to make a row due; a literal calendar date that a test needs to stay in the future.

## 7. Test-double rules the gate enforces (shared with `tdd-go`)

1. A test is triggered by a new observable behavior, never by a new method or type.
2. Fake only unmanaged dependencies (other services, message buses, storage, clock). Databases
   run for real in containers; a database shared with another application is a contract, so its
   DDL is dumped, not hand-written, and fixtures are real-shaped rows/documents.
3. The feature's own repository/reader/writer is never a mocking target.
4. Four or more fakes in one test means the decision logic must be extracted into a pure
   function (functional core) and the shell covered by one acceptance test.
5. No change-detectors: no SQL-text, call-count, call-order, or unexported-state assertions.
6. Every remaining fake has a contract test or recorded fixture proving it matches the real thing.

## 8. Porting to another repo or stack

Copy the directory. Run the audit script for what it can count; add stack greps at the
marked block (PHPUnit `@group integration` vs `markTestSkipped`, Jest `describe.skip`,
Vitest `test.skipIf`, Playwright fixtures). Keep the table and the AC rules unchanged. Add
one pointer line to the target repo's AGENTS.md or CLAUDE.md: "seam changes require a
reality AC (skill: reality-gate)". Without the pointer the skill is never loaded.
