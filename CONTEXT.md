# Jimmy Kit — Domain Glossary

Shared vocabulary for every skill in this kit. Skills (e.g. `zoom-out`) reference "the project's domain glossary" — this is it. Pattern borrowed from mattpocockSkills' CONTEXT.md.

## Language

**Skill**: one folder under `skills/<category>/<name>/` with a `SKILL.md` (frontmatter `name` matches the folder). _Avoid:_ prompt, command.

**Failure statement**: the one-line opener `> **This skill exists to stop:** …` — the agent mistake the skill prevents. A skill that can't state one shouldn't exist.

**Exit 0 / 1 / 2**: verification states — pass with evidence / fail with evidence / **unverifiable**. Exit 2 is never a pass; "spec'd" is not "done". Owned by `quality-gates`.

**Claim labels**: `[VERIFIED]` (source + date + scope + still true) · `[ASSUMPTION]` (openly unproven, with a plan to check) · `[GUESS]` (unproven and dressed as fact — the dangerous one). Owned by `analyst`.

**Tier**: ceremony level of a change — Tier 1 just do it · Tier 2 announce and proceed · Tier 3 present options and let someone choose. Ceremony scales with risk, not size. Owned by `change-tiers`.

**ADR / Decision entry**: what was decided · why (reasoning) · losing alternatives with their losing reasons. Newest first. Owned by `decision-log`. _Avoid:_ meeting notes.

**Gate**: a checkpoint that blocks progress until evidence exists — never a reminder. A checklist line without a required-evidence column is a "confidence tick", not a gate.

**Council seat**: one of four anonymized reviewer archetypes in `product-council` (CEO/Business, PD/Strategy, CTO/Engineering, UX/Human). A seat must state its **acceptance condition**; criticism without one is out of order.

**Initiative vs Key Result**: an initiative is a bet ("we believe X moves KR Y by Z because…"); a KR is an outcome with metric + baseline + target + date. Shipping an initiative proves nothing about the KR. Owned by `okr-outcome-architect`.

**Source tokens**: `[sage]` = upstream Sage repo (github.com/xoai/sage) · `[docs]` = your internal docs repo. Deep-dives only; skills run without them; a MUST READ step stops and asks when its file is missing.

**Work paths**: where skills write inside the repo they are installed in — everything under `.jimmy/` (one namespaced dir, mirrors upstream `.sage/`): `.jimmy/work/<feature>/` (in-progress artifacts: brief, spec, plan, screenshots, `decisions.md` for that feature) · `.jimmy/docs/` (durable outputs: research briefs, audits, voice & tone) · `.jimmy/decisions.md` (global ADRs) · `.jimmy/adr/NNNN-slug.md` (numbered engineering ADRs) · `.jimmy/constitution.md` (project principles). _Avoid:_ `.sage/`, the target repo's `docs/`, tool-specific paths.

## Relationships
- The `routing` skill dispatches problems to skill chains (map: `docs/OPERATING-WORKFLOW.md`).
- `product-council` gates the ENVISION → DELIVER transition.
- Every self-authored skill carries a Failure statement and a HOW-TO-USE section; canonical upstream bodies stay close to upstream, minus Sage-runtime commands/paths (K5).

## Flagged ambiguities
- "done" — resolved: done means exit 0 (evidence attached), never "spec written" or "code merged".
- "test" (A/B) vs "test" (QA) — say "experiment" for A/B, "verification" for QA.
- "personalization" — reserved for systems choosing among hundreds of options per user; a screen with three options is not personalization.
