/**
 * Generic Practice Lab: Type-Safe 5W1H Analytics Event Schemas
 * Standard: TypeScript + Zod v3
 */

import { z } from "zod";

// Base 5W1H Envelope Schema
export const BaseEventSchema = z.object({
  // WHO
  user_id: z.string().uuid().nullable(),
  anonymous_id: z.string().uuid(),
  learner_segment: z.enum([
    "anonymous_visitor",
    "reverse_trial",
    "paid_vip",
    "expired_free",
    "churned",
  ]),
  target_band: z.enum(["5.0", "5.5", "6.0", "6.5", "7.0", "7.5", "8.0+"]).optional(),

  // WHEN
  timestamp: z.string().datetime(),
  session_id: z.string().uuid(),

  // WHERE
  device_type: z.enum(["desktop_web", "mobile_ios", "mobile_android", "mobile_web", "tablet"]),
  app_version: z.string(),
  screen_name: z.string(),

  // WHY & HOW
  trigger_source: z.enum([
    "direct",
    "push_notification",
    "streak_reminder",
    "email_campaign",
    "organic_search",
    "paid_ad",
  ]),
  experiment_variant: z.string().optional(),
});

// Category 1: Funnel & Conversion Events
export const LandingViewedSchema = BaseEventSchema.extend({
  event_name: z.literal("landing_viewed"),
  utm_source: z.string().optional(),
  utm_campaign: z.string().optional(),
  h1_variant_id: z.string(),
});

export const HeroCtaClickedSchema = BaseEventSchema.extend({
  event_name: z.literal("hero_cta_clicked"),
  button_text: z.string(),
  placement: z.literal("hero"),
});

export const DiagnosticLeadSavedSchema = BaseEventSchema.extend({
  event_name: z.literal("diagnostic_lead_saved"),
  lead_email_hash: z.string().length(64), // SHA-256 hash (no plain PII)
  weak_skill: z.enum(["speaking", "writing", "reading", "listening"]),
  predicted_band: z.number().min(0).max(9),
});

// Category 2: Lab Core Interactions
export const LabTestStartedSchema = BaseEventSchema.extend({
  event_name: z.literal("lab_test_started"),
  skill_type: z.enum([
    "speaking_part1",
    "speaking_part2",
    "speaking_part3",
    "writing_task1",
    "writing_task2",
  ]),
  test_id: z.string(),
  is_retry: z.boolean(),
});

export const SpeakingRecordingCompletedSchema = BaseEventSchema.extend({
  event_name: z.literal("speaking_recording_completed"),
  test_id: z.string(),
  question_id: z.string(),
  duration_seconds: z.number().positive(),
  audio_file_size_kb: z.number().positive(),
});

// Category 3: AI Feedback & Scoring
export const AiGradingCompletedSchema = BaseEventSchema.extend({
  event_name: z.literal("ai_grading_completed"),
  test_id: z.string(),
  skill_type: z.string(),
  ai_latency_ms: z.number().positive(),
  overall_band_score: z.number().min(0).max(9),
  top_3_error_codes: z.array(z.string()).length(3),
  tokens_consumed: z.number().int().positive(),
});

export const RetakeQuestionClickedSchema = BaseEventSchema.extend({
  event_name: z.literal("retake_question_clicked"),
  test_id: z.string(),
  question_id: z.string(),
  previous_score: z.number().min(0).max(9),
});

// Category 4: Friction & UX Health
export const RageClickDetectedSchema = BaseEventSchema.extend({
  event_name: z.literal("rage_click_detected"),
  element_id: z.string(),
  click_count: z.number().min(3),
  time_window_ms: z.number(),
});

export const TestAbandonedMidwaySchema = BaseEventSchema.extend({
  event_name: z.literal("test_abandoned_midway"),
  test_id: z.string(),
  question_index: z.number().int().nonnegative(),
  time_spent_seconds: z.number().positive(),
  abandon_reason: z
    .enum(["user_closed_tab", "network_disconnect", "mic_error", "timeout"])
    .optional(),
});

// Category 5: Retention & Monetization
export const StreakIncrementedSchema = BaseEventSchema.extend({
  event_name: z.literal("streak_incremented"),
  streak_count: z.number().int().positive(),
  longest_streak: z.number().int().positive(),
});

// Registry of All Event Schemas
export const EventSchemas = {
  landing_viewed: LandingViewedSchema,
  hero_cta_clicked: HeroCtaClickedSchema,
  diagnostic_lead_saved: DiagnosticLeadSavedSchema,
  lab_test_started: LabTestStartedSchema,
  speaking_recording_completed: SpeakingRecordingCompletedSchema,
  ai_grading_completed: AiGradingCompletedSchema,
  retake_question_clicked: RetakeQuestionClickedSchema,
  rage_click_detected: RageClickDetectedSchema,
  test_abandoned_midway: TestAbandonedMidwaySchema,
  streak_incremented: StreakIncrementedSchema,
} as const;
