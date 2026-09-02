# Scenario — okr-outcome-architect (written BEFORE finalization)
**Rationale:** given an OKR set full of disguised projects, an unaided agent polishes wording instead of catching structural failures.
**Sample input (4 planted bugs):** "O: Launch the product successfully. KR1: Complete the 6 tracking gates. KR2: Ship the results teaser. KR3: Improve user satisfaction. KR4: Run 4 marketing campaigns."
**Expected behaviors:**
- [ ] Flags O as a project; proposes an outcome ("guests see enough value in one visit to come back and register")
- [ ] Flags KR1/KR2 as initiatives → moves them to the initiative layer; replaces with outcome KRs
- [ ] Flags KR3 missing all 4 parts; KR4 as output → leads + CAC
- [ ] Output in the ❌/⚠️/✅ table format with sufficiency/necessity tests, Committed/Stretch labels, owners
- [ ] Does NOT invent baselines — marks them "[baseline required — measure first]"
**Status:** [PASS — exit 0] Author dry run 2026-08-30 · Independent run #1 2026-08-30 PASS (see below).

---
## Independent run #1 — 2026-08-30 (fresh agent, Claude Code / Fable 5; given SKILL.md + sample input only, no access to this file)
**Result: PASS — exit 0 (5/5).**
- [x] O flagged as activity ("launch" = project, "successfully" undefined); proposed *"Turn guest test-takers into learners who come back, so that the launch grows the registered learner base."*
- [x] KR1 (tracking gates) and KR2 (teaser) reclassified as initiatives/enablers; replaced by outcome KRs (7-day return rate as lagging anchor; guest→registered conversion as leading).
- [x] KR3 flagged 0/4 parts → satisfaction proxy or drop (necessity test); KR4 flagged output trap → new guest test starts + cost per completed test.
- [x] Combined ❌/⚠️/✅ issue table; both sanity tests (sufficiency/necessity) run on the set; Committed/Stretch, ranking and one-owner-per-KR called out; §7 60-second checklist filled current vs proposed.
- [x] No baselines invented — every target written as `[baseline TBD] → [target]`, with an explicit "not finishable today — measure first" blocking note. Also stopped-and-asked for the business outcome ("launch… so that WHAT?").

**Friction reported by the runner (skill-improvement candidates):**
1. §0-A says run sanity tests "on every O–KR pair" but §1 phrases them about the whole set — clarify.
2. "Stop and ask" vs Mode A deliverable: when no baseline exists (the common case) the skill doesn't say whether to halt or deliver with placeholders. Add one line: deliver with `[baseline TBD]` placeholders.
3. "A table per issue" → "one row per issue" reads better.
4. "Volume limits" step has nothing to check for a single-Objective set.

**Friction 1-4 addressed 2026-09-02** — wording/scoping only, no behavior change, so run #1 PASS still stands (no re-run required): (1) §0-A now reads "on the set as a whole (all KRs vs the Objective)"; (2) the all-modes note now says AUDIT still delivers, with every unknown written as `[baseline TBD - measure first] -> [target]`; (3) "one row per issue"; (4) volume limits marked "(skip if a single Objective)".

**Source-fidelity review 2026-09-02** (against the two source handbook PDFs, using `write-a-skill`'s Review Checklist) - 7 gaps found: 6 fixed in SKILL.md, the 7th was this file's own missing closure note (above). The six: the OKR-Initiative matrix had no table shape for mode C to build; §4 had no nested weighted example for "sums to 100% at each level"; §7 was missing the source's "KRs ranked or weighted within each Objective" check; the description spent ~85 chars on provenance (now in README only) and lacked triggers for check-ins/stretch/weighting; no handoffs to `tracking-architect` / `product-strategy` / `product-council` / `prd`; the "Aspirational" alias for Stretch was dropped. Not re-scenario-tested - five are additive reference material and one restores a checklist row; nothing in the mode workflows changed. Content that stays deliberately dropped: the source's Quick Reference Card (all 13 Q&A already answered elsewhere in the skill). Content deliberately added beyond source: "1-2 leading" metrics per Objective (source says only "at least one lagging, add leading").
