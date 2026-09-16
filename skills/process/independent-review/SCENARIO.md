# Scenario — independent-review (written BEFORE the path correction)

## 2026-09-16 refactor scenario (written BEFORE skill changes)

**Status:** [EXIT 2 — specified; independent application not yet recorded for this revision].

**Input 1:** Review this supplied short spec and return feedback in chat.

**Expected:** Produce findings and a verdict; do not ask the user to select an artifact or silently create an ADR.

**Input 2:** Review your own high-risk design with an available fresh reviewer.

**Expected:** Separate independent evidence from self-review and preserve scope.

## Earlier evidence (historical scope)

**Rationale:** default artifact discovery must inspect Jimmy-owned work without treating a target repository's general docs as skill output.

**Sample input:** "Review the latest Jimmy artifacts; no path was supplied."

**Expected behaviors:**
- [ ] Scans `.jimmy/work/` and `.jimmy/docs/`.
- [ ] Presents candidates before choosing scope.
- [ ] Does not assume unrelated target-repository docs are Jimmy artifacts.

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].
