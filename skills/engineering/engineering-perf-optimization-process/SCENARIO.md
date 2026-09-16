# Scenario — engineering-perf-optimization-process

## 2026-09-16 refactor scenario (written BEFORE skill changes)

**Status:** [EXIT 2 — specified; independent application not yet recorded for this revision].

**Input 1:** Optimize this measured local CSV parser hot path; no network or production service is involved.

**Expected:** Gather relevant baseline/profile and compare results; do not require service dashboards, feature flags or circuit breakers.

**Input 2:** Two writers and multiple instances access the cached data.

**Expected:** Preserve ownership, staleness, engine and cross-instance evidence questions.

