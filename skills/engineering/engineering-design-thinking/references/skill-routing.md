# Skill Routing Reference

This is the canonical routing contract for `engineering-design-thinking`, `improve-codebase-architecture`, `tdd-go`, and `zero-tech-debt`. Links are conditional ownership transfers, not a mandatory pipeline. `tdd-go` is the Go implementation owner, not a stack-neutral name.

## Select the current owner by problem state

| Current state | Owner |
|---|---|
| Actual/expected gap, option, boundary, public contract, or authority is unsettled | `engineering-design-thinking` |
| Architecture health must be inspected or candidates discovered and ranked | `improve-codebase-architecture` |
| Observable behavior and scope are accepted; Go implementation is needed | `tdd-go` |
| Observable behavior and scope are accepted; non-Go implementation is needed | The target project's named test-first implementation workflow |
| One behavior-preserving cleanup end state and compatibility policy are accepted | `zero-tech-debt` |

Specialist skills operate inside a phase; they do not silently replace its owner. For example, `engineering-rest-api-design` can detail a contract, return it to design for acceptance, and then `tdd-go` implements accepted Go behavior. For TypeScript or another non-Go stack, use the target project's test-first workflow and conventions; if none is named, implement vertical RED-GREEN slices through the public interface without pretending that `tdd-go` owns the work.

## Handoff artifact

Routing transfers ownership. Stop the current workflow, load the destination, and carry:

```text
from_skill: current owner
to_skill: next owner
trigger: exact state change that requires transfer
accepted_decisions: settled behavior, end state, and authority
evidence: code, tests, runtime, legacy, or review evidence
verification_state: RED, GREEN, baseline, or not_started
owned_scope: files, features, and contracts the next owner may touch
required_output: decision, ranked candidates, behavior slice, or cleanup
return_condition: new evidence or accepted decision needed before return
```

The destination accepts a complete artifact without repeating approval. Ask only for missing, contradictory, or expanded fields.

## Four-skill bidirectional routing contract

| Pair | Forward route | Reverse route | Required handoff evidence |
|---|---|---|---|
| `engineering-design-thinking` ↔ `improve-codebase-architecture` | Design -> discovery when context needs scoped architecture evidence or candidate ranking. | Discovery -> design when a candidate needs a product choice, option comparison, boundary, public contract, or ADR authority. | Scope, constraints, evidence questions/candidates, open decision, return condition. |
| `engineering-design-thinking` ↔ `tdd-go` | Design -> TDD after behavior, interface, risks, and scope are accepted. | TDD -> design when RED exposes an unapproved requirement, contract, boundary, or scope expansion. | Accepted behavior/interface, or failing example, alternatives, and decision needed. |
| `engineering-design-thinking` ↔ `zero-tech-debt` | Design -> cleanup after one behavior-preserving end state and compatibility policy are accepted. | Cleanup -> design when end state, authority, compatibility, or external contract is unknown. | End state, authority, invariants, compatibility evidence, rollback. |
| `improve-codebase-architecture` ↔ `tdd-go` | Discovery -> TDD when an accepted candidate fixes a bug or changes observable behavior. | TDD -> discovery only after GREEN when a broader candidate lies outside the accepted slice. | Selected candidate plus behavior delta, or green-state candidate evidence. |
| `improve-codebase-architecture` ↔ `zero-tech-debt` | Discovery -> cleanup after one behavior-preserving candidate is selected and bounded. | Cleanup -> discovery when candidate ranking remains or several end states compete. | Ranked/selected candidate, deletion test, invariants, compatibility evidence. |
| `tdd-go` ↔ `zero-tech-debt` | TDD -> cleanup after GREEN when separately accepted structural cleanup remains. | Cleanup -> TDD before an accepted behavior change or bug fix. | Green tests plus cleanup ledger, or accepted behavior delta and current invariants. |

## Loop and authority guards

1. One skill owns the current phase; do not invoke all four merely because they are linked.
2. A return route must add evidence or an accepted decision; never bounce the same unchanged question.
3. `tdd-go` does not widen architecture while RED.
4. `improve-codebase-architecture` discovers and ranks; design decides; TDD changes behavior; cleanup executes an accepted behavior-preserving end state.
5. Do not ask for approval already carried by a complete handoff.

Skip full design only when the behavior, interface, authority, and implementation boundary are already clear. An accepted bug fix may start at `tdd-go`; ambiguity discovered during RED routes back to design.

For non-Go handoffs, keep the same artifact and set `to_skill` to the concrete project workflow or `project test-first workflow (<stack>)`. Do not route TypeScript or React implementation to `tdd-go`.
