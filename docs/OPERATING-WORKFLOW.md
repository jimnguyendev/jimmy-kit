# Operating Workflow — how the 48 skills fit together

Three layers. The spine is Sage's intent spectrum (UNDERSTAND → ENVISION → DELIVER → REFLECT); this kit extends it with an intake thinking layer and a red-team gate.

## Layer 1 — Intake: the 7 questions (run in your head first)
0. How big is this, what does "done" mean, who confirms? → `change-tiers`
1. What do I actually KNOW? (label [VERIFIED]/[ASSUMPTION]/[GUESS]) → `analyst`
2. What job is the user hiring us for? → `jtbd`
3. Which assumption kills everything if wrong — cheapest way to test it? → spike
4. At least 2 options — and how does each fail? → `architect` + `decision-log`
5. Which hard case breaks the spec? → `prd` / `ux-specify`
6. What evidence counts as done? → `quality-gates`
7. How do I say it back in 4 lines? (Bottom line / Verified / NOT verified / Lesson)

## Layer 2 — Mandatory gate before building or pitching
`product-council` — 4 role lenses (CEO/Business · PD/Strategy · CTO/Engineering · UX/Human); every seat must state its acceptance condition. Verdict ⚠/✗ → back to Layer 1.

## Layer 3 — The 4-phase chain
| Phase | Skills | Produces |
|---|---|---|
| UNDERSTAND | analyst · jtbd · ux-discovery · problem-solving · zoom-out · youtube-transcript | Problem statement + jobs + sourced benchmark |
| ENVISION | opportunity-map · ux-brief · ux-design · prd · ux-specify · ux-writing · ux-plan-tasks | Spec with hard-cases-first + clean copy |
| DELIVER | architect · change-tiers · decision-log · constitution · quality-gates · okr-outcome-architect · the `skills/engineering/` category | 2 options + ADR + gates + bets wired to KRs |
| REFLECT | tracking-architect · growth-markov-duolingo · engagement-matrix-analytics · advanced-rfm-segmentation · ux-review · independent-review · ux-cro-audit · retrospective | Gated metrics + independent review + WHEN/CHECK/BECAUSE lessons |

## Ten real problems → skill chains
1. **"Conversion is low, do something"** → analyst (label the claim) → tracking-architect (is the number gated?) → jtbd → product-council → prd → okr-outcome-architect → quality-gates → retrospective.
2. **"Just build feature X"** (solution smuggled into the brief) → 7 questions flip it → jtbd → product-council (PD seat catches solution bias) → opportunity-map → prd.
3. **Audit / optimize a landing or pricing page** → ux-cro-audit (15-topic table) → ux-writing → tracking-architect (before/after events) → single-variable A/B.
4. **"Boss dislikes the design" / popup demands** → ux-cro-audit negotiation mode (stakeholder fear map; change the trigger, don't ban the goal).
5. **Write or review quarterly OKRs** → okr-outcome-architect → OKR–initiative matrix → weekly confidence check-ins.
6. **"Is tracking done?" / add an event** → tracking-architect (MUST READ registry; status by gates; 4-line report).
7. **"Retention is dropping"** → growth-markov-duolingo (which transition leaks) → engagement-matrix-analytics (which feature retains) → advanced-rfm-segmentation (which segment to save) → okr-outcome-architect (bet wired to a KR).
8. **A/B test ended / incident closed** → retrospective (WHEN/CHECK/BECAUSE; 5-whys) → decision-log (ADR) → constitution if the new rule needs enforcement.
9. **Leadership pitch next week** → product-council red-team → 4-line report → 10-slide narrative → tough-question bank.
10. **Technical decision** (pick a technology, change architecture) → change-tiers → architect (≥2 options + what-happens-when-this-fails) → decision-log → quality-gates.

## Five laws that apply to every problem
1. No [VERIFIED] problem, no solution writing. 2. Exit 2 (unverifiable) is never a pass. 3. Ceremony scales with risk, not size. 4. A rule that matters needs a mechanism, not a reminder. 5. Every claim carries a source + date, or an [ASSUMPTION] label.
