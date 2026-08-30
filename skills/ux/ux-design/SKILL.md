---
name: "ux-design"
description: "End-to-end UX design process — research, evaluation, specification, design, review woven into the development workflow. Use when a feature needs design work coordinated across phases, or when unsure which ux-* skill applies (this one routes)."
version: "2.0.0"
type: bundle
includes:
  - "ux-audit"
  - "ux-research"
  - "ux-evaluate"
  - "ux-brief"
  - "ux-discovery"
  - "ux-specify"
  - "ux-plan-tasks"
  - "ux-heuristic-review"
  - "ux-writing"
requires:
  sage: ">=1.0.0"
tags: [ux, design, research, usability, microcopy]
sources:
  - "Don't Make Me Think — Steve Krug"
  - "The Design of Everyday Things — Don Norman"
  - "The Elements of User Experience — Jesse James Garrett"
  - "Lean UX — Jeff Gothelf & Josh Seiden"
  - "Microcopy: The Complete Guide — Kinneret Yifrah"
  - "Strategic Writing for UX — Torrey Podmajersky"
constitution-additions: "ux-design.constitution-additions.md"
---

# UX Design

Installs 9 skills for the complete UX workflow:

## Redesign Path (pre-elicitation)
- **ux-audit** → **ux-research** → **ux-evaluate** → **ux-brief**

## Forward Path (alongside development)
- **ux-discovery** → **ux-specify** → **ux-plan-tasks** → **ux-heuristic-review**

## Cross-Cutting
- **ux-writing** — Voice and tone guides, microcopy, content audits

Each skill works independently. Install the bundle for the full chain.
