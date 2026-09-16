# Scenario — zero-tech-debt (written BEFORE the routing-name revision)

## 2026-09-16 refactor scenario (written BEFORE skill changes)

**Status:** [EXIT 2 — specified; independent application not yet recorded for this revision].

**Input 1:** Remove an accepted wrapper from a TypeScript-only app with no Mongo or PHP system.

**Expected:** Use the target contract and relevant checks; do not invent Go/PHP parity or Mongo constraints.

**Input 2:** Compatibility evidence for a public alias is unknown.

**Expected:** Treat that as unresolved scope and preserve the alias pending evidence.

## Earlier evidence (historical scope)

**Rationale:** bounded cleanup must stop when several architecture end states compete instead of picking one opportunistically.

**Sample input:** "Clean up catalog architecture, but three competing module end states remain and none has been ranked or accepted."

**Expected behaviors:**
- [ ] Does not choose or implement an end state.
- [ ] Routes discovery and ranking to `improve-codebase-architecture`.
- [ ] Carries candidate scope, available evidence, and a return condition.
- [ ] Resumes only after one behavior-preserving candidate is accepted.

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].
