# Decision log — Jimmy Kit
> Newest first. Each entry: decision · why · rejected alternatives with losing reasons.

## 2026-08-30 · K5 — No Sage runtime dependencies inside skills (supersedes the "verbatim" clause of K2)
**Decision:** Every command, script or path that only works with the Sage runtime is replaced by a kit-runnable equivalent: `sage-*-gate.sh` → described as generic pre-edit hooks / gate checks; `sage-screenshot.sh` → any available screenshot tool; `sage add …` → "bundled in this kit"; `sage/core/...` doc paths → `[sage]` token (optional upstream deep-dive); `/sage-*` → kit skill names; `.sage/*` → `.jimmy/*` one-to-one (`.jimmy/work/<feature>/`, `.jimmy/docs/`, `.jimmy/decisions.md`, `.jimmy/constitution.md`; feature-level ADRs in `.jimmy/work/<feature>/decisions.md`). A single namespaced dir keeps skill output out of the target repo's own `docs/` and makes it one `.gitignore` line if a team wants it untracked. Bodies otherwise stay close to upstream (no re-voicing, no restructuring) so diffs against upstream remain readable.
**Why:** the kit's own rule is "skills must run without [sage]/[docs]"; dead commands violate it and confuse every non-Sage user (Codex, Cursor). An upstream-diff that shows only these substitutions is still easy to sync.
**Rejected:** writing outputs to `docs/work/` (first draft this session — collides with the target repo's own docs); keeping verbatim + appendix notes (tried this session for ux-review — the dead command is still the first thing the agent reads); shipping the Sage runtime with the kit (contradicts K1).

## 2026-08-30 · K4 — kafka-patterns removed; kit trimmed to 48 skills
**Decision:** Drop `engineering/kafka-patterns` from the kit (owner's call: not needed by the target teams). Kit = 48 skills, 7 categories. Same session: independent scenario runs recorded in the 3 SCENARIO.md files, review checklist findings fixed (relative links to bundled scripts/templates, Vietnamese remnants translated, personal author handles removed, H1s added to the Pocock one-liners, `ux-cro-audit` gained row 15 "Failure & empty states" after the independent run missed the AI-failure branch).
**Why:** a reference-style Kafka pattern catalogue is infrastructure knowledge, not a workflow skill, and had no consumer in the operating model. **Rejected:** keeping it as `user-invocable: false` reference (still costs review/translation effort every sync).

## 2026-08-30 · K3 — Routing skill added from upstream
**Decision:** Port sage-routing verbatim as `routing` (process/), with a kit appendix pointing at the 10-problem routing table in OPERATING-WORKFLOW.md.
**Why:** a kit of 49 skills without a router forces every user to memorize the map. **Rejected:** writing a custom router (upstream's is battle-tested; ours is just the table).

## 2026-08-30 · K2 — English-only, voice-infused council, linked-kit hygiene
**Decision:** All kit content in English (skills, templates, scenarios); product-council seats carry anonymized voice profiles (philosophy + speaking style of two real practitioners, unnamed by request) so debates read human, not bureaucratic; cross-skill references use kit names only; [docs]/[sage] tokens for external deep-dives.
**Why:** company-wide + cross-agent reuse; naming real colleagues in a distributed skill affects them.
**Rejected:** bilingual files (drift risk); naming the practitioners (asymmetric risk to them); scrubbing heritage /sage-* mentions inside canonical bodies (breaks upstream fidelity).

## 2026-08-30 · K1 — Kit created
**Decision:** Extract the company skill set into `jimmy-kit` (this repo, sibling of `sage`): 48 skills in 7 categories, all English, brand-neutral examples (generic edtech), README carries provenance. Sources: the practice-labs skill set (de-branded), jimmy-skills engineering pack, learning-be special skills (zoom-out, diagnose, domain-modeling, zero-tech-debt, …), Matt Pocock skills (grill-me, prototype, triage, …).
**Why:** company-wide reuse across agents (Claude/Codex/Gemini); Vietnamese-only skills and personal/brand references don't travel.
**Rejected:** shipping as a Sage pack (requires sage CLI for every user — may revisit); keeping Vietnamese with EN summaries (splits the audience); bundling all internal docs (stale-copy risk — deep-dives stay optional via [docs] token).
