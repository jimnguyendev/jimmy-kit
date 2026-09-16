# Scenario — product-vision (written BEFORE the skill was finalized)

## Current revision — 2026-09-16 (K16)

**Status: EXIT 2 — prospective cases; no independent run recorded for this revision.**

**Static baseline finding (not a behavioral run):** Discovery description exceeds 300 characters and obscures the main trigger.

**Sample input:** Select product-vision for its named product task from skill descriptions, then apply its existing specialist method.

**Expected behavior:** Find the skill from a concise situation-triggered description; retain its existing methodology and applicable boundaries.

**Validation needed:** run the case with a fresh agent, paste its output and grade each expectation. Static checks alone do not promote this revision to PASS.

## Historical scenarios and results (unchanged)

**Rationale (the failure to prevent):** an agent asked to prioritize a backlog orders features by who asked loudest and endorses deleting a "low-usage" feature on click data.
**Sample input:** "Prioritize these 12 requests and drop the unused export feature."
**Expected behaviors (pass when all check):**
- [ ] Writes/checks a one-sentence vision before ordering anything
- [ ] Reframes each request as the user question it answers
- [ ] Runs a ripple-effect check before any removal and asks for external user input
- [ ] Names the North Star the roadmap serves
**Status:** [UNVERIFIED — exit 2] Not yet run. Paste the first real run here to promote to exit 0.
**Revised 2026-09-09:** an unsourced "10% of features" figure removed from the Design Ladder example. Status stays exit 2.
