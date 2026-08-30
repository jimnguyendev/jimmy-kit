# Growth Analysis & 7-State Markov Model Report

> **Product:** [name / e.g. an AI practice-test product]
> **Review window:** [DD/MM/YYYY → DD/MM/YYYY] · **Author:** [analyst / PM]

## 1. LIFECYCLE SNAPSHOT

| User state | Symbol | Users | % of database | Assessment |
| :-- | :-: | :-: | :-: | :-- |
| New (today) | N | [1,200] | [2.0%] | [stable / rising / falling] |
| Current (core) | C | [15,400] | [25.6%] | [healthy: >60% of DAU] |
| Reactivated (this week) | R | [1,100] | [1.8%] | [notification effect] |
| Resurrected (>30d) | Res | [450] | [0.7%] | [win-back campaign] |
| At-risk weekly | sWAU | [5,800] | [9.6%] | ⚠️ [streak-intervention zone] |
| At-risk monthly | sMAU | [11,200] | [18.6%] | 🔴 [sliding toward Dead] |
| Dead / dormant | Dead | [25,000] | [41.6%] | [churned] |
| **TODAY'S DAU** | **N+C+R+Res** | **[18,150]** | **100% DAU** | **Target: [20,000]** |

## 2. TRANSITION PROBABILITY MATRIX (P)
Fill the 7×7 matrix from event data; bold the two health-critical cells (C→C and sWAU→C).

### The 3 survival metrics
1. **P(C→C) = [82%]** — core retention. Target > 80%; this carries the whole model.
2. **P(C→sWAU) = [18%]** — missed-day rate. Keep < 20%; above 25%, inspect lesson difficulty or system errors.
3. **P(sWAU→C) = [45%]** — streak-rescue rate. Share of one-day-off users pulled back next day (push + streak freeze).

## 3. 30-DAY DAU FORECAST
Today [18,150] → D14 [20,400] → D30 [22,800].
- **Input assumption:** average new users N = [1,200 ± 100]/day — label [ASSUMPTION].
- **Upside scenario:** raising P(C→C) from 82% → 84% yields **[24,500] (+7.4%)** DAU at D30 with zero extra ad spend.

## 4. INTERVENTION ACTION PLAN

| Leak | Priority | Concrete product fix | Owner | Deadline |
| :-- | :-: | :-- | :-- | :-: |
| C → sWAU | P0 | Personalize smart-push send time (evening peak) | Growth lead | DD/MM |
| sWAU → C | P0 | Grant one streak-freeze token for sudden busy days | Product lead | DD/MM |
| sMAU → Dead | P1 | Diagnostic win-back email: "3 unfixed errors are waiting" | CRM | DD/MM |
