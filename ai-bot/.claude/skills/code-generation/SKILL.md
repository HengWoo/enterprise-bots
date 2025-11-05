---
name: code-generation
description: "Generate and execute code safely for data analysis and transformations"
version: 1.0.0
author: Campfire AI Team
license: MIT
category: development
priority: high
---

# Code Generation Skill

## Overview

This skill enables safe code generation for Python scripts and SQL queries to perform complex data analysis, financial calculations, and operations analytics. All generated code is validated with linting tools before execution in a sandboxed Docker environment.

## When to Use Code Generation

Generate code instead of using tools when:
- ✅ Complex data transformations (>3 steps)
- ✅ Precise calculations requiring type safety
- ✅ Reusable logic needed across requests
- ✅ Performance-critical operations
- ✅ Financial calculations with verification
- ✅ Operations analytics with trend analysis

Do NOT generate code when:
- ❌ Simple operations (use existing tools)
- ❌ One-time calculations
- ❌ Unsafe operations (file system modifications)
- ❌ User data manipulation (updates/deletes)

## Supported Languages

### Python (Priority 1)
- **Use cases:** Financial calculations, data analysis, trend detection
- **Templates:** Financial analysis, operations analytics
- **Validation:** ruff + mypy
- **Execution:** Docker sandbox via Bash tool

### SQL (Priority 2)
- **Use cases:** Data queries, report generation
- **Templates:** Revenue reports, comparison queries, top items
- **Validation:** Safety checks (read-only enforcement)
- **Execution:** SQLite read-only mode

## Workflow: Generate Python Data Analysis

### Step 1: Identify Requirements

Before generating code, determine:
- What analysis is needed?
- What data schema is provided?
- What calculations are required?
- What outputs are expected?

**Example User Request:**
> "Analyze this sales data and calculate profit margins"

**Requirements Analysis:**
- Analysis type: Financial calculations
- Data schema: `{"date": "datetime", "revenue": "float", "cost": "float"}`
- Calculations: Profit margin, total revenue, total cost
- Output: Summary with insights

### Step 2: Generate Code

Use `CodeGenerator` from `src.codegen` module:

```python
from src.codegen import CodeGenerator, TemplateType

# Initialize generator
generator = CodeGenerator()

# Generate Python script
code = generator.generate_python_script(
    purpose="Calculate profit margins from sales data",
    template_type=TemplateType.FINANCIAL_ANALYSIS,
    data_schema={
        "date": "datetime",
        "revenue": "float",
        "cost": "float"
    },
    calculation_types=["profit_margin", "growth_rate"]
)

# Result: GeneratedCode object with:
# - code.code (str): Generated Python script
# - code.file_path (str): Path to saved file
# - code.validated (bool): Validation status
```

### Step 3: Validate Code

Validate with ruff and mypy before execution:

```python
from src.codegen import lint_python_code, format_validation_report

# Lint the generated code
validation = lint_python_code(code.code, check_types=True)

if not validation.valid:
    # Show errors to user
    report = format_validation_report(validation)
    print(report)

    # Attempt auto-fix if possible
    if validation.auto_fixable:
        from src.codegen import auto_fix_python_code
        fixed_code = auto_fix_python_code(code.code)

        # Re-validate
        validation = lint_python_code(fixed_code)
```

### Step 4: Execute Safely

Execute in Docker sandbox with timeout:

```python
from src.codegen import execute_generated_code

# Execute with safety constraints
result = await execute_generated_code(
    code=code.code,
    language="python",
    input_data=sales_data,  # User's data
    bash_tool=bash_tool,     # Reference to Bash tool
    timeout=30               # 30 second limit
)

# Check result
if result.success:
    print(result.output)  # Analysis results
else:
    print(f"Error: {result.errors}")
```

### Step 5: Return Results

Present results to user with proper formatting:

```python
# Parse output
analysis_results = json.loads(result.output)

# Format response
response = f"""
<h2>📊 Profit Margin Analysis</h2>

<h3>Financial Summary</h3>
<ul>
  <li>Total Revenue: {analysis_results['total_revenue']}</li>
  <li>Total Cost: {analysis_results['total_cost']}</li>
  <li>Profit: {analysis_results['profit']}</li>
  <li>Profit Margin: {analysis_results['profit_margin']}</li>
</ul>

<h3>💡 Insights</h3>
<ul>
  {"\n".join(f"<li>{insight}</li>" for insight in analysis_results['insights'])}
</ul>

<p><small>Generated code saved at: {code.file_path}</small></p>
"""

return {"content": [{"type": "text", "text": response}]}
```

## Workflow: Generate SQL Report

### Step 1: Identify Query Requirements

**Example User Request:**
> "Show me revenue by day for the past month"

**Requirements:**
- Query type: Revenue by period
- Table: `transactions`
- Date column: `created_at`
- Revenue column: `amount`
- Time range: Last 30 days

### Step 2: Generate SQL Query

```python
from src.codegen import CodeGenerator
from datetime import date, timedelta

generator = CodeGenerator()

# Calculate date range
end_date = date.today()
start_date = end_date - timedelta(days=30)

# Generate query
query = generator.generate_sql_query(
    purpose="Daily revenue report for past 30 days",
    query_type="revenue_by_period",
    table_name="transactions",
    columns={
        "date_column": "created_at",
        "revenue_column": "amount"
    },
    filters={
        "start_date": f"'{start_date.isoformat()}'",
        "end_date": f"'{end_date.isoformat()}'"
    },
    limit=30
)
```

### Step 3: Validate SQL

Ensure query is read-only and safe:

```python
from src.codegen import lint_sql_query

# Validate SQL safety
validation = lint_sql_query(query.code)

if not validation.valid:
    # Show security errors
    print(f"⚠️ SQL validation failed: {validation.get_summary()}")

    # Check for dangerous keywords
    for error in validation.errors:
        if error.rule_id == 'SQL001':
            print(f"🔒 Dangerous operation detected: {error.message}")
```

### Step 4: Execute Query

Execute in read-only mode:

```python
from src.codegen import execute_generated_code

# Execute SQL query
result = await execute_generated_code(
    code=query.code,
    language="sql",
    database_path="/campfire-db/production.sqlite3",
    bash_tool=bash_tool,
    timeout=10
)

# Parse results
if result.success:
    data = json.loads(result.output)
    # Process and display results
```

## Available Templates

### Financial Analysis (Python)

**Template Type:** `TemplateType.FINANCIAL_ANALYSIS`

**Available Calculations:**
- `profit_margin` - (Revenue - Cost) / Revenue × 100
- `roi` - (Gain - Investment) / Investment × 100
- `growth_rate` - (Current - Previous) / Previous × 100

**Data Schema Requirements:**
- Numeric columns: revenue, cost, or similar
- Optional: date column for trend analysis

**Example:**
```python
code = generator.generate_python_script(
    purpose="Calculate quarterly financial metrics",
    template_type=TemplateType.FINANCIAL_ANALYSIS,
    data_schema={"revenue": "float", "cost": "float", "date": "datetime"},
    calculation_types=["profit_margin", "roi", "growth_rate"]
)
```

### Operations Analytics (Python)

**Template Type:** `TemplateType.OPERATIONS_ANALYTICS`

**Available Aggregations:**
- `daily_summary` - Group by date, calculate count/sum/mean
- `completion_rate` - Completed / Total × 100
- `cycle_time` - Average (End Date - Start Date)

**Automatic Features:**
- Trend analysis (increasing/decreasing/stable)
- Anomaly detection (z-score based)
- Recommendations based on thresholds

**Example:**
```python
code = generator.generate_python_script(
    purpose="Analyze task completion metrics",
    template_type=TemplateType.OPERATIONS_ANALYTICS,
    data_schema={
        "id": "int",
        "status": "str",
        "created_at": "datetime",
        "value": "float"
    },
    calculation_types=["completion_rate", "cycle_time"]
)
```

### SQL Report Generation

**Template Type:** `TemplateType.SQL_REPORT`

**Available Query Types:**
- `revenue_by_period` - Revenue aggregated by date
- `top_items` - Top N items by value
- `comparison_report` - Period-over-period comparison

**Safety Checks:**
- ✅ Read-only (SELECT only)
- ✅ LIMIT clause enforced
- ✅ No subqueries modifying data
- ✅ No DELETE/UPDATE/DROP allowed

**Example:**
```python
query = generator.generate_sql_query(
    purpose="Top 10 dishes by revenue",
    query_type="top_items",
    table_name="dish_sales",
    columns={
        "item_column": "dish_name",
        "value_column": "revenue"
    },
    filters={"filter_condition": "revenue > 0"},
    limit=10
)
```

## Quick Generators

For common use cases, use quick generator methods:

### Profit Margin Calculator

```python
code = generator.generate_profit_margin_calculator(
    revenue_col="revenue",
    cost_col="cost"
)
```

### Operations Dashboard

```python
code = generator.generate_operations_dashboard(
    status_col="status",
    date_col="created_at"
)
```

### Revenue Report Query

```python
query = generator.generate_revenue_report_query(
    table="transactions",
    date_col="created_at",
    revenue_col="amount"
)
```

## Safety Rules

### ALWAYS:
1. ✅ Validate code with linting before execution
2. ✅ Execute in Docker sandbox via Bash tool
3. ✅ Set execution timeouts (max 30 seconds)
4. ✅ Use read-only database mode for SQL
5. ✅ Store generated code for audit trail
6. ✅ Handle execution errors gracefully

### NEVER:
1. ❌ Execute user-provided code directly
2. ❌ Skip validation steps
3. ❌ Allow database modifications (UPDATE/DELETE)
4. ❌ Execute code without timeout limits
5. ❌ Access production data without read-only mode
6. ❌ Generate code for file system modifications

## Error Handling

### Validation Errors

If code fails validation:

```python
if not validation.valid:
    # Attempt auto-fix
    if validation.auto_fixable:
        fixed_code = auto_fix_python_code(code.code)
        validation = lint_python_code(fixed_code)

    # If still invalid, inform user
    if not validation.valid:
        return {
            "content": [{
                "type": "text",
                "text": f"⚠️ Generated code has errors:\n{format_validation_report(validation)}"
            }]
        }
```

### Execution Errors

If execution fails:

```python
if not result.success:
    if result.timeout:
        message = f"⏱️ Execution timed out after {result.execution_time_ms:.0f}ms"
    else:
        message = f"❌ Execution failed:\n{result.errors}"

    return {"content": [{"type": "text", "text": message}]}
```

## Performance Guidelines

### Token Efficiency
- Generate code only for complex operations
- Use existing tools for simple calculations
- Cache generated code for repeated use

### Execution Time
- Set appropriate timeouts based on data size
- Small datasets (<100 rows): 5-10 seconds
- Medium datasets (100-1000 rows): 10-20 seconds
- Large datasets (>1000 rows): 20-30 seconds

### Resource Limits
- Maximum timeout: 30 seconds (enforced)
- Maximum result size: 10MB (JSON output)
- Maximum SQL rows: 1000 (use LIMIT)

## Example Use Cases

### Use Case 1: Financial Dashboard

**User Request:** "Create a financial dashboard with key metrics"

**Workflow:**
1. Generate profit margin calculator
2. Generate ROI calculator
3. Generate growth rate calculator
4. Execute all three analyses
5. Combine results into HTML dashboard

### Use Case 2: Operations Report

**User Request:** "Show me operations performance for this week"

**Workflow:**
1. Generate operations analytics script
2. Calculate completion rate, cycle time
3. Detect trends and anomalies
4. Generate recommendations
5. Present formatted report

### Use Case 3: Revenue Comparison

**User Request:** "Compare revenue between Q1 and Q2"

**Workflow:**
1. Generate SQL comparison query
2. Execute for Q1 period
3. Execute for Q2 period
4. Calculate percentage change
5. Present comparison table

## Integration with Other Skills

### With Verification Skill
```python
# Generate and verify calculations
from src.verification import verify_financial_balance

# Generate code
code = generator.generate_profit_margin_calculator()

# Execute
result = await execute_generated_code(code.code, "python", sales_data)

# Verify results
verification = verify_financial_balance(
    revenue=result['total_revenue'],
    cost=result['total_cost'],
    profit=result['profit']
)

if not verification.passed:
    # Show verification warnings
    print(f"⚠️ Verification issues: {verification.get_summary()}")
```

### With File Registry
```python
# Generate code and offer download
code = generator.generate_python_script(...)

# Register file for download
from src.file_registry import file_registry
token = file_registry.register_file(
    file_path=code.file_path,
    original_filename="analysis_script.py",
    content_type="text/x-python"
)

# Include download link in response
download_url = f"http://localhost:8000/files/download/{token}"
```

## Troubleshooting

### Issue: Validation Fails

**Solution:**
1. Check linting output for specific errors
2. Attempt auto-fix if errors are fixable
3. Manually review generated code
4. Adjust data schema or calculation types

### Issue: Execution Times Out

**Solution:**
1. Reduce data size (use sampling)
2. Increase timeout limit (up to 30s max)
3. Optimize calculations (use simpler logic)
4. Split into multiple smaller analyses

### Issue: SQL Returns No Results

**Solution:**
1. Check filter conditions (date ranges, etc.)
2. Verify table and column names
3. Test query in SQLite directly
4. Check for NULL values in data

## Best Practices

1. **Start Simple:** Begin with quick generators before custom code
2. **Validate Early:** Lint code before execution
3. **Test with Samples:** Use small datasets first
4. **Monitor Timeouts:** Track execution times for optimization
5. **Cache Results:** Save analysis results for future reference
6. **Document Changes:** Log all code generation for audit trail

## Summary

The code generation skill enables safe, validated code creation for complex data analysis tasks. Always validate before execution, use sandboxed environments, and follow safety rules to ensure reliable results.

**Key Takeaways:**
- ✅ Use templates for common patterns
- ✅ Validate with ruff/mypy before execution
- ✅ Execute in Docker sandbox with timeouts
- ✅ Handle errors gracefully
- ✅ Focus on financial and operations use cases
