---
name: subscription-paywall
description: "Design paywalls, trials, and pricing pages for subscription products using behavioral psychology and a revenue tree. Use when deciding freemium vs trial vs reverse trial, when a pricing table under-converts, when churn is high after month one, when a use case only happens monthly, or when someone proposes locking a feature behind the paywall."
---

# Subscription Strategy & Paywall Design

> **This skill exists to stop:** locking the one feature that solves the user's pain behind the paywall (so free users never see value), and selling a once-a-month use case as a monthly subscription.


## 🤖 0. HOW TO USE (agent workflow)
**A. Choose the model:** freemium / free trial / **reverse trial**. Default recommendation for products whose value needs to be *felt* before it is understood: reverse trial (full access, then step down).
**B. Audit a pricing page:** rule of three, center-stage target tier, anchor tier, one highlighted "recommended" — then check honesty (no fake urgency, 1-click cancel).
**C. Locate the lever on the revenue tree** (§3) before touching anything: which branch does this change move, by how much, measured by which event?
**D. Frequency check:** if the core use case is A30 (monthly), add A1/A7 companions before scaling paid acquisition.
**Standard output:** model choice + why · pricing table mock · revenue-tree node targeted · one A/B with a single variable · churn hypothesis.

## 1. Reverse trial vs freemium
Freemium's two blind spots: (1) **locking the hero feature** — the team guesses which features are "advanced" and locks the one that actually kills the pain, so free users conclude the product is useless; (2) **free forever** — free is so generous nobody upgrades. Reverse trial: sign up with email only → 100% access for N days → user invests time and data, reaches the aha moment → auto-downgrade → loss aversion does the selling. The user stays in the ecosystem either way.

## 2. Pricing-table psychology
- **Center-stage effect:** the middle option reads as "balanced and safe"; with a highlight border and a "Most popular" label, mid-tier selection can roughly double.
- **Decoy / anchor:** the expensive top tier exists to make the middle one feel like a deal.
- **Rule of three:** Basic – Pro (target) – Enterprise. More than three = decision paralysis.
- **Honesty line:** anchors are fine; fake countdowns, hidden renewals, buried cancel links are not.

## 3. Revenue tree (find the lever before acting)
```
PROFIT = REVENUE − COST(servers, CAC, ops)
REVENUE = Paying users × ARPU
Paying users = New paying (traffic × conversion) + Retained paying (renewals) − Churned (cancel rate)
ARPU = tier pricing + add-ons / cross-sell
```
Every paywall or feature change must name the branch it moves. "Improve the pricing page" is not a plan; "raise New paying via conversion, measured by checkout_completed / pricing_viewed" is.

## 4. Retention mechanics
- **A30 → A1/A7:** a monthly-only use case makes users feel they pay for 29 idle days. Add daily/weekly companions (instant balance alerts, daily prompts, morning suggestions) around the monthly core.
- **First-use onboarding vs the cold screen:** an empty screen after sign-up is a churn event. Interactive walkthrough, sample data, or ready templates so the aha moment lands inside the first 60 seconds.
- **State model:** Trial → {Free, Pro, Lost} with measured transition probabilities — hand the matrix to `growth-markov-duolingo`.

## Applied context (edtech)
Reverse trial: 7 days of full graded practice, then step down to one diagnostic test per week; the paywall message names what they lose ("your error memory and percentile history pause"). Pricing table: Basic (self-study) – Pro (unlimited AI grading, recommended) – Intensive (with mentor review) as anchor. Frequency: the monthly mock test is A30 — daily 15-second speaking prompts are the A1 companion.
