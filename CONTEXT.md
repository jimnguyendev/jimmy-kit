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

**Problem Frame**: the decision artifact that names owner and stakeholders, evidence-backed actual state, expected state, the gap and why it matters, abstraction level, constraints, assumptions, cause hypotheses, success evidence, and out-of-scope boundaries. It must be solution-free. Owned by `engineering-design-thinking`.

**First-principles mode**: a bounded derivation that separates facts, conventions, and assumptions; decomposes to testable fundamentals; maps their interactions; and rebuilds options. It is used when evidence and familiar patterns conflict, not as permission for endless analysis.

**Solution ideality**: `Benefits / (Resources Required + Harmful Effects)`. It is a comparison lens, not fake precision; every term needs evidence or an assumption label.

**Contradiction**: an apparent need for opposite properties under the same condition. Test separation in time, space, condition, or parts/whole before accepting a compromise; if separation does not work, record the real trade-off and decision authority.

**Learning record**: `Claim -> Evidence -> Decision -> Outcome -> Model update`. Shipping closes implementation, not learning; the observed outcome must update, narrow, or reverse the decision model.

**Essential vs accidental complexity**: essential complexity belongs to the real domain, required state, failure, or coordination; accidental complexity comes from a design choice. The five scan axes are shared mutable state, side effects, dependencies, control flow, and code size.

**Complexity treatment**: `reduce` removes an unnecessary moving part · `isolate` puts a necessary moving part behind one owner and a small interface · `accept` keeps essential complexity explicitly. Moving it behind more indirection is relocation, not improvement.

**Functional Core / Imperative Shell**: an optional architecture in which explicit value transformations and domain rules form the core while required state, effects, dependencies, and coordination stay in the shell. It is not a mandate to use functions everywhere or classes in the shell.

**Feature-first locality**: organize code around a business capability so the behavior, transport, persistence mapping, and feature-local types that change together remain close. It is a default, not permission to ignore a target repository's accepted architecture.

**Dependency DAG**: a one-way directed acyclic graph of package/module dependencies. Go enforces package cycles at compile time; other stacks may not, but the ownership and coupling principle is stack-neutral.

**Consumer-owned contract**: the smallest role/interface defined by the module that needs the behavior, satisfied by a provider and wired at the composition root. Use it for a real independent seam, not for every implementation or as the first response to a cycle.

**Council seat**: one of four anonymized reviewer archetypes in `product-council` (CEO/Business, PD/Strategy, CTO/Engineering, UX/Human). A seat must state its **acceptance condition**; criticism without one is out of order. By default, Tier 1 and already-approved Tier 2 bypass council. Explicit red-team/pitch requests and consequential product/platform decisions are exceptions: they invoke council directly but do not expand the rest of the workflow unless the work is Tier 3.

**Initiative vs Key Result**: an initiative is a bet ("we believe X moves KR Y by Z because…"); a KR is an outcome with metric + baseline + target + date. Shipping an initiative proves nothing about the KR. Owned by `okr-outcome-architect`.

**Source token**: `[sage]` = upstream Sage repo (github.com/xoai/sage), public. Skills carry no internal-doc links; provenance is in README. A MUST READ step refers to the user's own project file and stops-and-asks when it is missing.

**Work paths**: where skills write inside the repo they are installed in — everything under `.jimmy/` (one namespaced dir, mirrors upstream `.sage/`): `.jimmy/work/<feature>/` (in-progress artifacts: brief, spec, plan, screenshots, `decisions.md` for that feature) · `.jimmy/docs/` (durable outputs: research briefs, audits, voice & tone) · `.jimmy/decisions.md` (global ADRs) · `.jimmy/adr/NNNN-slug.md` (numbered engineering ADRs) · `.jimmy/constitution.md` (project principles). _Avoid:_ `.sage/`, the target repo's `docs/`, tool-specific paths.

## Relationships
- The `routing` skill dispatches problems to skill chains (map: `docs/OPERATING-WORKFLOW.md`).
- `product-council` gates the full Tier 3 flow. Direct explicit red-team/pitch and consequential product/platform requests are council-only exceptions to the default Tier 1/Tier 2 bypass.
- Every self-authored skill carries a Failure statement and a HOW-TO-USE section; canonical upstream bodies stay close to upstream, minus Sage-runtime commands/paths (K5).

## Flagged ambiguities
- "done" — resolved: done means exit 0 (evidence attached), never "spec written" or "code merged".
- "test" (A/B) vs "test" (QA) — say "experiment" for A/B, "verification" for QA.
- "personalization" — reserved for systems choosing among hundreds of options per user; a screen with three options is not personalization.
