# Scenario — quality-gates (written BEFORE the path correction)

**Rationale:** a gate sequence can accidentally direct ADRs to the target repository's `docs/` instead of Jimmy's namespace.

**Sample input:** "Show the required artifact path from accepted architecture decision to implementation spec."

**Expected behaviors:**
- [ ] Places ADRs under `.jimmy/adr/`.
- [ ] Places the implementation spec under `.jimmy/work/`.
- [ ] Preserves approval/rejection gates between artifacts.

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].
