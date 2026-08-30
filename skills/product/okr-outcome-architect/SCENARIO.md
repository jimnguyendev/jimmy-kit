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
