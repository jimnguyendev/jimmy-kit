-- ============================================================================
-- Duolingo 7-State User Lifecycle State Classification Query
-- Dialect: Standard ANSI SQL / PostgreSQL / SQLite (with date math adaptations)
-- ============================================================================

WITH daily_user_activity AS (
  -- 1. Get distinct active days for each user
  SELECT DISTINCT
    user_id,
    DATE(event_timestamp) AS active_date
  FROM user_activity_events
  WHERE event_timestamp >= CURRENT_DATE - INTERVAL '60 days'
),
user_calendar AS (
  -- 2. Generate calendar matrix for all registered users over target evaluation days
  SELECT 
    u.user_id,
    u.created_at::DATE AS signup_date,
    c.eval_date
  FROM users u
  CROSS JOIN (
    SELECT (CURRENT_DATE - INTERVAL '1 day' * generate_series(0, 30))::DATE AS eval_date
  ) c
  WHERE c.eval_date >= u.created_at::DATE
),
activity_flags AS (
  -- 3. Calculate rolling activity flags
  SELECT 
    uc.user_id,
    uc.eval_date,
    uc.signup_date,
    -- Active today
    CASE WHEN a_today.active_date IS NOT NULL THEN 1 ELSE 0 END AS is_active_today,
    -- Active in last [D-7, D-1] (6-day lookback)
    MAX(CASE WHEN a_past.active_date BETWEEN uc.eval_date - INTERVAL '7 days' AND uc.eval_date - INTERVAL '1 day' THEN 1 ELSE 0 END) AS is_active_last_7d,
    -- Active in last [D-30, D-8] (22-day lookback)
    MAX(CASE WHEN a_past.active_date BETWEEN uc.eval_date - INTERVAL '30 days' AND uc.eval_date - INTERVAL '8 days' THEN 1 ELSE 0 END) AS is_active_last_30d
  FROM user_calendar uc
  LEFT JOIN daily_user_activity a_today 
    ON uc.user_id = a_today.user_id AND uc.eval_date = a_today.active_date
  LEFT JOIN daily_user_activity a_past 
    ON uc.user_id = a_past.user_id
  GROUP BY uc.user_id, uc.eval_date, uc.signup_date, a_today.active_date
),
state_classified AS (
  -- 4. Map conditions to 7 Duolingo states
  SELECT 
    user_id,
    eval_date,
    CASE 
      -- Active Today
      WHEN is_active_today = 1 AND eval_date = signup_date THEN 'N'
      WHEN is_active_today = 1 AND is_active_last_7d = 1 THEN 'C'
      WHEN is_active_today = 1 AND is_active_last_7d = 0 AND is_active_last_30d = 1 THEN 'R'
      WHEN is_active_today = 1 AND is_active_last_7d = 0 AND is_active_last_30d = 0 AND eval_date > signup_date THEN 'Res'
      -- Inactive Today
      WHEN is_active_today = 0 AND is_active_last_7d = 1 THEN 'sWAU'
      WHEN is_active_today = 0 AND is_active_last_7d = 0 AND is_active_last_30d = 1 THEN 'sMAU'
      ELSE 'Dead'
    END AS user_state
  FROM activity_flags
)
-- 5. Export Daily State Counts
SELECT 
  eval_date,
  user_state,
  COUNT(DISTINCT user_id) AS user_count
FROM state_classified
GROUP BY eval_date, user_state
ORDER BY eval_date DESC, user_state;
