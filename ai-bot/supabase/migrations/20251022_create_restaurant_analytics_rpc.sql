-- Restaurant Analytics RPC Functions
-- Created: 2025-10-22
-- Purpose: Provide AI bot with analytical queries for Chinese restaurant POS data

-- ============================================================================
-- 1. Daily Revenue Summary
-- ============================================================================
CREATE OR REPLACE FUNCTION get_daily_revenue(target_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE (
  total_revenue DECIMAL,
  order_count BIGINT,
  avg_order_value DECIMAL,
  completed_orders BIGINT,
  pending_orders BIGINT,
  cancelled_orders BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    COALESCE(SUM(CASE WHEN status = 'completed' THEN total ELSE 0 END), 0) as total_revenue,
    COUNT(*) as order_count,
    COALESCE(AVG(CASE WHEN status = 'completed' THEN total ELSE NULL END), 0) as avg_order_value,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_orders,
    COUNT(*) FILTER (WHERE status = 'pending') as pending_orders,
    COUNT(*) FILTER (WHERE status = 'cancelled') as cancelled_orders
  FROM rsp_orders
  WHERE DATE(ordered_at AT TIME ZONE 'Asia/Shanghai') = target_date;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_daily_revenue IS '获取指定日期的营业额汇总 (Daily revenue summary)';


-- ============================================================================
-- 2. Revenue by Zone
-- ============================================================================
CREATE OR REPLACE FUNCTION get_revenue_by_zone(
  start_date DATE DEFAULT CURRENT_DATE,
  end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
  zone TEXT,
  total_revenue DECIMAL,
  order_count BIGINT,
  avg_order_value DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    COALESCE(t.zone, '未知区域') as zone,
    SUM(o.total) as total_revenue,
    COUNT(o.id) as order_count,
    AVG(o.total) as avg_order_value
  FROM rsp_orders o
  LEFT JOIN rsp_tables t ON o.table_id = t.id
  WHERE DATE(o.ordered_at AT TIME ZONE 'Asia/Shanghai') BETWEEN start_date AND end_date
    AND o.status = 'completed'
  GROUP BY t.zone
  ORDER BY total_revenue DESC;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_revenue_by_zone IS '按区域统计营业额 (Revenue by dining zone)';


-- ============================================================================
-- 3. Top Selling Dishes
-- ============================================================================
CREATE OR REPLACE FUNCTION get_top_dishes(
  start_date DATE DEFAULT CURRENT_DATE,
  end_date DATE DEFAULT CURRENT_DATE,
  top_n INTEGER DEFAULT 10
)
RETURNS TABLE (
  item_name TEXT,
  total_quantity BIGINT,
  total_revenue DECIMAL,
  order_count BIGINT,
  avg_price DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    oi.item_name,
    SUM(oi.quantity) as total_quantity,
    SUM(oi.total_price) as total_revenue,
    COUNT(DISTINCT oi.order_id) as order_count,
    AVG(oi.unit_price) as avg_price
  FROM rsp_order_items oi
  JOIN rsp_orders o ON oi.order_id = o.id
  WHERE DATE(o.ordered_at AT TIME ZONE 'Asia/Shanghai') BETWEEN start_date AND end_date
    AND o.status = 'completed'
    AND oi.is_return = false
  GROUP BY oi.item_name
  ORDER BY total_quantity DESC
  LIMIT top_n;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_top_dishes IS '获取最畅销菜品 (Top selling dishes by quantity)';


-- ============================================================================
-- 4. Kitchen Station Performance
-- ============================================================================
CREATE OR REPLACE FUNCTION get_station_performance(
  start_date DATE DEFAULT CURRENT_DATE,
  end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
  station_name TEXT,
  station_name_english TEXT,
  total_items BIGINT,
  total_revenue DECIMAL,
  avg_item_price DECIMAL,
  order_count BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    COALESCE(s.name, '未分配') as station_name,
    COALESCE(s.name_english, 'unassigned') as station_name_english,
    SUM(oi.quantity) as total_items,
    SUM(oi.total_price) as total_revenue,
    AVG(oi.unit_price) as avg_item_price,
    COUNT(DISTINCT oi.order_id) as order_count
  FROM rsp_order_items oi
  LEFT JOIN rsp_stations s ON oi.station_id = s.id
  JOIN rsp_orders o ON oi.order_id = o.id
  WHERE DATE(o.ordered_at AT TIME ZONE 'Asia/Shanghai') BETWEEN start_date AND end_date
    AND o.status = 'completed'
    AND oi.is_return = false
  GROUP BY s.name, s.name_english
  ORDER BY total_revenue DESC;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_station_performance IS '按厨房工作站统计业绩 (Kitchen station performance)';


-- ============================================================================
-- 5. Hourly Revenue Pattern
-- ============================================================================
CREATE OR REPLACE FUNCTION get_hourly_revenue(target_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE (
  hour_of_day INTEGER,
  order_count BIGINT,
  total_revenue DECIMAL,
  avg_order_value DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    EXTRACT(HOUR FROM ordered_at AT TIME ZONE 'Asia/Shanghai')::INTEGER as hour_of_day,
    COUNT(*) as order_count,
    SUM(total) as total_revenue,
    AVG(total) as avg_order_value
  FROM rsp_orders
  WHERE DATE(ordered_at AT TIME ZONE 'Asia/Shanghai') = target_date
    AND status = 'completed'
  GROUP BY EXTRACT(HOUR FROM ordered_at AT TIME ZONE 'Asia/Shanghai')
  ORDER BY hour_of_day;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_hourly_revenue IS '按小时统计营业额 (Revenue by hour of day)';


-- ============================================================================
-- 6. Table Turnover Rate
-- ============================================================================
CREATE OR REPLACE FUNCTION get_table_turnover(
  start_date DATE DEFAULT CURRENT_DATE,
  end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
  zone TEXT,
  table_no TEXT,
  order_count BIGINT,
  total_revenue DECIMAL,
  avg_order_value DECIMAL,
  capacity INTEGER
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    t.zone,
    t.table_no,
    COUNT(o.id) as order_count,
    COALESCE(SUM(o.total), 0) as total_revenue,
    COALESCE(AVG(o.total), 0) as avg_order_value,
    t.capacity
  FROM rsp_tables t
  LEFT JOIN rsp_orders o ON t.id = o.table_id
    AND DATE(o.ordered_at AT TIME ZONE 'Asia/Shanghai') BETWEEN start_date AND end_date
    AND o.status = 'completed'
  WHERE t.active = true
  GROUP BY t.zone, t.table_no, t.capacity
  ORDER BY order_count DESC;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_table_turnover IS '按餐桌统计翻台率 (Table turnover rate)';


-- ============================================================================
-- 7. Return/Refund Analysis
-- ============================================================================
CREATE OR REPLACE FUNCTION get_return_analysis(
  start_date DATE DEFAULT CURRENT_DATE,
  end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
  item_name TEXT,
  return_count BIGINT,
  return_quantity BIGINT,
  return_revenue_loss DECIMAL,
  total_orders_with_item BIGINT,
  return_rate DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  WITH return_items AS (
    SELECT
      oi.item_name,
      COUNT(*) as return_count,
      SUM(oi.quantity) as return_quantity,
      SUM(oi.total_price) as return_revenue_loss
    FROM rsp_order_items oi
    JOIN rsp_orders o ON oi.order_id = o.id
    WHERE DATE(o.ordered_at AT TIME ZONE 'Asia/Shanghai') BETWEEN start_date AND end_date
      AND oi.is_return = true
    GROUP BY oi.item_name
  ),
  total_items AS (
    SELECT
      oi.item_name,
      COUNT(DISTINCT oi.order_id) as total_orders
    FROM rsp_order_items oi
    JOIN rsp_orders o ON oi.order_id = o.id
    WHERE DATE(o.ordered_at AT TIME ZONE 'Asia/Shanghai') BETWEEN start_date AND end_date
    GROUP BY oi.item_name
  )
  SELECT
    r.item_name,
    r.return_count,
    r.return_quantity,
    r.return_revenue_loss,
    t.total_orders,
    ROUND((r.return_count::DECIMAL / NULLIF(t.total_orders, 0) * 100), 2) as return_rate
  FROM return_items r
  JOIN total_items t ON r.item_name = t.item_name
  ORDER BY return_rate DESC;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_return_analysis IS '退菜分析 (Return/refund analysis by dish)';


-- ============================================================================
-- 8. Order Type Distribution
-- ============================================================================
CREATE OR REPLACE FUNCTION get_order_type_distribution(
  start_date DATE DEFAULT CURRENT_DATE,
  end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
  order_type TEXT,
  order_count BIGINT,
  total_revenue DECIMAL,
  avg_order_value DECIMAL,
  percentage_of_total DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  WITH order_stats AS (
    SELECT
      o.order_type,
      COUNT(*) as order_count,
      SUM(o.total) as total_revenue,
      AVG(o.total) as avg_order_value
    FROM rsp_orders o
    WHERE DATE(o.ordered_at AT TIME ZONE 'Asia/Shanghai') BETWEEN start_date AND end_date
      AND o.status = 'completed'
    GROUP BY o.order_type
  ),
  total_orders AS (
    SELECT SUM(order_count) as total_count
    FROM order_stats
  )
  SELECT
    os.order_type,
    os.order_count,
    os.total_revenue,
    os.avg_order_value,
    ROUND((os.order_count::DECIMAL / NULLIF(t.total_count, 0) * 100), 2) as percentage_of_total
  FROM order_stats os, total_orders t
  ORDER BY os.order_count DESC;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_order_type_distribution IS '订单类型分布 (dine_in/takeout/delivery distribution)';


-- ============================================================================
-- 9. Revenue Trend (Multi-day comparison)
-- ============================================================================
CREATE OR REPLACE FUNCTION get_revenue_trend(
  start_date DATE,
  end_date DATE
)
RETURNS TABLE (
  date DATE,
  total_revenue DECIMAL,
  order_count BIGINT,
  avg_order_value DECIMAL,
  completed_orders BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    DATE(ordered_at AT TIME ZONE 'Asia/Shanghai') as date,
    SUM(total) as total_revenue,
    COUNT(*) as order_count,
    AVG(total) as avg_order_value,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_orders
  FROM rsp_orders
  WHERE DATE(ordered_at AT TIME ZONE 'Asia/Shanghai') BETWEEN start_date AND end_date
  GROUP BY DATE(ordered_at AT TIME ZONE 'Asia/Shanghai')
  ORDER BY date;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_revenue_trend IS '营业额趋势 (Revenue trend over date range)';


-- ============================================================================
-- 10. Quick Stats (Dashboard summary)
-- ============================================================================
CREATE OR REPLACE FUNCTION get_quick_stats(target_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE (
  metric TEXT,
  value TEXT,
  description TEXT
) AS $$
DECLARE
  v_total_revenue DECIMAL;
  v_order_count BIGINT;
  v_avg_order DECIMAL;
  v_top_dish TEXT;
  v_busiest_hour INTEGER;
  v_total_tables BIGINT;
  v_active_tables BIGINT;
BEGIN
  -- Get revenue stats
  SELECT
    COALESCE(SUM(total), 0),
    COUNT(*),
    COALESCE(AVG(total), 0)
  INTO v_total_revenue, v_order_count, v_avg_order
  FROM rsp_orders
  WHERE DATE(ordered_at AT TIME ZONE 'Asia/Shanghai') = target_date
    AND status = 'completed';

  -- Get top dish
  SELECT item_name INTO v_top_dish
  FROM rsp_order_items oi
  JOIN rsp_orders o ON oi.order_id = o.id
  WHERE DATE(o.ordered_at AT TIME ZONE 'Asia/Shanghai') = target_date
    AND o.status = 'completed'
    AND oi.is_return = false
  GROUP BY item_name
  ORDER BY SUM(quantity) DESC
  LIMIT 1;

  -- Get busiest hour
  SELECT EXTRACT(HOUR FROM ordered_at AT TIME ZONE 'Asia/Shanghai')::INTEGER INTO v_busiest_hour
  FROM rsp_orders
  WHERE DATE(ordered_at AT TIME ZONE 'Asia/Shanghai') = target_date
    AND status = 'completed'
  GROUP BY EXTRACT(HOUR FROM ordered_at AT TIME ZONE 'Asia/Shanghai')
  ORDER BY COUNT(*) DESC
  LIMIT 1;

  -- Get table stats
  SELECT COUNT(*), COUNT(*) FILTER (WHERE active = true)
  INTO v_total_tables, v_active_tables
  FROM rsp_tables;

  -- Return results
  RETURN QUERY VALUES
    ('今日营业额', '¥' || ROUND(v_total_revenue, 2)::TEXT, '已完成订单的总金额'),
    ('订单数量', v_order_count::TEXT, '今日总订单数'),
    ('平均订单金额', '¥' || ROUND(v_avg_order, 2)::TEXT, '平均每单金额'),
    ('最畅销菜品', COALESCE(v_top_dish, '暂无数据'), '销量最高的菜品'),
    ('最忙时段', COALESCE(v_busiest_hour::TEXT || ':00', '暂无数据'), '订单最多的小时'),
    ('餐桌数量', v_active_tables::TEXT || '/' || v_total_tables::TEXT, '活跃餐桌/总餐桌');
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_quick_stats IS '快速统计摘要 (Quick dashboard summary)';


-- ============================================================================
-- Grant permissions (adjust based on your RLS setup)
-- ============================================================================
-- If using service role, these are already accessible
-- If using anon/authenticated roles, you may need:
-- GRANT EXECUTE ON FUNCTION get_daily_revenue TO authenticated;
-- GRANT EXECUTE ON FUNCTION get_revenue_by_zone TO authenticated;
-- etc.
