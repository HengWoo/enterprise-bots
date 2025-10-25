-- Debugging Script for Empty Revenue Issue
-- Run these queries in Supabase SQL Editor to identify the problem

-- ============================================================================
-- STEP 1: Check actual table structure
-- ============================================================================
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'rsp_orders'
ORDER BY ordinal_position;

-- Expected columns: id, receipt_no, order_type, status, subtotal, tax, total, ordered_at, etc.


-- ============================================================================
-- STEP 2: Check if there's any data in the table
-- ============================================================================
SELECT COUNT(*) as total_orders FROM rsp_orders;


-- ============================================================================
-- STEP 3: Check sample data from rsp_orders
-- ============================================================================
SELECT
    id,
    receipt_no,
    status,
    subtotal,
    tax,
    total,
    ordered_at,
    DATE(ordered_at AT TIME ZONE 'Asia/Shanghai') as order_date
FROM rsp_orders
LIMIT 10;


-- ============================================================================
-- STEP 4: Check what dates we have data for
-- ============================================================================
SELECT
    DATE(ordered_at AT TIME ZONE 'Asia/Shanghai') as order_date,
    COUNT(*) as order_count,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_count,
    SUM(CASE WHEN status = 'completed' THEN total ELSE 0 END) as total_revenue
FROM rsp_orders
GROUP BY DATE(ordered_at AT TIME ZONE 'Asia/Shanghai')
ORDER BY order_date DESC
LIMIT 30;


-- ============================================================================
-- STEP 5: Test the RPC function with today's date
-- ============================================================================
SELECT * FROM get_daily_revenue();


-- ============================================================================
-- STEP 6: Test with explicit date (use a date from Step 4)
-- ============================================================================
-- Replace '2025-10-22' with a date that has data from Step 4
SELECT * FROM get_daily_revenue('2025-10-22'::DATE);


-- ============================================================================
-- STEP 7: Check if column name is different (maybe it's not 'total')
-- ============================================================================
-- This will show all numeric columns in the table
SELECT
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'rsp_orders'
    AND (data_type LIKE '%numeric%'
         OR data_type LIKE '%decimal%'
         OR data_type LIKE '%float%'
         OR data_type LIKE '%double%'
         OR data_type LIKE '%money%');


-- ============================================================================
-- STEP 8: Manual calculation (bypass RPC) - Compare results
-- ============================================================================
-- This does exactly what the RPC function should do
SELECT
    COALESCE(SUM(CASE WHEN status = 'completed' THEN total ELSE 0 END), 0) as total_revenue,
    COUNT(*) as order_count,
    COALESCE(AVG(CASE WHEN status = 'completed' THEN total ELSE NULL END), 0) as avg_order_value,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_orders,
    COUNT(*) FILTER (WHERE status = 'pending') as pending_orders,
    COUNT(*) FILTER (WHERE status = 'cancelled') as cancelled_orders
FROM rsp_orders
WHERE DATE(ordered_at AT TIME ZONE 'Asia/Shanghai') = CURRENT_DATE;


-- ============================================================================
-- STEP 9: Check rsp_receipts table instead (has cumulative_total)
-- ============================================================================
SELECT
    receipt_no,
    receipt_type,
    cumulative_total,
    created_at::DATE as date
FROM rsp_receipts
ORDER BY created_at DESC
LIMIT 10;


-- ============================================================================
-- STEP 10: Check if we should use cumulative_total from receipts
-- ============================================================================
SELECT
    DATE(r.created_at) as date,
    COUNT(DISTINCT r.receipt_no) as receipt_count,
    MAX(r.cumulative_total) as max_cumulative_total,
    -- Join to orders to get actual totals
    SUM(o.total) as total_from_orders
FROM rsp_receipts r
LEFT JOIN rsp_orders o ON r.receipt_no = o.receipt_no
WHERE r.receipt_type = 'customer_order'
GROUP BY DATE(r.created_at)
ORDER BY date DESC
LIMIT 10;


-- ============================================================================
-- DIAGNOSTIC: Show everything we know about the data
-- ============================================================================
SELECT
    'Table' as info_type,
    'rsp_orders' as detail,
    COUNT(*)::TEXT as value
FROM rsp_orders

UNION ALL

SELECT
    'Oldest Order',
    MIN(ordered_at)::TEXT,
    ''
FROM rsp_orders

UNION ALL

SELECT
    'Newest Order',
    MAX(ordered_at)::TEXT,
    ''
FROM rsp_orders

UNION ALL

SELECT
    'Total Column Type',
    data_type,
    ''
FROM information_schema.columns
WHERE table_name = 'rsp_orders' AND column_name = 'total'

UNION ALL

SELECT
    'Sample Total Value',
    total::TEXT,
    ''
FROM rsp_orders
WHERE total IS NOT NULL
LIMIT 1;
