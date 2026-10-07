# Scenario — engineering-perf-optimization-process

## 2026-09-16 refactor scenario (written BEFORE skill changes)

**Status:** [EXIT 2 — specified; independent application not yet recorded for this revision].

**Input 1:** Optimize this measured local CSV parser hot path; no network or production service is involved.

**Expected:** Gather relevant baseline/profile and compare results; do not require service dashboards, feature flags or circuit breakers.

**Input 2:** Two writers and multiple instances access the cached data.

**Expected:** Preserve ownership, staleness, engine and cross-instance evidence questions.

## 2026-10-07 iterative loop scenario (written BEFORE skill changes)

**Status:** [EXIT 2 — specified; independent application not yet recorded for this revision].

**Input 3:** p95 of the renewal webhook handler is 140 ms; the target is under 80 ms. Improve it over several attempts.

**Expected:** Proves the harness separates a slow case from an easy one, then freezes it; the harness prints errors and work completed alongside latency; each attempt changes one thing, is measured as a median over enough samples to clear noise, keeps the regression gate green, and is kept or reverted with a decision-log row either way; stops once the target is confirmed, the budget is spent, or a plateau is justified, and does not keep changing code after the target holds.
