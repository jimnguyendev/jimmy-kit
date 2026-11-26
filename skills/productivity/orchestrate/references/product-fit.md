# Product fit before the first plan

Read before the first technical plan of a product area, and whenever a model concept (tenant,
app, market, language, channel) is about to be decided. Advisor rounds and gates prove technical
correctness, never that the right thing is being built.

Origin: a replacement of a third-party product was built from the team's own spec and patterns
borrowed from other repos. It was never anchored to an inventory of how the company uses the
old product. Markets, a channel, role names, per-environment provider config, multi-language and
multi-app each surfaced as the owner's reaction to a screen, and dev had no real content, so empty
and broken screens stayed hidden until an audit.

## Usage inventory

- WHEN a product area starts or is extended · CHECK a usage inventory of the system being replaced
  or used exists first: apps/products that use it, accounts, channels, every live object type
  (campaigns, journeys, reports, ...) with its volume · BECAUSE the owner must not be the
  requirements-discovery mechanism, one complaint at a time. When the old system or a copied tool
  has source, the parity rows come from a [reference inventory](#reference-inventory), which a lint checks.
- WHEN the inventory exists · CHECK it is mapped into a **parity table**, one row per old screen or
  flow: `old screen/flow | volume in use | new screen | status (planned / landed / dropped + reason)`.
  Every row is a screen in the plan or an explicit drop · BECAUSE a gap found later is a rework.
- WHEN a model concept is decided (tenant, app, market, language, channel) · CHECK ask "how many of
  these does the company have now and next year?" across the whole company, not only the first
  caller; record the answer in the plan · BECAUSE a concept sized to the only caller makes the next
  caller a redesign.
- Read the inventory from the system itself (read-only API or export), not from memory. A fact
  the owner already confirmed is not asked again.

Owner questions that remain after the inventory are real product choices; ask them as decision
briefs (skill `ketchup`).

The parity table feeds packet scoping and the UI done-ness check in
[verification.md](verification.md#done-means-walked-as-a-user).

## Reference inventory

When a plan claims parity with a reference product (an open-source tool the team copies, or the
product being replaced), scope is fixed from an inventory file before the plan is packetized.

Origin: a messaging workflow builder was compared with two reference builders in a 16-row table at
node-kind level. The root judged seven rows "covered", "not built" or "not applicable" by itself,
from recon summaries and memory. Nobody listed the references' triggers, operations and options from
their source, so each gap surfaced only when the owner asked "does it have X?". Tests, the wave audit
and the walks then looked only at what was built.

### How it is read

- Read from the reference's source clone at a named commit, option by option: triggers, operations,
  parameters, options, outputs, limits. Never from memory, docs prose or an agent's summary.
- "A developer can do it through another API" is `MISSING` or `PARTIAL`, never `HAVE`.
- The agent that writes the inventory records what exists; it does not judge need. Need is the
  decision column, and cuts are the owner's.
- One file per area, under `.orchestrate/recon/` or `.jimmy/work/<feature>/`. List each file on an
  `inventory: <path>` line in SPRINT.md.

### File format

```markdown
reference: builder-a @ 3f2a9c1
reference: builder-b @ 8be41d0

| id | reference feature | ref | ours | status | decision |
|---|---|---|---|---|---|
| T1 | Webhook trigger with a secret header check | builder-a:nodes/webhook/trigger.ts | webhook trigger | HAVE | |
| T2 | Schedule trigger with a cron expression and time zone | builder-a:nodes/schedule/node.ts:40 | daily schedule, no cron | PARTIAL | build 214 |
| O1 | Send email with CC and reply-to | builder-b:actions/email.go:88 | | MISSING | propose-later — no team sends with CC today; needs a template field |
| O2 | HTTP request with response pagination | builder-a:nodes/http/paginate.ts | | MISSING | drop — owner 26/11: "journeys never page third-party responses" |
| O3 | Wait until a date field of the user | builder-b:steps/wait.go:120 | | MISSING | propose-drop — every live wait is a fixed delay |
| X1 | Self-hosted runner pool | builder-a:runner/pool.ts | | N/A | n/a — one managed worker pool, no customer runners |
```

- `reference: <name> @ <commit>`: one line per reference, outside the table. `<name>` is a key of
  `references` in `.claude/orchestrator.json` whose clone path exists, which also makes
  `REFERENCE_CITED` live for that reference.
- Tables: one or more, each with at least the columns `id`, `status` and `decision`; `reference
  feature`, `ref` and `ours` as above. Extra columns are allowed, order is free, headers match by
  name, case-insensitive. Rows are table lines right after the header separator.
- `id`: unique in the file; a packet cites it.
- `status`: exactly `HAVE`, `PARTIAL`, `MISSING` or `N/A`. `HAVE` needs a non-empty `ours`.
- `decision`, for `PARTIAL` and `MISSING`, one of:
  - `build <packet id>` (the id contains a digit): a packet builds it;
  - `drop — owner <date>: "<quote>"` or `later — owner <date>: "<quote>"`: the owner's words;
  - `propose-drop — <reason>` or `propose-later — <reason>` (10+ letters): the root's proposal,
    waiting on the owner.
- `decision` for `N/A`: `n/a — <reason>` (10+ letters). `HAVE` rows need none.
- Dates: `DD/MM`, `DD/MM/YYYY` or `YYYY-MM-DD`. Separators: `—`, `–`, `-` or `:`. Quotes:
  `"…"` or `“…”`. Cells may be wrapped in backticks. Fenced code and HTML comments are ignored.

A root never writes `drop` or `later` without the owner's dated words. A standing "decide, don't
ask" rule covers technical choices, not dropping a reference feature. Until the owner answers, the
row stays `propose-*`: it is printed on the strike list of every report and named in HANDOFF.

### What checks it

- `orchestration_lint.py --phase scope --inventory <file> [<file> …]` checks each file and prints
  counts per status, counts per decision kind, and the **strike list**: every `propose-*` row as
  `<id> · <reference feature> · <reason>`, under "propose drop" and "propose later". It exits 1 on
  `SCOPE_INVENTORY`, `SCOPE_UNDECIDED` or `SCOPE_ROOT_DROP`; `propose-*` rows pass. A plan is not
  packetized while it fails. Paste the strike list into the owner's report as one brief: "which of
  these rows do we drop?"
- A packet's `scope: <inventory>#<id>[, <id>…]` line makes phases `review` and `dispatch` run the
  same checks on that file, and fail when a cited id is missing or its decision is not `build …`.
- `--phase handoff` fails `SCOPE_PENDING_OWNER` while an inventory listed in SPRINT.md has
  `propose-*` rows and `Waiting on owner` does not name the file.
- The unit-end walk follows the inventory's `build` rows
  ([verification.md](verification.md#done-means-walked-as-a-user)).
