# Decision log — Jimmy Kit
> Newest first. Each entry: decision · why · rejected alternatives with losing reasons.

## 2026-08-30 · K8 — Proposal only: five frameworks from the lecture series (drafts/, not skills/)
**Decision:** Do NOT add skills unilaterally. Gap analysis shows five frameworks (growth loops, paywall/subscription, GTM, product vision, stage-gate strategy) absent from the kit; drafts parked in `drafts/from-lecture-series/` pending the owner's call, to be rebuilt via `write-a-skill` if approved.
**Why:** the owner asked whether the kit was missing these ideas — not for them to be written; and drafts written outside the kit's own process (write-a-skill, scenario-first) don't meet the bar. **Rule reaffirmed:** skills carry no internal-doc links; provenance lives in README only.

## 2026-08-30 · K8 — Five skills distilled from the lecture-notes series
**Decision:** Add growth-loops, subscription-paywall, go-to-market, product-vision, product-strategy (product/), and enrich advanced-rfm-segmentation with the 11 RFM personas + K-means/elbow appendix. Source: the internal lecture guides v05–v09 and v12 (`[docs] guides/`), which the kit had only partially absorbed (v10, v11, v13).
**Why:** the guides carried five frameworks with no home in the kit (loops/hooks, paywall psychology + revenue tree, GTM sequencing, vision/systems thinking, stage-gate strategy); each is a recurring product decision. **Rejected:** bundling the guides verbatim (Vietnamese, brand-bound, stale-copy risk) — distilled to English skills with [docs] pointers instead. Scenarios written, not yet run (exit 2).

## 2026-08-31 · K7 — capture-knowledge-go and port-service removed (46 skills)
**Decision:** Drop both from the kit (owner's call). `capture-knowledge-go`: a shell without its engine — the stripped adaptation of a SQLite/FTS-backed skill reduced to "explore, then write a Markdown brief", which agents do natively and `zoom-out` already covers in-conversation; its only in-kit consumer was port-service. `port-service`: genuinely strong guardrails (dry-run migrations, read-only source, phase gates) but situational — useful only when a service port/merge is actually planned, and written against a specific Go repo + the non-bundled Go pack. Both survive in the origin repo and git history; re-import when a port is scheduled.
**Why:** a company kit should not carry skills 95% of installers never trigger — they are routing noise and per-sync maintenance cost. **Rejected:** generalizing capture-knowledge-go (the generic version is agent default behavior); keeping port-service "just in case" (the trigger condition is knowable — a planned port — so import-on-demand beats carry-always).

## 2026-08-31 · K6 — Eager dispatcher block ships as a template (fixes a dangling port)
**Decision:** `routing` was ported assuming Sage's always-on layer ("the eager layer carries the keyword map") which the kit never shipped — in Sage that map lives in the generated CLAUDE.md/AGENTS.md (Rule 0), not in the skill. Fix: `templates/eager-dispatcher.md` (~35 lines: kit keyword map → skill chains, council gate, evidence rule) is the single source; target repos append it to their AGENTS.md (USAGE §3); `routing` points at it and keeps Layers 2–3 (classifier fallback, confirmation format, worked examples).
**Why:** without an always-on layer the router body was a dangling reference, natural-language requests could bypass routing entirely, and the "mandatory" council gate had no instruction behind it.
**Rejected:** porting Sage's full runtime (generator, navigator, classifier persona, hooks — contradicts K1/K5); duplicating the map into routing's body AND a template (two hand-maintained copies is how Sage itself drifted — one source, referenced from the skill); a YAML route registry with generators (right shape at Sage's scale, overkill for one 35-line block; revisit if a third copy of the map ever appears).

## 2026-08-30 · K5 — No Sage runtime dependencies inside skills (supersedes the "verbatim" clause of K2)
**Decision:** Every command, script or path that only works with the Sage runtime is replaced by a kit-runnable equivalent: `sage-*-gate.sh` → described as generic pre-edit hooks / gate checks; `sage-screenshot.sh` → any available screenshot tool; `sage add …` → "bundled in this kit"; `sage/core/...` doc paths → `[sage]` token (optional upstream deep-dive); `/sage-*` → kit skill names; `.sage/*` → `.jimmy/*` one-to-one (`.jimmy/work/<feature>/`, `.jimmy/docs/`, `.jimmy/decisions.md`, `.jimmy/constitution.md`; feature-level ADRs in `.jimmy/work/<feature>/decisions.md`; numbered engineering ADRs formerly at `docs/adr/` → `.jimmy/adr/`, runbooks → `.jimmy/docs/runbooks/`). A single namespaced dir keeps skill output out of the target repo's own `docs/` and makes it one `.gitignore` line if a team wants it untracked. Bodies otherwise stay close to upstream (no re-voicing, no restructuring) so diffs against upstream remain readable.
**Why:** the kit's own rule is "skills must run without [sage]/[docs]"; dead commands violate it and confuse every non-Sage user (Codex, Cursor). An upstream-diff that shows only these substitutions is still easy to sync.
**Rejected:** writing outputs to `docs/work/` (first draft this session — collides with the target repo's own docs); keeping verbatim + appendix notes (tried this session for ux-review — the dead command is still the first thing the agent reads); shipping the Sage runtime with the kit (contradicts K1).

## 2026-08-30 · K4 — kafka-patterns removed; kit trimmed to 48 skills
**Decision:** Drop `engineering/kafka-patterns` from the kit (owner's call: not needed by the target teams). Kit = 48 skills, 7 categories. Same session: independent scenario runs recorded in the 3 SCENARIO.md files, review checklist findings fixed (relative links to bundled scripts/templates, Vietnamese remnants translated, personal author handles removed, H1s added to the Pocock one-liners, `ux-cro-audit` gained row 15 "Failure & empty states" after the independent run missed the AI-failure branch).
**Why:** a reference-style Kafka pattern catalogue is infrastructure knowledge, not a workflow skill, and had no consumer in the operating model. **Rejected:** keeping it as `user-invocable: false` reference (still costs review/translation effort every sync).

## 2026-08-30 · K3 — Routing skill added from upstream
**Decision:** Port sage-routing verbatim as `routing` (process/), with a kit appendix pointing at the 10-problem routing table in OPERATING-WORKFLOW.md.
**Why:** a kit of 49 skills (48 after K4) without a router forces every user to memorize the map. **Rejected:** writing a custom router (upstream's is battle-tested; ours is just the table).

## 2026-08-30 · K2 — English-only, voice-infused council, linked-kit hygiene
**Decision:** All kit content in English (skills, templates, scenarios); product-council seats carry anonymized voice profiles (philosophy + speaking style of two real practitioners, unnamed by request) so debates read human, not bureaucratic; cross-skill references use kit names only; [docs]/[sage] tokens for external deep-dives.
**Why:** company-wide + cross-agent reuse; naming real colleagues in a distributed skill affects them.
**Rejected:** bilingual files (drift risk); naming the practitioners (asymmetric risk to them); scrubbing heritage /sage-* mentions inside canonical bodies (breaks upstream fidelity).

## 2026-08-30 · K1 — Kit created
**Decision:** Extract the company skill set into `jimmy-kit` (this repo, sibling of `sage`): 48 skills in 7 categories, all English, brand-neutral examples (generic edtech), README carries provenance. Sources: the internal product skill set (de-branded), the internal engineering pack, backend-repo special skills (zoom-out, diagnose, domain-modeling, zero-tech-debt, …), Matt Pocock skills (grill-me, prototype, triage, …).
**Why:** company-wide reuse across agents (Claude/Codex/Gemini); Vietnamese-only skills and personal/brand references don't travel.
**Rejected:** shipping as a Sage pack (requires sage CLI for every user — may revisit); keeping Vietnamese with EN summaries (splits the audience); bundling all internal docs (stale-copy risk — deep-dives stay optional via [docs] token).
