-- Menu Engineering RPC Functions
-- Analyzes dish profitability using Boston Matrix methodology
-- Uses product_cost_analysis view + rsp_order_items sales data

-- ============================================================================
-- 1. Menu Profitability Analysis (Boston Matrix)
-- ============================================================================
CREATE OR REPLACE FUNCTION get_menu_profitability(
    start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    end_date DATE DEFAULT CURRENT_DATE,
    min_quantity INTEGER DEFAULT 10
)
RETURNS TABLE (
    product_name TEXT,
    quantity_sold BIGINT,
    total_revenue DECIMAL,
    avg_selling_price DECIMAL,
    estimated_cost DECIMAL,
    gross_profit DECIMAL,
    profit_margin DECIMAL,
    popularity_score DECIMAL,
    profitability_score DECIMAL,
    category TEXT,
    rank_by_profit INTEGER,
    rank_by_quantity INTEGER
) AS $$
DECLARE
    avg_quantity DECIMAL;
    avg_profit_margin DECIMAL;
BEGIN
    -- Create temp table with sales + cost data
    DROP TABLE IF EXISTS temp_menu_sales;
    CREATE TEMP TABLE temp_menu_sales AS
    SELECT
        TRIM(oi.item_name) as dish_name,
        COUNT(DISTINCT oi.order_id) as order_count,
        SUM(oi.quantity) as total_quantity,
        SUM(oi.total_price) as total_revenue,
        AVG(oi.unit_price) as avg_price,
        COALESCE(pc.total_ingredient_cost, 0) as unit_cost,
        COALESCE(pc.margin_percentage, 0) as cost_margin
    FROM rsp_order_items oi
    JOIN rsp_orders o ON oi.order_id = o.id
    LEFT JOIN product_cost_analysis pc ON TRIM(LOWER(oi.item_name)) = TRIM(LOWER(pc.product_name))
    WHERE DATE(o.ordered_at AT TIME ZONE 'Asia/Shanghai') BETWEEN start_date AND end_date
        AND oi.total_price > 0
        AND oi.is_return IS DISTINCT FROM true
    GROUP BY TRIM(oi.item_name), pc.total_ingredient_cost, pc.margin_percentage
    HAVING SUM(oi.quantity) >= min_quantity;

    -- Calculate averages for categorization
    SELECT
        AVG(total_quantity),
        AVG((total_revenue - (unit_cost * total_quantity)) / NULLIF(total_revenue, 0) * 100)
    INTO avg_quantity, avg_profit_margin
    FROM temp_menu_sales;

    -- Return categorized results
    RETURN QUERY
    WITH ranked_dishes AS (
        SELECT
            dish_name,
            total_quantity,
            total_revenue,
            avg_price,
            unit_cost * total_quantity as estimated_total_cost,
            total_revenue - (unit_cost * total_quantity) as gross_profit_calc,
            CASE
                WHEN total_revenue > 0 THEN
                    ((total_revenue - (unit_cost * total_quantity)) / total_revenue * 100)
                ELSE 0
            END as profit_margin_calc,
            (total_quantity::DECIMAL / NULLIF(avg_quantity, 0) * 100) as popularity_pct,
            CASE
                WHEN total_revenue > 0 THEN
                    (((total_revenue - (unit_cost * total_quantity)) / total_revenue * 100) / NULLIF(avg_profit_margin, 0) * 100)
                ELSE 0
            END as profitability_pct,
            RANK() OVER (ORDER BY total_revenue - (unit_cost * total_quantity) DESC) as profit_rank,
            RANK() OVER (ORDER BY total_quantity DESC) as quantity_rank
        FROM temp_menu_sales
    )
    SELECT
        dish_name,
        total_quantity,
        total_revenue,
        avg_price,
        estimated_total_cost,
        gross_profit_calc,
        profit_margin_calc,
        popularity_pct,
        profitability_pct,
        -- Boston Matrix categorization
        CASE
            WHEN popularity_pct >= 100 AND profitability_pct >= 100 THEN '⭐ Stars'
            WHEN popularity_pct < 100 AND profitability_pct >= 100 THEN '🧩 Puzzles'
            WHEN popularity_pct >= 100 AND profitability_pct < 100 THEN '🐴 Plowhorses'
            ELSE '🐕 Dogs'
        END as category,
        profit_rank::INTEGER,
        quantity_rank::INTEGER
    FROM ranked_dishes
    ORDER BY gross_profit_calc DESC;

    DROP TABLE IF EXISTS temp_menu_sales;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_menu_profitability IS '菜单工程分析：计算菜品盈利能力并分类 (Menu Engineering: Boston Matrix categorization)';


-- ============================================================================
-- 2. Top Profitable Dishes
-- ============================================================================
CREATE OR REPLACE FUNCTION get_top_profitable_dishes(
    start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    end_date DATE DEFAULT CURRENT_DATE,
    top_n INTEGER DEFAULT 10
)
RETURNS TABLE (
    product_name TEXT,
    quantity_sold BIGINT,
    total_revenue DECIMAL,
    total_cost DECIMAL,
    gross_profit DECIMAL,
    profit_margin DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        TRIM(oi.item_name) as product_name,
        SUM(oi.quantity) as quantity_sold,
        SUM(oi.total_price) as total_revenue,
        COALESCE(SUM(oi.quantity * pc.total_ingredient_cost), 0) as total_cost,
        SUM(oi.total_price) - COALESCE(SUM(oi.quantity * pc.total_ingredient_cost), 0) as gross_profit,
        CASE
            WHEN SUM(oi.total_price) > 0 THEN
                (SUM(oi.total_price) - COALESCE(SUM(oi.quantity * pc.total_ingredient_cost), 0)) / SUM(oi.total_price) * 100
            ELSE 0
        END as profit_margin
    FROM rsp_order_items oi
    JOIN rsp_orders o ON oi.order_id = o.id
    LEFT JOIN product_cost_analysis pc ON TRIM(LOWER(oi.item_name)) = TRIM(LOWER(pc.product_name))
    WHERE DATE(o.ordered_at AT TIME ZONE 'Asia/Shanghai') BETWEEN start_date AND end_date
        AND oi.total_price > 0
        AND oi.is_return IS DISTINCT FROM true
    GROUP BY TRIM(oi.item_name)
    ORDER BY gross_profit DESC
    LIMIT top_n;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_top_profitable_dishes IS '最赚钱的菜品排行 (Top dishes by gross profit)';


-- ============================================================================
-- 3. Low Profit Dishes (Dogs)
-- ============================================================================
CREATE OR REPLACE FUNCTION get_low_profit_dishes(
    start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    end_date DATE DEFAULT CURRENT_DATE,
    bottom_n INTEGER DEFAULT 10
)
RETURNS TABLE (
    product_name TEXT,
    quantity_sold BIGINT,
    total_revenue DECIMAL,
    total_cost DECIMAL,
    gross_profit DECIMAL,
    profit_margin DECIMAL,
    recommendation TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        TRIM(oi.item_name) as product_name,
        SUM(oi.quantity) as quantity_sold,
        SUM(oi.total_price) as total_revenue,
        COALESCE(SUM(oi.quantity * pc.total_ingredient_cost), 0) as total_cost,
        SUM(oi.total_price) - COALESCE(SUM(oi.quantity * pc.total_ingredient_cost), 0) as gross_profit,
        CASE
            WHEN SUM(oi.total_price) > 0 THEN
                (SUM(oi.total_price) - COALESCE(SUM(oi.quantity * pc.total_ingredient_cost), 0)) / SUM(oi.total_price) * 100
            ELSE 0
        END as profit_margin,
        CASE
            WHEN SUM(oi.quantity) < 10 THEN '考虑下架（销量过低）'
            WHEN SUM(oi.total_price) - COALESCE(SUM(oi.quantity * pc.total_ingredient_cost), 0) < 0 THEN '亏损菜品！立即调价或下架'
            WHEN (SUM(oi.total_price) - COALESCE(SUM(oi.quantity * pc.total_ingredient_cost), 0)) / SUM(oi.total_price) < 0.2 THEN '利润率过低，建议提价或降成本'
            ELSE '关注并优化'
        END as recommendation
    FROM rsp_order_items oi
    JOIN rsp_orders o ON oi.order_id = o.id
    LEFT JOIN product_cost_analysis pc ON TRIM(LOWER(oi.item_name)) = TRIM(LOWER(pc.product_name))
    WHERE DATE(o.ordered_at AT TIME ZONE 'Asia/Shanghai') BETWEEN start_date AND end_date
        AND oi.total_price > 0
        AND oi.is_return IS DISTINCT FROM true
    GROUP BY TRIM(oi.item_name)
    HAVING SUM(oi.quantity) >= 5  -- Only dishes sold at least 5 times
    ORDER BY gross_profit ASC
    LIMIT bottom_n;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_low_profit_dishes IS '低盈利菜品分析 (Low profit dishes with recommendations)';


-- ============================================================================
-- 4. Cost Coverage Analysis
-- ============================================================================
CREATE OR REPLACE FUNCTION get_cost_coverage_rate(
    start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    total_dishes BIGINT,
    dishes_with_cost_data BIGINT,
    coverage_rate DECIMAL,
    total_revenue_covered DECIMAL,
    total_revenue_uncovered DECIMAL,
    revenue_coverage_rate DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    WITH sales_data AS (
        SELECT
            TRIM(oi.item_name) as dish_name,
            SUM(oi.total_price) as revenue,
            CASE WHEN pc.product_name IS NOT NULL THEN 1 ELSE 0 END as has_cost
        FROM rsp_order_items oi
        JOIN rsp_orders o ON oi.order_id = o.id
        LEFT JOIN product_cost_analysis pc ON TRIM(LOWER(oi.item_name)) = TRIM(LOWER(pc.product_name))
        WHERE DATE(o.ordered_at AT TIME ZONE 'Asia/Shanghai') BETWEEN start_date AND end_date
            AND oi.total_price > 0
            AND oi.is_return IS DISTINCT FROM true
        GROUP BY TRIM(oi.item_name), pc.product_name
    )
    SELECT
        COUNT(*)::BIGINT as total_dishes,
        SUM(has_cost)::BIGINT as dishes_with_cost_data,
        ROUND(SUM(has_cost)::DECIMAL / NULLIF(COUNT(*), 0) * 100, 2) as coverage_rate,
        SUM(CASE WHEN has_cost = 1 THEN revenue ELSE 0 END) as total_revenue_covered,
        SUM(CASE WHEN has_cost = 0 THEN revenue ELSE 0 END) as total_revenue_uncovered,
        ROUND(SUM(CASE WHEN has_cost = 1 THEN revenue ELSE 0 END) / NULLIF(SUM(revenue), 0) * 100, 2) as revenue_coverage_rate
    FROM sales_data;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_cost_coverage_rate IS '成本数据覆盖率分析 (Cost data coverage analysis)';


-- ============================================================================
-- 5. Dishes Missing Cost Data
-- ============================================================================
CREATE OR REPLACE FUNCTION get_dishes_missing_cost(
    start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    end_date DATE DEFAULT CURRENT_DATE,
    top_n INTEGER DEFAULT 20
)
RETURNS TABLE (
    product_name TEXT,
    quantity_sold BIGINT,
    total_revenue DECIMAL,
    avg_selling_price DECIMAL,
    order_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        TRIM(oi.item_name) as product_name,
        SUM(oi.quantity) as quantity_sold,
        SUM(oi.total_price) as total_revenue,
        AVG(oi.unit_price) as avg_selling_price,
        COUNT(DISTINCT oi.order_id) as order_count
    FROM rsp_order_items oi
    JOIN rsp_orders o ON oi.order_id = o.id
    LEFT JOIN product_cost_analysis pc ON TRIM(LOWER(oi.item_name)) = TRIM(LOWER(pc.product_name))
    WHERE DATE(o.ordered_at AT TIME ZONE 'Asia/Shanghai') BETWEEN start_date AND end_date
        AND oi.total_price > 0
        AND oi.is_return IS DISTINCT FROM true
        AND pc.product_name IS NULL  -- Missing cost data
    GROUP BY TRIM(oi.item_name)
    ORDER BY total_revenue DESC
    LIMIT top_n;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_dishes_missing_cost IS '缺少成本数据的菜品 (Dishes missing cost data, ordered by revenue)';
