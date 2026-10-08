---
name: orchestrate
description: Coordinates repository work through durable task packets, optional Planner/Advisor review, routed Executors, and root-owned verification. Use when the user asks to orchestrate, dispatch, delegate, configure a multi-model workflow, resume a sprint, or invokes /orchestrate.
---

# Orchestrate — root decides, specialists contribute

The model running the current task is always the **root orchestrator**. It owns intent,
architecture, the canonical plan, packet boundaries, integration, acceptance commands,
and the final answer. Planner and Advisor are read-only contributors. Executors implement
bounded packets. No child result is accepted without root verification.

## State on disk

```text
.orchestrate/                    # gitignored, survives tasks
  SPRINT.md                      # status board; first file read on resume
  HANDOFF.md                     # compact cross-task context named by SPRINT.md
  plans/NNN-<slug>.md            # canonical plan + Advisor findings ledger
  packets/NNN-<slug>.md          # one independently verifiable implementation slice
```

`SPRINT.md` records: goal, date, workflow, root, Planner, Advisor, Executor, handoff path,
and `NNN · slug · state · owner · plan version · verdict`. States are
`draft → plan-review → approved → dispatched → review → verified → landed` plus `blocked`.
Never rewrite historical sprint notes merely to adopt this schema.

Keep the current state compact. SPRINT/HANDOFF carry decisions, owners, statuses, and links;
large command transcripts and superseded detail belong under `.orchestrate/archive/`. A status
line is not evidence: point to the contract, packet, or recorded artifact that is evidence.

On `/orchestrate resume`, read `SPRINT.md` and its named handoff, then continue from the
first non-`landed` packet. Do not re-ask facts already on disk. First run creates the state
directory and header before packet 001.

`.orchestrate/` is gitignored and absent from executor worktrees. Give an executor the
absolute packet path in the main checkout.

## Workflow resolution

Resolve in this order:

1. Explicit current invocation (`workflow=`, `planner=`, `advisor=`, `executor=`).
2. Current sprint header.
3. `.claude/orchestrator.json`.
4. `legacy` with the configured executor.

Explicit seat labels are authoritative. Omitted Planner means `root`; omitted Advisor means
`none`. Never silently move a model between seats or substitute an unavailable required
route. A task-local override is not persisted unless the user asks.

This kit supports the `legacy` workflow below. If a saved sprint or explicit invocation
requires another workflow, stop and ask for a supported workflow instead of installing a
routing plugin or silently changing the requested route.

For `legacy`, resolve the executor from current args → sprint pin →
`.claude/orchestrator.json` → `sonnet`:

- `sonnet|opus|haiku`: spawn one general-purpose executor in an isolated worktree with the
  prompt `Read and execute the packet at <ABSOLUTE path>.` Reuse it for delta feedback.
- `opencode`: run the configured model once from repo root. Never run two opencode writers
  concurrently. Mirror required out-of-repo sources into `.orchestrate/legacy-src/` because
  its sandbox rejects them. If the CLI/model is absent, stop or use a user-approved fallback.

## Per-packet lifecycle

1. **Scope.** State the outcome and boundaries. Resolve genuine ambiguity once.
2. **Recon gate.** Before Advisor review, freeze the planning inputs in the machine-readable
   contract: upstream revision, isolated checkout/tooling, and any stable observed signature.
   Every recon item is `PASS` or a reasoned `N/A`; a failed or changing gate stops the cycle.
   Verify exact files, symbols, ADRs, legacy sources, and acceptance commands at their source.
3. **Plan.** Root writes the plan, or obtains a Planner draft. The review unit is the **next release unit**
   (normally one packet), while a longer roadmap records only high-level goals and
   dependencies. When an Advisor is explicitly requested, record its verdict and the root's
   disposition of findings in [PLAN_REVIEW.md](PLAN_REVIEW.md).
   No executor starts from an unapproved plan.
4. **Packetize.** Copy [PACKET.md](PACKET.md). One packet is one bounded change/commit with
   explicit file ownership, stop conditions, and exact acceptance commands.
   The AC is where quality is decided, not Verify: an executor optimizes for the criteria it
   is given, so a question the AC never asks is a question nobody asks. A packet touching a
   cost-bearing seam (database, another service, a list/response path) states its cost budget (AC-007) and, when container tests are the evidence, its
   engine parity (AC-006). Neither needs database expertise to review — both print a number.
   An executor cannot measure what it cannot reach: a packet whose AC needs a real database
   carries the read-only DSN and the exact command, or root runs that AC itself and says so.
5. **Dispatch.** One packet per executor run. The packet's implementation, evidence,
   runtime-parity, release, and landing **verdict dimensions** are tracked separately. Name both
   an **evidence owner** (who proves the harness/claim) and a **runtime-fix owner** (who changes
   behavior) for each systemic drift route. Parallelize only independent packets with
   non-overlapping writes and integration order recorded in the plan.
6. **Verify.** Root reviews the diff for scope, parity, architecture, naming and unrelated
   changes, then runs every acceptance command itself. Executor prose is not evidence.
   A packet touching a seam (SQL, document store, cache, gRPC/HTTP client, config, response
   shape) MUST carry a reality AC — a named container-backed test run with `-v` whose
   `--- PASS` line is pasted, or a replay diff against the legacy system — in addition to
   the unit command. Exit code 0 with tests skipped is not evidence. A container-backed test is
   evidence only when the container is the engine the deployment runs (AC-006); a seam
   packet is verified only when its cost number (queries, rows, bytes or calls per request)
   was measured on real-sized data (AC-007). Template and audit: skill `reality-gate`
   (`templates/acceptance-criteria.md`).
7. **Iterate.** Send a short delta describing failed evidence and required correction. Maximum
   three implementation iterations; then root re-scopes, takes over the sticking point, or
   reports the blocker.
8. **Land.** Merge/commit only after root verification; record commit and verdict in SPRINT.md.
9. **Hygiene.** Capture durable decisions in ADR/docs and refresh HANDOFF.md at milestones. A
   material requirement, baseline, route, or ownership change ends the review episode: obtain user
   authorization for a **fresh cycle** and rerun recon/review rather than patching an approved plan.

## Non-negotiable rules

- Root writes plans, packets, ADRs, reviews, and performs final verification.
- Planner and Advisor never edit, execute commands, direct Executors, or contact each other.
- Executors do not spawn descendants and do not use Planner/Advisor routes.
- An explicit `no subagents` instruction wins.
- Never weaken permissions, approvals, Goal controls, legacy parity, or repo instructions.
- Large/architectural sprint: preview the roadmap and workflow before dispatching packet 001.
- A misunderstood packet is an orchestration defect: fix the packet, not the model.
