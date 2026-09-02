---
name: growth-loops
description: "Design and diagnose growth loops and habit hooks instead of one-off campaigns. Use when someone asks 'how do we grow this', when acquisition depends on ad budget with nothing compounding, when defining an Active User for the first time, when retention curves need reading (smile curve = PMF signal), or when a B2B/B2C product needs a referral or content loop."
---

# Growth Loops & Habit Hooks

> **This skill exists to stop:** growing by campaigns (spend → spike → decay) instead of by loops (output of one cycle feeds the next), and debating "retention" without a written Active-User definition.


## 🤖 0. HOW TO USE (agent workflow)
**A. Map the existing loop:** Trigger → Action → Value/Reward → Investment/Output → (feeds the next Trigger). Name each node concretely; if the loop doesn't close, say so — you have a funnel, not a loop.
**B. Measure the loop:** the three control metrics — **Trigger reach**, **Frequency** (daily/weekly cadence of the core action), **Response rate** (share of triggered users who do the core action). Report all three with window + source.
**C. Pick a lever (one at a time):** optimize the existing loop (shorten Trigger→Action) · add a new loop (referral, content) · expand channels (embed where users already live). Every lever ships with the metric it should move.
**D. Read retention honestly:** cohort curve first; a curve that flattens then bends up (smile) is the PMF signal — a curve sliding to zero means fix the product before scaling anything.
**Standard output:** loop diagram + 3 metrics table + one lever + the cohort curve verdict. Never propose "run more ads" as a growth plan.

## 1. Anatomy of a loop
```
TRIGGER (why they open it today)  →  ACTION (the core behavior)
        ↑                                      ↓
INVESTMENT / OUTPUT (what they leave behind  ←  VALUE / REWARD (what they got)
   that creates the next trigger — for them or for someone else)
```
A B2B invoicing product: new invoice arrives (trigger) → open and reconcile (action) → 80% less data entry (value) → send a reconciliation link to the counterparty (investment) → that counterparty gets a trigger. A learning product: results shared or a streak reminder is the investment that re-triggers.

## 2. The three control metrics
| Metric | Question | Typical failure |
|---|---|---|
| Trigger | What real event makes them open it? | "Notifications" with no event behind them |
| Frequency | Daily, weekly, monthly? | A monthly use case (A30) can't sustain a habit — see subscription-paywall |
| Response rate | Of those triggered, how many act? | High reach, low response = wrong trigger or too much friction |

## 3. Three scaling levers (in order of cost)
1. **Optimize the existing loop** — cut steps between trigger and action; this is where most of the lift usually is.
2. **Add a loop** — referral (output goes to another person), content (output becomes searchable), collaboration (output invites a teammate).
3. **Expand channels** — embed inside ecosystems users already live in (chat platforms, workspace tools, LMS).

## 4. Hook model (habit layer)
Trigger (external → internal) → Action (simplest behavior in anticipation of reward) → **Variable** reward → Investment (data, effort, reputation that loads the next trigger). Variable reward is what makes the second visit likely; a fixed reward habituates.

## 5. Active-user discipline & cohort reading
Write the Active-User definition before any metric ("a business is active if it processes ≥1 invoice in the month"; "a learner is active if they complete ≥1 graded attempt in the week"). Then read cohorts: declining-to-zero = leaky bucket; flattening = retained core; **flattening then rising (smile curve)** = returning after a pause — product-market fit signal. Three insight patterns worth hunting in event data: period-end bottlenecks, repeat-buyer stability, seasonality.

## Applied context (edtech)
Loop: exam date approaching (trigger) → take a graded attempt (action) → see percentile + the one blocking error (value) → the error is remembered and surfaces as next week's target (investment → next trigger). Metrics: trigger reach = learners with an exam date on file; frequency = attempts/week; response = attempts per reminder. Smile curve appears when learners return 2 weeks before the exam — design a "remaining errors" cycle for it.
