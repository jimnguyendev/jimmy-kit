---
name: retrospective
description: "Use when an A/B test just ended (win or lose — run it either way), when an incident was just resolved and nobody has extracted the lesson, when the same mistake appears a second time (a sign the old rule had no mechanism), or at sprint/milestone end to mint new rules in WHEN/CHECK/BECAUSE form."
---

# Retrospective & Continuous Learning

> **This skill exists to stop:** incidents passing without producing a rule — or lessons written as "be more careful," which nobody can reuse.

> 📁 **Source note:** `[sage]` = upstream Sage repo (github.com/xoai/sage, public) — optional deeper reading; this skill runs fully on the rules inlined here. A step marked **MUST READ** points at a file in *your own* project (e.g. an event registry) — if it is missing, stop and ask instead of improvising.

## 🤖 0. HOW TO USE (agent workflow)
**A. A/B test retro:** compare the original bet ("we believed X would move KR Y by Z because…") with actuals; if multiple variables were mixed, report "result unreadable" instead of inventing a conclusion.
**B. Incident post-mortem:** 5-whys to the root; lesson in strict WHEN/CHECK/BECAUSE form; log it in the team lesson book.
**C. Mint new rules:** every rule must trace to a real failure (date/ticket/witness — kaizen) AND answer "what mechanism keeps it" — a rule that's only a reminder gets demoted to SHOULD.
📄 Full original (203 lines): [sage] skills/sage-reflect/SKILL.md.

> Core stance: *"Sprint fast, A/B relentlessly, fix what breaks. No solution is perfect on paper — but never step in the same pothole twice."*

## 🏛️ 1. THE LESSON FORMULA: WHEN / CHECK / BECAUSE
Every win or failure becomes a system rule with three clauses:
```
WHEN   (what context occurs)     e.g. "When a guest finishes a trial test without leaving contact info…"
CHECK  (what to verify or do)    e.g. "…auto-save locally and show ONE gentle save-your-progress prompt…"
BECAUSE(why)                     e.g. "…because forcing sign-up at that moment dropped continuation by double digits."
```

## 🔍 2. ROOT-CAUSE HUNTING (5-WHYS)
When a metric drops or a feature flops, don't blame people — dig five layers. Example chain: retention low → users don't return after day one → no reminder reaches them → no contact channel captured → **root cause: the trial flow never designed a post-result claim step.** Fix the missing step, not the symptom.

## 📝 3. RETROSPECTIVE REPORT TEMPLATE
```markdown
# Retrospective: [project / A/B test]
## 1. The Bet — we believed [initiative] would move [metric] from [A] to [B] because [reason].
## 2. Actuals — window, sample size, result (hit / missed, actual number).
## 3. Root-cause analysis — what worked (1–2), what failed (where users hit friction).
## 4. Lessons — Rule 1: WHEN … CHECK … BECAUSE …  (repeat)
## 5. Next action — [ ] Roll out 100%  [ ] Pivot (replace the initiative, never lower the KR)  [ ] Kill & clean up
```
