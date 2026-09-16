# Feature Portfolio Report (Engagement Matrix)

> **Worked example only:** All counts, rates, thresholds, and actions below are illustrative assumptions. Replace with sourced measurements and locally justified decisions. Leave unavailable values explicitly unknown; do not report these examples as observed results.


> **Product:** [e.g. an AI practice-test product] · **Window (30 days):** [DD/MM → DD/MM]
> **MAU:** [20,000] · **Features scored:** [8] · **Median split:** B̃ = [41.5%] breadth | F̃ = [3.74] frequency

## 1. FOUR-QUADRANT SNAPSHOT
- **Top-right (Core):** e.g. AI speaking grading (78% MAU, 6.0x) · per-sentence pronunciation (71%, 8.5x) → verify customer value and agreed reliability budget.
- **Top-left (Power/Niche):** deep grammar-error analysis (21%, 9.1x) · band-8 sample audio (25.5%, 8.0x) → investigate relevance beyond existing users before an adoption test.
- **Bottom-right (Utility):** weekend full mock test (64%, 1.3x) · monthly report (57.5%, 1.0x) → keep stable.
- **Bottom-left (Ghost):** 4-level topic filter (4.3%, 1.4x) · handwriting notes (2.1%, 1.5x) → inspect cadence, customer evidence, telemetry, and dependencies.

## 2. PORTFOLIO DETAIL & ACTIONS

| Feature | Quadrant | Breadth (%MAU) | Freq (/user) | Tech status | Candidate investigation / action |
| :-- | :-: | :-: | :-: | :-: | :-- |
| `ai_speaking_grading` | **CORE** | 78.0% | 6.03 | latency 18s | Measure streaming TTFB against the product budget |
| `pronunciation_repeat` | **CORE** | 71.0% | 8.45 | stable | Optimize mobile audio cache |
| `grammar_error_deepdive` | **NICHE** | 21.0% | 9.05 | good | Test discovery after a score if customer evidence supports it |
| `sample_band8_audio` | **NICHE** | 25.5% | 8.04 | good | Surface inside diagnostic results |
| `full_mock_test_weekend` | **UTILITY** | 64.0% | 1.29 | stable | Keep weekend schedule |
| `monthly_report_view` | **UTILITY** | 57.5% | 1.04 | stable | Auto-email on the 1st |
| `topic_filter_4level` | 🔴 **GHOST** | 4.25% | 1.41 | redundant | Check whether the filter serves important rare jobs |
| `handwritten_notes` | 🔴 **GHOST** | 2.10% | 1.45 | tech debt | Assess dependent workflows and customer impact before proposing removal |

## 3. RETENTION COHORT / SMILE-CURVE AUDIT
- Baseline D30 retention: **[32.4%]** (flattening).
- Observed association to measure (not causal effect): users touching deep grammar analysis in week 1 hit **[58.2%] D30 (+25.8pp)**.
- Return-cycle hypothesis to validate: a "remaining-errors diagnosis, 2 weeks before exam day" cycle to pull users back at D60–D90.
