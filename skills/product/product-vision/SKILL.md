---
name: product-vision
description: "Set or repair a product vision so the team stops being a feature factory. Use when requests are being built in the order they arrive, when nobody can say what the product is for in 3–5 years, when a team wants to delete a 'low-usage' feature, when users keep asking for features that don't fix their problem, or when design is treated as decoration."
---

# Product Vision & Systems Thinking

> **This skill exists to stop:** the feature factory — building whatever the loudest customer or executive asks for, until the product is a patchwork nobody can explain — and its cousin, deleting a feature because internal click data was low.

## Quick start
Paste a backlog or a "delete this feature" request and get back: a one-sentence vision check, each request reframed as the user question it answers, a ripple-effect map for any removal, and the North Star the roadmap serves.


## 🤖 0. HOW TO USE (agent workflow)
**A. Vision check:** can the team state, in one sentence, what core value the product delivers to whom over the next 3–5 years? If not, draft it before any roadmap talk. Then draw the **ecosystem map** — every actor who touches the product (end user, operator, partner, admin, support), not just the main screen.
**B. Reframe requests as questions:** for every feature request, write the user's *question* it answers ("how do I…?"). Requests with no question behind them go to the parking lot.
**C. Ripple check before removal:** never delete or change a feature on internal usage data alone — map who else depends on its output, then ask real users outside the building.
**D. Design maturity:** locate the org on the Design Ladder (styling → process → strategy) and name the next rung; don't ask for strategic design from a team still doing styling.
**Standard output:** one-sentence vision · ecosystem map · questions-behind-requests table · ripple-effect map for any proposed removal · the one North Star the roadmap serves.

## 1. Danish Design Ladder (where design sits in the org)
Level 1 **Non-design** (function only) → Level 2 **Styling** (logo, packaging at the end) → Level 3 **Process** (design shapes flows and systems: design system, consistent journeys) → Level 4 **Strategy** (design discovers new business — e.g. a heavyweight photo tool spinning out a focused product for a segment that used 10% of the features). Most SMEs sit at level 1–2; the leap to 3 is a process change, not a hire.

## 2. Product vision — three jobs it does
1. **Keystone:** what core value, for whom, over 3–5 years. Without it, a business plan alone produces a feature factory.
2. **Ecosystem map:** every stakeholder sees their touchpoint — a ride-hailing product is rider app + driver app + merchant portal + dispatch + support tooling, not one screen.
3. **North Star for experience:** a long-horizon concept the team can steer by (the 1987 "knowledge navigator" concept video predated the tablet + assistant it described by 23 years).

## 3. Questions vs answers
See the product as **answers to users' questions**, not a list of features. "I want to hang a TV" → a precise, safe hole → a light drill with laser guide for first-timers. A document editor is "how do I not lose my file when I forget it at home?" (cloud), "how do five of us edit one contract?" (co-authoring), "how do I not look unprofessional?" (spell-check). Every feature must trace back to a question; the persona is whoever asks it.

## 4. Systems thinking & the ripple effect
A product's value is more than the sum of parts. Team A removes an "unused" export button to clean the UI → Team B's weekly report breaks (it consumed that export) → enterprise customers churn. **Local optimization can destroy someone else's workflow.** Real case: a team planned to delete a "low-click" template feature; external interviews revealed customers would cancel contracts over it — it was their lifeline when stuck.

## 5. The 8-year lesson — users know the pain, not the design
A survey product shipped one question per week and then spent eight years building whatever customers asked for; adoption stayed flat and large accounts churned, because the root problem (data too sparse to analyze) was never addressed — features were band-aids. **Users know exactly what hurts; they almost never know how to design the cure. Don't let them write your spec.** The turnaround came from bringing in a domain expert (organizational-behavior PhD), resetting the north star ("any question, any time, to anyone"), and a release–learn–refine rebuild over ~18 months.

## Applied context (edtech)
Vision sentence: "help self-studying learners know exactly where they stand and what to fix next, without a human tutor." Ecosystem map: learner · guest · mentor/reviewer · content/academic team · admissions · analytics. Questions behind requests: "add a leaderboard" → "how do I know if I'm improving relative to others?" — answered better by percentile than by a leaderboard. Ripple check before removing the "mock test" tab: monthly reports and mentor workflows read its data.
