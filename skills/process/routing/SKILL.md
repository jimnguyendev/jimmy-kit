---
name: routing
description: Choose a workflow. Use when the user asks where to start or a request spans skills and its current decision or next action is unclear.
version: "1.0.0"
type: system
---

# Routing depth

Choose the smallest workflow that resolves the user's current decision. The optional
kit dispatcher in the target repo's AGENTS.md provides shortcuts; this skill also
works on its own when only selected skills are installed.

## Dosage and authority

- **Tier 1:** act directly or use one short skill. No menu or council.
- **Tier 2:** announce and proceed with one or two relevant skills. Reuse accepted
  scope, supplied context, and existing authorization; do not add approval stops
  for specs, plans, or skill handoffs.
- **Tier 3:** use the full intake and council for unresolved consequential decisions.
  If the user already accepted a decision, carry it forward. Ask only about a
  material gap, contradiction, changed risk, or action outside that authorization.

This dosage rule governs the workflow recipes below and in linked skills. A recipe
is not a new permission boundary. Continue authorized work through relevant checks
and fixes; finish when the requested output and its acceptance criteria are met.

## Select by intent and current state

Use the request and available evidence to classify in context; routine routing does
not need a classifier subagent. Topic words alone do not determine the workflow.

| Current need | Relevant owner |
|---|---|
| Problem or decision is unclear | `analyst`; `engineering-design-thinking` for an engineering gap |
| Customer jobs or evidence are unknown | `jtbd` or `ux-discovery` |
| Accepted needs need requirements | `prd`; `ux-specify` for user-facing gaps |
| A technical choice is unresolved | `architect` or `engineering-design-thinking` |
| Accepted behavior needs implementation | Appropriate engineering skill; `tdd-go` only for Go |
| A bug needs diagnosis | `diagnose` |
| A document or code needs review | `independent-review` |
| An existing UI needs usability review | `ux-review`; conversion questions use `ux-cro-audit` |
| A retention bottleneck is unknown | `growth-markov-duolingo`; other analytics only if needed |

Load only available skills. If a specialist is absent, state that limitation and
apply the relevant criteria from the current skill or target project. Do not
invoke nonexistent commands or require installing the entire kit.

## When to ask

One clear route: announce it and proceed. Multiple compatible skills: select the
smallest sufficient set. If different routes would produce materially different
outcomes and the user's intent does not settle the choice, ask one focused
question with a recommendation. A routing menu is optional, not a default gate.

## Worked examples

- "Audit our checkout UX" → review the supplied UI; no menu unless scope is unclear.
- "Audit this API's error handling" → code/contract review, not UX review.
- "Add the approved event" → inspect the existing tracking contract, implement,
  and verify; no new PRD or repeated approval.
- "Improve onboarding conversion" → inspect the available funnel and experience;
  ask only if missing evidence prevents a meaningful next step.
- "Change the button color to blue" → Tier 1; make and inspect the change.

## The failure this prevents

The routing chain exists because the alternative is an agent that treats every
request as a DELIVER request — the default failure mode, and the one that ships
a fix for a problem nobody diagnosed. If a request is a question, answering it
with an implementation is not efficiency. It is a wrong answer that took work.


---

## Applied context — kit routing table (not part of the original)
This kit's concrete routing map lives in `docs/OPERATING-WORKFLOW.md`: real problem shapes → conditional skill chains, plus the 7-question intake layer and the risk-dosed product-council gate. Classify dosage first: Tier 1 may act directly, Tier 2 normally uses one or two skills, and Tier 3 uses the full intake plus council. By default, Tier 1 and already-approved Tier 2 bypass council. Explicit red-team/pitch requests and consequential product/platform decisions are exceptions: they invoke council directly but do not expand the rest of the workflow unless the work is Tier 3. Stop when the current output settles the decision. The map is optional when the full kit is installed. When routing is needed, choose by problem shape first (vague metric complaint → analyst+tracking-architect; solution-in-disguise → engineering-design-thinking Problem Frame; page optimization → ux-cro-audit; quarterly goals → okr-outcome-architect; retention drop → growth-markov chain; post-test/incident → retrospective+decision-log; tech decision → change-tiers+architect). Time estimates are "guesses wearing a number's clothing" — give ranges with conditions.
