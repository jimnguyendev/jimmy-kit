---
name: ux-cro-audit
description: "CRO & Stakeholder Negotiation Suite — ethical conversion optimization (15-topic landing/pricing/in-app-screen audit), design-defense negotiation (stakeholder fear map, trigger/popup policy), and VoC mining. Use when optimizing conversion, auditing a landing or pricing page, writing headlines/price framing, when 'the boss dislikes the design', or when Sales/Marketing demand popups. NOT for general UX quality/heuristic review — that's the ux-review skill."
---

# CRO & Stakeholder Negotiation Suite

> **This skill exists to stop:** auditing UX by feel ("looks off") and optimizing conversion with dark patterns — instead of pointing at specific elements with sourced rules.

> 🔀 **Division of labor with ux-review:** this skill covers CONVERSION + NEGOTIATION; general UX quality/usability/heuristics → use `ux-review` (canonical, ships with its own gates).

> 📁 **Source convention:** `[sage]` = upstream Sage repo; `[docs]` = your internal docs repo (optional deep-dives). Missing files: the skill runs on the rules inlined here.

## 🤖 0. HOW TO USE (agent workflow)

**A. AUDIT a page/screen** ("audit this landing"): run the 3-question filter (§3) on the flow's main screen → sweep the 15-topic table (§7), only reporting rows with real findings, each pointing at a concrete element → check triggers/popups (§4) and visual safety (§5) → **enumerate the non-happy paths** (row 15: every async/AI/network step must have a specified failure, empty and low-confidence state). Output table: `# | exact location | disease | fix | severity`. Generic remarks ("UI feels dated") are invalid.

**Severity scale:** *launch-blocking* = breaks or coerces the core arc of the flow (§3 three questions unanswered, dark pattern, unspecified failure branch, payment/registration wall before any value) · *should-fix* = measurable conversion or trust leak with a known fix · *nice-to-have* = polish. Rows that don't apply to the surface type (e.g. hero/social proof on an in-app result screen) are listed once as "swept, n/a".

**Spec-only input** (no screenshot / URL): still run the full audit; write "exact location" descriptively and tag it `[UNVERIFIED]`; close with the list of what you need to see. For a scored deliverable use `templates/ux_audit_scorecard.md` (1–9 per topic, P0/P1/P2 map to launch-blocking/should-fix/nice-to-have).

**B. NEGOTIATE with stakeholders** ("boss dislikes it", "marketing wants popups", "brand demands the color"): identify which group in the fear map (§2) → speak THEIR language of concerns → never oppose the goal, change HOW it's reached (move the trigger, re-zone the space). Output: a concrete dialogue script (feeling→goal question, trade-off option) per §2 templates.

**C. VERIFICATION plan** ("test with users before dev"): assemble the 5-user guerrilla plan (§6): single task, observation criteria, evidence capture.

⚠️ All modes: every major recommendation traces to a sourced rule in this skill or carries an [ASSUMPTION] label. Never invent benchmark numbers.

## 🏛️ 1. CORE STRATEGY: COMMODITY vs MOAT

Selling generic features a free chatbot also does ("AI grammar scoring", "1,000 practice tests", "instant feedback") is the commodity trap. Shift the message to what only you own: *"diagnoses the ONE pronunciation error pinning you at band 5.5"*, *"a 14-day plan to fix your plateau"*, *"your percentile against 18 million real test submissions."* Sell the diagnosis and the proprietary data, not the commodity wrapper.

## 🤝 2. NEGOTIATING & DEFENDING DESIGN

Core principle: **never fight the other side's goal — accept it, then change how it's reached.**

| Stakeholder | Really cares about | Biggest fear | How to present for a yes |
| :--- | :--- | :--- | :--- |
| **Executives (CEO/BOD)** | Revenue, growth, positioning | Wasted spend, slowed business | Talk conversion, retention, market opportunity. Never layers and effects. |
| **Engineering (CTO/leads)** | Stability, scalability, deadlines | Out-of-scope surprises, forced rebuilds | Show happy path + edge cases; prove the design reuses existing components. |
| **Sales/Marketing** | Leads, close rate, this month's target | Customers confused, numbers dipping | Show the design lifts sign-ups; hand them ready flows and materials. |
| **Customers/learners** | Clarity, speed, no tricks | Complexity, forced payment, wasted time | Self-explanatory UI; try one question, get a result, no long forms. |

**When the boss critiques by feel ("I just don't like it"):**
1. Move from feeling to goal: *"Which part misses — is the information cluttered, or are you worried customers won't see the price clearly?"*
2. Offer a trade-off: *"If the goal is highlighting the annual price, I'll enlarge the price table and drop this secondary text — does that resolve it?"*

## 🎮 3. INVISIBLE ONBOARDING & THE 3-QUESTION FILTER

> "A good product barely needs onboarding — users just know what to do." *(internal product-leadership note)*

Naming note: the "3-question home screen" principle comes from internal product reviews; the "level 1-1" label is classic game-design shorthand for invisible onboarding (the first level that teaches every mechanic without a word of instructions).

**Within 3 seconds, the main screen must answer:** 1. WHERE AM I? · 2. WHAT DO I DO NEXT? · 3. HOW FAR TO MY GOAL?

Standard guest experience arc: an obvious next action (no spare buttons) → a safe 15-second anonymous try (waveform reacts instantly) → a surprise reward (result in 5s: the ONE blocking error + percentile) → pull to the flag (unlock a 7-day trial). ⚠️ Cut 50% of screen junk: duplicate tabs, "For You" blocks that duplicate navigation, heavyweight input-output pickers.

## 🚫 4. TRIGGER ZONING & ANTI-POPUP POLICY

* The disease: sales teams stacking popups that fire on app open. A real bank app once queued ~20 prioritized popups; users closed them in under a second.
* Three negotiation rules: **1. No popups on open** — the user came to do something. **2. Move the trigger to task completion** — pitch when they're done and relaxed, like the cashier at checkout, not the greeter at the door. **3. Zone the space** — promos get a small fixed area [ASSUMPTION: ~20% of viewport works as a starting rule], never covering the main flow.

## 🎨 5. VISUAL SAFETY

*"If everything is brand-red, what color is left for danger?"* — warning colors for system errors and security risks stay protected at full contrast, never diluted into backgrounds and ordinary buttons.

## 🔍 6. LEAN GUERRILLA TESTING — 5 USERS, 1 DAY

1. Five real users from the target segment. 2. One single task ("open this page, try one speaking question, see your score"). 3. Observe in silence — note stalls >3s, mis-taps, confusion. 4. Fix the dumbest failures the same day, before dev. (Basis: Nielsen's finding that ~5 users surface most usability issues.)

## 📑 7. THE 15-TOPIC CRO AUDIT TABLE

| # | Topic | Common disease | Standard fix |
| :-: | :--- | :--- | :--- |
| 1 | Hero H1 | Generic noun ("AI test prep") | Pain-extracting action line ("Catch the ONE error pinning you at 5.5") |
| 2 | Top nav | No login for returning learners | Fixed login, top right |
| 3 | CTA weight | CTA sinks into the page | Max contrast + risk-free promise ("Try 1 question free, no card") |
| 4 | Social proof | Fake reviews, stock models | Real score reports + before/after videos |
| 5 | Price framing | Naked big number | Comparison math (one retake fee vs a year of unlimited practice) |
| 6 | Mobile flow | 2-column table shatters | Accordion + sticky bottom CTA |
| 7 | Free-tier clarity | "Free" but asks for a card | "Try 1 question anonymously, no account" |
| 8 | Registration friction | 5-field form before any value | Value-first: score first, then 1-tap SSO save |
| 9 | Authority | Anonymous algorithm | Named examiners/experts behind the rubric |
| 10 | Objection handling | Ignoring "why not just use a chatbot?" | FAQ comparing head-on: proprietary data + error memory |
| 11 | Audio/mic UX | Dead mic, no warning | Live waveform + 10s-silence alert |
| 12 | Cognitive load | Dumping 40 errors | Highlight the ONE fatal error, tuck the other 39 |
| 13 | Reverse trial | Card required upfront | 7-day full unlock, transparent countdown |
| 14 | Dark-pattern check | Sneaky renewals, hidden cancel | 1-click cancel, explicit terms, no hidden fees |
| 15 | Failure & empty states | AI grading / upload / payment step has no specified failure, timeout or low-confidence branch — user sees a spinner or a blank result | Spec every branch: plain-language error, retry, what is preserved (answers, score), a human fallback for AI low-confidence; **unspecified = launch-blocking** |

## 📝 8. VOICE-OF-CUSTOMER PAIN MINING

> "You don't write copy. You SWIPE it from your customers." — Joanna Wiebe (Copyhackers)

1. Mine real conversations (internal support/chat corpus) + competitors' 1-star reviews. 2. Capture verbatim emotional language ("stuck at 5.5 no matter what", "scared of telesales calls"). 3. Lift it into H1/H2 copy, replacing internal jargon.
