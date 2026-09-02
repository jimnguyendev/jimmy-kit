# Scenario — product-council (written BEFORE the skill was finalized)
**Rationale (the failure to prevent):** given a feature idea, an unaided agent produces generic praise-and-suggestions from a single viewpoint, missing each executive's signature question and never stating acceptance conditions.
**Sample input:** "Red-team this: send guests their test results via a chat-app message."
**Non-trigger cases (added before the dosage revision):** "Change this internal button label" and "implement an analytics event whose registry contract is already approved." Native skill discovery must not select `product-council` for either case.
**Expected behaviors (pass when all check):**
- [ ] Checks evidence first (funnel numbers? job?) — refuses to debate on a [GUESS]
- [ ] All 4 seats, each with: hardest question + specific hole + ACCEPTANCE CONDITION
- [ ] PD seat catches the solution bias (the channel is a solution — is the job "review my result" or "be reminded to return"?)
- [ ] CTO seat demands tradeoffs + accompanying telemetry + A/B plan; CEO seat demands a clickable mock + comparison table; UX seat inspects trigger timing and contact-request anxiety
- [ ] Conflict table + verdict with homework
- [ ] Tier 1 and already-approved Tier 2 work do not trigger the council merely because they involve a feature, implementation, or presentation artifact
- [ ] An explicit request to review or rehearse a pitch triggers the council even when the user did not use the words "Tier 3" or "consequential"
**Status:** [PASS — exit 0] Original council behavior passed; the revised native-discovery description passed Tier 1, approved Tier 2, and explicit-pitch cases on 2026-09-02.

---
## Independent run #1 — 2026-08-30 (fresh agent, Claude Code / Fable 5; given SKILL.md + sample input only, no access to this file)
**Result: PASS — exit 0 (5/5).**
- [x] Step 0 evidence gate triggered STOP: request is a solution, zero sourced numbers, unclear scope. Wrote the 4 questions it would ask (problem in one sentence without "chat"; guest→Register + 7-day return with dashboard/date; which app / do we already hold the handle; anything clickable). Continued only under explicitly tagged [GUESS] placeholders and capped the verdict accordingly.
- [x] 4 seats, each with hardest question + specific hole + ACCEPTANCE CONDITION, first-person, with analogy and quotable close.
- [x] PD caught the solution bias: "is the job REGISTER, RETURN, or feel-seen — three features sharing a channel"; demanded the 2-day slice (email-me-my-results reusing existing send path).
- [x] CTO: cost/message + break-even, two-option tradeoff table, unauthenticated-contact identity object as a data contract, 5 named events (`guest_contact_captured` … `register_from_message`), A/B plan. CEO: clickable mock + 3-column comparison table, "at most one new decision". UX: moved the trigger after the score / to exit-idle moment, flagged contact-request privacy anxiety ("will you message me forever?"), 5-user guerrilla test first.
- [x] 4-row conflict table with reconciliations; verdict ✗ Back to the problem with 3 homework items; routed back to `analyst` / `jtbd` → `prd`, `tracking-architect` if slice ships.

Note: author dry run returned ⚠; independent run returned ✗ — stricter because the fresh agent had no numbers at all. Both consistent with the gate.

## Independent discovery run — 2026-09-02

The fresh agent saw only frontmatter descriptions for the five plausible skills, not their bodies or this scenario:

```text
1. Internal button label: load ux-writing. Product Council: No.
2. Approved analytics event implementation: load none of these; the taxonomy/schema decision is settled. Product Council: No.
3. Shared identity-platform decision and consequential leadership pitch: load engineering-design-thinking and product-council. Product Council: Yes.
```

**Result:** PASS — 3/3 discovery choices; Tier 1 and approved Tier 2 did not trigger council.

## Independent explicit-pitch discovery rerun — 2026-09-02

The fresh agent saw only frontmatter names and descriptions for the plausible skills, not their bodies or this scenario. The third prompt deliberately omitted the words "Tier 3" and "consequential."

```text
1. Change this internal button label. Load none. Product Council: No.
2. Implement this approved analytics event; schema and taxonomy are settled. Load none. Product Council: No.
3. Review and rehearse this leadership pitch for our proposed retention feature. Load product-council. Product Council: Yes.
```

**Result:** PASS — 3/3; explicit pitch review triggers natively while ordinary Tier 1 and approved Tier 2 work do not.

**Friction reported by the runner (skill-improvement candidates):**
1. Step 0 has no fallback rule when the user can't supply data — suggest: "if forced to proceed, verdict ≤ ⚠ and missing evidence is homework #1".
2. STANDARD OUTPUT shows one line per seat while voice rules demand 3–6 sentences — mild tension; state that a labelled paragraph is fine.
3. "Next skill in chain" when verdict is ✗ is actually a *previous* phase — say so.
4. PD's "three home-screen jobs" question is home-screen-specific; generalize to "the three questions of the surface under review".
