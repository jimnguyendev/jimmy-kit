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
- Executor route: `<configured seat or legacy executor>`
- Owned write paths: `<exact files/directories; must not overlap a parallel packet>`
- Depends on / integration order: `<packet IDs or none>`

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
- <packet-specific constraints, e.g. "write BSON field-for-field per appendix E">

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

## Acceptance references
- AC-001
- AC-002

## Report back (exact format)
- Status: `DONE` or `BLOCKED`
- Route metadata visible to Executor, or `not exposed`
- Changed files list · what each change does (1 line each)
- AC-001..AC-NNN exit statuses (root runs the commands from the contract)
- Anything you were unsure about or deviated on, flagged loudly
- Remaining risks and integration assumptions
- Suggested commit message (one line, house style)
```
