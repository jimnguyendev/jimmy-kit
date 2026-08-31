<!-- Jimmy Kit eager dispatcher v1 — append this block to the TARGET repo's AGENTS.md
     (and let CLAUDE.md point at AGENTS.md). It is the always-on Layer 1 that the
     `routing` skill's Layers 2–3 assume. Single source: edit it HERE in the kit,
     then re-copy; do not fork per-repo. -->

## Jimmy Kit — route every request (always-on)

Before any substantial response: check whether a Jimmy Kit skill covers this.
If one does, read it and follow it. Keyword match first — deterministic:

| Request mentions | Go to |
|---|---|
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
+ confirmation format); the 10 problem-shape chains live in the kit's
`docs/OPERATING-WORKFLOW.md`.

Two standing rules on top of the map:
- **Gate:** before building or pitching anything new, run `product-council`; verdict ⚠/✗ means back to the problem, not forward to code.
- **Evidence:** no `[VERIFIED]` problem → no solution writing; label every claim `[VERIFIED]` / `[ASSUMPTION]` / `[GUESS]`; never invent numbers or baselines.
