<!-- Jimmy Kit eager dispatcher v1 — append this block to the TARGET repo's AGENTS.md
     (and let CLAUDE.md point at AGENTS.md). It is the always-on Layer 1 that the
     `routing` skill's Layers 2–3 assume. Single source: edit it HERE in the kit,
     then re-copy; do not fork per-repo. -->

## Jimmy Kit — route every request (always-on)

For a substantial task, use a Jimmy Kit skill when its specific guidance improves the work.
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
| review / audit / evaluate an existing UI for usability | `ux-review` — conversion, pricing or landing page → `ux-cro-audit` |
| review / audit a document, plan, code, or non-UI artifact | `independent-review` |
| OKR / quarterly goals / key results | `okr-outcome-architect` |
| red-team / debate / council / "what will leadership ask" | `product-council` |
| tracking / event / instrument / funnel numbers | `tracking-architect` |
| retention / churn / segments / DAU | `growth-markov-duolingo` → `engagement-matrix-analytics` → `advanced-rfm-segmentation` |
| retro / lessons / post-mortem / A/B ended | `retrospective` → `decision-log` |
| stuck after 3+ attempts / complexity spiraling | `problem-solving` |
| prove it works in the real app · agent keeps asking a human to run/click/paste · make this repo verifiable by agents · verify skill is stale | `verify-app` |
| Go code / Go tests / Go review / go.mod / golangci-lint | `tdd-go` for new behavior, else the matching `backend-go-*` skill (`golang` group) |
| MySQL / PostgreSQL / MongoDB / ClickHouse schema, index, slow query, connection pool | the matching `database` group skill (`mysql`, `postgres`, `mongodb-*`, `clickhouse-*`); Go data-access code → `backend-go-database` |
| tests pass but QA / real DB / real UI fails · acceptance criteria for a packet touching SQL, config, or response shape · "integration green" · regression replay suite | `reality-gate` |

One clear match → announce and proceed. Several compatible matches → choose the smallest sufficient set. Ask only when materially different outcomes remain unresolved.
None, or the request is ambiguous → load the `routing` skill (classifier fallback
+ confirmation format); the problem-shape chains live in the kit's
`docs/OPERATING-WORKFLOW.md`.

Standing rules on top of the map:
- **Gate:** run `product-council` as part of the full Tier 3 flow. By default, Tier 1 and already-approved Tier 2 bypass council. Explicit red-team/pitch requests and consequential product/platform decisions are exceptions: they invoke council directly but do not expand the rest of the workflow unless the work is Tier 3. Verdict ⚠/✗ means back to the problem, not forward to code.
- **Authority:** accepted scope, context, and authorization carry through skill handoffs. Continue authorized work through relevant verification and fixes. Ask only for an unresolved material decision, expanded scope, or an external action not already authorized. This dosage rule takes precedence over generic workflow recipes.
- **Constitution:** apply relevant engineering principles — test changed behavior, no silent failures, secrets never in code, dependencies explicit, changes reversible. Installing skills does not install hooks or CI enforcement.
- **Evidence:** distinguish verified facts from assumptions where they affect a decision; never invent numbers or baselines. Missing evidence blocks only the conclusion or action that depends on it; useful drafts and investigation may proceed with explicit limits.
