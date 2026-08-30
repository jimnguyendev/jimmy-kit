-- ============================================================================
-- Customer State Migration Matrix: H1 vs H2 Cycle Transition
-- Dialect: Standard ANSI SQL / PostgreSQL / DuckDB / BigQuery
-- ============================================================================

WITH cycle_1_rfm AS (
  -- 1. Compute RFM Persona Tier in Cycle 1 (e.g. First Half of the Year H1)
  SELECT 
    user_id,
    rfm_segment_label AS tier_h1 -- 'Top VIP', 'Potential', 'Regular', 'At-Risk', 'Lost'
  FROM user_rfm_history
  WHERE cycle_name = '2026_H1'
),
cycle_2_rfm AS (
  -- 2. Compute RFM Persona Tier in Cycle 2 (e.g. Second Half of the Year H2)
  SELECT 
    user_id,
    rfm_segment_label AS tier_h2
  FROM user_rfm_history
  WHERE cycle_name = '2026_H2'
),
migration_pairs AS (
  -- 3. Pair users across both cycles
  SELECT 
    h1.user_id,
    h1.tier_h1,
    COALESCE(h2.tier_h2, 'Lost') AS tier_h2
  FROM cycle_1_rfm h1
  LEFT JOIN cycle_2_rfm h2 ON h1.user_id = h2.user_id
)
-- 4. Calculate Transition Matrix Counts and Retention %
SELECT 
  tier_h1,
  tier_h2,
  COUNT(user_id) AS user_count,
  ROUND(COUNT(user_id) * 100.0 / SUM(COUNT(user_id)) OVER (PARTITION BY tier_h1), 2) AS migration_pct,
  CASE 
    WHEN tier_h1 = tier_h2 THEN 'RETENTION (Main Diagonal)'
    WHEN (tier_h1 = 'Top VIP' AND tier_h2 IN ('At-Risk', 'Lost')) THEN '🔴 RED ALERT: VIP Churn Leakage'
    WHEN (tier_h1 IN ('Potential', 'Regular') AND tier_h2 = 'Top VIP') THEN '🟢 GROWTH: Upsell Success'
    ELSE 'Normal Shift'
  END AS strategic_signal
FROM migration_pairs
GROUP BY tier_h1, tier_h2
ORDER BY tier_h1, tier_h2;
