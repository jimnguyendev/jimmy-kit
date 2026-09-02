# Jimmy Kit — Product & Engineering Skills

A curated, self-contained skill kit for AI agents (Claude Code / Codex / Gemini): product discovery, spec discipline, quality gates, analytics, UX, and engineering workflows. 51 skills across 7 categories, organized around one operating loop:

**UNDERSTAND → ENVISION → DELIVER → REFLECT**, as a maximal map rather than a mandatory pipeline. Ceremony scales with risk: Tier 1 may use no skill, Tier 2 normally uses one or two, and Tier 3 uses the full 7-question intake plus `product-council`. By default, Tier 1 and already-approved Tier 2 bypass council. Explicit red-team/pitch requests and consequential product/platform decisions are exceptions: they invoke council directly but do not expand the rest of the workflow unless the work is Tier 3. See `docs/OPERATING-WORKFLOW.md`.

## Engineering philosophy

> Programming is thinking, not typing. Structure serves clarity, not paradigm.

Seven principles drive engineering decisions across the kit. They do not add a mandatory engineering phase to product, UX, or analytics work; those requests keep their own risk-based routes.

| Area | Principle |
|---|---|
| Organize | 1. **Organize around business capabilities.** Group code by capability, not global technical layers. |
| Organize | 2. **Start with fewer packages.** Split only when observed pain proves a boundary; apply the same rule to modules in other stacks. |
| Organize | 3. **Keep names short.** Avoid repeating package or type context. |
| Organize | 4. **Keep types near usage.** Keep transport and persistence types near the boundary that owns them. |
| Organize | 5. **Keep dependency direction one-way.** Package/module imports form a directed acyclic graph (DAG). |
| Optimize | 6. **Constrain before you optimize.** Set targets, find the hot path, profile, then make the simplest sufficient change. |
| Ship | 7. **Enforce correctness with gates.** Require evidence and reversible delivery. |

For circular dependencies, first move responsibility to the correct owner, then merge a fake boundary, and only then introduce a small consumer-owned contract at a real seam. Go enforces import DAGs at compile time; the design principle applies to every stack. The operational reference is `skills/engineering/codebase-design/references/engineering-philosophy.md`.

## Install
```bash
npx skills add jimnguyendev/jimmy-kit        # any agent (Claude Code, Codex, Cursor, …)
```
or, in Claude Code: `/plugin marketplace add jimnguyendev/jimmy-kit` → `/plugin install jimmy-kit@jimmy-kit`.

Full guide (Claude Code / Codex / Cursor, global vs per-repo, where outputs go, how to start a session): **`docs/USAGE.md`**.

Run `scripts/link-skills.sh` to symlink all 51 skills into `~/.claude/skills` (or pass a target dir), or copy individual folders into your project's `.claude/skills/` / `.agents/skills/`. `scripts/list-skills.sh` lists everything. Skills write their outputs to `.jimmy/` in the repo they are installed in (`work/<feature>/`, `docs/`, `decisions.md`, `adr/NNNN-slug.md`, `constitution.md`) — add it to `.gitignore` if you don't want it tracked. Shared vocabulary: `CONTEXT.md`. Each skill is self-contained; cross-references degrade gracefully (see Source convention inside each skill).

## Categories
| Folder | What's inside |
|---|---|
| `skills/product/` | jtbd · opportunity-map · prd · problem-solving · okr-outcome-architect · product-council · growth-loops · subscription-paywall · go-to-market · product-vision · product-strategy |
| `skills/ux/` | ux-brief · ux-design · ux-discovery · ux-plan-tasks · ux-review · ux-specify · ux-writing · ux-cro-audit |
| `skills/process/` | analyst · architect · constitution · decision-log · quality-gates · change-tiers · independent-review · retrospective · routing |
| `skills/analytics/` | tracking-architect · growth-markov-duolingo · engagement-matrix-analytics · advanced-rfm-segmentation |
| `skills/engineering/` | domain-modeling · codebase-design · improve-codebase-architecture · zero-tech-debt · tdd-go · diagnose · prototype · triage · engineering-design-thinking · engineering-perf-optimization-process · engineering-rest-api-design |
| `skills/productivity/` | zoom-out · handoff · write-a-skill · grilling · grill-with-docs · grill-me · orchestrate |
| `skills/utilities/` | youtube-transcript |

## Credits & provenance (keep when redistributing)
- **Sage** — github.com/xoai/sage: the process backbone (gates, tiers, constitution, review, analyst, architect — bodies kept close to upstream; Sage-runtime commands and `.sage/` paths replaced with kit-runnable equivalents — see docs/DECISIONS.md K5). Renamed here: sage-gates→quality-gates, sage-tiers→change-tiers, sage-decisions→decision-log, sage-review→independent-review, sage-reflect→retrospective, sage-analyst→analyst, sage-architect→architect, sage-constitution→constitution, sage-routing→routing.
- **sage-product pack** — github.com/xoai/sage-product: jtbd, prd, opportunity-map, problem-solving, ux-brief/design/discovery/plan-tasks/review/specify/writing (close to upstream; same K5 substitutions).
- **Matt Pocock skills** — github.com/yykui/mattpocockSkills: zoom-out, handoff, write-a-skill, grill-me, grilling, grill-with-docs, diagnose, prototype, triage, orchestrate.
- Internal lecture series (growth loops, subscription strategy, GTM, product vision, product strategy, retention analytics, RFM) — distilled into growth-loops, subscription-paywall, go-to-market, product-vision, product-strategy and the analytics skills; lecture notes themselves are not bundled.
- OKR handbook + stakeholder/UX field lessons: internal materials and public UX Foundation talks, anonymized; examples use a generic edtech context.

## Conventions
`[sage]` = upstream Sage repo (public, optional deeper reading). Skills are self-contained: no internal-doc links inside skills; provenance lives here in README. Every self-authored skill opens with a one-line failure statement ("this skill exists to stop: …") and a HOW-TO-USE section with modes and output formats. Decision history: `docs/DECISIONS.md`.

## License
MIT — see `LICENSE`. Upstream material (Sage, sage-product, mattpocockSkills) keeps its original MIT-style attribution.
