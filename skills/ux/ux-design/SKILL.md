---
name: ux-design
description: >-
  Use when a feature needs UX work coordinated across research, specification, and review, or when the right UX skill is unclear for a redesign, usability issue, or conversion concern.
version: "2.0.0"
tags: [ux, design, research, usability, microcopy]
sources:
  - "Don't Make Me Think — Steve Krug"
  - "The Design of Everyday Things — Don Norman"
  - "The Elements of User Experience — Jesse James Garrett"
  - "Lean UX — Jeff Gothelf & Josh Seiden"
  - "Microcopy: The Complete Guide — Kinneret Yifrah"
  - "Strategic Writing for UX — Torrey Podmajersky"
---

# UX Design

> **This skill exists to stop:** running an entire UX workflow when a focused decision needs only one mode, or routing that decision to an unavailable skill.

## 🤖 0. HOW TO USE

This is a dispatcher. Select the smallest useful next step from the table; output the selected skill/mode, the decision it will inform, and the evidence already available. Each skill works independently and must be installed separately if absent; this entrypoint does not install a bundle or runtime hooks.

| Need | Skill / mode | Result |
|---|---|---|
| Extract the current visual system | `ux-review` — audit | Current design system |
| Understand user behavior or plan interviews | `ux-discovery` — BUILD / ARCHITECT; interview reference when needed | Context notes, research plan, evidence-grounded personas/journeys |
| Research category conventions | `ux-discovery` — research | Dated category benchmarks |
| Compare current UI with category evidence | `ux-review` — evaluate | Keep/change classifications |
| Turn accepted direction into a brief | `ux-brief` | Visual direction and constraints |
| Fill UX gaps in a specification | `ux-specify` — BUILD / ARCHITECT | State coverage, accessibility, acceptance criteria |
| Plan validation for a substantial flow | `ux-plan-tasks` — ARCHITECT only | Relevant validation tasks and completion evidence |
| Check implementation usability | `ux-review` — heuristic, BUILD / ARCHITECT | Evidence-backed severity findings |
| Write or review interface words | `ux-writing` — FIX / BUILD / ARCHITECT | Microcopy, voice guide, or content audit |
| Improve conversion or negotiate stakeholder demands | `ux-cro-audit` | Ethical conversion findings or negotiation script |

A redesign may use audit → research → evaluate → brief, but only missing evidence justifies earlier steps. An accepted brief may go straight to specification or implementation. A narrow usability question can use heuristic review directly. Conversion work can also need a focused usability check; keep the two findings tied to their respective user and business goals.

Reuse supplied screenshots, research, accepted scope, and prior decisions. Missing `.jimmy/` artifact files do not invalidate equivalent evidence in the conversation or project. Ask only about unresolved decisions that materially affect the next step. Never manufacture research, measurements, or user quotations to fill a gap.

## Optional supporting guidance

Load only when the corresponding role needs additional guidance:
- [Analyst guidance](persona-enrichments/analyst.enrichment.md)
- [Developer guidance](persona-enrichments/developer.enrichment.md)
- [Reviewer guidance](persona-enrichments/reviewer.enrichment.md)
- [Suggested project UX principles](ux-design.constitution-additions.md)

These are reference material, not automatically installed personas or enforcement.
