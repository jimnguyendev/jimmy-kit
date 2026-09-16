# Scenario — growth-loops (written BEFORE the skill was finalized)

## Current revision — 2026-09-16 (K16)

**Status: EXIT 2 — prospective cases; no independent run recorded for this revision.**

**Static baseline finding (not a behavioral run):** Discovery description exceeds 300 characters and obscures the main trigger.

**Sample input:** Select growth-loops for its named product task from skill descriptions, then apply its existing specialist method.

**Expected behavior:** Find the skill from a concise situation-triggered description; retain its existing methodology and applicable boundaries.

**Validation needed:** run the case with a fresh agent, paste its output and grade each expectation. Static checks alone do not promote this revision to PASS.

## Historical scenarios and results (unchanged)

**Rationale (the failure to prevent):** an agent asked "how do we grow this?" answers with channels and campaigns and never names a closed loop or an Active-User definition.
**Sample input:** "We want to grow the practice product — what should we do?"
**Expected behaviors (pass when all check):**
- [ ] Refuses "run ads" as a plan; maps Trigger→Action→Value→Investment and says whether the loop closes
- [ ] Reports the 3 control metrics with window + source or marks them missing
- [ ] Picks ONE lever with the metric it should move
- [ ] Reads the cohort curve before recommending scale
- [ ] Calls a **flattening** curve the PMF signal; if it sees a smile, names the cycle driving the return instead of treating it as extra proof
**Status:** [UNVERIFIED — exit 2] Not yet run. Paste the first real run here to promote to exit 0.
**Revised 2026-09-09:** curve-reading check added — the earlier wording credited the smile curve as the PMF signal. Status stays exit 2.
