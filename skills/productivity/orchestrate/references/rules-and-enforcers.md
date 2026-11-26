# Rules and what enforces them

A rule that lives only in prose gets skipped under load: in one sprint the root skipped four of them
and nothing failed. This table says, for every non-negotiable rule of `SKILL.md` and for the
lifecycle rules a script can read, what fails when it is broken. `prose only` means nothing checks it.

**The `/correct` rule.** A `prose only` rule that is broken twice gets a check in the same change that
records the second break. The check's failure message names the fix, and a test reproduces the real
mistake and fails without the check. Prose is the last resort. The general principle is pstack's
principle-encode-lessons-in-structure (MIT, Lauren Tan, github.com/cursor/plugins/tree/main/pstack):
a lesson written as an instruction a second time becomes a lint, a metadata field, a runtime check or
a script; when the fix is structural, only the structural fix ships, because the instruction is the
symptom. A lesson that needs judgement stays prose, made prominent and given one example of the failure.

Scripts are called from the installed skill: `<installed-skill-dir>/scripts/`. Opt-outs are in the last column.

## Non-negotiable rules

| Rule | Enforced by | Opt out |
|---|---|---|
| Root writes plans, packets, ADRs, reviews, and performs final verification. | prose only | none |
| Planner and Advisor never edit, execute commands, direct Executors, or contact each other. | `advisor-review.sh` runs its route in a read-only sandbox; the rest is prose only | none |
| Executors do not spawn descendants and do not use Planner/Advisor routes. | prose only (a packet constraint) | none |
| Executors never open a browser; one verification agent owns the one browser. | prose only (a packet constraint) | none |
| Nothing lands except through `land.sh` with every gate green on the merged result. | `land.sh` runs `.orchestrate/gates` on the merged HEAD and merges with that SHA; going around the script is prose only | none |
| An explicit `no subagents` instruction wins. | prose only | none |
| Never weaken permissions, approvals, Goal controls, legacy parity, or repo instructions. | prose only | none |
| Large/architectural sprint: preview the roadmap and workflow before dispatching packet 001. | prose only | none |
| Every owner question is a decision brief (skill `ketchup`); a bundled one-liner is not a question. | `orchestration_lint.py --phase handoff` for HANDOFF (`OWNER_*`, `BRIEF_*`); chat text is prose only | none |
| A misunderstood packet is an orchestration defect: fix the packet, not the model. | prose only | none |

## Lifecycle rules a script reads

| Rule | Enforced by | Opt out |
|---|---|---|
| Land only on a quiet machine: timing tests fail under load. | `land.sh` waits for the 1-minute load average to drop to `ORCH_MAX_LOAD`; exit 3 after `ORCH_LOAD_WAIT` s | `ORCH_MAX_LOAD=0`, or a larger `ORCH_MAX_LOAD` / `ORCH_LOAD_WAIT` |
| A forge failure after green gates must not cost a second run of the gates. | `land.sh` retries the create call (`ORCH_CREATE_TRIES`, `ORCH_CREATE_SLEEP`), prints the forge's response, and `--resume` / `ORCH_SKIP_GATES_FOR_SHA` skips gates only for the commit recorded green | do not pass `--resume` |
| A plan touching queue, lease, retry, backoff, lock, fencing, idempotency, rebalance, offset, outbound calls or a state machine needs an independent Advisor. | `orchestration_lint.py --phase dispatch`: `ADVISOR_REQUIRED` unless the packet has `advisor: PLAN_APPROVED <existing review file>` or `advisor: waived by <who> — <reason>` | the named waiver |
| Every packet names its executor; the project can forbid models (the root's own). | `orchestration_lint.py --phase dispatch`: `EXECUTOR_FORBIDDEN` for a missing `executor:` line or a model in `forbidden_executor_models` | edit `.claude/orchestrator.json` with the owner's agreement |
| A health pass runs after every wave. | `orchestration_lint.py --phase dispatch --sprint SPRINT.md`: `AUDIT_DUE` when more than `audit_every` (default 6) packets are `landed` since the last `audit:` line | `"audit_every": <n>` in `.claude/orchestrator.json`; record the audit |
| A packet adds at most 3 new tests, each guarding a named risk; never one case per role, finding or row; UI copy and layout go to the root's walk. Was prose only (AGENTS.md, `tdd-go`, `backend-go-testing`) and broken across a whole sprint. | `orchestration_lint.py --phase dispatch`: `TESTS_SECTION` (no `## Tests`, or no line), `TEST_RISK` (a `- new:` line without `guards: <reason>`, or two lines guarding one risk), `TEST_BUDGET` (more than 3 `- new:` lines), `TEST_PER_ITEM` (per-item wording in an AC or Tests line) | `test budget: waived by <who> — <reason>` lifts `TEST_BUDGET` only |
| Each new test names its layer, and one risk or AC is tested at one layer: a rule table at unit, one route row for the handler path, acceptance only for a seam. A pruning audit traced most of 50 cut Go tests to one packet writing a unit and an acceptance test for the same AC. | `orchestration_lint.py --phase dispatch`: `TEST_LAYER` (a `- new:` line without `unit:`, `route:`, `acceptance:` or `vitest:`, or two lines at different layers guarding the same risk text or the same `AC-NNN`) | none |
| Every packet has Volume and budget numbers or a reasoned `N/A`. | `orchestration_lint.py` phases `review` and `dispatch`: `VOLUME_BUDGET` | `N/A — <reason>` |
| A measured number travels with its run count, spread and limiter (pstack principle-explain-the-number). | `orchestration_lint.py` phases `review` and `dispatch`: `VOLUME_BUDGET` for a Volume and budget line that reports a measured or baseline number without `runs: <count, spread>` and `limiter: <what bounded it>` | none; a target without a measurement is not checked |
| Dispatch only from an approved plan and packet, with matching versions, paths and acceptance IDs. | `orchestration_lint.py` with `--contract`: `PLAN_APPROVAL`, `PACKET_APPROVAL`, `VERSION_MISMATCH`, `PATH_MISMATCH`, `ACCEPTANCE_*`, `RECON_*` | none |
| A packet that claims parity with a reference product cites a file of that reference's clone. A packet listed a tool "like <reference product>" from the root's memory; the reference hides that tool from external clients, so the scope was invented, and a saved prose rule did not stop the second occurrence. | `orchestration_lint.py` phases `review` and `dispatch`: `REFERENCE_CITED` for a packet line (outside fenced code) that names a reference configured in `"references": {"<name>": "<clone path, relative to the project root or absolute>"}` without `ref: <path>[:line]` (the path must exist inside that clone) or `ref: none — <reason>` | no `references` key in `.claude/orchestrator.json` turns the rule off; `ref: none — <reason>` per line |
| Land runs only the gates whose paths the diff touches. A comment-only diff went through fifteen gates including container suites; picking a smaller gates file by hand was itself a prose rule. | `gates.sh` / `land.sh`: a gates line `name @glob[,glob...]: command` is skipped (`SKIP name: no changed path matches ...`) when `git diff --name-only <default branch>...HEAD` matches none of its globs; `land.sh` passes the default branch as base on the merged result | write the gate without `@` (always runs); `ORCH_GATES_ALL=1` runs everything |
| A session that has been compacted twice hands off to a new one (one release unit per session). In one project the four longest sessions held two thirds of a month's spend and most of the owner's corrections. | `orchestrate-context.sh snapshot` counts compactions per session id in `.orchestrate/compactions/<id>`; `resume` prints the count and, from the second, the instruction to finish the unit, rewrite HANDOFF.md and tell the owner to continue in a new session. The instruction is read by the root; obeying it is prose only | none |
| Call `land.sh` and `gates.sh` from the installed skill. | `orchestrate-context.sh resume` warns about a project copy | none |
| Every packet names where its scope came from: inventory rows it builds, the owner's dated words, or the landed behaviour it fixes. A plan claimed parity with two reference builders from a 16-row table and each gap surfaced only when the owner asked "does it have X?". | `orchestration_lint.py` phases `review` and `dispatch`: `SCOPE_SOURCE` for no valid `scope:` line; `SCOPE_INVENTORY` when the cited inventory is missing or malformed, a cited id is not in it, or a cited row's decision is not `build <packet id>` | none |
| Scope is fixed from an inventory read from the reference's source, and every row carries a decision. | `orchestration_lint.py --phase scope --inventory <file>…`, and phases `review` and `dispatch` for the inventory a packet cites: `SCOPE_INVENTORY` (no table with `id`, `status`, `decision`; a repeated id; a status other than `HAVE`, `PARTIAL`, `MISSING`, `N/A`; a `HAVE` row with an empty `ours`; no `reference: <name> @ <commit>` line, or a name that is not a key of `references` with an existing clone), `SCOPE_UNDECIDED` (a `PARTIAL` / `MISSING` row without a valid decision, an `N/A` row without `n/a — <reason>`) | none; reading option by option from the source, not from memory or docs prose, is prose only |
| Scope cuts are the owner's: a root never writes `drop` or `later` without the owner's dated words. A standing "decide, don't ask" rule covers technical choices, not dropping a reference feature. | `SCOPE_ROOT_DROP` for a `drop` / `later` decision without `owner <date>: "<quote>"`; the root writes `propose-drop` / `propose-later`, which do not fail dispatch | none |
| Proposed cuts reach the owner. | `--phase scope` prints the strike list (every `propose-*` row) for the owner's report; `orchestration_lint.py --phase handoff`: `SCOPE_PENDING_OWNER` while an inventory named on an `inventory:` line of SPRINT.md (next to the handoff, or `--sprint`) has `propose-*` rows and `Waiting on owner` does not name the file | none |

## Lifecycle rules left as prose

| Rule | Why no check yet | Opt out |
|---|---|---|
| Verify runs against the real artifact (the feature, the stored value, the diff), never an executor's report or "it compiles"; a failed check first suspects the observation; a check the root reruns becomes a script or a line in `.orchestrate/gates`. | Judgement at Verify; the rerun half is enforced once the check is in `.orchestrate/gates` | none |
| Before a third delta on the same gate, the delta opens with `premise:` and `observation:`. | Deltas are chat messages to the executor, not files a script reads | none |
| The unit-end walk follows the inventory's `build` rows (each walked: done / not done), not the list of what was built. | The walk is a browser session the root reads, not a file | none |

## Linting a packet without a contract

```bash
python3 <installed-skill-dir>/scripts/orchestration_lint.py --phase dispatch \
  --packet .orchestrate/packets/NNN-slug.md [--plan .orchestrate/plans/NNN-slug.md] \
  [--sprint .orchestrate/SPRINT.md] [--config .claude/orchestrator.json]
```

This runs the packet-only rules (`SCOPE_*`, `VOLUME_BUDGET`, `ADVISOR_REQUIRED`, `EXECUTOR_FORBIDDEN`, `TESTS_SECTION`,
`TEST_RISK`, `TEST_LAYER`, `TEST_BUDGET`, `TEST_PER_ITEM`) and, with
`--sprint`, `AUDIT_DUE`. With `--contract`, `--plan` and `--packet` the same rules run next to the contract
checks. The config is the `.claude/orchestrator.json` nearest above the packet or sprint file unless `--config` is given.

Packet metadata the lint reads (one line each, in the "Approved plan and routing" section):

```text
- Executor: opus
- Advisor: PLAN_APPROVED .orchestrate/plans/NNN-slug-review.md
- Advisor: waived by <who> — <reason of at least 10 letters>
- Scope: .orchestrate/recon/builder-triggers.md#T2, T5
- Scope: owner 26/11 — "<the owner's words, quoted>"
- Scope: fix — <the landed behaviour or audit finding it fixes, 10+ letters>
```

The inventory path is relative to the project root (or the packet's directory) or absolute; the
inventory grammar is in [product-fit.md](product-fit.md#reference-inventory). A `scope:` line in the
inventory form is exempt from `REFERENCE_CITED`: the inventory's `reference:` header is checked instead.

Checking inventories on their own, before a plan is packetized and for the owner's report:

```bash
python3 <installed-skill-dir>/scripts/orchestration_lint.py --phase scope \
  --inventory .orchestrate/recon/builder-triggers.md [.orchestrate/recon/builder-actions.md …] \
  [--config .claude/orchestrator.json]
```

The packet's `## Tests` section, one line per new test (HTML comments are ignored):

```text
- new: acceptance: TestOutbox_RetryAfterCrash — guards: a crash between claim and send loses the message; fails if the claim is not released, passes if the claim query is rewritten
- new: vitest: src/journeys/list.test.tsx › pages past 50 — guards: journeys after the 50th are unreachable; fails if the next page is never requested, passes if the list component is restructured
- none — <reason of at least 10 letters>
test budget: waived by <who> — <reason of at least 10 letters>
```

The lint checks the layer and `guards:`; the `fails if …, passes if …` half (the pstack two-edit check) is
read by the root at packet review and at Verify. `TEST_LAYER` compares the `guards:` text before
`; fails if` and every `AC-NNN` it names, so writing the AC id makes the one-layer rule bite.

A measured number in the Volume and budget section (a `Measured:` or `Baseline:` line, or
"measured 41 ms" inside another line; the `MEASURED` pattern of `orchestration_lint.py`):

```text
- Measured: p99 41 ms — runs: 5, median 41, range 39-44 ms — limiter: index scan on ledger_user_idx, from EXPLAIN (ANALYZE, BUFFERS) — load: 3.1
```

`TEST_PER_ITEM` reads the lines of every `## Acceptance…` and `## Tests` section and any line naming
an `AC-NNN`; its phrases are the `TEST_PER_ITEM` pattern of `orchestration_lint.py`.

The risk words are the `RISK_WORDS` constant of `orchestration_lint.py`; the lint matches them
as word starts in the packet and in the plan given with `--plan`.

## Health pass after a wave

A wave is the packets landed since the last recorded audit. The pass has two parts, in this order:

1. Performance and scale audit: every list, query, loop and outbound call a wave packet added, at 1x,
   10x and 100x of the Volume and budget numbers (skills `engineering-perf-optimization-process`,
   `reality-gate`).
2. Zero-tech-debt cleanup: wrappers, aliases, dead fields and duplicated rules the wave left behind
   (skill `zero-tech-debt`).

Write the findings and fixes to a report file, then add one line to `SPRINT.md`, after the last landed row it covers:

```text
audit: .orchestrate/audits/2026-11-17-wave-3.md
```

The linter counts `landed` rows after the last `audit:` line whose file exists. A line naming a file
that does not exist resets nothing. Rows are `NNN · slug · landed · …` lines or table rows
(`| NNN | slug | landed | … |`).
