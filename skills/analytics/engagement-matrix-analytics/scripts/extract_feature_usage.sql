-- ============================================================================
-- Amplitude 4-Quadrant Engagement Matrix: Feature Usage Extraction
-- Dialect: Standard ANSI SQL / PostgreSQL / DuckDB / BigQuery
-- ============================================================================

WITH window_params AS (
  SELECT 
    CURRENT_DATE - INTERVAL '30 days' AS start_date,
    CURRENT_DATE AS end_date
),
monthly_active_users AS (
  -- 1. Calculate Total MAU during the 30-day evaluation window
  SELECT COUNT(DISTINCT user_id) AS total_mau
  FROM user_activity_events
  CROSS JOIN window_params p
  WHERE event_timestamp >= p.start_date AND event_timestamp < p.end_date
),
feature_raw_usage AS (
  -- 2. Aggregate unique users and event counts per feature
  SELECT 
    event_name AS feature_name,
    COUNT(DISTINCT user_id) AS unique_users,
    COUNT(*) AS total_events
  FROM user_activity_events
  CROSS JOIN window_params p
  WHERE event_timestamp >= p.start_date 
    AND event_timestamp < p.end_date
    AND event_category IN ('lab_core', 'ai_feedback', 'study_tools')
  GROUP BY event_name
)
-- 3. Compute Breadth (% MAU) and Frequency (Events / User)
SELECT 
  f.feature_name,
  f.unique_users,
  f.total_events,
  m.total_mau,
  ROUND((f.unique_users * 100.0 / m.total_mau), 2) AS breadth_pct,
  ROUND((f.total_events * 1.0 / f.unique_users), 2) AS frequency
FROM feature_raw_usage f
CROSS JOIN monthly_active_users m
ORDER BY breadth_pct DESC, frequency DESC;
