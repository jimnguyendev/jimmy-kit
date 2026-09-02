<!-- Jimmy Kit eager dispatcher v1 — append this block to the TARGET repo's AGENTS.md
     (and let CLAUDE.md point at AGENTS.md). It is the always-on Layer 1 that the
     `routing` skill's Layers 2–3 assume. Single source: edit it HERE in the kit,
     then re-copy; do not fork per-repo. -->

## Jimmy Kit — route every request (always-on)

Before any substantial response: check whether a Jimmy Kit skill covers this.
Choose by the current problem state before topic keywords. An implementation verb does not prove the problem, contract, or boundary is accepted. Then use the deterministic map:

Dose the workflow before following the map:
- **Tier 1:** act directly or use one short skill; no menu or council.
- **Tier 2:** announce and proceed with one or two relevant skills; stop when the decision is resolved.
- **Tier 3:** run the full intake and council gate.

| Request mentions | Go to |
|---|---|
| proposed solution is named but stakeholder / actual state / expected state / evidence is unclear | `engineering-design-thinking` → Problem Frame |
| build / implement / create / add / ship / feature | `change-tiers` → (spec? if none: `prd`) → engineering skills → `quality-gates` |
| fix / bug / error / crash / failing / debug | `diagnose` |
| architect / redesign / migrate / rewrite / "which technology" | `architect` → `decision-log` |
| understand / research / interview / user needs / jobs | `jtbd` (+ `ux-discovery`) |
| design / wireframe / brief / PRD / prototype / mockup | `ux-brief` / `prd` / `prototype` |
| audit / evaluate / usability / UX review | `ux-review` — conversion, pricing or landing page → `ux-cro-audit` |
| OKR / quarterly goals / key results | `okr-outcome-architect` |
| red-team / debate / council / "what will leadership ask" | `product-council` |
| tracking / event / instrument / funnel numbers | `tracking-architect` |
| retention / churn / segments / DAU | `growth-markov-duolingo` → `engagement-matrix-analytics` → `advanced-rfm-segmentation` |
| retro / lessons / post-mortem / A/B ended | `retrospective` → `decision-log` |
| stuck after 3+ attempts / complexity spiraling | `problem-solving` |

One match → announce it and go. Several → present them as options.
None, or the request is ambiguous → load the `routing` skill (classifier fallback
+ confirmation format); the problem-shape chains live in the kit's
`docs/OPERATING-WORKFLOW.md`.

Two standing rules on top of the map:
- **Gate:** run `product-council` as part of the full Tier 3 flow. By default, Tier 1 and already-approved Tier 2 bypass council. Explicit red-team/pitch requests and consequential product/platform decisions are exceptions: they invoke council directly but do not expand the rest of the workflow unless the work is Tier 3. Verdict ⚠/✗ means back to the problem, not forward to code.
- **Constitution:** the five base principles in the `constitution` skill bind every change — tests before code, no silent failures, secrets never in code, dependencies explicit and pinned, changes reversible.
- **Evidence:** no `[VERIFIED]` problem → no solution writing; label every claim `[VERIFIED]` / `[ASSUMPTION]` / `[GUESS]`; never invent numbers or baselines.
