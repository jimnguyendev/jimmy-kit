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
  requirements-discovery mechanism, one complaint at a time.
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
