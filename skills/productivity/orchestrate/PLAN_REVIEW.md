# Plan review — template

> Save as `.orchestrate/plans/NNN-<slug>.md`. Root owns this document and its version.

```md
# Plan NNN — <slug>

- Version: v1
- Status: DRAFT | REVIEW | APPROVED | NOT_ADVISOR_APPROVED | BLOCKED
- Root: <current task model>
- Planner: <route or root> — <route state>
- Advisor: <route or none> — <route state>
- Executor: <route> — <route state>
- Advisor reviews: 0/5
- Acceptance contract: `.orchestrate/contracts/NNN-<slug>.json`
- Recon gate references: RG-001, RG-002 (all must be PASS or reasoned N/A before review)

## Intent and acceptance
<User outcome, production/parity constraints, and acceptance reference IDs only. The contract is the
single source for commands and expected outcomes.>

## Status dimensions
These are the five verdict dimensions for this review episode.
- Implementation verdict: PENDING
- Evidence verdict: PENDING
- Runtime parity verdict: NOT_APPLICABLE
- Release verdict: BLOCKED_UNTIL_VERIFIED
- Landing verdict: UNLANDED

## Next release unit
<The one packet/release unit under this review.>

## High-level roadmap
<Future objectives and dependencies only; future ownership remains provisional.>

If a material requirement changes, start a fresh cycle with new recon and review.

## Verified repository evidence
- `<path>:<line>` — <fact verified at source>

## Canonical plan v1
1. <ordered step>

## Executor slices
| Packet | Objective | Owned write paths | Depends on | Parallel-safe with |
|---|---|---|---|---|
| NNN-A | ... | ... | none | NNN-B |

## Risks and stop conditions
- <risk or contradiction that must stop implementation>
- Systemic drift route: <route class; actions; evidence owner; runtime-fix owner; allowance policy>

## Findings ledger
| ID | Raised in | Finding | Disposition | Reason/evidence | Closed in |
|---|---|---|---|---|---|
| F-001 | v1 | ... | OPEN | ... | — |

## Advisor decision history
| Review | Plan version | Decision | Observed route state | Notes |
|---|---|---|---|---|
| 1 | v1 | PLAN_REVISE | route accepted | F-001 |

## Root approval
- Approved version: <vN or none>
- Root semantic check: <pass/fail + evidence>
- Executor release: <yes/no>

## Acceptance references
- AC-001
- AC-002
```
