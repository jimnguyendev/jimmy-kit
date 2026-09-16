# Growth Analysis & 7-State Markov Model Report

> **Worked example only:** All counts, rates, thresholds, and actions below are illustrative assumptions. Replace with sourced measurements and locally justified decisions. Leave unavailable values explicitly unknown; do not report these examples as observed results.


> **Product:** [name / e.g. an AI practice-test product]
> **Review window:** [DD/MM/YYYY → DD/MM/YYYY] · **Author:** [analyst / PM]

## 1. LIFECYCLE SNAPSHOT

| User state | Symbol | Users | % of database | Assessment |
| :-- | :-: | :-: | :-: | :-- |
| New (today) | N | [1,200] | [2.0%] | [stable / rising / falling] |
| Current (core) | C | [15,400] | [25.6%] | [compare with measured baseline] |
| Reactivated (this week) | R | [1,100] | [1.8%] | [investigate return reasons] |
| Resurrected (>30d) | Res | [450] | [0.7%] | [win-back campaign] |
| At-risk weekly | sWAU | [5,800] | [9.6%] | ⚠️ [streak-intervention zone] |
| At-risk monthly | sMAU | [11,200] | [18.6%] | 🔴 [sliding toward Dead] |
| Dead / dormant | Dead | [25,000] | [41.6%] | [churned] |
| **TODAY'S DAU** | **N+C+R+Res** | **[18,150]** | **100% DAU** | **Target: [20,000]** |

## 2. TRANSITION PROBABILITY MATRIX (P)
Fill the 7×7 matrix from event data; bold the two health-critical cells (C→C and sWAU→C).

### The 3 survival metrics
1. **P(C→C) = [82%]** — core retention. Compare with a product-specific baseline and target.
2. **P(C→sWAU) = [18%]** — missed-day rate. Investigate changes against comparable cohorts; do not infer a cause from a rate alone.
3. **P(sWAU→C) = [45%]** — return rate. Share of at-risk weekly users active the next day; trigger attribution needs separate evidence.

## 3. 30-DAY DAU FORECAST
Today [18,150] → D14 [20,400] → D30 [22,800].
- **Input assumption:** average new users N = [1,200 ± 100]/day — label [ASSUMPTION].
- **Upside scenario:** raising P(C→C) from 82% → 84% yields **[24,500] (+7.4%)** DAU at D30 with zero extra ad spend.

## 4. INTERVENTION ACTION PLAN

| Leak | Priority | Candidate intervention to test | Owner | Deadline |
| :-- | :-: | :-- | :-- | :-: |
| C → sWAU | P0 | Personalize smart-push send time (evening peak) | Growth lead | DD/MM |
| sWAU → C | P0 | Grant one streak-freeze token for sudden busy days | Product lead | DD/MM |
| sMAU → Dead | P1 | Diagnostic win-back email: "3 unfixed errors are waiting" | CRM | DD/MM |
