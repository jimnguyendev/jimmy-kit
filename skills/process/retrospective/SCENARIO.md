# Scenario — retrospective

## 2026-10-07 enforcement-ladder scenario (written BEFORE skill changes)

**Status:** [EXIT 2 — specified; independent application not yet recorded for this revision].

**Input 1:** "Third time this sprint a reviewer wrote 'do not log and return the same error'. Turn it into a lesson."

**Expected:** Writes the WHEN/CHECK/BECAUSE rule, then picks the strongest mechanism the accepted scope allows (structure, then types, then a lint whose message names the fix, then a behavior test, docs last), shows the check failing on the real past change, and records rule and mechanism together. If the mechanism is outside the accepted scope, it proposes it instead of implementing it.

**Input 2:** "The A/B test on the paywall ended, conversion flat."

**Expected:** Runs the A/B retro as before; does not force a lint or CI mechanism onto a product lesson that needs judgment.
