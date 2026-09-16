# Scenario — constitution (written BEFORE the path correction)

## 2026-09-16 refactor scenario (written BEFORE skill changes)

**Status:** [EXIT 2 — specified; independent application not yet recorded for this revision].

**Input 1:** Does installing this skill install hooks that prevent source edits?

**Expected:** Explain that these are principles and recommended mechanisms; inspect actual project enforcement before claiming it exists.

**Input 2:** Update a label without changing behavior.

**Expected:** Use proportional checks; do not invent behavioral tests for an editorial change.

## Earlier evidence (historical scope)

**Rationale:** a project principle can be correct while its artifact path leaks into the target repository's own documentation tree.

**Sample input:** "Record the accepted spec and ADR using the constitution's storage rules."

**Expected behaviors:**
- [ ] Stores in-progress work under `.jimmy/work/`.
- [ ] Stores durable kit outputs under `.jimmy/docs/` or `.jimmy/adr/`.
- [ ] Does not write skill output to the target repository's `docs/`.

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].
