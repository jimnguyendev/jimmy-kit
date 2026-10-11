---
name: orchestrate
description: Coordinates repository work through durable task packets, optional Planner/Advisor review, routed Executors, and root-owned verification and landing. Use when the user asks to orchestrate, dispatch, delegate, configure a multi-model workflow, land packets, resume a sprint (including after compaction or a session limit), or invokes /orchestrate.
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
  gates                          # `name: command` per line; run by scripts/gates.sh and land.sh
  AUTO-STATE.md                  # written by the PreCompact hook from git and ps; never hand-edited
  LEARNINGS.md                   # WHEN · CHECK · BECAUSE lines learned during the sprint
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

`.orchestrate/` is gitignored and absent from executor worktrees. Give a Claude executor the
absolute packet path in the main checkout; opencode cannot read outside its cwd, so copy the
brief and packet into `<worktree>/.orchestrate/` first.

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

- `sonnet|opus|haiku`: the root creates the packet's worktree in the target repo
  (`git worktree add`), then spawns one general-purpose executor with the prompt
  `Work only in <ABSOLUTE worktree>. Read and execute the packet at <ABSOLUTE path>.`
  Do not rely on the Agent tool's worktree isolation: it isolates the session cwd's repo, which
  is not always the target. Reuse the executor for delta feedback.
- `opencode`: run `opencode run -m <provider>/<model> "<prompt>" < /dev/null` once inside the
  packet's worktree, with the brief, packet and any out-of-repo sources copied into
  `<worktree>/.orchestrate/` (its sandbox rejects reads outside the cwd; without `< /dev/null`
  it waits on stdin, without `-m` it falls back to a default model). Never run two opencode
  writers concurrently. If the CLI/model is absent, stop or use a user-approved fallback.

## Model routing

When the user has not pinned a seat per packet, route by packet kind (details and evidence:
[references/dispatch-and-land.md](references/dispatch-and-land.md#model-routing)):

| Packet kind | Executor |
|---|---|
| Easy backend that copies a feature already in the repo (the packet names it) | low-cost model via opencode; never frontend |
| Normal backend, and all frontend | Sonnet |
| Hard: auth, queue/dispatch, lease/retry, rich editors, performance | Opus |
| Root | Opus |

## Per-packet lifecycle

1. **Scope.** State the outcome and boundaries. Resolve genuine ambiguity once.
2. **Recon gate.** Before Advisor review, freeze the planning inputs in the machine-readable
   contract: upstream revision, isolated checkout/tooling, and any stable observed signature.
   Every recon item is `PASS` or a reasoned `N/A`; a failed or changing gate stops the cycle.
   Verify exact files, symbols, ADRs, legacy sources, and acceptance commands at their source.
   Before dispatch, verify the actual executor checkout exists, the absolute packet is readable,
   the workspace and the executor's temporary directory are writable in its execution environment,
   and the required commands are available. Record the probe and observed result in recon;
   blocked access or missing tooling stops dispatch instead of sending an unprepared executor.
   PASS observations must contain every expected field with the expected value; extra observed
   evidence is allowed. The linter checks recorded evidence, not the environment itself.
3. **Plan.** Root writes the plan, or obtains a Planner draft. The review unit is the **next release unit**
   (normally one packet), while a longer roadmap records only high-level goals and
   dependencies. When an Advisor is explicitly requested, record its verdict and the root's
   disposition of findings in [PLAN_REVIEW.md](PLAN_REVIEW.md).
   For a contract-backed cycle, prepare the matching draft packet metadata and acceptance IDs,
   then run `python3 <installed-skill-dir>/scripts/orchestration_lint.py --contract <contract.json> --plan <plan.md> --packet <packet.md> --phase review`
   before requesting review. A stale version, mismatched path, missing AC, or failed recon stops
   the call. After approval, run the same command with `--phase dispatch` before execution.
   Material behavior/data/security/contract or proof findings can block approval. Wording and
   formatting preferences are editorial; correct them locally without a fresh model round unless
   the user or project explicitly requires one. Never omit a required approval.
   No executor starts from an unapproved plan.
   Before the packets of a plan are dispatched, three things land on the default branch:
   - **Contracts and ADRs.** A contract-level finding (a status code, a limit, a field another
     feature must write) changes the contract and an ADR first. Executors optimize for the packet
     and the contract; a gap left in plan prose is not implemented. Check the owning feature
     exposes every field a dependent packet needs.
   - **Shared seams.** When parallel packets need a seam another packet builds (service auth,
     admin SSO, a caller context), root lands the context package plus a local-only mock first,
     so the wave runs without ordering or faked features.
   - **Design.** FE packets point at a design spec exported into the repo, never at a live design
     tool or canvas screenshots ([references/design-export.md](references/design-export.md)).
   A plan that touches queue, lease, retry, fencing or idempotency semantics needs an Advisor from
   a different model family with read access to the repo, including code already landed, and
   reruns until no material finding is open. If none is configured, stop and ask for one.
   Origin: three rounds took one dispatcher plan from 15 findings (9 high) to 0; the third
   found two double-send paths in clients already merged.
4. **Packetize.** Copy [PACKET.md](PACKET.md). One packet is one bounded change/commit with
   explicit file ownership, stop conditions, and exact acceptance commands.
   The AC is where quality is decided, not Verify: an executor optimizes for the criteria it
   is given, so a question the AC never asks is a question nobody asks. A packet touching a
   cost-bearing seam (database, another service, a list/response path) states its cost budget (AC-007) and, when container tests are the evidence, its
   engine parity (AC-006). Neither needs database expertise to review — both print a number.
   An executor cannot measure what it cannot reach: a packet whose AC needs a real database
   carries the read-only DSN and the exact command, or root runs that AC itself and says so.
   Every packet has a **Volume and budget** section: data volume after 13 months, a latency or
   throughput target, and the load run or `EXPLAIN ANALYZE` on a seeded realistic size that
   proves it, or `N/A — <reason>`. Root rejects a send-path, dispatch-loop or growing-table query
   packet that has no numbers; the contract linter rejects a packet without the section. Origin: the
   throughput target existed in an ADR from day one but was never an AC; the first load test
   came after 35 packets and found four bottlenecks the packets themselves asked for.
5. **Dispatch.** One packet per executor run. The packet's implementation, evidence,
   runtime-parity, release, and landing **verdict dimensions** are tracked separately. Name both
   an **evidence owner** (who proves the harness/claim) and a **runtime-fix owner** (who changes
   behavior) for each systemic drift route. Parallelize only independent packets with
   non-overlapping writes and integration order recorded in the plan. Each packet gets its own
   worktree, ports and scratch paths derived from its number. Executors never open a browser or
   a UI-driving tool. Rules: [references/dispatch-and-land.md](references/dispatch-and-land.md).
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
   Frontend is driven against the real service before it lands, by one verification subagent
   that owns one browser and returns verdicts plus evidence paths; root reads the evidence and
   looks at every FE land in that same browser. Mocked-API tests cannot reveal a backend defect,
   and the root's context is not spent on DOM trees
   ([references/verification.md](references/verification.md)).
7. **Iterate.** Send a short delta describing failed evidence and required correction. Maximum
   three implementation iterations; then root re-scopes, takes over the sticking point, or
   reports the blocker.
8. **Land.** Only through `scripts/land.sh <worktree> "<title>"`: it merges the default branch
   into the packet, runs every gate in `.orchestrate/gates` (`scripts/gates.sh`) on the merged
   result, merges with the head SHA once the forge reports mergeable, and removes the worktree
   only after the merge succeeded. A clean git merge can still fail to build; a gate the land
   step does not run is a gate nobody runs. Record PR/commit and verdict in SPRINT.md.
9. **Hygiene.** Rewrite HANDOFF.md after every land (what landed, what runs with agent IDs and
   pids, next actions, standing user rules, and `Waiting on owner` as decision briefs or `None.`,
   checked with `orchestration_lint.py --phase handoff --handoff .orchestrate/HANDOFF.md`); the
   PreCompact/SessionStart hook in
   `scripts/orchestrate-context.sh` restores it after compaction
   ([references/context-and-resume.md](references/context-and-resume.md)). Add a
   WHEN · CHECK · BECAUSE line to LEARNINGS.md when a failure teaches a rule. After a session
   limit, resume each stopped agent with `SendMessage`; do not respawn it. Capture durable
   decisions in ADR/docs. A material requirement, baseline, route, or ownership change ends the
   review episode: obtain user authorization for a **fresh cycle** and rerun recon/review rather
   than patching an approved plan.

## Progress reports

At the first concrete artifact, a failed check, or a blocker, report the changed file paths,
the exact check and its observed result, and the next bounded action. For a blocker, name the
action, target, and failure reason. Inspect the owned diff before claiming an executor made
no progress; silence alone is not evidence. Keep user updates concise and link durable evidence.

An end-of-wave report follows skill `ketchup`: one sentence counting the decisions waiting on the
owner, what landed and what it means, what still runs and what could not be checked, the calls
the root made itself (one line each with the reason), then the briefs.

## Asking the owner

The root decides engineering calls itself and records them (HANDOFF, ADR, PR body). It asks the
owner only for a product choice, approval of an outward-facing or irreversible action not already
authorized, spending, access it lacks, or a scope change. A standing "decide, don't ask"
instruction narrows this further.

Every question to the owner is a **decision brief** from skill `ketchup`, one per decision, in the
owner's language and writing rules: the decision in one sentence; what it is (every PR, ADR, tool
or term explained, no bare ids); why now; options with cost and visible effect; recommendation and
why; what happens with no answer ("I wait; X stays blocked", or a reversible timed default that names the owner's standing authority to decide); evidence. The owner must be able to
decide without opening a link. This applies wherever the question appears:

- chat text and end-of-wave reports;
- AskUserQuestion: the briefs go in the message first; the question is the decision sentence and
  the options mirror the brief's, recommended first;
- HANDOFF's `Waiting on owner` section, in the file form the linter checks
  ([references/context-and-resume.md](references/context-and-resume.md#handoff-after-every-land)).

After a compaction-resume, a session limit, or a long silence, the first owner-facing message is
a `/ketchup` catch-up before any new question. Origin: the root asked "open the PR on the kit?
accept ADR-0017?" and six one-line tech-debt items with unexplained library names; the owner had
to ask what each meant before deciding.

## Non-negotiable rules

- Root writes plans, packets, ADRs, reviews, and performs final verification.
- Planner and Advisor never edit, execute commands, direct Executors, or contact each other.
- Executors do not spawn descendants and do not use Planner/Advisor routes.
- Executors never open a browser; one verification agent owns the one browser.
- Nothing lands except through `land.sh` with every gate green on the merged result.
- An explicit `no subagents` instruction wins.
- Never weaken permissions, approvals, Goal controls, legacy parity, or repo instructions.
- Large/architectural sprint: preview the roadmap and workflow before dispatching packet 001.
- Every owner question is a decision brief (skill `ketchup`); a bundled one-liner is not a question.
- A misunderstood packet is an orchestration defect: fix the packet, not the model.
