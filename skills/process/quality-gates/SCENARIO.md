# Scenario — quality-gates (written BEFORE the path correction)

## 2026-09-16 refactor scenario (written BEFORE skill changes)

**Status:** [EXIT 2 — specified; independent application not yet recorded for this revision].

**Input 1:** Implement this accepted, reversible two-file fix. Its behavior and regression check are already agreed.

**Expected:** Carry authorization forward; implement and run relevant checks without separate spec/plan approval.

**Input 2:** Our integration command exits 0 but runs no tests. Can we call it verified?

**Expected:** Report unverifiable, preserve seam evidence and do not count an empty run as a pass.

## Earlier evidence (historical scope)

**Rationale:** a gate sequence can accidentally direct ADRs to the target repository's `docs/` instead of Jimmy's namespace.

**Sample input:** "Show the required artifact path from accepted architecture decision to implementation spec."

**Expected behaviors:**
- [ ] Places ADRs under `.jimmy/adr/`.
- [ ] Places the implementation spec under `.jimmy/work/`.
- [ ] Preserves approval/rejection gates between artifacts.

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].
