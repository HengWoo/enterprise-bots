# 运营数据库 - 快速参考表

## 1. 表结构速查表

| 表名 | 记录数 | 列数 | 主键 | 外键数 | 大小 | 质量评分 | 用途 |
|------|--------|------|------|--------|------|---------|------|
| rsp_restaurants | 1 | 6 | UUID | 0 | <1KB | 10/10 | 餐厅配置 |
| rsp_stations | 4-6 | 8 | UUID | 1 | <5KB | 10/10 | 工作站 |
| rsp_tables | 15-30 | 8 | UUID | 1 | <5KB | 9/10 | 餐桌配置 |
| rsp_orders | ~3000 | 13 | UUID | 3 | ~10MB | 7/10 | 订单主表 |
| rsp_order_items | ~9000 | 13 | UUID | 2 | ~15MB | 6.5/10 | 菜品明细 |
| rsp_receipts | ~1200 | 15 | UUID | 1 | ~50MB | 7.5/10 | POS小票 |

---

## 2. 字段完整性矩阵

### rsp_orders 字段完整性

| 字段 | 类型 | 非空 | NULL% | 质量 | 备注 |
|------|------|------|-------|------|------|
| id | UUID | ✅ | 0% | ✅ | 主键 |
| restaurant_id | UUID | ✅ | 0% | ✅ | FK |
| receipt_id | UUID | ⚠️ | 5% | ✅ | 外卖可能无小票 |
| table_id | UUID | ⚠️ | 25% | ✅ | 外卖/外带为NULL |
| receipt_no | VARCHAR | ✅ | 0% | ✅ | POS凭证号 |
| order_type | VARCHAR | ✅ | 0% | ✅ | dine_in/takeout/delivery |
| status | VARCHAR | ✅ | 0% | 🔴 | 多为pending，使用total>0判断 |
| ordered_at | TIMESTAMP | ✅ | 0% | ✅ | 下单时间 |
| prepared_at | TIMESTAMP | ⚠️ | 95% | 🔴 | 几乎不填 |
| completed_at | TIMESTAMP | ⚠️ | 95% | 🔴 | 几乎不填 |
| subtotal | FLOAT | ✅ | 0% | ⚠️ | 精度问题(FLOAT) |
| tax | FLOAT | ⚠️ | 70% | ⚠️ | 多为NULL |
| total | FLOAT | ✅ | 0% | ✅ | 主要的金额字段 |

### rsp_order_items 字段完整性

| 字段 | 类型 | 非空 | NULL% | 质量 | 备注 |
|------|------|------|-------|------|------|
| id | UUID | ✅ | 0% | ✅ | 主键 |
| order_id | UUID | ✅ | 0% | ✅ | FK |
| menu_item_id | UUID | ⚠️ | 99% | 🔴 | 主数据链接失效！ |
| item_name | VARCHAR | ✅ | 0% | 🔴 | 自由文本，多种写法 |
| unit_price | FLOAT | ✅ | 0% | ⚠️ | 精度问题 |
| quantity | INT | ✅ | 0% | ✅ | 数量准确 |
| total_price | FLOAT | ✅ | 0% | ⚠️ | 精度问题 |
| station_id | UUID | ⚠️ | 20% | ⚠️ | 缺失率高 |
| raw_station | VARCHAR | ⚠️ | 30% | ⚠️ | 原始文本，用于回填 |
| station_source | VARCHAR | ⚠️ | 40% | ⚠️ | auto/manual |
| status | VARCHAR | ⚠️ | 60% | 🔴 | 多为NULL |
| is_combo_parent | BOOLEAN | ⚠️ | 95% | ⚠️ | 组合菜支持不完整 |
| parent_combo_id | UUID | ⚠️ | 99% | ⚠️ | 同上 |
| is_return | BOOLEAN | ⚠️ | 90% | 🔴 | 退菜标记不准确 |

---

## 3. NULL值分布热力图

```
表\字段                高  中  低
─────────────────────────────────
rsp_orders
├─ prepared_at       ███ 95% 🔴🔴🔴
├─ completed_at      ███ 95% 🔴🔴🔴
├─ tax               ██░ 70% 🔴🔴
├─ receipt_id        █░░  5% ✅
├─ table_id          ██░ 25% ✅(正常)
└─ (其他)            ░░░  0% ✅

rsp_order_items
├─ menu_item_id      ███ 99% 🔴🔴🔴
├─ is_return         ███ 90% 🔴🔴🔴
├─ is_combo_parent   ███ 95% 🔴🔴🔴
├─ parent_combo_id   ███ 99% 🔴🔴🔴
├─ status            ██░ 60% 🔴🔴
├─ station_id        ██░ 20% 🔴
├─ raw_station       ██░ 30% 🔴
├─ station_source    ██░ 40% 🔴
└─ (其他)            ░░░  0% ✅

rsp_receipts
├─ raw_esc_pos       ██░ 40% ⚠️
├─ source_ip         ██░ 30% ⚠️
├─ document_json     ██░ 20% ⚠️
├─ processed_at      █░░  5% ✅
└─ (其他)            ░░░  0% ✅
```

**图例:**
- `███` = NULL率 > 80% (严重问题)
- `██░` = NULL率 20-80% (需要改进)
- `█░░` = NULL率 < 20% (可接受)
- `░░░` = NULL率 < 5% (优秀)

---

## 4. 关键问题优先级对照表

| 问题ID | 问题 | 影响表 | 受影响字段 | 严重程度 | 修复难度 | 优先级 |
|--------|------|--------|-----------|---------|---------|--------|
| Q001 | item_name未规范化 | rsp_order_items | item_name | 🔴HIGH | 中等 | **P0** |
| Q002 | 订单status逻辑不当 | rsp_orders | status | 🔴HIGH | 低 | **P0** |
| Q003 | menu_item_id缺失 | rsp_order_items | menu_item_id | 🔴HIGH | 中等 | **P0** |
| Q004 | station_id缺失20% | rsp_order_items | station_id | 🟡MID | 中等 | **P1** |
| Q005 | prepared_at/completed_at | rsp_orders | prepared_at, completed_at | 🟡MID | 高 | **P1** |
| Q006 | orders/receipts重复 | 两表 | 所有金额字段 | 🟡MID | 高 | **P1** |
| Q007 | 金额精度问题 | 两表 | subtotal, total_price等 | 🟡MID | 低 | **P1** |
| Q008 | table_no冗余 | rsp_tables | table_no, zone, table_number | 🟢LOW | 低 | **P2** |
| Q009 | is_return准确率低 | rsp_order_items | is_return | 🟢LOW | 中等 | **P2** |
| Q010 | semantic_json不稳定 | rsp_receipts | semantic_json | 🟢LOW | 高 | **P2** |

---

## 5. 索引清单与优化建议

### 现有索引

| 表 | 索引名 | 类型 | 列 | 优化 |
|----|--------|------|-----|------|
| rsp_orders | pk | PRIMARY | id | ✅ |
| rsp_orders | fk_restaurant | FK | restaurant_id | ✅ |
| rsp_orders | idx_receipt_no | UNIQUE | receipt_no | ✅ |
| rsp_orders | idx_ordered_at | INDEX | ordered_at | ✅ |
| rsp_orders | idx_order_type | INDEX | order_type | ✅ |
| rsp_order_items | pk | PRIMARY | id | ✅ |
| rsp_order_items | fk_order | FK | order_id | ✅ |
| rsp_order_items | idx_item_name | INDEX | item_name | 🔴 (低效) |
| rsp_tables | pk | PRIMARY | id | ✅ |
| rsp_tables | idx_zone | INDEX | zone | ✅ |
| rsp_receipts | pk | PRIMARY | id | ✅ |
| rsp_receipts | idx_receipt_no | UNIQUE | receipt_no | ✅ |
| rsp_receipts | idx_created_at | INDEX | created_at | ✅ |

### 建议新增索引

| 表 | 列 | 类型 | 原因 |
|-----|-----|------|------|
| rsp_order_items | order_id, item_name | COMPOSITE | 快速查找订单的菜品 |
| rsp_order_items | station_id | INDEX | 按工作站统计 |
| rsp_orders | restaurant_id, ordered_at | COMPOSITE | 日期范围查询 |
| rsp_tables | restaurant_id, zone | COMPOSITE | 按区域查询 |

---

## 6. 数据一致性检查清单

运营人员可以定期使用以下查询检查数据一致性：

### 检查1: 订单总金额一致性

```sql
-- 检查orders.total是否等于order_items的sum
SELECT
    o.id,
    o.receipt_no,
    o.total as order_total,
    SUM(oi.total_price) as items_total,
    ABS(o.total - SUM(oi.total_price)) as diff
FROM rsp_orders o
LEFT JOIN rsp_order_items oi ON o.id = oi.order_id
GROUP BY o.id, o.receipt_no, o.total
HAVING ABS(o.total - SUM(oi.total_price)) > 0.01
LIMIT 100;

-- 预期结果：返回空 (没有差异)
-- 发现差异：检查是否有数据导入错误
```

### 检查2: 菜品项目的quantity-price一致性

```sql
-- 检查 total_price ≈ unit_price × quantity
SELECT
    id,
    item_name,
    unit_price,
    quantity,
    total_price,
    (unit_price * quantity) as calc_total,
    ABS(total_price - (unit_price * quantity)) as diff
FROM rsp_order_items
WHERE ABS(total_price - (unit_price * quantity)) > 0.01
LIMIT 100;

-- 预期结果：返回空 (所有计算都一致)
```

### 检查3: orders和receipts的receipt_no一致性

```sql
-- 检查是否所有orders都有matching receipt
SELECT
    COUNT(DISTINCT o.receipt_no) as orders_count,
    COUNT(DISTINCT r.receipt_no) as receipts_count,
    COUNT(DISTINCT o.receipt_no) - COUNT(DISTINCT r.receipt_no) as diff
FROM rsp_orders o
LEFT JOIN rsp_receipts r ON o.receipt_no = r.receipt_no;

-- 预期结果：diff ≈ 0 或很小 (允许5%缺失率)
```

### 检查4: 菜品-工作站关联

```sql
-- 检查station_id未填充的比例
SELECT
    ROUND(COUNT(*) FILTER (WHERE station_id IS NULL)::FLOAT / COUNT(*) * 100, 2) as missing_rate
FROM rsp_order_items;

-- 预期结果：< 25% (目标 < 5%)
```

### 检查5: 退菜比例

```sql
-- 检查退菜数据
SELECT
    ROUND(COUNT(*) FILTER (WHERE is_return = true)::FLOAT / COUNT(*) * 100, 2) as return_rate
FROM rsp_order_items;

-- 预期结果：1-3% (健康的退菜率)
```

---

## 7. 常见错误SQL查询与修正

### ❌ 错误示例1: 使用status='completed'

```sql
-- 错误！大部分订单status为pending
SELECT SUM(total) as revenue
FROM rsp_orders
WHERE status = 'completed'
  AND DATE(ordered_at) = CURRENT_DATE;
-- 返回值偏低 (丢失90%数据)
```

### ✅ 正确做法:

```sql
-- 正确！使用total>0判断订单完成
SELECT SUM(total) as revenue
FROM rsp_orders
WHERE total > 0  -- 有总金额 = 订单已结算
  AND DATE(ordered_at AT TIME ZONE 'Asia/Shanghai') = CURRENT_DATE;

-- 或者使用RPC函数（推荐）
SELECT * FROM get_daily_revenue(CURRENT_DATE);
```

---

### ❌ 错误示例2: 直接用cumulative_total计算营业额

```sql
-- 错误！cumulative_total是POS的运行累计，会重置
SELECT SUM(cumulative_total)
FROM rsp_receipts
WHERE DATE(created_at) = CURRENT_DATE;
-- 结果错误，POS重启会导致计算失败
```

### ✅ 正确做法:

```sql
-- 正确！用day range
SELECT MAX(cumulative_total) - MIN(cumulative_total) as daily_revenue
FROM rsp_receipts
WHERE DATE(created_at AT TIME ZONE 'Asia/Shanghai') = CURRENT_DATE
  AND receipt_type = 'customer_order';
```

---

### ❌ 错误示例3: item_name分组不规范

```sql
-- 错误！同一菜品有多种写法，分组会分散
SELECT item_name, SUM(quantity)
FROM rsp_order_items
GROUP BY item_name
ORDER BY 2 DESC;
-- "糟辣椒炒饭" 和 "糟辣椒 炒饭" 被分别统计
```

### ✅ 正确做法:

```sql
-- 正确！规范化item_name（使用TRIM, LOWER）
SELECT TRIM(LOWER(item_name)) as dish, SUM(quantity)
FROM rsp_order_items
GROUP BY TRIM(LOWER(item_name))
ORDER BY 2 DESC;

-- 或者使用RPC函数（已规范化）
SELECT * FROM get_top_dishes(CURRENT_DATE, CURRENT_DATE, 10);
```

---

## 8. 性能基准线

### 查询性能目标

| 查询类型 | 目标 | 现状 | 状态 |
|---------|------|------|------|
| 单日营业额 | <100ms | ~50ms | ✅ 优秀 |
| 30天趋势 | <500ms | ~200ms | ✅ 优秀 |
| 菜品排行 | <1s | ~300ms | ✅ 优秀 |
| 工作站业绩 | <1s | ~400ms | ✅ 优秀 |
| 表格翻台率 | <1s | ~600ms | ✅ 优秀 |

### 表大小增长预测

| 时间点 | rsp_orders | rsp_order_items | rsp_receipts | 总大小 |
|--------|-----------|-----------------|------------|-------|
| 2025-10 | ~10 MB | ~15 MB | ~50 MB | ~80 MB |
| 2026-01 | ~15 MB | ~22 MB | ~75 MB | ~120 MB |
| 2026-10 | ~40 MB | ~60 MB | ~200 MB | ~310 MB |
| 2027-10 | ~80 MB | ~120 MB | ~400 MB | ~610 MB |

**结论:** 短期内（2年内）无需分区或存档

---

## 9. RPC函数调用速查表

### 日常分析

| 问题 | 调用 | 示例 |
|------|------|------|
| 今日营业额 | `get_daily_revenue()` | 每日晨会 |
| 各区域业绩 | `get_revenue_by_zone(start, end)` | 周报 |
| 热销菜品 | `get_top_dishes(start, end, 10)` | 周报 |
| 工作站业绩 | `get_station_performance(start, end)` | 月报 |

### 趋势分析

| 问题 | 调用 | 周期 |
|------|------|------|
| 周营业趋势 | `get_revenue_trend('2025-10-19', '2025-10-25')` | 周 |
| 月营业趋势 | `get_revenue_trend('2025-10-01', '2025-10-31')` | 月 |
| 时段分布 | `get_hourly_revenue(CURRENT_DATE)` | 日 |

### 运营分析

| 问题 | 调用 | 用途 |
|------|------|------|
| 翻台效率 | `get_table_turnover(start, end)` | 餐桌优化 |
| 退菜分析 | `get_return_analysis(start, end)` | 质量控制 |
| 订单类型 | `get_order_type_distribution(start, end)` | 渠道分析 |

---

## 10. 数据入库流程

```
POS机
  │
  ├─→ 打印收据(ESC/POS格式)
  │
  ├─→ 同步到 rsp_receipts 表
  │   ├─ receipt_no (唯一)
  │   ├─ plain_text (原始文本)
  │   ├─ semantic_json (LLM解析)
  │   └─ cumulative_total
  │
  ├─→ 触发 ETL 流程
  │   ├─ 解析 semantic_json
  │   ├─ 创建 rsp_orders 记录
  │   ├─ 创建 rsp_order_items 记录
  │   └─ 分配 station_id
  │
  └─→ 数据可查询 (~5秒延迟)

质量检查点:
  ✓ receipt_no 唯一性
  ✓ 金额完整性
  ✓ 菜品名称合法性
  ✓ 工作站分配有效性

常见问题:
  ⚠️ 菜品名称解析失败 → 手动映射
  ⚠️ station_id 分配失败 → 默认分配
  ⚠️ is_return 判断失败 → 需人工复核
```

---

## 更新历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| 1.0 | 2025-10-25 | 初版发布 |

---

**最后更新:** 2025-10-25
**下次审查:** 2025-11-25
