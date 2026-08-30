# Scenario — ux-cro-audit (written BEFORE finalization)
**Rationale:** asked to audit a landing page, an unaided agent produces aesthetic vibes ("feels dated") instead of element-level findings tied to sourced rules.
**Sample input:** "Audit the guest results screen (results partially locked behind a Register button)."
**Expected behaviors:**
- [ ] Runs the 3-question filter on the main screen first
- [ ] Output table: exact location → disease → fix → severity (launch-blocking / should-fix / nice-to-have)
- [ ] Catches registration friction (#8 value-first) and cognitive load (#12 one fatal error)
- [ ] Flags the AI-grading-failure branch as launch-blocking if unspecified; proposes no dark patterns
**Status:** [PASS — exit 0] First run 2026-08-30 (author dry run on spec, not live UI — declared limitation).
