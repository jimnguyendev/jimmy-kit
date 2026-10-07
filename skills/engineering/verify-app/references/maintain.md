# Maintain mode

A feature map drifts as soon as the app changes. This pass keeps a `verify-<app>` skill honest. The unit of rigor is the feature: every feature file gets read against source and driven live; not every sentence needs its own command.

## Outcome

End with exactly one, and say which:

- **clean** — every feature had source and live coverage; nothing to change.
- **changed** — one change set with proven corrections to the verify skill.
- **blocked** — coverage could not finish or a fix could not be proven; name what blocked it.

## Edit scope

Edit only the verify skill's own directory: its SKILL.md, `features/`, and the helpers it owns. Never edit product code here. A described behavior the app no longer has is either doc drift (fix the map) or a product regression (report it; do not rewrite the map to match a bug).

## Pass

1. **Locate the target.** The project-local skill with Launch/Drive sections and a `features/` map. Several candidates: ask which. None: switch to Create mode.
2. **Index hygiene.** Run `scripts/check_feature_map.py <skill dir>/features`; fix missing, extra or dead index entries.
3. **Source pass.** For each feature file, a read-only reader explains from source how the feature works now, flags likely drift with file citations, and proposes one live recipe. Run readers in parallel up to a small bound (four is a sane default); without sub-agents, read serially. Readers never drive the app and never edit.
4. **Reconcile.** Every feature file has a summary. Merge recipes into as few app states as practical. Spot-check cited drift. Look at recent churn for user-facing surfaces missing from the map; call one missing only with a concrete source path.
5. **Live pass.** Required even when source looks clean. One coordinator drives, following the skill's own launch model. Hold three rules throughout: run Doctor before the first drive, on each fresh session, and after any failed drive (reset or relaunch when Doctor cannot see the problem); evidence survives every cleanup and is checked at its location; nothing a drive started outlives its use. A Doctor failure caused by the skill itself is drift: fix it in scope, restart only what the fix invalidated, retry once, then call the pass blocked. A feature is "verified-unreachable" only with the missing prerequisite and the route attempted.
6. **Triage.** Wrong or missing description → doc drift, fix. Working behavior the harness cannot drive → harness gap, fix and re-drive before shipping. Broken app behavior → product gap, report outside the change set.
7. **Ship or stop.** `changed`: one change set, every changed file re-read. `clean` or `blocked`: no change set; report coverage honestly.

Keep run notes (features covered, unreachable prerequisites, confirmed drift, outcome) under `.jimmy/work/verify-<app>/`, not in the skill.
