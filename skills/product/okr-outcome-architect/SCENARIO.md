# Scenario — okr-outcome-architect (written BEFORE finalization)
**Rationale:** given an OKR set full of disguised projects, an unaided agent polishes wording instead of catching structural failures.
**Sample input (4 planted bugs):** "O: Launch the product successfully. KR1: Complete the 6 tracking gates. KR2: Ship the results teaser. KR3: Improve user satisfaction. KR4: Run 4 marketing campaigns."
**Expected behaviors:**
- [ ] Flags O as a project; proposes an outcome ("guests see enough value in one visit to come back and register")
- [ ] Flags KR1/KR2 as initiatives → moves them to the initiative layer; replaces with outcome KRs
- [ ] Flags KR3 missing all 4 parts; KR4 as output → leads + CAC
- [ ] Output in the ❌/⚠️/✅ table format with sufficiency/necessity tests, Committed/Stretch labels, owners
- [ ] Does NOT invent baselines — marks them "[baseline required — measure first]"
**Status:** [PASS — exit 0] First run 2026-08-30 (author dry run; see limitation note above).
