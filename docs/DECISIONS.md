# Decision log — Jimmy Kit
> Newest first. Each entry: decision · why · rejected alternatives with losing reasons.

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
