# Scenario — domain-modeling (written BEFORE the path correction)

**Rationale:** single-context and multi-context examples must agree on the namespace for engineering ADRs.

**Sample input:** "Create the first domain glossary and architecture decision in a single-context repository."

**Expected behaviors:**
- [ ] Keeps `CONTEXT.md` at the relevant context root.
- [ ] Stores the ADR under `.jimmy/adr/`.
- [ ] Does not introduce a target-repository `docs/adr/` convention.

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].
