# Feature Portfolio Report (Engagement Matrix)

> **Product:** [e.g. an AI practice-test product] · **Window (30 days):** [DD/MM → DD/MM]
> **MAU:** [20,000] · **Features scored:** [8] · **Median split:** B̃ = [41.5%] breadth | F̃ = [3.74] frequency

## 1. FOUR-QUADRANT SNAPSHOT
- **Top-right (Core):** e.g. AI speaking grading (78% MAU, 6.0x) · per-sentence pronunciation (71%, 8.5x) → protect absolutely; latency budget enforced.
- **Top-left (Power/Niche):** deep grammar-error analysis (21%, 9.1x) · band-8 sample audio (25.5%, 8.0x) → inject into onboarding to widen.
- **Bottom-right (Utility):** weekend full mock test (64%, 1.3x) · monthly report (57.5%, 1.0x) → keep stable.
- **Bottom-left (Ghost):** 4-level topic filter (4.3%, 1.4x) · handwriting notes (2.1%, 1.5x) → 60-day kill deadline.

## 2. PORTFOLIO DETAIL & ACTIONS

| Feature | Quadrant | Breadth (%MAU) | Freq (/user) | Tech status | Action |
| :-- | :-: | :-: | :-: | :-: | :-- |
| `ai_speaking_grading` | **CORE** | 78.0% | 6.03 | latency 18s | Optimize streaming TTFB; UX flow frozen |
| `pronunciation_repeat` | **CORE** | 71.0% | 8.45 | stable | Optimize mobile audio cache |
| `grammar_error_deepdive` | **NICHE** | 21.0% | 9.05 | good | **Growth lever:** suggest right after a score lands |
| `sample_band8_audio` | **NICHE** | 25.5% | 8.04 | good | Surface inside diagnostic results |
| `full_mock_test_weekend` | **UTILITY** | 64.0% | 1.29 | stable | Keep weekend schedule |
| `monthly_report_view` | **UTILITY** | 57.5% | 1.04 | stable | Auto-email on the 1st |
| `topic_filter_4level` | 🔴 **GHOST** | 4.25% | 1.41 | redundant | Hide 2 levels; no lift in 30 days → remove |
| `handwritten_notes` | 🔴 **GHOST** | 2.10% | 1.45 | tech debt | **Deprecate**; delete next sprint (−45KB bundle) |

## 3. RETENTION COHORT / SMILE-CURVE AUDIT
- Baseline D30 retention: **[32.4%]** (flattening).
- Niche-feature effect: users touching deep grammar analysis in week 1 hit **[58.2%] D30 (+25.8pp)**.
- Smile-curve play: a "remaining-errors diagnosis, 2 weeks before exam day" cycle to pull users back at D60–D90.
