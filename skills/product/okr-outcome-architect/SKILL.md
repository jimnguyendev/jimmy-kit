---
name: okr-outcome-architect
description: "OKR & Outcome Architecture — adapted from an internal OKR handbook shared by product leadership. Use when writing, auditing, scoring, weighting, or aligning company/team OKRs, mapping roadmap initiatives to KRs, separating outcomes from outputs, or diagnosing broken metric systems. Triggers: write OKRs, review my OKRs, are these KRs good, quarterly goals, map roadmap to OKRs, OKR weighting."
---

# OKR & Outcome Architecture

> **This skill exists to stop:** projects and initiatives disguised as Key Results — teams celebrating shipped work that moved no business outcome (the #1 mistake in the handbook).

## 🤖 0. HOW TO USE (agent workflow)

**A. AUDIT an existing OKR set** ("review these OKRs"):
1. Run the 2 sanity tests (§1) on every O–KR pair.
2. Grade each Objective against the 4 rules (§2), each KR against the 4 parts + 2 diagnostic tests (§3), scan the 4 metric traps.
3. Check priorities: volume limits, Committed/Stretch labels, ranking, owners (§4).
4. Output: a `❌ current | ⚠️ why it fails | ✅ proposed fix` table per issue + the 60-second checklist result (§7). No generic praise — every remark points at a specific line.

**B. WRITE a new OKR set** ("help me set this quarter's OKRs"):
1. Ask before writing: what's the strategy / why-now? Which business outcome? Which metrics HAVE baselines? (No baseline → the KR can't be written yet — go measure first.)
2. Draft per §2–§3; every Objective gets ≥1 lagging + 1–2 leading metrics.
3. Self-run the 60-second checklist before presenting.

**C. MAP roadmap ↔ OKRs** ("which KR does this work serve?"): build the OKR–Initiative matrix (§5), answer its three questions, label non-OKR work explicitly.

⚠️ All modes: if the user supplies Objectives/KRs missing baselines or a business outcome — stop and ask. Never invent numbers.

## 🧠 1. THE CORE IDEA

```
Objective   = WHERE do you want to go?        (qualitative, inspiring, one sentence)
Key Result  = HOW DO YOU KNOW you arrived?    (quantitative, measurable)
Initiative  = HOW will you attempt it?        (a bet / hypothesis)
```

Two sanity tests that catch most broken OKRs:
1. **Hit 100% of KRs but missed the Objective** → your KRs are WRONG.
2. **Achieved the Objective but missed every KR** → your KRs measured the WRONG THING.

## 🎯 2. OBJECTIVES TIED TO BUSINESS OUTCOMES

Rules: **outcome, not activity** (a meaningful change of state, not work you'll do) · **inspiring and memorable** (the team can recite it) · **time-bound** (usually a quarter) · **one sentence** (a paragraph = two objectives).

Template: `"[Verb] [the meaningful change] so that [the business impact]"` — then finish the sentence *"…so that WHAT business outcome?"* If you can't, it isn't tied to the business yet.

| ❌ Bad | ⚠️ Why it fails | ✅ Better |
| :--- | :--- | :--- |
| "Launch the new onboarding flow" | A project, not an outcome | "Make new users feel confident in their first session" |
| "Be the best CRM in the market" | Unmeasurable, no timeframe, no focus | "Become the preferred CRM for mid-market SaaS sales teams" |
| "Improve customer satisfaction" | Vague, no business stake | "Turn support from a cost center into a retention driver" |
| "Increase revenue 20%" | That's a KR, not an Objective | "Establish enterprise as our primary growth engine" |

## 📊 3. KEY RESULTS THAT PROVE THE OBJECTIVE

Rules: **2–5 per Objective** (more = unfocused) · **outcome metrics, not output** · **each KR independently meaningful** (drop one and still believe the Objective? then drop it) · format: `"Move [metric] from [baseline] to [target] by [date]"`.

Two diagnostic tests — **Sufficiency:** "If we hit 100% of these KRs, do I genuinely believe the Objective is achieved?" No → a KR is missing. **Necessity:** "If we removed this KR, would the rest still prove it?" Yes → it's decorative; drop or replace.

Every KR needs 4 parts: **metric · baseline · target · date.** Any missing → not measurable yet.

| ❌ Bad KR | ⚠️ Why | ✅ Better |
| :--- | :--- | :--- |
| "Launch loyalty program" | A project | "Repeat purchase rate 18% → 28%" |
| "Run 4 marketing campaigns" | Output | "12,000 qualified leads at CAC ≤ $35" |
| "Hire 5 engineers" | Input | "Deploy frequency weekly → daily" |
| "Improve user satisfaction" | No baseline/target | "NPS 32 → 45" |

**Leading vs lagging:** lagging (revenue, retention, NPS) proves impact but moves slowly; leading (activation, WAU, time-to-value) signals fast but must genuinely link to the outcome. Pair **≥1 lagging** (anchor) with **1–2 leading** (steering wheel).

**Four metric traps:** vanity (easy to grow, no business effect) · activity (counting work done) · unmeasurable ("improve quality" → define a proxy or drop) · out-of-control (share price → find a closer proxy you can move).

## ⚖️ 4. PRIORITIZATION, WEIGHTS & CHECK-INS

**Volume limits (the rule most teams break):** company 3–5 Objectives · team 2–4 · 2–5 KRs each. If everything is a priority, nothing is.

**Two tiers — label every OKR:** **Committed** (must hit, 100%, missing = real problem) vs **Stretch** (~70% is success). Never mix silently — teams treat stretch as committed and burn out, or the reverse and miss.

**Rank, don't average:** list Objectives in priority order; when the mid-quarter tradeoff hits (it will), the rank says what to drop.

**Weights — two ways:** **A. Ranked order** (simpler; recommended for new teams). **B. Explicit % weights** (when you must roll up scores): sum to 100% at each level · reflect **importance, never effort** · round to 5/10% (37%/23% is false precision) · within ~5% → make equal · mid-quarter re-weighting rare and explicit.

Scoring (if weighted): `Objective score = Σ(KR% × KR weight)`; `Overall = Σ(Objective score × weight)`. Skip weights when: ≤2 Objectives · team new to OKRs · nobody uses the rolled-up score.

> 💡 **The honest truth:** arguing whether a KR is 25% or 30% almost never produces better outcomes. The discipline of CHOOSING beats the precision of the number.

**Confidence check-ins:** every 1–2 weeks score each KR 0.1/0.3/0.5/0.7/0.9. A drop 0.7 → 0.3 is the act-now alarm — don't wait for quarter-end.

## 🗺️ 5. MAPPING ROADMAP (INITIATIVES) TO OKRs

The most common execution failure isn't bad OKRs — it's the gap between OKRs and daily work.

Every initiative must be expressible as: `"We believe [initiative] will move [KR] by [amount] because [reasoning]."` Can't fill the blanks → you're not betting, just working.

**OKR–Initiative matrix** (map every initiative to KRs, High/Med/Low) exposes three questions: **1.** Any KR with no initiative? A wish, not a plan. **2.** Any unmapped initiative? Maybe still right (debt, infra) — but say so explicitly. **3.** Over-betting on one KR? Five initiatives on KR1.2 and zero on KR1.1 = unbalanced.

**Healthy unmapped work:** keep-the-lights-on, incidents, compliance, enabling tech debt. Rule of thumb: **60–70% of capacity on OKR-mapped work.** 100% mapped → over-planning or hidden work; <40% → your OKRs aren't where the team lives.

> 🚨 **Mid-quarter: replace the INITIATIVE, never lower the KR.** The KR is the destination; the initiative was one route. The temptation runs the other way — and it's almost always wrong.

## 🚫 6. EIGHT TRAPS TEAMS DON'T SEE COMING

1. **Cascade by copy-paste** — lower OKRs must contribute at their own altitude, not reword the parent's.
2. **OKRs tied to compensation** → sandbagging. Keep them separate.
3. **Set & forget** — no weekly/biweekly check-ins = wall decoration.
4. **Health metrics confused with OKRs** — uptime/security are guardrails you protect, tracked separately.
5. **100% hit rate every quarter** — targets too soft; stretch should land ~70%.
6. **Mid-quarter sunk cost** — a KR clearly unreachable by week 6: say so openly; don't grind a meaningless number.
7. **No owner per KR** — one accountable name, never "the team."
8. **Strategy confusion** — OKRs are the RESULT of strategy, not a substitute. Can't explain why this OKR matters NOW → you skipped the strategy step.

## ✅ 7. THE 60-SECOND SELF-CHECK

**Objectives:** outcome not project · passes "so that…" · one memorable sentence · time-bound.
**KRs:** metric+baseline+target+date · passes sufficiency & necessity · ≥1 lagging · no disguised projects.
**Priority & weights:** 2–4 O/team · 2–5 KR/O · ranked or weighted to 100% · Committed/Stretch labeled · one owner per KR.
**Roadmap:** every KR has ≥1 initiative · every initiative names its KR bet · non-OKR work labeled · ~60–70% capacity on OKR work.

## 🏆 8. WORKED EXAMPLE

**Objective:** *Make new users successful enough in week one that they keep coming back.* (Outcome; ties to retention.)
**KRs:** 1. Day-7 retention **22% → 35%** *(lagging — the proof)* · 2. New users completing the aha-moment action **41% → 65%** *(leading — the driver)* · 3. Time-to-first-value **8.5 → 4 min** *(leading — the friction)*.
**Why it works:** the Objective is a state, not a project; hitting all three genuinely proves it; one lagging + two leading; every KR has all four parts.
**Why the popular alternative fails:** ❌ *"Launch new onboarding, ship interactive tutorial, run research with 20 users"* — all projects; you could finish all three with zero impact on whether users return.
