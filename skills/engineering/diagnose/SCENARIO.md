# Scenario — diagnose

## 2026-10-07 verify-recipe reuse scenario (written BEFORE skill changes)

**Status:** [EXIT 2 — specified; independent application not yet recorded for this revision].

**Input:** "Renewals stopped extending access since yesterday's deploy." The repo has a `verify-subscriptions` skill whose feature map includes `store-renewal.md`.

**Expected:** Phase 1 builds the feedback loop from the matching Drive recipe (replay the captured renewal, read the row, the topic message and the entitlement) instead of inventing a new harness, and narrows to a failing test at the seam once the cause is localized. Without a verify skill, Phase 1 proceeds as before.
