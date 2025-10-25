---
name: Campfire Financial Analysis
description: Analyzes Chinese financial statements and Excel workbooks. Calculates financial ratios (ROE, ROA, margins). Uses 16 specialized MCP tools for transparent Excel analysis. Validates account structures before calculations. Generates bilingual (Chinese/English) financial reports. Use when analyzing Excel files with financial data or when users ask about profitability, revenue, expenses, cost structure, or investment analysis.
---

# Campfire Financial Analysis

## Quick Start

When users upload Excel financial statements or ask about financial analysis:

1. **Validate first** - Always use `validate_account_structure` before calculations
2. **Extract data** - Use simple MCP tools (get_excel_info, show_excel_visual, read_excel_region)
3. **Calculate metrics** - Apply financial formulas (ROE, ROA, margins)
4. **Generate report** - Create comprehensive Chinese/English analysis

## Core Capabilities

### Financial Ratio Analysis

**Key Metrics:**
- **ROE (净资产收益率)** = 净利润 / 股东权益 × 100%
- **ROA (总资产收益率)** = 净利润 / 总资产 × 100%
- **Gross Margin (毛利率)** = (营业收入 - 营业成本) / 营业收入 × 100%
- **Net Profit Margin (净利率)** = 净利润 / 营业收入 × 100%
- **Operating Margin (营业利润率)** = 营业利润 / 营业收入 × 100%

Complete formulas and Chinese terminology: See [reference/ratios.md](reference/ratios.md)

### MCP Tools Available (16 Tools)

**Simple Tools (5) - Data Extraction:**
1. `get_excel_info` - Get file structure (rows, columns, sheets)
2. `show_excel_visual` - Display data in readable format
3. `search_in_excel` - Find cells containing specific terms
4. `read_excel_region` - Extract rectangular regions (raw data)
5. `calculate` - Basic math (sum, average, max, min)

**Navigation Tools (3) - LSP-like Financial Navigation:**
6. `find_account` - Search accounts by name pattern
7. `get_financial_overview` - High-level financial structure
8. `get_account_context` - Get account with parent/children context

**Thinking Tools (3) - Reflection & Validation:**
9. `think_about_financial_data` - Assess data sufficiency
10. `think_about_analysis_completeness` - Check completeness
11. `think_about_assumptions` - Validate assumptions

**Memory Tools (3) - Session Management:**
12. `save_analysis_insight` - Store insights for future reference
13. `get_session_context` - View session history and progress
14. `write_memory_note` - Document patterns and knowledge

**Validation Tools (1) - Structure Validation:**
15. `validate_account_structure` - **MANDATORY** validation before calculations

## Analysis Workflow

### Step 1: Validation (MANDATORY)

**CRITICAL:** NEVER perform calculations without validation!

```
1. Call validate_account_structure tool
2. Show account hierarchy to user
3. Ask confirmation questions:
   - "Is this account structure correct?"
   - "What depreciation/amortization periods apply?"
   - "Should I use only leaf accounts to avoid double counting?"
4. Document user confirmations
5. Only proceed after explicit user approval
```

**Why validation matters:**
- Prevents double-counting errors (e.g., using parent + child accounts)
- Confirms depreciation assumptions (typically 3-5 years)
- Ensures accurate total calculations

### Step 2: Data Exploration

```
1. get_excel_info() → Understand file structure
2. show_excel_visual() → Examine layout
3. search_in_excel("Total") → Find subtotal columns
4. search_in_excel("收入") → Locate revenue accounts
5. get_financial_overview() → See top-level structure
```

### Step 3: Intelligent Extraction

```
1. find_account("营业收入") → Search revenue accounts
2. get_account_context("营业收入") → Get revenue details with context
3. read_excel_region() → Extract specific data ranges
4. think_about_financial_data() → Assess data sufficiency
```

### Step 4: Calculation & Verification

```
1. calculate(type="sum", values=[...]) → Calculate totals
2. Apply financial formulas (see ratios.md)
3. think_about_assumptions() → Validate calculation approach
4. Cross-verify with account structure
```

### Step 5: Analysis & Insights

```
1. Compare with industry benchmarks (see ratios.md)
2. Identify trends and patterns
3. save_analysis_insight() → Store key findings
4. think_about_analysis_completeness() → Check if all requirements met
```

### Step 6: Report Generation

```
1. Generate bilingual (Chinese/English) report
2. Include all validated assumptions
3. Show calculation audit trail
4. Provide strategic recommendations
5. Use Chinese report format (see chinese-formats.md)
```

## Chinese Financial Terminology

**Revenue (收入):**
- 营业收入 = Operating Revenue
- 食品收入 = Food Revenue
- 酒水收入 = Beverage Revenue
- 其他收入 = Other Revenue

**Costs (成本):**
- 营业成本 = Operating Cost
- 食品成本 = Food Cost
- 酒水成本 = Beverage Cost

**Expenses (费用):**
- 人工成本 = Labor Cost
- 租金 = Rent
- 水电费 = Utilities
- 折旧摊销 = Depreciation & Amortization

**Profit (利润):**
- 营业利润 = Operating Profit
- 利润总额 = Total Profit
- 净利润 = Net Profit

Complete mapping: See [reference/chinese-formats.md](reference/chinese-formats.md)

## Multi-Turn Intelligence

The agent supports progressive analysis refinement across conversation turns:

**Turn 1:** User uploads file → Validate structure → Explore data
**Turn 2:** User asks specific question → Navigate to relevant accounts → Extract data
**Turn 3:** User requests deeper analysis → Calculate metrics → Generate insights
**Turn 4:** Follow-up questions → Reference session context → Provide comprehensive answer

**Use memory tools to maintain context:**
- `get_session_context()` - Review what's been done
- `save_analysis_insight()` - Store discoveries
- `write_memory_note()` - Document patterns

## Industry Benchmarks

**Restaurant Industry:**
- Gross Margin: 60-70%
- Net Profit Margin: 5-10%
- Food Cost: 28-35%
- Labor Cost: 25-35%
- Rent: 5-10%

**Retail Industry:**
- Gross Margin: 30-50%
- Net Profit Margin: 3-5%
- Inventory Turnover: 4-8 times/year

**Manufacturing:**
- Gross Margin: 20-40%
- Net Profit Margin: 5-15%
- ROA: 5-10%
- ROE: 10-20%

Complete benchmarks: See [reference/ratios.md](reference/ratios.md)

## Error Prevention

**Common Mistakes to Avoid:**

❌ **Double Counting**
- Using both parent account AND child accounts
- Solution: `validate_account_structure` + use only leaf accounts

❌ **Wrong Period Assumptions**
- Assuming 5-year depreciation when it's actually 3 years
- Solution: Ask user to confirm assumptions explicitly

❌ **Ignoring Account Hierarchy**
- Treating all accounts as equals without considering parent-child relationships
- Solution: Use `get_account_context()` to see relationships

❌ **Skipping Validation**
- Calculating without confirming structure
- Solution: ALWAYS call `validate_account_structure` first

## When to Use This Skill

**Trigger Scenarios:**
- User uploads Excel file with financial data
- User asks about ROE, ROA, profitability, margins
- User mentions "财务报表", "损益表", "资产负债表"
- User requests revenue analysis, cost analysis, expense breakdown
- User wants to compare periods or analyze trends
- User asks about Chinese financial terms or accounting standards

**Keywords that should trigger this skill:**
- ROE, ROA, margins, profitability, 盈利能力
- Financial statement, income statement, balance sheet
- 财务报表, 损益表, 资产负债表, 现金流量表
- Revenue, cost, expense, 收入, 成本, 费用
- Excel analysis, spreadsheet analysis, 表格分析
- Investment analysis, 投资分析
- Depreciation, amortization, 折旧, 摊销
