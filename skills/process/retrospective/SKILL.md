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

## 🔩 4. PICK THE MECHANISM (strongest that fits the accepted scope)
A rule minted in step C is only as strong as what enforces it. Try, in order, and stop at the first that works:
1. **Structure** — one owner per piece of state, one supported way per task, internals the wrong caller cannot import.
2. **Types** — the bad state cannot be written; if it still compiles, a **lint or CI check whose message names the right function or file**.
3. **Behavior test** — through the public interface; a test that would still pass if every call returned nothing does not count.
4. **Docs or agent rules** — last, and only for judgment calls nothing can check.

Prove each new check against the real past mistake: it must fail on that change and pass on the fix. Keep one table (in the target repo's agent instructions) pairing each rule with what enforces it; a rule that recurs while listed as enforced means the mechanism failed, so move it up the list. Exceptions sit on the offending line with a reason, an expiry date and an approver.

Implement the mechanism only inside the work the user already accepted. When the strongest fit is outside it (a new CI job, a cross-team lint), write it as a proposal in the report's Next action. Product and A/B lessons usually stay at level 4: they need judgment, not a lint.

