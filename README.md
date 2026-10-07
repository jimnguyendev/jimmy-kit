# Jimmy Kit — Product & Engineering Skills

A curated, self-contained skill kit for AI agents (Claude Code / Codex / Gemini): product discovery, spec discipline, quality gates, analytics, UX, engineering workflows, Go, and databases (MySQL, PostgreSQL, MongoDB, ClickHouse). 94 skills across 8 installable groups, organized around one operating loop:

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

Install everything, or only the groups you need. Groups are defined once in `groups.json`.

| Group | Skills | What it covers |
|---|---|---|
| `core` | 16 | routing, change tiers, quality gates, decisions, review, retrospective, grilling, handoff, orchestrate, write-a-skill |
| `engineer` | 14 | verify-app, design thinking, domain modeling, codebase design, diagnose, triage, REST API design, perf process, reality-gate, backend-core, kafka-patterns |
| `golang` | 29 | tdd-go, capture-knowledge-go, the `backend-go-*` pack |
| `database` | 10 | MySQL, PostgreSQL, MongoDB, ClickHouse, Go database access |
| `product` | 11 | JTBD, PRD, OKRs, product council, growth loops, paywall, GTM, vision, strategy |
| `ux` | 8 | UX brief → review, CRO audit |
| `analytics` | 4 | tracking architecture, retention, engagement, RFM |
| `utilities` | 2 | YouTube and Facebook transcripts |

```bash
# Claude Code plugin: add the marketplace once, then install groups (or jimmy-kit@jimmy-kit for all)
/plugin marketplace add jimnguyendev/jimmy-kit
/plugin install core@jimmy-kit
/plugin install golang@jimmy-kit
/plugin install database@jimmy-kit

# Any agent via npx: print the exact command for your groups, then run it
python3 scripts/kit.py npx --group core,golang,database --agent codex

# Local clone: symlink chosen groups into an agent's skills dir
scripts/link-skills.sh ~/.claude/skills --group core,golang,database
python3 scripts/kit.py groups                  # list groups and counts
```
Pair `core` with any other group: it carries the routing and gates the other groups hand off to. A backend Go service typically wants `core,engineer,golang,database`.

Full guide (Claude Code / Codex / Cursor, global vs per-repo, where outputs go, how to start a session, how to make agents prove changes on the running app with `verify-app`): **`docs/USAGE.md`**.

Run `scripts/link-skills.sh` to symlink all 94 skills into `~/.claude/skills` (or pass a target dir and `--group`), or copy individual folders into your project's `.claude/skills/` / `.agents/skills/`. `scripts/list-skills.sh` lists everything. Skills write their outputs to `.jimmy/` in the repo they are installed in (`work/<feature>/`, `docs/`, `decisions.md`, `adr/NNNN-slug.md`, `constitution.md`) — add it to `.gitignore` if you don't want it tracked. Shared vocabulary: `CONTEXT.md`. Each skill is self-contained; cross-references degrade gracefully (see Source convention inside each skill).

## Categories
| Folder | What's inside |
|---|---|
| `skills/product/` | jtbd · opportunity-map · prd · problem-solving · okr-outcome-architect · product-council · growth-loops · subscription-paywall · go-to-market · product-vision · product-strategy |
| `skills/ux/` | ux-brief · ux-design · ux-discovery · ux-plan-tasks · ux-review · ux-specify · ux-writing · ux-cro-audit |
| `skills/process/` | analyst · architect · constitution · decision-log · quality-gates · change-tiers · independent-review · retrospective · routing |
| `skills/analytics/` | tracking-architect · growth-markov-duolingo · engagement-matrix-analytics · advanced-rfm-segmentation |
| `skills/engineering/` | domain-modeling · codebase-design · improve-codebase-architecture · zero-tech-debt · diagnose · prototype · triage · engineering-design-thinking · engineering-perf-optimization-process · engineering-rest-api-design · reality-gate · verify-app · backend-core · kafka-patterns |
| `skills/golang/` | tdd-go · capture-knowledge-go · 27 `backend-go-*` skills (testing, testify, concurrency, context, errors, observability, performance, benchmark, safety, security, linter, naming, code style, project layout, design patterns, structs/interfaces, data structures, dependency management, modernize, documentation, CI, gRPC, CLI, popular libraries, samber/hot, stay updated, troubleshooting) |
| `skills/database/` | backend-go-database · mysql · postgres · clickhouse-best-practices · clickhouse-architecture-advisor · infra-clickhouse · mongodb-connection · mongodb-schema-design · mongodb-query-optimizer · mongodb-natural-language-querying |
| `skills/productivity/` | zoom-out · handoff · write-a-skill · grilling · grill-with-docs · grill-me · orchestrate |
| `skills/utilities/` | youtube-transcript, facebook-transcript |

## Credits & provenance (keep when redistributing)
- **Sage** — github.com/xoai/sage: the process backbone (gates, tiers, constitution, review, analyst, architect — bodies kept close to upstream; Sage-runtime commands and `.sage/` paths replaced with kit-runnable equivalents — see docs/DECISIONS.md K5). Renamed here: sage-gates→quality-gates, sage-tiers→change-tiers, sage-decisions→decision-log, sage-review→independent-review, sage-reflect→retrospective, sage-analyst→analyst, sage-architect→architect, sage-constitution→constitution, sage-routing→routing.
- **sage-product pack** — github.com/xoai/sage-product: jtbd, prd, opportunity-map, problem-solving, ux-brief/design/discovery/plan-tasks/review/specify/writing (close to upstream; same K5 substitutions).
- **Matt Pocock skills** — github.com/yykui/mattpocockSkills: zoom-out, handoff, write-a-skill, grill-me, grilling, grill-with-docs, diagnose, prototype, triage, orchestrate.
- Internal lecture series (growth loops, subscription strategy, GTM, product vision, product strategy, retention analytics, RFM) — distilled into growth-loops, subscription-paywall, go-to-market, product-vision, product-strategy and the analytics skills; lecture notes themselves are not bundled.
- **pstack** — [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan (MIT): ideas adapted, in the kit's own words, into `verify-app` (verification skill + feature map + maintenance pass), `write-a-skill`'s blind evaluation reference, `retrospective`'s mechanism ladder, and the iteration loop in `engineering-perf-optimization-process`.
- **Go pack** (`skills/golang/`, `backend-core`, `kafka-patterns`, `backend-go-database`) — the author's own Go backend skills, originally derived from [samber/cc-skills-golang](https://github.com/samber/cc-skills-golang) (MIT) and since rewritten.
- **Vendored database skills** (kept verbatim, each folder carries its upstream LICENSE and, where upstream ships one, NOTICE; source commit in `groups.json`): `mysql`, `postgres` from [planetscale/database-skills](https://github.com/planetscale/database-skills) (MIT); `clickhouse-best-practices`, `clickhouse-architecture-advisor`, `infra-clickhouse` from [ClickHouse/agent-skills](https://github.com/ClickHouse/agent-skills) (Apache-2.0); `mongodb-*` from [mongodb/agent-skills](https://github.com/mongodb/agent-skills) (Apache-2.0).
- OKR handbook + stakeholder/UX field lessons: internal materials and public UX Foundation talks, anonymized; examples use a generic edtech context.

## Conventions
`[sage]` = upstream Sage repo (public, optional deeper reading). Skills are self-contained: no internal-doc links inside skills; provenance lives here in README. Every self-authored skill opens with a one-line failure statement ("this skill exists to stop: …") and a HOW-TO-USE section with modes and output formats. Decision history: `docs/DECISIONS.md`.

## License
MIT — see `LICENSE`. Upstream material (Sage, sage-product, mattpocockSkills, samber/cc-skills-golang, pstack) keeps its original MIT-style attribution. Vendored database skills keep their own licenses (MIT or Apache-2.0) in their folders. The pstack notice is in `THIRD_PARTY_NOTICES.md`.
