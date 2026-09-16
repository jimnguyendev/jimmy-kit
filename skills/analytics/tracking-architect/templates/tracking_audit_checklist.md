# Tracking QA & Acceptance Checklist

> **Goal:** Events in the agreed scope conform to the existing registry and validation stack. Adapt the example fields and thresholds below to that contract.
> Record each check as PASS, FAIL, or UNVERIFIABLE with evidence and window; an unavailable metric is never zero. Schema conformance does not prove end-to-end delivery.

## 📋 1. 5W1H DATA INTEGRITY
- [ ] **WHO:** `user_id` present when signed in and `null` otherwise? `anonymous_id` persistent on device?
- [ ] **WHEN:** `timestamp` in ISO-8601 UTC?
- [ ] **WHAT:** event names exactly match the existing registry convention (snake_case is only an example)?
- [ ] Versioning and compatibility follow the registry policy (for example an existing `schema_version` field or versioned envelope)?
- [ ] **WHERE:** `device_type` and `screen_name` auto-populated?
- [ ] **WHY/HOW:** `trigger_source` and `experiment_variant` recording the live A/B variant?

## 🔒 2. PII AUDIT
- [ ] No `password` fields in any payload.
- [ ] Identity fields follow the project’s approved pseudonymous identity policy; hashes are not assumed anonymous.
- [ ] No card numbers or OTP codes logged.

## ⚡ 3. PERFORMANCE & FRICTION SIGNALS
- [ ] `ai_grading_completed` carries accurate `ai_latency_ms` and `tokens_consumed`?
- [ ] Rage-click detector follows the validated product rule (illustrative threshold: ≥3 clicks/second)?
- [ ] `audio_silence_warning` follows the validated product rule (illustrative threshold: 10s of silence)?
