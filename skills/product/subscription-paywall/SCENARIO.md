# Scenario — subscription-paywall (written BEFORE the skill was finalized)

## Current revision — 2026-09-16 (K16)

**Status: EXIT 2 — prospective cases; no independent run recorded for this revision.**

**Static baseline finding (not a behavioral run):** Discovery description exceeds 300 characters and obscures the main trigger.

**Sample input:** Select subscription-paywall for its named product task from skill descriptions, then apply its existing specialist method.

**Expected behavior:** Find the skill from a concise situation-triggered description; retain its existing methodology and applicable boundaries.

**Validation needed:** run the case with a fresh agent, paste its output and grade each expectation. Static checks alone do not promote this revision to PASS.

## Historical scenarios and results (unchanged)

**Rationale (the failure to prevent):** an agent asked to "improve conversion on the pricing page" tweaks copy and adds urgency instead of locating the revenue-tree lever and checking the trial model.
**Sample input:** "Our free plan converts at 1%. Lock more features?"
**Expected behaviors (pass when all check):**
- [ ] Checks whether the locked feature is the hero feature (freemium blind spot #1)
- [ ] Recommends a model (reverse trial by default) with reasoning
- [ ] Names the revenue-tree branch and the measuring event
- [ ] Flags any dark pattern; proposes one single-variable A/B
- [ ] Quotes no invented lift multiplier for a psychological effect — proposes measuring it
- [ ] Treats retention (not the model choice) as the core, and checks the signup gate (card vs email)
**Status:** [UNVERIFIED — exit 2] Not yet run. Paste the first real run here to promote to exit 0.
**Revised 2026-09-09:** two checks added after a source audit found §2 had inherited an unsourced "mid-tier selection roughly doubles" claim. Status stays exit 2.
