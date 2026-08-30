# Tracking QA & Acceptance Checklist

> **Goal:** 100% of product events comply with the type-safe data contract before release.

## 📋 1. 5W1H DATA INTEGRITY
- [ ] **WHO:** `user_id` present when signed in and `null` otherwise? `anonymous_id` persistent on device?
- [ ] **WHEN:** `timestamp` in ISO-8601 UTC?
- [ ] **WHAT:** event names `lowercase_snake_case`, exactly matching the event schema registry?
- [ ] **WHERE:** `device_type` and `screen_name` auto-populated?
- [ ] **WHY/HOW:** `trigger_source` and `experiment_variant` recording the live A/B variant?

## 🔒 2. PII AUDIT
- [ ] No `password` fields in any payload.
- [ ] No raw email/phone — hashed (e.g. SHA-256) before any third-party analytics.
- [ ] No card numbers or OTP codes logged.

## ⚡ 3. PERFORMANCE & FRICTION SIGNALS
- [ ] `ai_grading_completed` carries accurate `ai_latency_ms` and `tokens_consumed`?
- [ ] Rage-click detector fires on ≥3 clicks/second on dead buttons?
- [ ] `audio_silence_warning` fires after 10s of silent mic?
