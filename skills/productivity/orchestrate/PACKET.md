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
- Executor route: `<configured seat or legacy executor>` (default routing: SKILL.md "Model routing")
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
     measured on and the target it must meet. -->
- Data volume: <rows or items the path sees after 13 months of production growth>
- Budget: <latency p99 or throughput target, e.g. "count < 50 ms", "220 sends/s per worker">
- Proof: <the load run (provider latency > 0) or EXPLAIN ANALYZE on a seeded realistic size, named as an AC>

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
     packet states, not a default. -->

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
