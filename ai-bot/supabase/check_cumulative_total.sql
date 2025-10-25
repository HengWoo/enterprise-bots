-- Check if cumulative_total is suitable for revenue calculation

-- ============================================================================
-- 1. Check sample receipts with cumulative_total
-- ============================================================================
SELECT
    receipt_no,
    receipt_type,
    cumulative_total,
    created_at,
    DATE(created_at AT TIME ZONE 'Asia/Shanghai') as date
FROM rsp_receipts
ORDER BY created_at DESC
LIMIT 20;


-- ============================================================================
-- 2. Compare cumulative_total vs order totals for TODAY
-- ============================================================================
WITH receipt_revenue AS (
    SELECT
        MAX(cumulative_total) - MIN(cumulative_total) as revenue_from_cumulative,
        COUNT(*) as receipt_count
    FROM rsp_receipts
    WHERE DATE(created_at AT TIME ZONE 'Asia/Shanghai') = CURRENT_DATE
        AND receipt_type = 'customer_order'
),
order_revenue AS (
    SELECT
        SUM(total) as revenue_from_orders,
        COUNT(*) as order_count
    FROM rsp_orders
    WHERE DATE(ordered_at AT TIME ZONE 'Asia/Shanghai') = CURRENT_DATE
        AND total > 0
)
SELECT
    r.revenue_from_cumulative as "Revenue (Cumulative Total)",
    o.revenue_from_orders as "Revenue (Order Totals)",
    (r.revenue_from_cumulative - o.revenue_from_orders) as "Difference",
    r.receipt_count,
    o.order_count
FROM receipt_revenue r, order_revenue o;


-- ============================================================================
-- 3. Check for historical date (Oct 21 - has 123 orders)
-- ============================================================================
WITH receipt_revenue AS (
    SELECT
        MAX(cumulative_total) - MIN(cumulative_total) as revenue_from_cumulative,
        MIN(cumulative_total) as min_cumulative,
        MAX(cumulative_total) as max_cumulative,
        COUNT(*) as receipt_count
    FROM rsp_receipts
    WHERE DATE(created_at AT TIME ZONE 'Asia/Shanghai') = '2025-10-21'
        AND receipt_type = 'customer_order'
),
order_revenue AS (
    SELECT
        SUM(total) as revenue_from_orders,
        COUNT(*) as order_count
    FROM rsp_orders
    WHERE DATE(ordered_at AT TIME ZONE 'Asia/Shanghai') = '2025-10-21'
        AND total > 0
)
SELECT
    r.revenue_from_cumulative as "Revenue (Cumulative)",
    r.min_cumulative as "Day Start Cumulative",
    r.max_cumulative as "Day End Cumulative",
    o.revenue_from_orders as "Revenue (Orders)",
    (r.revenue_from_cumulative - o.revenue_from_orders) as "Difference",
    r.receipt_count,
    o.order_count
FROM receipt_revenue r, order_revenue o;


-- ============================================================================
-- 4. Check if cumulative_total ever resets or has gaps
-- ============================================================================
SELECT
    DATE(created_at AT TIME ZONE 'Asia/Shanghai') as date,
    MIN(cumulative_total) as min_cumulative,
    MAX(cumulative_total) as max_cumulative,
    MAX(cumulative_total) - MIN(cumulative_total) as calculated_daily_revenue,
    COUNT(*) as receipt_count
FROM rsp_receipts
WHERE receipt_type = 'customer_order'
GROUP BY DATE(created_at AT TIME ZONE 'Asia/Shanghai')
ORDER BY date DESC
LIMIT 10;


-- ============================================================================
-- 5. Check if cumulative_total is monotonically increasing
-- ============================================================================
WITH daily_range AS (
    SELECT
        DATE(created_at AT TIME ZONE 'Asia/Shanghai') as date,
        MIN(cumulative_total) as day_min,
        MAX(cumulative_total) as day_max
    FROM rsp_receipts
    WHERE receipt_type = 'customer_order'
    GROUP BY DATE(created_at AT TIME ZONE 'Asia/Shanghai')
    ORDER BY date
)
SELECT
    date,
    day_min,
    day_max,
    LAG(day_max) OVER (ORDER BY date) as prev_day_max,
    CASE
        WHEN LAG(day_max) OVER (ORDER BY date) IS NULL THEN 'First Day'
        WHEN day_min >= LAG(day_max) OVER (ORDER BY date) THEN '✅ Continuous'
        WHEN day_min < LAG(day_max) OVER (ORDER BY date) THEN '⚠️ Overlaps'
        ELSE '❓ Unknown'
    END as continuity_check
FROM daily_range
ORDER BY date DESC
LIMIT 10;
