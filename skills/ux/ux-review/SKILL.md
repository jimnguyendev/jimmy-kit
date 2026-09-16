---
name: ux-review
description: >-
  Use when reviewing an existing UI for design consistency, category gaps, or usability failures, or when a redesign needs a baseline. For conversion and stakeholder negotiation, use ux-cro-audit.
version: "1.0.0"
type: process
tags: [ux, review, audit, evaluate, heuristics, assessment]
---

# UX Review

> **This skill exists to stop:** unsupported UI judgments, lost usability failures, and repeated research caused by treating artifact filenames as evidence.

## 🤖 0. HOW TO USE

Choose by the decision requested and read only the corresponding local reference. A full redesign may combine modes, but a focused review does not require the full chain.

| Mode | Trigger / required evidence | Load | Output |
|---|---|---|---|
| Audit | Extract visual patterns from supplied or captured screenshots | [Audit](references/audit.md) | Current design system; inconsistencies and observed coverage |
| Evaluate | Compare current-state evidence with dated category observations | [Evaluate](references/evaluate.md) | Evidence-backed keep/change classifications and priorities |
| Heuristic | Assess a flow, spec, or implementation for usability failures | [Heuristic](references/heuristic.md) | Concrete findings, severity, and PASS / FAIL / UNVERIFIABLE checks |

Heuristic BUILD uses the Critical Four plus relevant accessibility checks; ARCHITECT adds all ten heuristics and Norman's principles. For ethical conversion, pricing friction, and stakeholder negotiation use `ux-cro-audit`; use this skill for visual-system or usability questions on any surface, including pricing pages.

## Shared input and evidence contract

- Reuse supplied evidence, accepted scope, and accepted decisions. `.jimmy/work/<feature>/current-design-system.md` and `category-benchmarks.md` are conventional storage paths, not prerequisites. Request or collect only missing material evidence.
- Observations cite a screenshot, element, interaction, or dated source. Distinguish measured values, visual estimates, hypotheses, and unobserved behavior. Never invent user research, quotations, benchmarks, or test results.
- A static screenshot supports visual findings, not claims about keyboard access, recovery, or live timing. Spec-only heuristic review is valid but identifies proposed behavior and marks implementation checks UNVERIFIABLE.
- Check affected loading, empty, error, timeout, retry, and destructive-action states. Preserve input and recovery; include relevant accessibility barriers. Missing evidence is a named limitation, not a passing check.
- Continue authorized work using settled directions. Ask only for unresolved material choices, such as a new consequential brand change.

## Output and completion

Return mode, scope, evidence, findings, and remaining evidence gaps. Keep durable handoff artifacts under `.jimmy/work/<feature>/`: `current-design-system.md`, `design-evaluation.md`, or `heuristic-assessment.md`. A small standalone answer may stay inline. Complete when the requested decision has enough evidence and relevant checks are reported honestly; more modes are not a completion requirement.

## Applied context (edtech) — kit notes

Upstream specialist methods are retained in the local mode references. The kit uses any available screenshot tool and the `.jimmy/work/<feature>/` layout. The heuristic checklist is manual guidance, not a bundled enforcement runtime.
