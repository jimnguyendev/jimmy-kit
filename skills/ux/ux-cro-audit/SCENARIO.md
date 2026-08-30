# Scenario — ux-cro-audit (written BEFORE finalization)
**Rationale:** asked to audit a landing page, an unaided agent produces aesthetic vibes ("feels dated") instead of element-level findings tied to sourced rules.
**Sample input:** "Audit the guest results screen (results partially locked behind a Register button)."
**Expected behaviors:**
- [ ] Runs the 3-question filter on the main screen first
- [ ] Output table: exact location → disease → fix → severity (launch-blocking / should-fix / nice-to-have)
- [ ] Catches registration friction (#8 value-first) and cognitive load (#12 one fatal error)
- [ ] Flags the AI-grading-failure branch as launch-blocking if unspecified; proposes no dark patterns
**Status:** [PASS — exit 0] Independent run #2 2026-08-30 4/4 after adding §7 row 15 (see below). Run #1 same day was PARTIAL 3/4 (missed the AI-failure branch). Author dry run 2026-08-30 PASS on spec.

---
## Independent run #1 — 2026-08-30 (fresh agent, Claude Code / Fable 5; given SKILL.md + sample input + a 4-line spec of the screen, no access to this file)
**Result: PARTIAL — exit 1 (3 of 4 checks; one planted issue missed).**
- [x] Ran the §3 3-question filter on the main screen first (WHERE AM I pass-provisional / WHAT NEXT pass-but-coercive / HOW FAR fail).
- [x] 10-row table `# | exact location | disease | fix | severity` using launch-blocking / should-fix / nice-to-have; listed swept-clean rows; listed what it needs to see to close the audit.
- [x] Caught registration friction (#8, findings 1–3: blur withholds the reward, "unlock" implies payment, multi-field form at highest intent) and cognitive load / one-fatal-error (#12, findings 1 and 6). Explicitly flagged the blur as borderline dark pattern and proposed honest locked cards instead — no dark patterns proposed.
- [ ] **MISSED:** the AI-grading-failure branch (what the guest sees when grading fails / low-confidence result) was not raised as a finding. It appears only incidentally in finding 9 as a colour example ("grading failed, retry"). Expected: launch-blocking "unspecified error branch".

**Why it was missed (diagnosis):** the §7 sweep is landing-page oriented (hero, nav, social proof, price…) and has no row for *system-failure / empty / error states*; the skill never tells the auditor to enumerate non-happy paths. Fix candidate: add a §7 row "#15 Failure & empty states — every async/AI step has a specified failure branch; unspecified = launch-blocking".

**Other friction reported by the runner:**
1. `templates/ux_audit_scorecard.md` (1–9 scores, P0/P1/P2) conflicts with §0's severity words and is never referenced from SKILL.md — link it or reconcile.
2. No guidance for spec-only input (no screenshot) even though §0 demands "concrete element"; allow "described location + [UNVERIFIED]".
3. No criteria for choosing between the 3 severity levels.
4. §7 rows 1/4/5/11 don't apply to an in-app results screen — note which rows apply to which surface type.
5. §3 "(internal product-leadership note)" and §4 "a real bank app" are unsourced, in tension with §0's "traces to a sourced rule".

---
## Independent run #2 — 2026-08-30 (fresh agent, after fix: §7 row 15 "Failure & empty states", severity criteria, spec-only rule)
**Result: PASS — exit 0 (4/4).**
- [x] §3 filter first (Q3 "how far to my goal" = No; blurred breakdown is exactly where the answer would live).
- [x] 10-row findings table, every location tagged `[UNVERIFIED]`, n/a rows listed once, "what I need to see" list, optional scorecard appended.
- [x] #8 registration friction (finding 1, launch-blocking; finding 10 return path) and #12 cognitive load (finding 7) caught; blur flagged as curiosity-gap coercion → honest locked module, no dark patterns proposed.
- [x] **Finding 4 — AI grading failure/timeout/partial/low-confidence branches unspecified → launch-blocking**, with all four branches specced and "no Register CTA on a failure state". The gap from run #1 is closed by row 15.

Friction reported (fixed in the same session): scorecard template said 14 topics and lacked row 15 → synced; naming drift rows 9/13 → aligned; scoring on spec = estimate, findings table is primary → stated in template footer. Left as-is: §3 guest arc is speaking-test-flavoured (kit example domain).
