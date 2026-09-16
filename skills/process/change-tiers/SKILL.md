---
name: change-tiers
description: Size workflow effort. Use when deciding how much discovery, planning, review, or verification a change warrants.
version: "1.0.0"
type: system
---

# Tiers

> 📁 **Source note:** `[sage]` = upstream Sage repo (github.com/xoai/sage, public) — optional deeper reading; this skill runs fully on the rules inlined here. A step marked **MUST READ** points at a file in *your own* project (e.g. an event registry) — if it is missing, stop and ask instead of improvising.

Tier is the answer to one question: **how much process does this deserve?**

Too much process on a trivial change is bureaucracy, and users learn to route
around it. Too little on a consequential one is how a "quick fix" becomes an
outage. Tier is where that judgment is made explicit instead of being made
silently, differently, every time.

## The three tiers

| Tier | Response | What it looks like |
|---|---|---|
| **Tier 1** | Just do it. | Small, reversible, no material design decision. No manifest, no spec, no confirmation. |
| **Tier 2** | Announce and proceed. | Multiple steps, creates artifacts. Say what you are doing, then do it. |
| **Tier 3** | Card and choose. | Consequential unresolved choices. Present trade-offs and resolve those choices; reuse existing approval. |

## The bias

Assess risk, uncertainty, reversibility, and acceptance evidence. Raise the tier
when a concrete unresolved risk warrants it, not merely because several files change.

Any of these puts a task at **Tier 2 minimum**, regardless of how small the
diff looks:

- a behavior change
- an API change
- a decision the team would want to see

Tier 2 means announce and proceed, not mandatory spec/plan approval. Reuse
accepted behavior and existing authorization. For Tier 3, ask about the consequential
choice that remains open; do not reopen decisions already accepted by the user.

## Tier 1 is a real escape hatch, not a trap

Tier 1 needs no kit manifest, spec, or routing menu. Apply the target project's
actual controls and a relevant check. This kit does not install hooks or a manifest
state machine. A tiny behavior change can still have a large blast radius, so
inspect that risk instead of using line count as the shortcut.

## Rationalizations that do not survive contact

| The thought | Why it is wrong |
|---|---|
| "It is literally one line" | One line that changes behavior is a behavior change. The diff size is not the blast radius. |
| "The design is obvious" | Obvious to you, now, with your context. Write it down and find out. |
| "I will note it in the commit message" | A commit message is not a decision record and nobody reads it before the fact. |
| "The user just wants it done" | The user wants it *right*. They will not thank you for speed on the change that broke checkout. |


---

## Applied context (edtech)
> Real tiering: landing copy fix = Tier 1 · new tracking event = Tier 2 · AI-failure UX + percentile method = Tier 3 · a 2-day cost-measurement spike = Tier 1 effort that blocks everything (priority ≠ ceremony).
