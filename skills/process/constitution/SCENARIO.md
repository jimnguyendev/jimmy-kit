# Scenario — constitution (written BEFORE the path correction)

**Rationale:** a project principle can be correct while its artifact path leaks into the target repository's own documentation tree.

**Sample input:** "Record the accepted spec and ADR using the constitution's storage rules."

**Expected behaviors:**
- [ ] Stores in-progress work under `.jimmy/work/`.
- [ ] Stores durable kit outputs under `.jimmy/docs/` or `.jimmy/adr/`.
- [ ] Does not write skill output to the target repository's `docs/`.

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].
