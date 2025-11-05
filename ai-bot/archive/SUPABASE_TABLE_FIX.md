# Debugging Empty Revenue Issue

**Problem:** `get_daily_revenue()` returns empty `total_revenue`

**Possible Causes:**
1. No data for today's date
2. Column name mismatch (maybe not called `total`)
3. Using wrong column (`total` vs `cumulative_total`)
4. Data type issue or NULL values

---

## Quick Diagnosis (Run in Supabase SQL Editor)

### Step 1: Check Table Structure

```sql
-- What columns exist in rsp_orders?
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'rsp_orders'
ORDER BY ordinal_position;
```

**Look for:** Do you see a column called `total`? Or is it named differently?

---

### Step 2: Check Sample Data

```sql
-- Get 5 sample orders
SELECT *
FROM rsp_orders
LIMIT 5;
```

**Look for:** What is the revenue column actually called? Are there NULL values?

---

### Step 3: Check What Dates Have Data

```sql
SELECT
    DATE(ordered_at AT TIME ZONE 'Asia/Shanghai') as order_date,
    COUNT(*) as orders,
    COUNT(*) FILTER (WHERE status = 'completed') as completed
FROM rsp_orders
GROUP BY DATE(ordered_at AT TIME ZONE 'Asia/Shanghai')
ORDER BY order_date DESC
LIMIT 10;
```

**Look for:** Is there data for today? Or only historical dates?

---

### Step 4: Manual Revenue Calculation

```sql
SELECT
    SUM(total) as sum_of_total,
    COUNT(*) as order_count
FROM rsp_orders
WHERE DATE(ordered_at AT TIME ZONE 'Asia/Shanghai') = CURRENT_DATE;
```

**Look for:** Is sum showing 0 or NULL? This means no data for today.

---

## What to Share With Me

Please run these 4 queries above and **copy/paste the results** so I can help fix the RPC function!
