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
2. **Index hygiene.** Run `python3 <skill dir>/scripts/check_feature_map.py <skill dir>/features` (copy the checker from `verify-app/scripts/` if the skill predates it); fix what it reports.
3. **Source pass.** For each feature file, a read-only reader explains from source how the feature works now, flags likely drift with file citations, and proposes one live recipe. Run readers in parallel up to a small bound (four is a sane default); without sub-agents, read serially. Readers never drive the app and never edit.
4. **Reconcile.** Every feature file has a summary. Merge recipes into as few app states as practical. Spot-check cited drift. Look at recent churn for user-facing surfaces missing from the map; call one missing only with a concrete source path.
5. **Live pass.** Drive the app even when the source pass found nothing; reading code does not prove a recipe still works. A single coordinator does all driving, in one browser it owns (its own CDP port and profile), using the launch model the verify skill itself describes (one long-lived instance, or a fresh session per drive). When the pass is delegated, that coordinator is the one verification subagent of SKILL.md section 5.
   - Trust no instance blindly: Doctor runs before the first drive, whenever a fresh session starts, and after any drive that failed. If the process looks healthy but the app is stuck in a bad state, reset it or relaunch rather than retrying on top of it.
   - Evidence is never collateral damage: after every cleanup, open the evidence location and confirm the files are still there.
   - Leave nothing running: whatever a failed or finished drive started is stopped before the next one, including on a shared instance (stop the leftovers, not the instance).
   - When Doctor fails because the verify skill is wrong (a renamed script, a moved port), that is drift: fix it within the edit scope, restart only what the fix affects, and retry once; a second failure makes the pass `blocked`.
   - Mark a feature "verified-unreachable" only by naming the missing prerequisite (an account, an entitlement, an OS, an external state) and the route you tried; if the map never mentioned that prerequisite, that omission is drift too.
6. **Triage.** Wrong or missing description → doc drift, fix. Working behavior the harness cannot drive → harness gap, fix and re-drive before shipping. Broken app behavior → product gap, report outside the change set.
7. **Ship or stop.** `changed`: one change set, every changed file re-read. `clean` or `blocked`: no change set; report coverage honestly.

Keep run notes (features covered, unreachable prerequisites, confirmed drift, outcome) under `.jimmy/work/verify-<app>/`, not in the skill.
