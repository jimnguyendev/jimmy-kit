# Scenario — independent-review (written BEFORE the path correction)

**Rationale:** default artifact discovery must inspect Jimmy-owned work without treating a target repository's general docs as skill output.

**Sample input:** "Review the latest Jimmy artifacts; no path was supplied."

**Expected behaviors:**
- [ ] Scans `.jimmy/work/` and `.jimmy/docs/`.
- [ ] Presents candidates before choosing scope.
- [ ] Does not assume unrelated target-repository docs are Jimmy artifacts.

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].
