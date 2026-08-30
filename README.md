# Jimmy Kit — Product & Engineering Skills

A curated, self-contained skill kit for AI agents (Claude Code / Codex / Gemini): product discovery, spec discipline, quality gates, analytics, UX, and engineering workflows. 48 skills across 7 categories, organized around one operating loop:

**UNDERSTAND → ENVISION → DELIVER → REFLECT**, with a 7-question thinking layer on intake and a `product-council` red-team gate before anything gets built or pitched. See `docs/OPERATING-WORKFLOW.md`.

## Install
Full guide (Claude Code / Codex / Cursor, global vs per-repo, where outputs go, how to start a session): **`docs/USAGE.md`**.

Run `scripts/link-skills.sh` to symlink all 48 skills into `~/.claude/skills` (or pass a target dir), or copy individual folders into your project's `.claude/skills/` / `.agents/skills/`. `scripts/list-skills.sh` lists everything. Skills write their outputs to `.jimmy/` in the repo they are installed in (`work/<feature>/`, `docs/`, `decisions.md`, `adr/NNNN-slug.md`, `constitution.md`) — add it to `.gitignore` if you don't want it tracked. Shared vocabulary: `CONTEXT.md`. Each skill is self-contained; cross-references degrade gracefully (see Source convention inside each skill).

## Categories
| Folder | What's inside |
|---|---|
| `skills/product/` | jtbd · opportunity-map · prd · problem-solving · okr-outcome-architect · product-council |
| `skills/ux/` | ux-brief · ux-design · ux-discovery · ux-plan-tasks · ux-review · ux-specify · ux-writing · ux-cro-audit |
| `skills/process/` | analyst · architect · constitution · decision-log · quality-gates · change-tiers · independent-review · retrospective · routing |
| `skills/analytics/` | tracking-architect · growth-markov-duolingo · engagement-matrix-analytics · advanced-rfm-segmentation |
| `skills/engineering/` | domain-modeling · codebase-design · improve-codebase-architecture · zero-tech-debt · tdd-go · capture-knowledge-go · port-service · diagnose · prototype · triage · engineering-design-thinking · engineering-perf-optimization-process · engineering-rest-api-design |
| `skills/productivity/` | zoom-out · handoff · write-a-skill · grilling · grill-with-docs · grill-me · orchestrate |
| `skills/utilities/` | youtube-transcript |

## Credits & provenance (keep when redistributing)
- **Sage** — github.com/xoai/sage: the process backbone (gates, tiers, constitution, review, analyst, architect — bodies kept close to upstream; Sage-runtime commands and `.sage/` paths replaced with kit-runnable equivalents — see docs/DECISIONS.md K5). Renamed here: sage-gates→quality-gates, sage-tiers→change-tiers, sage-decisions→decision-log, sage-review→independent-review, sage-reflect→retrospective, sage-analyst→analyst, sage-architect→architect, sage-constitution→constitution, sage-routing→routing.
- **sage-product pack** — github.com/xoai/sage-product: jtbd, prd, opportunity-map, problem-solving, ux-brief/design/discovery/plan-tasks/review/specify/writing (close to upstream; same K5 substitutions).
- **Matt Pocock skills** — github.com/yykui/mattpocockSkills: zoom-out, handoff, write-a-skill, grill-me, grilling, grill-with-docs, diagnose, prototype, triage, orchestrate.
- OKR handbook + stakeholder/UX field lessons: internal materials and public UX Foundation talks, anonymized; examples use a generic edtech context.

## Conventions
`[sage]` = upstream Sage repo · `[docs]` = your internal docs repo (optional deep-dives). Every self-authored skill opens with a one-line failure statement ("this skill exists to stop: …") and a HOW-TO-USE section with modes and output formats. Decision history: `docs/DECISIONS.md`.

## License
MIT — see `LICENSE`. Upstream material (Sage, sage-product, mattpocockSkills) keeps its original MIT-style attribution.
