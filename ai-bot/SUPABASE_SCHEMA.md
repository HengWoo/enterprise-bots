# Supabase Restaurant Sales Platform - Actual Schema

**Database:** Restaurant POS System (餐饮销售平台)
**Inspected:** 2025-10-22
**Status:** ✅ All tables have data

---

## Table Overview

| Table | Purpose | Records | Key Fields |
|-------|---------|---------|------------|
| rsp_restaurants | 餐厅信息 | 1+ | name, address, timezone |
| rsp_stations | 档口/厨房工作站 | 3+ | name (荤菜, 素菜, etc.), restaurant_id |
| rsp_orders | 订单主表 | Many | receipt_no, order_type, status, total, ordered_at |
| rsp_order_items | 订单明细（菜品） | Many | item_name, quantity, unit_price, total_price, station_id |
| rsp_receipts | 小票/收据 | Many | receipt_no, plain_text, receipt_type, semantic_json |
| rsp_tables | 餐桌信息 | Many | table_no (A区-A1), zone, capacity |

---

## Detailed Schema

### 1. rsp_restaurants (餐厅信息)

**Purpose:** Restaurant master data

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| id | UUID | a1b2c3d4-... | Primary key |
| name | String | 智能餐厅 | Restaurant name |
| address | String | 贵州省贵阳市 | Full address |
| timezone | String | Asia/Shanghai | Timezone for the restaurant |
| created_at | Timestamp | 2025-09-28T16:02:08 | Creation time |
| updated_at | Timestamp | 2025-09-28T16:02:08 | Last update time |

**Sample Data:**
```
Restaurant: 智能餐厅
Location: 贵州省贵阳市
```

---

### 2. rsp_stations (档口/厨房工作站)

**Purpose:** Kitchen stations where different food types are prepared

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| id | UUID | b2c3d4e5-... | Primary key |
| restaurant_id | UUID | a1b2c3d4-... | Foreign key to restaurant |
| name | String | 荤菜 | Station name (Chinese) |
| name_english | String | hot_dishes | Station name (English) |
| display_order | Integer | 1 | Display order in UI |
| active | Boolean | true | Is station active? |
| created_at | Timestamp | 2025-09-28T16:02:37 | Creation time |

**Sample Stations:**
- 荤菜 (hot_dishes) - Meat dishes station
- 素菜 (vegetable_dishes) - Vegetable station
- 汤 (soup) - Soup station

---

### 3. rsp_orders (订单主表)

**Purpose:** Order headers with totals and status

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| id | UUID | 7d38be40-... | Primary key |
| restaurant_id | UUID | a1b2c3d4-... | Foreign key to restaurant |
| receipt_id | UUID | 7685c207-... | Foreign key to receipt |
| table_id | UUID | 2e80fa70-... | Foreign key to table |
| receipt_no | String | 140877542510010001 | Receipt number from POS |
| order_type | String | dine_in | Order type (dine_in, takeout, delivery) |
| status | String | pending | Order status (pending, completed, cancelled) |
| ordered_at | Timestamp | 2025-10-01T03:42:25 | When order was placed |
| prepared_at | Timestamp | NULL | When order was prepared (if completed) |
| completed_at | Timestamp | NULL | When order was completed |
| subtotal | Float | 254.0 | Order subtotal (¥) |
| tax | Float | NULL | Tax amount (if applicable) |
| total | Float | 254.0 | Total amount (¥) |
| source | String | pos_printer | Order source (pos_printer, manual, online) |
| created_at | Timestamp | 2025-10-04T16:22:13 | Database record creation time |
| updated_at | Timestamp | 2025-10-04T16:22:13 | Last update time |

**Key Insights:**
- Orders are linked to tables (dine-in)
- Track lifecycle: ordered → prepared → completed
- Total amounts in Chinese Yuan (¥)
- Source tracking (POS printer vs manual entry)

---

### 4. rsp_order_items (订单明细/菜品)

**Purpose:** Individual dishes/items in each order

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| id | UUID | f7f053f5-... | Primary key |
| order_id | UUID | 8cb16bc6-... | Foreign key to order |
| menu_item_id | UUID | NULL | Foreign key to menu (if standardized) |
| item_name | String | 糟辣椒炒饭 | Dish name (can be free-text) |
| unit_price | Float | 22.0 | Price per unit (¥) |
| quantity | Integer | 1 | Quantity ordered |
| total_price | Float | 22.0 | Total for this item (unit_price × quantity) |
| station_id | UUID | NULL | Which kitchen station prepares this |
| raw_station | String | NULL | Raw station text from receipt |
| station_source | String | auto | How station was assigned (auto/manual) |
| status | String | pending | Item status (pending, preparing, ready, served) |
| is_combo_parent | Boolean | NULL | Is this a combo meal parent? |
| parent_combo_id | UUID | NULL | Parent combo if this is a combo item |
| is_return | Boolean | NULL | Is this a return/refund item? |
| created_at | Timestamp | 2025-09-30T11:14:17 | Creation time |
| updated_at | Timestamp | 2025-09-30T11:14:17 | Last update time |

**Sample Dishes:**
- 糟辣椒炒饭 (Fried rice with pickled chili) - ¥22
- 老凯里非遗酸汤 (Traditional sour soup) - various prices

**Key Insights:**
- Can track which station prepares each dish
- Supports combo meals (parent/child relationships)
- Supports returns/refunds (is_return flag)
- Free-text item names (from POS receipts)

---

### 5. rsp_receipts (小票/收据)

**Purpose:** Raw receipt data from POS printers

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| id | UUID | 7685c207-... | Primary key |
| sqlite_id | Integer | NULL | Legacy ID from SQLite sync |
| restaurant_id | UUID | a1b2c3d4-... | Foreign key to restaurant |
| receipt_no | String | 140877542510010001 | Receipt number |
| raw_esc_pos | String | NULL | Raw ESC/POS printer data (binary) |
| plain_text | String | 退菜单\n(分单)... | Plain text from receipt |
| source_ip | String | NULL | IP address of POS device |
| document_json | JSON | NULL | Structured document data |
| semantic_json | JSON | {"receipt_type": "return_slip"...} | Parsed semantic data |
| receipt_type | String | customer_order | Type (customer_order, return_slip, kitchen_order) |
| parsing_method | String | structured | How it was parsed (structured/llm/manual) |
| has_structured_data | Boolean | NULL | Has structured fields? |
| receipt_timestamp | Timestamp | 2025-10-01T03:42:56 | When receipt was printed |
| created_at | Timestamp | 2025-10-04T16:22:12 | Database record creation |
| processed_at | Timestamp | NULL | When receipt was processed |
| synced_from_sqlite | Boolean | true | Synced from legacy SQLite DB? |
| cumulative_total | Integer | 216 | Running total from POS |

**Sample Receipt (Plain Text):**
```
退菜单
(分单)
桌号: C区-C2
菜品数量
(退)老凯里非遗酸汤 1/份

退菜原因: 错点
```

**Key Insights:**
- Raw data from POS receipt printers
- Contains plain text of full receipt
- Parsed into semantic JSON
- Tracks return slips (退菜单)
- Has cumulative totals from POS

---

### 6. rsp_tables (餐桌信息)

**Purpose:** Restaurant table configuration

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| id | UUID | 67d0f4f1-... | Primary key |
| restaurant_id | UUID | a1b2c3d4-... | Foreign key to restaurant |
| table_no | String | A区-A1 | Full table identifier (zone + number) |
| zone | String | A区 | Table zone/area |
| table_number | String | A1 | Table number within zone |
| capacity | Integer | 4 | Seating capacity |
| active | Boolean | true | Is table active/available? |
| created_at | Timestamp | 2025-09-28T16:03:03 | Creation time |

**Sample Tables:**
- A区-A1 (Zone A, Table 1) - Capacity: 4
- B区-B3 (Zone B, Table 3) - Capacity: 6
- C区-C2 (Zone C, Table 2) - Capacity: 4

**Key Insights:**
- Tables organized by zones (A区, B区, C区)
- Each table has capacity (number of seats)
- Can be activated/deactivated

---

## Relationships

```
rsp_restaurants (1)
    ├──→ rsp_stations (many)
    ├──→ rsp_tables (many)
    ├──→ rsp_orders (many)
    └──→ rsp_receipts (many)

rsp_orders (1)
    ├──→ rsp_order_items (many)
    ├──→ rsp_tables (1) - which table
    └──→ rsp_receipts (1) - source receipt

rsp_order_items (many)
    └──→ rsp_stations (1) - prepared by which station
```

---

## Useful Queries

### Daily Sales by Restaurant
```python
query_operations_data(
    'rsp_orders',
    filters={'status': 'completed'},
    columns='id, total, ordered_at',
    order_by='-ordered_at'
)
```

### Popular Menu Items (Top 10)
```python
query_operations_data(
    'rsp_order_items',
    columns='item_name, SUM(quantity) as total_qty, SUM(total_price) as revenue',
    # Note: GROUP BY not supported by basic query tool
)
```

### Table Turnover Analysis
```python
# Get all completed orders by table
query_operations_data(
    'rsp_orders',
    filters={'status': 'completed', 'table_id': 'specific-table-uuid'},
    columns='id, table_id, ordered_at, completed_at, total'
)
```

### Station Performance
```python
# Get items prepared by each station
query_operations_data(
    'rsp_order_items',
    columns='station_id, item_name, status',
    filters={'status': 'pending'}
)
```

---

## Business Metrics to Calculate

### Revenue Metrics
- **Daily Revenue:** SUM(orders.total) WHERE status='completed' AND DATE(ordered_at)=today
- **Revenue by Zone:** Join orders → tables, GROUP BY zone
- **Revenue by Station:** Join order_items → stations, SUM(total_price)

### Operational Metrics
- **Average Order Value (AOV):** AVG(orders.total)
- **Orders per Table:** COUNT(orders) / COUNT(DISTINCT tables)
- **Average Prep Time:** AVG(completed_at - ordered_at)
- **Table Turnover Rate:** COUNT(completed orders per table per day)

### Menu Analytics
- **Top 10 Dishes:** ORDER BY SUM(quantity) DESC LIMIT 10
- **Revenue by Dish:** SUM(total_price) GROUP BY item_name
- **Return Rate:** COUNT(is_return=true) / COUNT(all items)

### Time-based Analysis
- **Peak Hours:** COUNT(orders) GROUP BY HOUR(ordered_at)
- **Weekday vs Weekend:** Compare order volumes
- **Prep Time by Station:** AVG(time) GROUP BY station

---

## Data Quality Notes

1. **NULL values common:**
   - `prepared_at`, `completed_at` - only set when order completes
   - `menu_item_id` - not always linked to menu master
   - `station_id` - sometimes auto-assigned, sometimes manual

2. **Free-text fields:**
   - `item_name` - can be any text from POS (not standardized)
   - `plain_text` in receipts - raw receipt text

3. **Data sources:**
   - `synced_from_sqlite` - some data migrated from legacy system
   - `source` - tracks if from POS printer vs manual entry

4. **Business logic:**
   - `is_return` - return/refund items have this flag
   - `receipt_type` - different types: customer_order, return_slip, kitchen_order
   - `order_type` - dine_in, takeout, delivery

---

## Next Steps for Bot Configuration

1. **Update system prompt** with actual column names
2. **Define useful KPIs** based on available data
3. **Create query examples** that work with real schema
4. **Add business context** - what questions do restaurant managers ask?
5. **Handle aggregations** - current tools don't support GROUP BY, may need enhancement
