-- ============================================================================
-- Generic Practice Lab: Step-by-Step Funnel Drop-off Analysis Query
-- Dialect: Standard ANSI SQL / PostgreSQL / DuckDB / BigQuery
-- ============================================================================

WITH evaluation_window AS (
  SELECT 
    CURRENT_DATE - INTERVAL '14 days' AS start_time,
    CURRENT_DATE AS end_time
),
user_funnel_steps AS (
  SELECT 
    anonymous_id,
    device_type,
    experiment_variant,
    -- Step 1: Landing Page Viewed
    MIN(CASE WHEN event_name = 'landing_viewed' THEN event_timestamp END) AS t_landing,
    -- Step 2: Hero CTA Clicked
    MIN(CASE WHEN event_name = 'hero_cta_clicked' THEN event_timestamp END) AS t_cta,
    -- Step 3: Test Started
    MIN(CASE WHEN event_name = 'lab_test_started' THEN event_timestamp END) AS t_test_start,
    -- Step 4: Test Submitted & AI Graded
    MIN(CASE WHEN event_name = 'ai_grading_completed' THEN event_timestamp END) AS t_graded,
    -- Step 5: Diagnostic Lead Saved
    MIN(CASE WHEN event_name = 'diagnostic_lead_saved' THEN event_timestamp END) AS t_lead_saved,
    -- Step 6: Subscription Converted
    MIN(CASE WHEN event_name = 'subscription_checkout_started' THEN event_timestamp END) AS t_paid
  FROM user_activity_events
  CROSS JOIN evaluation_window w
  WHERE event_timestamp >= w.start_time AND event_timestamp < w.end_time
  GROUP BY anonymous_id, device_type, experiment_variant
),
funnel_aggregates AS (
  SELECT 
    device_type,
    COUNT(DISTINCT CASE WHEN t_landing IS NOT NULL THEN anonymous_id END) AS step1_landing,
    COUNT(DISTINCT CASE WHEN t_cta IS NOT NULL AND t_cta >= t_landing THEN anonymous_id END) AS step2_cta,
    COUNT(DISTINCT CASE WHEN t_test_start IS NOT NULL AND t_test_start >= t_cta THEN anonymous_id END) AS step3_test_started,
    COUNT(DISTINCT CASE WHEN t_graded IS NOT NULL AND t_graded >= t_test_start THEN anonymous_id END) AS step4_test_completed,
    COUNT(DISTINCT CASE WHEN t_lead_saved IS NOT NULL AND t_lead_saved >= t_graded THEN anonymous_id END) AS step5_lead_saved,
    COUNT(DISTINCT CASE WHEN t_paid IS NOT NULL AND t_paid >= t_lead_saved THEN anonymous_id END) AS step6_subscribed
  FROM user_funnel_steps
  GROUP BY device_type
)
SELECT 
  device_type,
  step1_landing,
  step2_cta,
  ROUND(step2_cta * 100.0 / NULLIF(step1_landing, 0), 2) AS conv_1_to_2_pct,
  step3_test_started,
  ROUND(step3_test_started * 100.0 / NULLIF(step2_cta, 0), 2) AS conv_2_to_3_pct,
  step4_test_completed,
  ROUND(step4_test_completed * 100.0 / NULLIF(step3_test_started, 0), 2) AS conv_3_to_4_pct,
  step5_lead_saved,
  ROUND(step5_lead_saved * 100.0 / NULLIF(step4_test_completed, 0), 2) AS conv_4_to_5_pct,
  step6_subscribed,
  ROUND(step6_subscribed * 100.0 / NULLIF(step5_lead_saved, 0), 2) AS conv_5_to_6_pct,
  -- Overall End-to-End Conversion Rate
  ROUND(step6_subscribed * 100.0 / NULLIF(step1_landing, 0), 2) AS overall_conversion_pct
FROM funnel_aggregates
ORDER BY step1_landing DESC;
