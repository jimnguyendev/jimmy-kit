# Codex-Orchestration adapter

Use this reference only when the selected workflow is `codex-orchestration`. It adapts the
role-routing plugin to this repository's durable `.orchestrate/` packet process.

## Preconditions and activation

1. Verify `codex plugin list --json` contains an enabled
   `codex-orchestration@codex-orchestration` at a version supported by its own instructions
   (Planner routing requires 0.5.1 or newer).
2. Installation/update is loaded only by a **new Codex task**. Do not claim the current task
   gained plugin skills after installation.
3. Run `/codex-orchestration status --require-effective` in the new task before dispatch.
   A saved profile in `.claude/orchestrator.json` is a preference, not proof of an effective
   or executed route.
4. Normalize and preview the mapping in this order before setup or task-local work:

   ```text
   Root: current task model
   Planner: <route> | root
   Advisor: <route> | none
   Executor: <route>
   Strict routes: true | explicitly best-effort for this task
   ```

The root model is never configured as a second seat. Exact labels are binding. Planner and
Advisor must use independent routes. Do not invent model IDs; let the plugin resolve display
names through the active host catalog.

Example project preference (not an activation command): root plans, Claude Fable 5 High
advises, GPT-5.6 Luna Extra High executes. The plugin normalizes Extra High to `xhigh`.

## Machine-readable contract flow

For a contract-backed cycle, the contract is the **single source** for recon expectations,
acceptance commands, expected outcomes, document coverage, and systemic drift routes. The plan
and packet carry intent and stable RG/AC references; they do not copy command or expected-result
prose. Run the dependency-free orchestration linter at `review`, `dispatch`, and `docs` phases.
The recon gate must be complete before the first Advisor call. A packet review considers only the
next release unit; future roadmap ownership is provisional until that unit gets its own recon and
review.

Each route records an **evidence owner** and a **runtime-fix owner**. The former owns proof that a
harness or claim is valid; the latter owns production behavior and parity correction. A green
harness therefore does not make runtime parity or release green.

## Planning and Advisor approval

Persist the canonical plan with [PLAN_REVIEW.md](PLAN_REVIEW.md).

1. Root prepares a self-contained brief: intent, acceptance, repo evidence, constraints,
   proposed executor slices, risks, and verification.
2. Configured Planner returns `PLAN_DRAFT`. If Planner is `root`, root writes version 1.
3. Send the numbered canonical version to a fresh, stateless Advisor call. Require first line
   `PLAN_APPROVED` or `PLAN_REVISE`.
4. On `PLAN_REVISE`, assign stable finding IDs. Planner/root returns `PLAN_REVISION`, the
   complete ledger, and a new plan version. Every finding is `INCORPORATED` or `REJECTED`
   with a concrete reason.
5. Repeat with a fresh Advisor call. Stop immediately on approval. Never exceed five Advisor
   reviews.
   A material requirement, baseline, route, or ownership change ends the review-budget episode.
   Start a **fresh cycle** with a new user-authorized plan/recon rather than spending another
   review on an already-approved episode.
6. If review five still requests revision, halt before implementation and ask the user to
   re-scope, override, or change a route. Never label the plan approved.

Carry only original constraints, canonical current plan, and compact ledger between calls.
Planner and Advisor report only to root and never contact one another.

## Route failure semantics

- Required Planner/Advisor unavailable or malformed: halt before executor work.
- Explicit current-task `best-effort` may let root replace a failed Planner; a failed Advisor
  yields `NOT_ADVISOR_APPROVED`. Never persist best-effort.
- Required Executor unavailable: halt. Root may implement only when delegation or the exact
  route was not required by the user.
- Distinguish `policy installed`, `route accepted`, `used and confirmed`, and `unavailable`.
  Child prose claiming a model name is not runtime evidence.
- Every routed spawn uses `fork_turns="none"` and a self-contained packet. Never fork full
  conversation history into a different model route.

## Executor release and integration

Create one [PACKET.md](PACKET.md) per independent slice. An executor receives only its packet,
owned paths, dependencies, stop conditions, and minimal verification. It must not call the
Advisor, spawn descendants, or guess through contradictions.

Parallel execution is allowed only when write ownership does not overlap. Root waits for all
required handoffs, reviews each diff, integrates in recorded order, and runs the full acceptance
suite. Executor completion is never acceptance.

Record the effective/observed route state, plan version, review count, packet owner and root
verdict in `.orchestrate/SPRINT.md` so a fresh task can resume without relying on chat history.
Keep the five verdict dimensions (implementation, evidence, runtime-parity, release, landing)
distinct in the packet and status board. An executor report is a handoff, never acceptance
evidence; the root remains the verifier and release authority.

Upstream behavior and setup commands: https://github.com/Cjbuilds/Codex-Orchestration
