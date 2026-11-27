# Task Packet — template

> Orchestrator: copy this file, fill EVERY section, save as `.orchestrate/packets/NNN-<slug>.md`.
> Write for an executor that has never seen the conversation. Executor: execute exactly;
> if a section contradicts the code you find, STOP and report the contradiction instead of improvising.

```md
# Packet NNN — <slug>

## Objective
<1–3 sentences: what exists after this packet that didn't before.>

## Approved plan and routing
- Canonical plan: `.orchestrate/plans/NNN-<slug>.md`, version `<vN>`
- Approval state: `APPROVED` | `PENDING` | `BLOCKED`
- Acceptance contract: `.orchestrate/contracts/NNN-<slug>.json`
- Executor: `<model, chosen when the packet is written: SKILL.md "Model routing"; never one the project forbids>`
- Advisor: `PLAN_APPROVED <path to the review file>` | `waived by <who> — <reason>` | omit when the plan touches none of queue, lease, retry, backoff, lock, fencing, idempot-, rebalance, offset, outbound, state machine
- Scope: `<inventory path>#<id>[, <id>…]` (the inventory rows this packet builds; each row's decision is `build NNN`) | `owner <date> — "<the owner's words>"` | `fix — <the landed behaviour or audit finding it fixes>`
- Worktree: `<absolute path root created with git worktree add; the executor works only here>`
- Ports and scratch: `<ports derived from the packet number, e.g. service 18000+NNN, dev server 5200+NNN; files under /tmp/<repo>-NNN/>`
- Owned write paths: `<exact files/directories; must not overlap a parallel packet>`
- Depends on / integration order: `<packet IDs or none>`
- Executor preflight evidence: `<recon ID and observed checkout/packet/workspace/temp/tooling check; required before dispatch>`

## Context (read these first, in order)
- <repo-relative file paths the work touches, with one line each on why>
- Rules that bind this work: AGENTS.md · .jimmy/adr/0001 (legacy schema parity) ·
  .jimmy/docs/be-rebuild/03-design.md §Invariants · .jimmy/docs/be-rebuild/05-language.md (naming gate)
- <any prior packet this builds on>

## Plan
1. <ordered, concrete steps — file-level, not vague>
2. …

## Constraints / Out of scope
- Do NOT touch: <files/areas>
- Do NOT rename/invent concepts — names come from 05-language.
- Do NOT spawn descendants, call Planner/Advisor, or expand owned write paths.
- STOP and report if source, schema, ownership, or acceptance evidence contradicts this packet.
- STOP and report if a field, endpoint or seam this packet needs is not exposed by its owner yet;
  do not work around another feature's ownership.
- Do NOT open a browser or a UI-driving tool. The root's single verification agent drives the UI
  after you report; verify with the gates, component tests, and calls against the real service.
- Do NOT bind ports, CDP ports, profiles or binary paths other than the ones listed above.
- <packet-specific constraints, e.g. "write BSON field-for-field per appendix E">

## Volume and budget
<!-- Required; the linter rejects a packet without it. A packet that adds a query over a growing
     table or a loop on a hot path (send, dispatch, ingest, import) fills all three lines with
     numbers. Any other packet writes one line: `- N/A — <why no such query or loop is touched>`.
     AC-007 (reality-gate) is the per-request cost; this section fixes the data size it is
     measured on and the target it must meet.
     Before the run, the Proof line says what the number decides (ship, change the plan) and the
     noise floor (the spread of two runs of unchanged code); a gap inside the spread is no result.
     A line that reports a measured number (a baseline here, the result at Verify) carries
     `runs: <count, median and range>` and `limiter: <resource or code path that bounded it, from a
     profile or counters taken during the run>`, plus the machine's `uptime` load at the time; the
     linter fails VOLUME_BUDGET without the first two (pstack principle-explain-the-number, MIT,
     Lauren Tan). -->
- Data volume: <rows or items the path sees after 13 months of production growth>
- Budget: <latency p99 or throughput target, e.g. "count < 50 ms", "220 sends/s per worker">
- Proof: <the load run (provider latency > 0) or EXPLAIN ANALYZE on a seeded realistic size, named as an AC; what the number decides and the noise floor>
- Measured: <only once a number exists: value with unit — runs: <count, median, range> — limiter: <what bounded it> — load: <uptime 1-min load>>

## Tests
<!-- Required; the linter rejects a packet without it (TESTS_SECTION). One line per NEW test, or
     one line `- none — <reason>`. Changed existing tests are not listed.
     - At most 3 new tests per packet (TEST_BUDGET). More needs a distinct named risk on every line
       and `test budget: waived by <who> — <reason>` in this section.
     - Every line names the behaviour that breaks silently without the test (TEST_RISK). Two lines
       guarding the same risk are one test.
     - Every line names its layer (TEST_LAYER), and one risk or AC is tested at one layer only:
       `unit:` a table for an input rule (`Validate()`) or a pure decision (diff, precedence,
       collapse), every row here; `route:` one row proving the handler path maps the rule (400
       with its code), never the table again; `acceptance:` only for a seam (the row written and
       read back, the request sent, a real engine); `vitest:` SPA code. A unit test and an
       acceptance test for the same AC fail the lint.
     - No test of an unexported helper whose numbers a route test already asserts, of a
       constructor default, a getter or an id generator, or of a dev fake's own rules (test the
       real client against the fake). Assert the error code the caller branches on, not the message.
     - SPA (vitest): branching logic in a pure-function `.test.ts`, the screen gets one wiring
       case; no second copy of a test per locale (the locale-file guard covers keys and plurals);
       no empty, loading or copy-only case. A new test file pays a jsdom setup and its imports, so
       add a case to the existing file.
     - Every line passes the two-edit check (pstack, principle-test-behavior-not-implementation,
       MIT, Lauren Tan, github.com/cursor/plugins/tree/main/pstack): the test fails if the guarded
       behaviour is broken and still passes if the internals are rewritten. Write both halves:
       `fails if <behaviour broken>, passes if <internals changed>`.
     - Never a test that pins copy text, log text, exact SQL, DOM structure or classes, or a snapshot.
     - Never one case per role, finding or row (TEST_PER_ITEM, also checked in the AC lines): test
       the rule once, at its owner.
     - UI copy and layout are verified by the root's walk with screenshots, not by tests.
     - Reality ACs (the container tests named in AC-006 / AC-007 evidence) count against the budget
       like any other new test. -->
- new: <unit|route|acceptance|vitest>: <TestName, or "<file> › <case>" for vitest> — guards: <the behaviour that breaks silently without it>; fails if <behaviour broken>, passes if <internals changed>

## Verdict dimensions
- Implementation verdict: PENDING
- Evidence verdict: PENDING
- Runtime parity verdict: NOT_APPLICABLE
- Release verdict: BLOCKED_UNTIL_VERIFIED
- Landing verdict: UNLANDED

## Systemic drift route
- Contract route: <route class or none>
- Actions: <stable action IDs>
- Evidence owner: <owner>
- Runtime-fix owner: <owner>
- Allowance policy: <forbidden or explicitly bounded allowance>

The contract is the single source for commands and expected outcomes; the acceptance-reference
section below contains IDs only.

<!-- Add AC-006 when a container-backed test is the evidence (engine parity), and AC-007
     when the packet touches a cost-bearing seam — a database read or write, a call to
     another service, a list/response path (cost budget). Both come from skill reality-gate. Omitting them is a decision the
     packet states, not a default.
     An AC asks for evidence that a named risk is handled: one command and its expected outcome.
     It never asks for a list of test cases ("every finding has an assertion", "one case per
     role"); the new tests are listed once, in ## Tests, within its budget. -->

## Executor checks (code-only)
<!-- Run before reporting DONE; paste each command and its exit status. Nothing here needs a
     container, a database or a browser. Wave mode: SKILL.md "Wave mode (default)". -->
- Build, `vet` with the integration tags, lint, architecture lint: <commands>
- Unit tests of the packages this packet touches: <narrow commands>
- Skill/schema checkers and, for a frontend packet, the API check, typecheck, lint and the vitest file this packet wrote: <commands>
- Do NOT run container tests, the full frontend suite, `EXPLAIN`, migrations or the preflight.

## Root checks on the integration branch
<!-- Run by the root once on `feat/<wave>` after every packet of the wave merged; not by the
     executor. A packet that lands alone runs them on its own branch. A failure is traced to the
     merge that brought it and returns to this packet's executor as a delta. -->
- Every gate of `.orchestrate/gates`: run by `land.sh`, and before it by hand where a failure needs tracing
- Container-backed tests and reality ACs of this packet (AC-006 / AC-007 evidence): <named `-v` commands>
- Migrations up and down, `EXPLAIN` on the seeded size of Volume and budget, preflight: <commands or N/A>

## Acceptance references
- AC-001
- AC-002

## Report back (exact format)
- Status: `DONE` or `BLOCKED`
- Route metadata visible to Executor, or `not exposed`
- Changed files list · what each change does (1 line each)
- AC-001..AC-NNN exit statuses (root runs the commands from the contract)
- Anything you were unsure about or deviated on, flagged loudly
- UI packets: how to reach each state you built (URL + seed step), for the verification agent
- Remaining risks and integration assumptions
- Suggested commit message (one line, house style)
```
