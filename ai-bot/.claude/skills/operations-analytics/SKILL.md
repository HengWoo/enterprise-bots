---
name: operations-analytics
description: Restaurant operations analytics with STAR framework, Supabase RPC tools documentation, and KPI interpretation standards
version: 1.0.0
created: 2025-11-04
---

# Operations Analytics Skill

**Purpose:** Comprehensive guide for analyzing restaurant operations data using STAR framework methodology, Supabase RPC analytics tools, and industry-standard KPIs.

**When to load this skill:**
- User requests operational analysis or reports
- Need to analyze revenue, orders, dishes, or stations
- Generating STAR-format reports
- Interpreting restaurant KPIs

---

## 📊 STAR Analysis Framework

**Every operations report MUST use STAR structure:**

### S - Situation (情境)
**What to include:**
- Analysis time range (today, this week, this month)
- Comparison baseline (yesterday, last week, last month)
- Goals or expectations
- Business context (weather, holidays, special events)

**Example:**
```
S - 情境：
- 分析日期：2025年10月22日，周二营业日
- 对比基准：上周二 (10月15日)
- 目标营业额：¥4,000
- 特殊情况：天气阴雨，附近工地停工
```

---

### T - Task/Metrics (任务/指标)
**What to include:**
- Key performance indicators (KPIs)
- Actual vs. target comparison
- Trend direction (up/down/stable)
- Percentage changes

**Example:**
```
T - 关键指标：
- 营业额：¥3,799 (目标¥4,000，达成95%)
- 订单数：22单 (比上周二 -12%)
- 平均订单金额：¥172 (比平时 +15%)
- 翻台率：2.8次/桌 (目标3次，达成93%)
```

---

### A - Analysis (分析)
**What to include:**
- Why did these results occur?
- What patterns were discovered?
- Root cause analysis
- Contributing factors

**Example:**
```
A - 深度分析：
1. 订单量下降原因：
   - 下雨天气影响 (-8%)
   - 周二工作日正常低谷 (-4%)

2. 客单价提升原因：
   - 客户倾向高价值菜品
   - 套餐推广效果显著

3. 关键发现：
   - A区靠窗座位翻台率最高 (3.5次)
   - 荤菜站出品占比60% (超过素菜站)
   - 午市表现强于晚市 (55% vs 45%)
```

---

### R - Recommendation (建议)
**What to include:**
- Actionable next steps
- Priority ranking
- Expected impact
- Resource requirements

**Example:**
```
R - 行动建议：

优先级1 (立即执行)：
1. 推出"周中工作日套餐"
   - 预期效果：增加10-15单
   - 所需资源：菜单设计、前厅培训

优先级2 (本周完成)：
2. 优化A区座位安排
   - 预期效果：提升翻台率5-10%
   - 所需资源：调整桌椅布局

优先级3 (持续优化)：
3. 加强晚市营销
   - 预期效果：平衡午晚市营业额
   - 所需资源：社交媒体推广、团购优惠
```

---

## 🔧 Supabase RPC Analytics Tools (10 Tools)

### 1. get_daily_revenue(target_date)
**Purpose:** Query daily revenue summary

**Parameters:**
- `target_date` (string): Date in format "YYYY-MM-DD"

**Returns:**
```json
{
  "total_revenue": 3799.50,
  "order_count": 22,
  "avg_order_value": 172.68,
  "completed_orders": 20,
  "pending_orders": 1,
  "cancelled_orders": 1
}
```

**Use cases:**
- "今天的营业额是多少？"
- "昨天有多少个订单？"
- "本周一的平均订单金额是多少？"

**Analysis tips:**
- Compare with previous day/week/month
- Calculate growth rate
- Check if target achieved
- Analyze order completion rate

---

### 2. get_revenue_by_zone(start_date, end_date)
**Purpose:** Compare revenue across dining zones (A区、B区、C区)

**Parameters:**
- `start_date` (string): Start date "YYYY-MM-DD"
- `end_date` (string): End date "YYYY-MM-DD"

**Returns:**
```json
[
  {
    "zone": "A区",
    "total_revenue": 1520.00,
    "order_count": 9,
    "avg_order_value": 168.89
  },
  {
    "zone": "B区",
    "total_revenue": 1365.00,
    "order_count": 8,
    "avg_order_value": 170.63
  }
]
```

**Analysis tips:**
- Identify high/low performing zones
- Analyze seating preferences
- Optimize zone allocation
- Plan zone-specific promotions

---

### 3. get_top_dishes(start_date, end_date, top_n)
**Purpose:** Rank bestselling dishes

**Parameters:**
- `start_date` (string): Start date
- `end_date` (string): End date
- `top_n` (integer): Number of dishes to return (default 10)

**Returns:**
```json
[
  {
    "item_name": "糟辣椒炒饭",
    "total_quantity": 12,
    "total_revenue": 264.00,
    "order_count": 10,
    "avg_price": 22.00
  }
]
```

**Analysis tips:**
- Monitor popularity trends
- Plan inventory based on demand
- Identify underperforming dishes
- Cross-sell opportunities

---

### 4. get_station_performance(start_date, end_date)
**Purpose:** Analyze kitchen station output and revenue

**Parameters:**
- `start_date` (string): Start date
- `end_date` (string): End date

**Returns:**
```json
[
  {
    "station_name": "荤菜站",
    "station_name_english": "hot_dishes",
    "total_items": 45,
    "total_revenue": 2250.00,
    "avg_item_price": 50.00
  },
  {
    "station_name": "素菜站",
    "station_name_english": "vegetable_dishes",
    "total_items": 28,
    "total_revenue": 840.00,
    "avg_item_price": 30.00
  }
]
```

**Analysis tips:**
- Balance station workload
- Identify bottlenecks
- Optimize staffing
- Equipment capacity planning

---

### 5. get_hourly_revenue(target_date)
**Purpose:** Analyze revenue distribution across hours

**Parameters:**
- `target_date` (string): Date "YYYY-MM-DD"

**Returns:**
```json
[
  {
    "hour_of_day": 12,
    "order_count": 8,
    "total_revenue": 1360.00,
    "avg_order_value": 170.00
  }
]
```

**Key hours:**
- Lunch peak: 11:30-13:30 (hours 11-13)
- Dinner peak: 18:00-20:00 (hours 18-20)

**Analysis tips:**
- Identify peak hours
- Plan staffing schedules
- Optimize prep times
- Inventory management

---

### 6. get_table_turnover(start_date, end_date)
**Purpose:** Measure table utilization efficiency

**Parameters:**
- `start_date` (string): Start date
- `end_date` (string): End date

**Returns:**
```json
[
  {
    "zone": "A区",
    "table_no": "A1",
    "order_count": 5,
    "total_revenue": 860.00,
    "capacity": 4
  }
]
```

**Analysis tips:**
- Identify high-turnover tables
- Optimize seating arrangements
- VIP table strategy
- Capacity planning

---

### 7. get_return_analysis(start_date, end_date)
**Purpose:** Analyze dish returns and quality issues

**Parameters:**
- `start_date` (string): Start date
- `end_date` (string): End date

**Returns:**
```json
[
  {
    "item_name": "某菜品",
    "return_count": 3,
    "return_quantity": 3,
    "return_revenue_loss": 90.00,
    "return_rate": 0.15
  }
]
```

**Red flags:**
- Return rate > 5% = immediate investigation needed
- Return rate > 10% = critical quality issue

**Analysis tips:**
- Identify quality problems
- Calculate loss impact
- Prioritize fixes
- Track improvement

---

### 8. get_order_type_distribution(start_date, end_date)
**Purpose:** Analyze dine-in, takeout, delivery distribution

**Parameters:**
- `start_date` (string): Start date
- `end_date` (string): End date

**Returns:**
```json
[
  {
    "order_type": "dine_in",
    "order_count": 18,
    "total_revenue": 3060.00,
    "percentage_of_total": 0.75
  },
  {
    "order_type": "takeout",
    "order_count": 4,
    "total_revenue": 680.00,
    "percentage_of_total": 0.20
  }
]
```

**Analysis tips:**
- Channel growth trends
- Pricing strategy per channel
- Resource allocation
- Marketing focus

---

### 9. get_revenue_trend(start_date, end_date)
**Purpose:** Daily revenue trend over time period

**Parameters:**
- `start_date` (string): Start date
- `end_date` (string): End date

**Returns:**
```json
[
  {
    "date": "2025-10-22",
    "total_revenue": 3799.50,
    "order_count": 22,
    "avg_order_value": 172.68
  }
]
```

**Analysis tips:**
- Identify growth patterns
- Seasonal trends
- Week-over-week comparison
- Forecast future revenue

---

### 10. get_quick_stats(target_date)
**Purpose:** One-call dashboard for key daily metrics

**Parameters:**
- `target_date` (string): Date "YYYY-MM-DD"

**Returns:**
```json
{
  "total_revenue": 3799.50,
  "order_count": 22,
  "avg_order_value": 172.68,
  "top_dish": "糟辣椒炒饭 (12份)",
  "peak_hour": "12:00 (8单)",
  "busiest_zone": "A区 (¥1,520)",
  "table_turnover_avg": 2.8
}
```

**Use cases:**
- "给我看看今天的概况"
- "今天表现怎么样？"
- "快速统计"

---

## 📊 Restaurant KPI Standards

### 1. Table Turnover Rate (翻台率)
**Definition:** Average times each table serves customers per day/session

**Calculation:**
```
翻台率 = 订单数 / 餐桌数
```

**Benchmark Standards:**
- **Excellent:** ≥ 3.0 times/table (lunch), ≥ 2.5 times/table (dinner)
- **Good:** 2.5-3.0 times (lunch), 2.0-2.5 times (dinner)
- **Needs Improvement:** < 2.5 times (lunch), < 2.0 times (dinner)

**Interpretation:**
```
A区-A1: 5次翻台 ✅ (优秀 - 靠窗位置受欢迎)
B区-B3: 2次翻台 ⚠️ (需改进 - 位置偏僻或服务速度慢)
C区-C5: 1次翻台 ❌ (严重 - 检查座位布局和流程)
```

---

### 2. Average Order Value / Customer Spending (客单价)
**Definition:** Average revenue per order

**Calculation:**
```
客单价 = 总营业额 / 订单数
```

**Benchmark Standards:**
- **Excellent:** ≥ ¥180
- **Good:** ¥150-180
- **Acceptable:** ¥120-150
- **Low:** < ¥120

**Factors affecting AOV:**
- Menu pricing
- Upselling effectiveness
- Customer demographics
- Promotions

**Improvement strategies:**
- Bundle meals/sets
- Recommend premium dishes
- Train staff on upselling
- Optimize menu layout

---

### 3. Return Rate (退菜率)
**Definition:** Percentage of dishes returned

**Calculation:**
```
退菜率 = 退菜次数 / 总订单项数 × 100%
```

**Benchmark Standards:**
- **Excellent:** < 1%
- **Acceptable:** 1-3%
- **Warning:** 3-5%
- **Critical:** > 5%

**Action thresholds:**
- Single dish return rate > 5% → Immediate kitchen investigation
- Single dish return rate > 10% → Remove from menu, investigate suppliers
- Overall return rate > 3% → Review quality control processes

---

### 4. Peak Hour Revenue Distribution
**Key time slots:**
- Lunch: 11:30-13:30 (should be ≥ 45% of daily revenue)
- Dinner: 18:00-20:00 (should be ≥ 40% of daily revenue)

**Healthy distribution:**
```
午市：45-50%
晚市：40-45%
其他：5-15%
```

**Red flags:**
```
午市 > 60% → 过度依赖午市，晚市需加强
晚市 < 30% → 晚市营销不足
```

---

### 5. Station Balance Index
**Definition:** Distribution of revenue across kitchen stations

**Healthy range:**
```
荤菜站：40-50%
素菜站：30-40%
汤品站：15-25%
```

**Warning signs:**
```
荤菜站 > 60% → 菜单失衡，增加素菜品种
某站 < 10% → 工作站利用不足
```

---

## 🚨 Data Analysis Best Practices

### ✅ Always Provide Context

**Bad example:**
```
营业额：¥3,799
订单数：22
```

**Good example:**
```
营业额：¥3,799
- vs 目标 (¥4,000): -5% ❌
- vs 昨天 (¥3,600): +5.5% ✅
- vs 上周二 (¥4,100): -7.3% ↓
- vs 月平均 (¥3,700): +2.7% ↑

💡 周二客流正常偏低，但比昨天和月平均都高，表现良好
```

---

### ✅ Explain WHY, Not Just WHAT

**Bad example:**
```
订单量下降12%
```

**Good example:**
```
订单量下降12%，原因分析：
1. 天气因素：下雨天客流减少 (影响-8%)
2. 工作日效应：周二本身客流较少 (影响-4%)
3. 缓解因素：客单价提升15%，部分弥补了订单下降
4. 预期：明天天气转晴，预计恢复正常水平
```

---

### ✅ Give Actionable Recommendations

**Bad example:**
```
营业额不理想，需要改进
```

**Good example:**
```
建议措施（按优先级）：

🔴 立即执行 (今日/明日)：
1. 明天天气转晴，预计客流恢复
   → 提前备货热销菜品（糟辣椒炒饭+30%）
   → 安排充足人手应对午市高峰

🟡 本周完成：
2. 推出"周中工作日套餐"
   → 目标：增加10-15单周二订单
   → 定价：¥48-68（保持客单价）

🟢 持续优化：
3. 加强社交媒体营销
   → 重点推广晚市优惠
   → 目标：平衡午晚市比例
```

---

### ✅ Flag Anomalies and Issues

**Critical issues to always mention:**
```
⚠️ 某菜品退菜率15% → 严重质量问题！
⚠️ 某工作站产出下降50% → 可能设备故障
⚠️ 某时段订单为0 → 系统故障或数据缺失
⚠️ 营业额异常偏高/偏低 (±30%) → 核实数据准确性
```

---

## 📝 Report Templates

### Template 1: Daily Operations Summary

```html
<h2>📊 [DATE] 营业分析报告</h2>

<h3>S - 情境</h3>
<ul>
  <li>分析日期：[DATE]，星期[X]</li>
  <li>对比基准：昨日/上周同日/月平均</li>
  <li>目标营业额：¥[TARGET]</li>
  <li>特殊情况：[天气/节假日/活动]</li>
</ul>

<h3>T - 关键指标</h3>
<ul>
  <li>营业额：¥[REVENUE] ([TARGET_ACHIEVEMENT]%达成)</li>
  <li>订单数：[ORDERS]单 (比[BASELINE] [CHANGE]%)</li>
  <li>客单价：¥[AOV] (比平时 [CHANGE]%)</li>
  <li>翻台率：[TURNOVER]次/桌 (目标[TARGET]次)</li>
</ul>

<h3>A - 深度分析</h3>
<p><strong>1. 为什么会出现这些结果？</strong></p>
<ul>
  <li>[原因1]：影响[X]%</li>
  <li>[原因2]：影响[Y]%</li>
</ul>

<p><strong>2. 发现了什么模式？</strong></p>
<ul>
  <li>[模式1]</li>
  <li>[模式2]</li>
</ul>

<h3>R - 行动建议</h3>
<p><strong>优先级1 (立即执行)：</strong></p>
<ol>
  <li>[建议1] - 预期效果：[IMPACT]</li>
</ol>

<p><strong>优先级2 (本周完成)：</strong></p>
<ol>
  <li>[建议2] - 预期效果：[IMPACT]</li>
</ol>
```

---

### Template 2: Station Performance Analysis

```html
<h2>🔧 厨房工作站业绩分析</h2>

<h3>各工作站产出对比</h3>
<table>
  <tr>
    <th>工作站</th>
    <th>出品数量</th>
    <th>营业额</th>
    <th>占比</th>
    <th>评价</th>
  </tr>
  <tr>
    <td>荤菜站</td>
    <td>[ITEMS]</td>
    <td>¥[REVENUE]</td>
    <td>[PERCENTAGE]%</td>
    <td>[✅/⚠️/❌]</td>
  </tr>
</table>

<h3>💡 工作站优化建议</h3>
<ul>
  <li><strong>荤菜站：</strong>[建议]</li>
  <li><strong>素菜站：</strong>[建议]</li>
  <li><strong>汤品站：</strong>[建议]</li>
</ul>
```

---

## 🎯 Key Principles

**Remember:**
1. **Always use STAR framework** - Every report needs S-T-A-R structure
2. **Provide context** - Numbers alone are meaningless
3. **Explain why** - Root cause analysis is critical
4. **Give actionable advice** - Recommendations must be specific and prioritized
5. **Flag issues** - Call out anomalies and problems immediately
6. **Think like an analyst** - Transform data into insights

**You are not a database query tool - you are a restaurant operations consultant!**

---

**Skill Version:** 1.0.0
**Created:** 2025-11-04
**For:** operations_assistant bot
**Dependencies:** Supabase RPC functions, Campfire MCP tools
