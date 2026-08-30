# Jimmy Kit — Product & Engineering Skills

A curated, self-contained skill kit for AI agents (Claude Code / Codex / Gemini): product discovery, spec discipline, quality gates, analytics, UX, and engineering workflows. 49 skills across 7 categories, organized around one operating loop:

**UNDERSTAND → ENVISION → DELIVER → REFLECT**, with a 7-question thinking layer on intake and a `product-council` red-team gate before anything gets built or pitched. See `docs/OPERATING-WORKFLOW.md`.

## Install
Copy the skill folders you need into your project's `.claude/skills/` (or `.agents/skills/`). Each skill is self-contained; cross-references degrade gracefully (see Source convention inside each skill).

## Categories
| Folder | What's inside |
|---|---|
| `skills/product/` | jtbd · opportunity-map · prd · problem-solving · okr-outcome-architect · product-council |
| `skills/ux/` | ux-brief · ux-design · ux-discovery · ux-plan-tasks · ux-review · ux-specify · ux-writing · ux-cro-audit |
| `skills/process/` | analyst · architect · constitution · decision-log · quality-gates · change-tiers · independent-review · retrospective · routing |
| `skills/analytics/` | tracking-architect · growth-markov-duolingo · engagement-matrix-analytics · advanced-rfm-segmentation |
| `skills/engineering/` | domain-modeling · codebase-design · improve-codebase-architecture · zero-tech-debt · tdd-go · capture-knowledge-go · port-service · kafka-patterns · diagnose · prototype · triage · design-thinking · perf-optimization · rest-api-design |
| `skills/productivity/` | zoom-out · handoff · write-a-skill · grilling · grill-with-docs · grill-me · orchestrate |
| `skills/utilities/` | youtube-transcript |

## Credits & provenance (keep when redistributing)
- **Sage** — github.com/xoai/sage: the process backbone (gates, tiers, constitution, review, analyst, architect — canonical bodies kept verbatim; `/sage-*` commands inside them are heritage of the original). Renamed here: sage-gates→quality-gates, sage-tiers→change-tiers, sage-decisions→decision-log, sage-review→independent-review, sage-reflect→retrospective, sage-analyst→analyst, sage-architect→architect, sage-constitution→constitution, sage-routing→routing.
- **sage-product pack** — github.com/xoai/sage-product: jtbd, prd, opportunity-map, problem-solving, ux-brief/design/discovery/plan-tasks/review/specify/writing (verbatim).
- **Matt Pocock skills** — github.com/yykui/mattpocockSkills: zoom-out, handoff, write-a-skill, grill-me, grilling, grill-with-docs, diagnose, prototype, triage, orchestrate.
- OKR handbook + stakeholder/UX field lessons: internal materials and public UX Foundation talks, anonymized; examples use a generic edtech context.

## Conventions
`[sage]` = upstream Sage repo · `[docs]` = your internal docs repo (optional deep-dives). Every self-authored skill opens with a one-line failure statement ("this skill exists to stop: …") and a HOW-TO-USE section with modes and output formats. Decision history: `docs/DECISIONS.md`.
