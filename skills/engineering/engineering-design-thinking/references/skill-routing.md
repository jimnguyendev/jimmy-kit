# Skill Routing Reference

This file is the canonical routing contract for `engineering-design-thinking`, `improve-arch-go`,
`tdd-go`, and `zero-tech-debt`. Local skill files define their own workflow and entry contract; do not
duplicate this matrix in them.

## Select the initial owner

| Current state | Initial owner |
|---|---|
| Problem, option, boundary, public contract, or authority is unsettled | `engineering-design-thinking` |
| Architecture health must be inspected or candidates must be discovered/ranked | `improve-arch-go` |
| Observable feature/bug behavior and scope are accepted; implementation is needed | `tdd-go` |
| One behavior-preserving cleanup end state and compatibility policy are accepted | `zero-tech-debt` |

Specialist skills such as `engineering-rest-api-design`, `backend-go-database`, and
`backend-go-testing` operate inside a phase; they do not silently replace its owner. Compose concerns
instead of choosing one row. Example for a new API:

```text
engineering-design-thinking
  -> engineering-rest-api-design (contract details)
  -> engineering-design-thinking (accept the contract)
  -> tdd-go (implement accepted behavior)
  -> backend-go-testing/backend-go-database inside the TDD slice as needed
```

## Handoff artifact

`Route` means transfer ownership in the current task, not merely mention another skill. Load the destination
skill, stop the current workflow, and carry this artifact:

```text
from_skill: current owner
to_skill: next owner
trigger: exact routing condition
accepted_decisions: settled behavior/end state/authority
evidence: code, tests, runtime, legacy, or review evidence
verification_state: RED, GREEN, baseline, or not_started
owned_scope: files/features/contracts the next owner may touch
required_output: decision, ranked candidates, behavior slice, or cleanup
return_condition: new evidence or decision required before the prior owner can resume
```

If the artifact is complete, the destination accepts it without repeating approval. Ask only for missing,
contradictory, or expanded fields.

## Four-skill bidirectional routing contract

| Pair | Forward route | Reverse route | Required handoff evidence |
|---|---|---|---|
| `engineering-design-thinking` ↔ `improve-arch-go` | Design -> review when context needs scoped architecture evidence or candidate ranking. | Review -> design when a candidate needs a product choice, option comparison, boundary, public contract, schema/auth choice, or ADR authority. | Scope, constraints, evidence questions/candidates, open decision, return condition. |
| `engineering-design-thinking` ↔ `tdd-go` | Design -> TDD after behavior, interface, risks, and scope are accepted. | TDD -> design when RED exposes an unapproved requirement, contract, boundary, or scope expansion. | Accepted behavior/interface, or failing example, alternatives, and decision needed. |
| `engineering-design-thinking` ↔ `zero-tech-debt` | Design -> cleanup after one behavior-preserving end state and compatibility policy are accepted. | Cleanup -> design when end state, authority, compatibility, or external contract is unknown. | End state, authority, invariants, compatibility evidence, rollback. |
| `improve-arch-go` ↔ `tdd-go` | Review -> TDD when an accepted candidate fixes a bug or changes observable behavior. | TDD -> review only after GREEN when a broader candidate lies outside the accepted slice. | Selected candidate plus behavior delta, or green-state candidate evidence. |
| `improve-arch-go` ↔ `zero-tech-debt` | Review -> cleanup after one behavior-preserving candidate is selected and bounded. | Cleanup -> review when candidate discovery/ranking remains or several end states compete. | Ranked/selected candidate, deletion test, invariants, compatibility evidence. |
| `tdd-go` ↔ `zero-tech-debt` | TDD -> cleanup after GREEN when separately accepted structural cleanup remains. | Cleanup -> TDD before an accepted behavior change or bug fix. | Green tests plus cleanup ledger, or accepted behavior delta and current invariants. |

## Loop and authority guards

1. Do not invoke all four merely because they are linked. An explicit current-task user request to use
   named skills still takes precedence; assign one phase owner at a time.
2. One skill owns the current phase. A handoff pauses it and names the next owner.
3. A return route must add evidence or an accepted decision; never bounce the same unchanged question.
4. `tdd-go` does not widen architecture while RED. Finish or pause the slice first.
5. `improve-arch-go` discovers and prioritizes; `engineering-design-thinking` decides; `tdd-go` changes
   behavior; `zero-tech-debt` executes accepted behavior-preserving cleanup.
6. Do not ask for approval already carried by a complete accepted handoff.

## Learning-be examples

```text
New REST behavior:
  engineering-design-thinking -> engineering-rest-api-design -> engineering-design-thinking -> tdd-go

Architecture health pass with accepted pure refactor:
  improve-arch-go -> zero-tech-debt

Cleanup discovers a public behavior change:
  zero-tech-debt -> engineering-design-thinking (if authority/contract unclear)
                 -> tdd-go (after behavior is accepted)
                 -> zero-tech-debt (remaining structural cleanup)
```

Skip full design only when the behavior, interface, authority, and implementation boundary are already
clear. An accepted bug fix may start at `tdd-go`; ambiguity discovered during RED routes back to design.
