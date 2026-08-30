---
name: tracking-architect
description: 5W1H Event Taxonomy, Type-Safe Data Contracts & Funnel Analytics skill. Use when designing event tracking plans, defining Zod schemas for analytics events, auditing tracking quality, instrumenting friction/rage-click detection, or writing SQL queries for conversion funnels and drop-off analysis.
---

# công ty Tracking Architect: 5W1H Type-Safe Event Taxonomy & Data Contracts

> **This skill exists to stop:** designing new events without checking the existing contract — spawning a third naming convention and fragmenting data (a failure that actually happened; see rationalization T5).

> 📁 **Source convention:** `[sage]` = upstream Sage repo (github.com/xoai/sage); `[docs]` = your internal docs repo (optional deep-dives — adjust paths to your setup). Sources are for deeper reading: if a file is missing, the skill still runs on the rules inlined here. The ONLY exception: a step marked **MUST READ** — if that file is missing, STOP and ask the user instead of improvising.

## 🤖 0. HOW TO USE (agent workflow)
**A. Add a new event:** MUST READ the event registry + tracking contract first — extend the existing taxonomy, never invent a new naming scheme. Every event carries 5W1H + `schema_version`.
**B. Audit tracking:** reconcile emitted events against the registry; report status against the runtime verification gates ("spec'd" ≠ "verified"). Output: item → status → missing gate.
**C. Funnel SQL:** production only; exclude QA/bot traffic and unsupported schema versions.
**MUST:** every tracking claim declares its verification status; an absent metric is absent, never zero.
---

## 🏛️ 1. Core Architecture: The 5W1H Universal Data Contract

Every analytics event emitted from Web, Mobile, or Backend **MUST** adhere to the strict 5W1H structural contract:

```mermaid
graph LR
    WHO["<b>WHO (Identity & Segment)</b><br/>• user_id (null if anonymous)<br/>• anonymous_id (UUID persistent)<br/>• learner_segment (Trial, Paid, Churned)<br/>• target_band (e.g. '6.5', '7.5')"]
    WHEN["<b>WHEN (Temporal Context)</b><br/>• timestamp (ISO 8601 UTC)<br/>• session_id (UUID)<br/>• day_in_journey (Day 1..30)"]
    WHAT["<b>WHAT (Event & Typed Payload)</b><br/>• event_name (lowercase_snake_case)<br/>• event_category (funnel, lab, ai, friction)<br/>• properties (Strict Zod Schema)"]
    WHERE["<b>WHERE (Spatial & Device Context)</b><br/>• device_type (desktop_web, mobile_ios...)<br/>• screen_name / skill_tab<br/>• component_id"]
    WHY["<b>WHY & HOW (Trigger & Variant)</b><br/>• trigger_source (Direct, Push, Streak)<br/>• experiment_variant (A/B Test ID)"]

    WHO --- WHEN --- WHAT --- WHERE --- WHY
```

### Golden Engineering Invariants

1. **Zero Untyped Logs:** No arbitrary `track('click', { foo: 'bar' })`. Every event must have an explicit TypeScript Zod schema.
2. **Server Verification for Macro-Conversions:** `purchase_completed` and `test_submitted` must be emitted or verified server-side. Client never directly declares a purchase complete.
3. **No PII in Tracking Payloads:** Raw passwords, plain credit cards, or unhashed personal phone numbers are strictly prohibited. Use SHA-256 for user identifiers when needed.

---

## 📋 2. Full Event Taxonomy Matrix (5 Core Categories)

```mermaid
graph TD
    subgraph TAXONOMY["5 CORE EVENT CATEGORIES (PREP PRACTICE LAB)"]
        C1["<b>1. FUNNEL (P0 Conversion):</b><br/>landing_viewed, hero_cta_clicked, price_comparison_hover, demo_error_clicked, diagnostic_lead_saved"]
        C2["<b>2. LAB CORE (Room Interaction):</b><br/>lab_test_started, mic_permission_resolved, speaking_recording_started, speaking_recording_completed, test_submitted"]
        C3["<b>3. AI FEEDBACK (Latency & Quality):</b><br/>ai_grading_requested, ai_stream_first_chunk (TTFB), ai_grading_completed, error_diagnostic_expanded, retake_question_clicked"]
        C4["<b>4. FRICTION (UX Health):</b><br/>rage_click_detected, audio_silence_warning, ai_grading_timeout_error, test_abandoned_midway"]
        C5["<b>5. RETENTION (Habit & Monetization):</b><br/>streak_incremented, streak_freeze_used, reverse_trial_countdown_seen, subscription_checkout_started"]
    end
```

---

## 🛠️ 3. Type-Safe Client Helper Implementation Pattern

```typescript
import { z } from "zod";
import { BaseEventSchema, EventSchemas } from "./tracking-schema";

export function trackEvent<K extends keyof typeof EventSchemas>(
  eventName: K,
  payload: z.infer<(typeof EventSchemas)[K]>,
) {
  const validation = EventSchemas[eventName].safeParse(payload);
  if (!validation.success) {
    console.error(
      `[Tracking Validation Error] Event '${eventName}' invalid:`,
      validation.error.format(),
    );
    if (process.env.NODE_ENV === "development") {
      throw new Error(`Invalid tracking payload for ${eventName}`);
    }
    return;
  }

  // Dispatch validated event to Analytics Pipeline (Segment / Mixpanel / Internal DB)
  window.analytics?.track(eventName, validation.data);
}
```

---

## 📊 4. Standard Funnel Conversion SQL (`funnel_dropoff_analysis.sql`)

Calculates step-by-step conversion and identifies the biggest drop-off choke points:

$$\text{Step Conversion Rate} = \frac{\text{Users completing Step } N}{\text{Users completing Step } N-1} \times 100\%$$

---

## 🛠️ 5. Scripts & Templates Included in this Skill

1. [`templates/tracking-schema.ts`](file:///Users/admin/workspaces/prep-fe/practice-labs/.claude/skills/tracking-architect/templates/tracking-schema.ts): Production TypeScript Zod Schemas for all 5 event categories.
2. [`scripts/funnel_dropoff_analysis.sql`](file:///Users/admin/workspaces/prep-fe/practice-labs/.claude/skills/tracking-architect/scripts/funnel_dropoff_analysis.sql): SQL query to compute step-by-step conversion and drop-off rates.
3. [`templates/tracking_audit_checklist.md`](file:///Users/admin/workspaces/prep-fe/practice-labs/.claude/skills/tracking-architect/templates/tracking_audit_checklist.md): Pre-release tracking QA checklist.
