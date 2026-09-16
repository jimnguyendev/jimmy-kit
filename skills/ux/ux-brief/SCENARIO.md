# Scenario — ux-brief (written BEFORE the cross-reference correction)

**Rationale:** the brief must hand off to skill names that exist in Jimmy Kit rather than an upstream runtime label.

**Sample input:** "Produce the confirmed redesign brief and identify its next consumers."

**Expected behaviors:**
- [ ] Writes the brief under `.jimmy/work/<feature>/`.
- [ ] Names `ux-specify` and `ux-plan-tasks` as consumers.
- [ ] Does not require an upstream command name.

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].

---
## Current revision — 2026-09-16 (written before refactor)

**Status: exit 2 — prospective cases; independent execution not yet recorded.**

**Sample input:** Create the redesign brief from accepted keep/change decisions and supplied evaluation evidence; no named artifact files exist.

**Expected behaviors:**
- [ ] Does not re-ask settled directions or approval to continue already authorized scope.
- [ ] Resolves only missing material decisions and names current UX consumers.
- [ ] Preserves brand, performance and accessibility constraints.
