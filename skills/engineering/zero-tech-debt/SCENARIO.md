# Scenario — zero-tech-debt (written BEFORE the routing-name revision)

**Rationale:** bounded cleanup must stop when several architecture end states compete instead of picking one opportunistically.

**Sample input:** "Clean up catalog architecture, but three competing module end states remain and none has been ranked or accepted."

**Expected behaviors:**
- [ ] Does not choose or implement an end state.
- [ ] Routes discovery and ranking to `improve-codebase-architecture`.
- [ ] Carries candidate scope, available evidence, and a return condition.
- [ ] Resumes only after one behavior-preserving candidate is accepted.

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].
