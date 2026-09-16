# Scenario — reality-gate (written BEFORE the skill was promoted into the kit)

**Rationale:** a coding-agent loop produced hundreds of green test files while a QA agent driving the real UI against the dev database hit many 500s and wrong response shapes. The skill must explain the gap from repo evidence and change what "verified" means for the next packet, not ask for more unit tests.

**Sample input:** "All tests pass, including `make test-integration`, but manual QA on the dev database reports 500s on two detail endpoints and `null` where the client expects `[]`. Why, and what do we change first?"

**Expected behaviors:**
- [ ] Runs the silent-skip probe (tagged suite with Docker down) before trusting "integration green".
- [ ] Checks the test schema against the real schema instead of trusting fixtures; names any fixture-only column as the bug source.
- [ ] Locates the regression/replay script named in reports and verifies it is tracked in git.
- [ ] Maps each reported bug to one of the eight mechanisms and cites file:line evidence.
- [ ] Compares the integration container's engine version with `SELECT VERSION()` on the deployed database before treating a green container run as evidence; on a seam bug, asks what one request costs (queries, rows, bytes, calls) on real-sized data.
- [ ] Finds the rule that would have caught the bug living un-gated (prose/table, not checklist/AC) and reports that as root cause.
- [ ] Proposes a reality AC (named `-v` container test with pasted `--- PASS`, or replay diff) for the next packet; does not recommend stricter test-first.

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].

## Author run on the origin repo (evidence for the script, not an independent run)

Go backend rewrite running in parallel with a legacy system; about 390 source files, 354 test files, 48 integration-tagged files. `scripts/audit.sh . --probe` with Docker stopped:

```text
RED  no tracked replay/certify/smoke suite directory (mechanism 4)
RED  scripts named in reports/handoffs but absent from git: <two replay scripts> (mechanism 4)
RED  integration harness has 60 t.Skip sites and no loud-skip guard (mechanism 1)
RED  13 assertions on SQL text (mechanism 3)
RED  DDL hand-written in Go test helpers, no dumped .sql under testdata (mechanism 2)
RED  config keys (101) vs .env.example (14) drift (mechanism 5)
RED  no golden responses and no OpenAPI response validation (mechanism 6)
Probe: exit=0 · RUN=0 PASS=0 SKIP=0 · docker=no → the suite skips silently
```

Real-run bugs mapped: a 500 caused by a column present only in the test DDL (mechanism 2); a timestamp off by the local UTC offset found only by replaying a real token (2 + 4); `data: null` vs `[]` (6). Root cause found un-gated: the TDD skill's "one acceptance test per feature with real containers and real router" rule existed only in prose and a table, not in its checklist or any packet AC; 3 of 20 features had one. Fix applied at the origin: rule added to the TDD checklist, to the orchestrator's verify step, and to the repo's agent instructions.

## Rollout evidence on the origin repo (same day, still not an independent fresh-agent run)

Applied the skill's Workflow B/C to five features through an orchestrated cycle (four executor
packets, root verification of every AC). Each packet: delete owned-port fakes and change
detectors, add one acceptance file on a harness that calls the production engine builder with
a config pointing at containers carrying the dumped legacy DDL.

Outcome the old suite could not produce:
- A **production 500 on every draft save** when the optional geo-IP URL was unset: the
  composition root assigned a typed-nil client pointer into an interface field, so the nil
  guard never fired. Found by the first acceptance run with the default (client-less) config;
  fixed with a regression case that was red before and green after.
- Three tables one feature queries had **no test DDL at all**; nobody knew because that
  feature's only container test hand-wrote its own thirteen `CREATE TABLE`s.
- A tinyint column made a long-standing "unsupported type 999" fixture physically impossible;
  a `DATE` column made a `23:59:59` expiry expectation impossible; a `NOT NULL` name column
  had never been seeded — each a fixture that only fit the hand-written schema.
- Two client-visible defects (a flag always `false` for learners with history; tag names
  rendered empty) and one fail-open (map options at the wrong level → 200 with an empty list).
- Roughly 5,300 lines of fake-backed tests removed across five packages; ~115 acceptance
  cases added; every gate rerun by the reviewer, not trusted from executor prose.

Lesson recorded for the AC template: never make `grep -q` the consumer of a pipeline whose
producer must finish (`go test … | tee log | grep -q PASS` killed the test run with SIGPIPE and
reported a false failure). Read the log after the process exits.
