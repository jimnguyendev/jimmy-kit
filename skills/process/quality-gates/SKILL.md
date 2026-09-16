---
name: quality-gates
description: Check completion evidence. Use when a required check fails, a project hook blocks work, or a change needs a pass/fail/unverifiable assessment.
version: "1.0.0"
type: system
---

# Gates

> 📁 **Source note:** `[sage]` = upstream Sage repo (github.com/xoai/sage, public) — optional deeper reading; this skill runs fully on the rules inlined here. A step marked **MUST READ** points at a file in *your own* project (e.g. an event registry) — if it is missing, stop and ask instead of improvising.

## Dosage and authorization

Follow `change-tiers`: Tier 1 uses a relevant check; Tier 2 announces and proceeds;
Tier 3 resolves consequential choices before the affected action. Accepted scope,
acceptance criteria, and authorization survive handoffs. Do not ask for separate
spec or plan approval when the user's request already authorizes that work.
Continue authorized implementation, verification, and fixes until acceptance
criteria are met. Ask only for a material missing decision, expanded scope, or
an external action not covered by the user's authorization.

## Hooks versus gates

| | Hooks | Gates |
|---|---|---|
| When | Before a tool call or edit | After work, on demand or in CI |
| Purpose | Enforce a configured precondition | Evaluate actual evidence |
| Availability | Only if the target project installs them | Run the target's applicable checks |
| Missing mechanism | Report that enforcement is absent | Report unverifiable, never pass |

This kit does not install pre-edit hooks, a manifest state machine, or numbered
runtime gates. A project may implement those mechanisms. If an edit is blocked,
read its actual hook output and configuration; do not infer a manifest or claim
that a Markdown instruction mechanically blocks edits. Never bypass a configured
project control merely because the kit uses lighter defaults.

## Workflow checks

**Build:**

1. Identify accepted behavior, scope, and evidence for completion. Reuse the user's
   request or existing brief/spec instead of requiring duplicate files.
2. For work with unresolved design choices, record a focused spec and plan under
   `.jimmy/work/<initiative>/`. Resolve only those choices before implementation.
3. Implement using the target project's testing conventions. For a bug or new
   behavior, prefer a failing example through the real affected interface.
4. Run the relevant checks, fix regressions caused by the change, and report the
   commands, results, and material verification gaps.

**Fix:** investigate with evidence, then choose scope by behavior, blast radius,
compatibility, and reversibility. An accepted surgical fix can proceed directly.
A change to a public contract or architecture needs that decision resolved first;
file count alone is not a reason to stop or restart discovery.

**Architect:** reuse known vision and constraints; investigate only missing or
contradictory information. Record consequential alternatives and their losing
reasons in `.jimmy/adr/`, and implementation scope in `.jimmy/work/`. Milestones
carry their own acceptance evidence without repeating already settled approvals.

**Delivery:** keep changes reversible at the affected boundary. Follow the target's
branch policy. Merging, publishing, or other external actions require user
authorization for that action; existing explicit authorization remains valid.

## Verify before claiming done

- The requested behavior or artifact matches the accepted scope.
- Applicable checks actually ran and passed. Preserve the command and meaningful
  output; summarize routine runs and include decisive evidence for disputed gates.
- Behavior changes have checks through the relevant interface. Editorial changes
  use suitable inspection/lint rather than invented behavioral tests.
- For persistence, config, or client-contract seams, use `reality-gate` when
  available: evidence must come from a real schema/runtime/request or contract
  comparison. Exit 0 without executed checks is insufficient.
- Independent review is appropriate for consequential or hard-to-verify work.
  Distinguish an independent review from the author's own self-check.

A failing or unrun required check prevents a claim of verified completion. Fix
verification setup within existing authorization when feasible; otherwise state
what is blocked and what evidence is still needed.

## The three-state exit contract

Gate scripts exit `0` pass, `1` fail, `2` **unverifiable**.

Exit 2 is the one that matters. It exists because "the suite is green" and
"there is no suite" are different claims that used to share exit 0 — which is
precisely how a gate reports success on code it never looked at.

**Exit 2 is never a pass.** It is also not a failure: it has produced no
evidence either way. On exit 2, continue safe evidence gathering within scope. If completion requires a waiver or additional authority, present the choice and record it:

```
[P] Proceed unverified — logged as a waiver in .jimmy/decisions.md
[F] Fix verification setup — install the runner, then re-run
```


---

## Applied context (edtech)
> Apply the exit 0/1/2 contract to: runtime verification gates of a tracking contract ("spec complete" with 0/6 gates run = exit 2) and evidence-attached QA acceptance checklists.
