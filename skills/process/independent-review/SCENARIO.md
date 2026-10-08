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

## Bounded live workflow corrections

**Sample input:** "Fix reachable workflow failures without restoring the removed role-routing plugin."
**Expected:** recon observations match expected fields before review; draft plan/packet/contract metadata is checked before a reviewer call; executor workspace and temporary-directory access are checked before dispatch; review findings separate material impacts from editorial preferences; progress names files, test results, and real blockers. Explicit approval requirements remain binding.
**Status:** [UNVERIFIED — exit 2 for instruction behavior] 2026-10-08: automated linter checks passed 20/20 and Go Advisor launcher checks passed 4/4. Before the code fixes, the missing/wrong-observation checks and stale-plan/pending-recon launcher checks failed because the unsafe inputs were accepted. Plain briefs, consistent contracts, and extra observed evidence remain supported. No model-behavior evaluation was run for the instruction changes; explicit approvals remain required.
