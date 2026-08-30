---
name: independent-review
description: "Review report with strengths, issues, risks, verdict"
version: 1.0.0
author: Sage
metadata:
  hermes:
    tags: [Sage, Workflow, review]
---

## When to Use
Load this skill when the user asks for an independent review of an artifact (spec, plan, design, code, document).

## Arguments
Hermes does NOT interpolate an in-body argument token. The user's arguments/flags arrive as a SEPARATE instruction line appended to this skill invocation. Wherever the steps below refer to "the user's arguments", use the text of that appended instruction line.

## Independent review (delegate_task)
When a step calls for an independent review, invoke `delegate_task` against the `sage-reviewer` skill. Hermes delegate_task has NO toolset-restriction parameter — read-only is prompt-enforced, and you MUST verify afterward that the reviewer made no edits (e.g. `git status` unchanged) before accepting its verdict.


# Review Workflow

> 📁 **Source convention:** `[sage]` = upstream Sage repo (github.com/xoai/sage); `[docs]` = your internal docs repo (optional deep-dives — adjust paths to your setup). Sources are for deeper reading: if a file is missing, the skill still runs on the rules inlined here. The ONLY exception: a step marked **MUST READ** — if that file is missing, STOP and ask the user instead of improvising.

Independent evaluation. Designed to work in a fresh session for maximum
objectivity, but also works within an existing session.

## Step 0: Mode Dispatch

`/review` has four modes. Parse `the arguments the user provided alongside this skill invocation (delivered as a separate instruction line, NOT a literal token)` for a mode flag; default is code /
artifact review.

| Invocation | Mode | Read the mode reference |
|---|---|---|
| `/review` (default) | Code / artifact quality | (this file, Steps 1–5) |
| `/review --ux` | UX assessment (audit → evaluate → heuristics) | `core/workflows/review-modes/ux.md` |
| `/review --design` | Design-system compliance + visual quality | `core/workflows/review-modes/design.md` |
| `/review --browser` | Functional / browser QA (optional Lightpanda) | `core/workflows/review-modes/browser.md` |

These modes fold in the former `/analyze`, `/design-review`, and `/qa`
workflows. On a mode flag, read the matching reference and follow it; the Rules
below still apply. `--ux` uses the `ux-review` skill, which is bundled in this kit
(`skills/ux/ux-review`) — if it is not installed, say so.

## Step 1: Identify What to Review

If not specified, scan `docs/work/` and `docs/` for recent
artifacts. Present them:

Sage: Available for review:

[1] docs/work/20260316-checkout/brief.md (updated today)
[2] docs/work/20260316-checkout/spec.md (updated today)
[3] docs/ux-audit-homepage.md (updated yesterday)

Which artifact should I review? Or describe what you'd like evaluated.

If the user specifies an artifact, proceed directly.

## Step 2: Gather Context

Search for prior knowledge using sage_memory_search — pass the
artifact topic and domain as query (string), limit as 5 (integer).
If the tool is not available, proceed without memory context.

Read the artifact fully.

Identify which skill or workflow produced this artifact — check for
skill prefixes in the filename, references in the content, or metadata.
Load the producing skill's quality criteria — these become the primary
evaluation framework. If the producing skill cannot be identified,
use the three general lenses in Step 3.

If this is a fresh session, note: "Sage: Reviewing with fresh eyes —
I wasn't involved in producing this work."

If this is the same session, note: "Sage: I produced this work, so my
review may have blind spots. For a more independent evaluation,
consider a fresh session or the /review command."

## Step 3: Evaluate

Review the artifact against three lenses:

For detailed code quality review, use the project's own review checklist if one
exists (`[sage]` quality-review capability upstream, optional); otherwise apply the
three lenses below to the code.

**Completeness** — Does it cover what it should? Are there missing
sections, unaddressed scenarios, or gaps in reasoning? Check against
the producing skill's quality criteria if available.

**Consistency** — Does it align with other project artifacts? Does
the spec match the brief? Does the plan match the spec? Are there
contradictions within the document itself?

**Quality** — Is the thinking sound? Are claims supported by evidence?
Are trade-offs named explicitly? Would a domain expert find this
credible? Is anything vague where it should be specific?

For each finding, note:
- What you observed (specific, with quotes or references)
- Why it matters (impact on downstream work)
- Suggested action (fix, clarify, investigate, or accept as-is)

## Step 4: Present Findings

Structure the review clearly:

```
## Review: [artifact name]

### Strengths
[What's well-done — be specific, not generic praise]

### Issues Found
[Each issue: observation → impact → suggestion]

### Risks
[Things that aren't wrong but could cause problems downstream]

### Verdict

[One of:]
  ✓ Ready to proceed — [minor notes if any]
  ⚠ Needs revision — [specific items to address]
  ✗ Significant gaps — [recommend rework before proceeding]
```

## Step 5: Next Steps

Based on the verdict:

- **Ready:** Recommend the natural next step in the workflow
- **Needs revision:** List specific items to address, offer to help
- **Significant gaps:** Recommend which step to return to and why

[A] Accept findings — proceed with suggested next step
[R] Revise — I'll address the issues found
[D] Discuss — let's talk about specific findings

Prepend review findings to `docs/DECISIONS.md`.

## Rules

- Be specific. "The spec is good" is not a review. "The spec covers
  the happy path thoroughly but doesn't address what happens when the
  payment gateway times out" is a review.
- Be honest. The purpose of review is to catch problems before they
  become expensive. Diplomatic honesty serves the user better than
  comfortable vagueness.
- Evaluate against criteria, not preferences. Use the producing skill's
  quality criteria when available. When not, use the three lenses above.
- Fresh session review is always recommended for high-stakes artifacts
  (briefs, specs, architecture decisions).


---

## Applied context (edtech)
> Real case: review caught dead cross-references between two documents rewritten an hour apart → new rule: "cite with a snapshot date." 
