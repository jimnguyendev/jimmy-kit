---
name: product-strategy
description: "Build a product strategy with validation gates, resource reality, and a mission statement — before roadmapping. Use when a new product or platform is proposed, when someone wants to skip validation and 'ship to everyone', when a roadmap exists but nobody checked whether money lasts to the end, when choosing what to compete on, or when a hardware/physical component is involved."
---

# Product Strategy & Stage-Gate Validation

> **This skill exists to stop:** strategies that never checked whether resources outlast R&D cost, and launches that jump from prototype to mass rollout because the pilot "looked fine".


## 🤖 0. HOW TO USE (agent workflow)
**A. Classify the product:** breakthrough (new to the world) · platform (shared foundation for a family) · derivative/incremental (inherits a frame). Classification sets the validation depth — breakthrough runs every gate; derivative may compress early gates. Say which and why.
**B. Choose the competitive weapon** explicitly: cost · core technology · experience · industrial design. One primary. "All four" is not a strategy.
**C. Resource law:** total resources (cash + committed funding) must exceed total R&D + validation cost with margin. If the sum fails, shrink scope now — not at the pilot stage.
**D. Gates:** define the validation stages (§2) and the exit criteria for each; **never skip to mass rollout after a failed pilot — run pilot 2, pilot 3.**
**E. Mission statement** (§4) before the roadmap; roadmap phases must trace back to it.
**Standard output:** classification + weapon · resource check (numbers) · gate plan with exit criteria · mission statement · phased roadmap.

## 1. Physical vs digital — what changes
Software can "ship and patch"; hardware cannot recall a million units to fix a firmware-adjacent mechanical flaw. The discipline hardware forces — validate in stages, small lots first — is worth importing into digital for anything expensive to reverse (pricing changes, data-model migrations, platform choices).

## 2. Stage-gate validation
| Stage (hardware) | Purpose | Sample size | Digital analogue |
|---|---|---|---|
| Kick-off | Concept & design | — | Problem framing, PRD |
| **EVT** — engineering validation | Does the core work? 90–95% of intended function | 5–20 hand-built units | Spike / prototype on the riskiest assumption |
| **DVT** — design validation | Durability, environment, "simple is best" — cut every spare part before tooling | dozens | Alpha with internal users; edge cases; performance |
| **PVT** — production validation | Can the factory make it? Yield, cycle time, component failures | 100–1,000 | Beta / pilot with a real cohort; ops load; support load |
| **MP** — mass production | Ship at scale | — | General availability |
**Rule:** a serious failure at PVT means PVT-2 and PVT-3, never MP. In digital terms: a failed pilot does not "graduate with notes".

## 3. Metrics framework
Digital products live on DAU/MAU, retention, CAC. Physical (and physical-adjacent) products need: **sales velocity** (sell-in vs sell-out), **resale value** (does the product hold price at 6–12 months — the market's quality verdict), **deposit-to-delivery conversion** (commitment after the demo), **VoC root-cause split** (complaints caused by engineering vs by sales/marketing promises). Whatever the product, split complaints by root cause before assigning blame.

## 4. Strategy framework — four steps
1. **Positioning & competition** — product type + competitive weapon (§0 A–B).
2. **Resource law** — cash + funding > R&D + validation cost. A great strategy that runs out of money at DVT is a dead project.
3. **Roadmap phasing** — which features in which phase, and what each phase must prove.
4. **Mission statement** — name and one-sentence core (what problem, for whom) · quantified business goals at 12 months (revenue, margin, users) · primary vs secondary segments · assumptions and constraints (max capital, tech limits, backup suppliers/vendors).

## Applied context (edtech)
Classify a new AI-graded practice product as *breakthrough* for the org (new grading engine, new funnel) → run every gate: spike the grading cost per attempt (EVT), alpha with internal tutors on edge cases like silent audio and mid-grade AI failure (DVT), a 300-learner pilot measuring return rate and support tickets (PVT), then general release. Resource law: token cost × projected free attempts must fit the budget before the pilot, not after. Weapon: experience + proprietary data, not price.
