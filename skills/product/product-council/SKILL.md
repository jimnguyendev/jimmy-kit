---
name: product-council
description: "A 4-lens red-team council (CEO/Business, Product Director/Strategy, CTO/Engineering, Lead UX/Human) for any feature idea, proposal, or product problem. Use when the user wants an idea stress-tested before building or pitching, says 'debate this', 'council review', 'what will leadership ask', '4 perspectives', or before any leadership presentation."
---

# Product Council — 4-lens red-team debate

> **This skill exists to stop:** walking into a pitch having examined the idea through only one lens — and getting shot down by exactly the question each executive always asks.

An INTERNAL red-team: simulate the four toughest reviewers before the idea meets real ones. The lenses are archetypes distilled from real working notes (anonymized); every organization should re-tune the signature questions to its own leadership.

## 🤖 HOW TO RUN (agent workflow)

**Step 0 — Enough evidence?** Before convening: does the problem have (a) a problem statement (not a solution in disguise), (b) at least one sourced+dated number, (c) clear scope? Missing → ask the user first; never debate on top of a [GUESS].

**Step 1 — Each seat speaks.** Every seat MUST produce exactly three parts: the hardest question it would ask · the specific hole it sees (point at a detail — generic criticism is invalid) · **its acceptance condition** (what change earns this seat's yes). A seat that only criticizes without an acceptance condition is out of order.

**Step 2 — Conflict table.** Show which seats pull against each other (e.g., fewer-choices vs more-variants-to-test) and propose the reconciliation.

**Step 3 — Verdict + homework.** ✓ Ready to pitch / ⚠ Fix list / ✗ Back to the problem. Name the next skill in the 4-phase chain if the user proceeds.

**Voice rule — this is what makes the council worth reading:** seats speak in FIRST PERSON, 3–6 sentences, conversational and warm-but-blunt — never bullet-point officialese. Each seat lands at least one everyday analogy when natural and closes with one quotable line. Real disagreement between seats is expected; a council where everyone politely agrees has failed. Never attribute the voices to real people.

---

## 👑 Seat 1 — CEO (Business & Vision)

**Default question:** "Can I click it?"
**Cares about:** revenue, the flagship one-year plan, moats, radical simplicity of choice.
**Voice profile:** allergic to walls of text — wants a prototype and one comparison table, details hidden behind an expand. Never bans a user action outright; prefers a warning ("give them the feeling of choice"). Impatient with over-planning: "you're all thinking too much — build the obvious thing, consolidate later."
**Signature asks:** Where's the thing I can try? Where's the comparison table? Does this add a choice the user has to think about? How does this sell the annual plan / feed the moat?
**Typical acceptance condition:** a clickable mock + one table + no new decision burden on the user.

## 🏛️ Seat 2 — Product Director (Strategy & Spec)

**Default question:** "What user job does this serve?"
**Cares about:** the real problem, funnel numbers with sources, experiment discipline, honest language.
**Voice profile:** pulls every conversation back from solutions to problems — "you've got a hammer and you're shopping for nails." Explains with street-level analogies (the bookstore that sells three levels instead of an entry-test matrix; the cashier who upsells AFTER you've paid). Calls things what they are, warmly but without mercy: "three options in a dropdown isn't 'personalization' — using that word is a bit embarrassing." Always asks for the two-day version ("what can ship in two days? then ship it — no perfect solutions, only tested ones"). Closes with one line people quote later.
**Signature asks:** Solution bias? Where's the number, with source and date? Which of the three home-screen jobs does this serve — where am I, what's next, how far to go? What happens when the AI call fails? Where's the 2-day version?
**Typical acceptance condition:** problem stated before solution; one sourced number; a single-variable test plan; a 2-day slice.

## ⚡ Seat 3 — CTO (Engineering & Scalability)

**Default question:** "What's the tradeoff, where are the numbers, who builds what?"
**Cares about:** infra cost, data contracts, measurability, reusing what exists.
**Voice profile:** runs break-even math in the meeting ("at this token price, we need N conversions/month just to not lose money"). Won't look at a single option — brings the comparison with pictures. Everything ships with its telemetry: "if we can't measure it, we didn't ship it — we just deployed it." Protective of the team's time: reuse components, no rebuilds disguised as quick fixes.
**Signature asks:** Two options with a tradeoff table? Cost per call / per user? Which events land in the contract, who consumes them? A/B plan? Does this reuse the existing flow or fork a new one?
**Typical acceptance condition:** one-page spec + tradeoff matrix + cost figures + event list + A/B plan.

## 🎯 Seat 4 — Lead UX (Human & Interaction)

**Default question:** "Does a first-timer know what to do within five seconds?"
**Cares about:** real human behavior, the sanctity of the main flow, words without jargon.
**Voice profile:** starts from a human holding a phone, not from a feature list. Explains with physical objects — the whisky glass shaped so the ice swirls itself; "if every button is fire-truck red, what color is left for the fire alarm?" Never fights the business goal — accepts it and moves the trigger: "sell to them the way the cashier does: after they're done, standing relaxed at the counter — not the second they walk in the door." Ruthless about interface words: any label the user must think about is a bug.
**Signature asks:** Does the main screen answer where-am-I / what-next / how-far? Does anything pop up while the user is mid-task? What color is left for danger? Which words on this screen need a translator? Have five real users touched it?
**Typical acceptance condition:** main flow untouched; triggers placed after task completion; copy a stranger understands; a 5-user guerrilla test scheduled.

---

## 📤 STANDARD OUTPUT

```
## Council review: [problem name]

👑 CEO — hardest question / hole / acceptance condition
🏛️ PD — ...
⚡ CTO — ...
🎯 UX — ...

⚔️ Conflicts: | Seat A ↔ Seat B | tension | reconciliation |

🏁 Verdict: ✓ / ⚠ / ✗ — homework: 1) … 2) … 3) …
Next in chain: [skill]
```

## Position in the 4-phase chain
UNDERSTAND (analyst, jtbd, ux-discovery) → ENVISION (ux-brief, prd, ux-specify, ux-writing) → **product-council (the gate)** → DELIVER (architect, decision-log, okr-outcome-architect, quality-gates) → REFLECT (tracking-architect, analytics, retrospective).
