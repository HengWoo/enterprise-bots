"""
Code Templates for Safe Code Generation

Provides pre-approved code templates for Python scripts and SQL queries.
All templates are designed for read-only data analysis and report generation.

Template Types:
1. Financial Calculations (Python)
2. Operations Analytics (Python)
3. SQL Report Generation (SQL)
"""

from enum import Enum
from typing import Dict, Any
from datetime import datetime


class TemplateType(str, Enum):
    """Supported code template types."""
    FINANCIAL_ANALYSIS = "financial_analysis"
    OPERATIONS_ANALYTICS = "operations_analytics"
    SQL_REPORT = "sql_report"


class CodeTemplate:
    """Pre-approved code templates for safe generation."""

    # ========================================================================
    # Template 1: Financial Calculations (Python)
    # ========================================================================
    FINANCIAL_ANALYSIS = '''"""
Generated Financial Analysis Script
Purpose: {purpose}
Generated: {timestamp}
"""

import pandas as pd
from typing import Dict, List, Optional
from decimal import Decimal, ROUND_HALF_UP


def analyze_financial_data(data: List[Dict]) -> Dict:
    """
    Analyze financial data and calculate key metrics.

    Args:
        data: List of financial records with schema: {data_schema}

    Returns:
        Dictionary containing calculated metrics and insights
    """
    # Convert to DataFrame for analysis
    df = pd.DataFrame(data)

    # Ensure numeric types
    for col in {numeric_columns}:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Remove any invalid data
    df = df.dropna()

    # Calculate metrics
    results = {{}}

    {calculation_code}

    # Generate insights
    insights = []
    {insight_code}

    results['insights'] = insights

    return results


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division with zero handling."""
    if denominator == 0:
        return default
    return numerator / denominator


def format_currency(amount: float, currency: str = "¥") -> str:
    """Format amount as currency."""
    return f"{{currency}}{{amount:,.2f}}"


def format_percentage(value: float) -> str:
    """Format value as percentage."""
    return f"{{value:.1f}}%"


# Main execution
if __name__ == "__main__":
    # Test with sample data
    sample_data = {sample_data}

    result = analyze_financial_data(sample_data)

    print("Financial Analysis Results:")
    print("=" * 50)
    for key, value in result.items():
        if key != 'insights':
            print(f"{{key}}: {{value}}")

    print("\\nInsights:")
    for i, insight in enumerate(result['insights'], 1):
        print(f"{{i}}. {{insight}}")
'''

    # ========================================================================
    # Template 2: Operations Analytics (Python)
    # ========================================================================
    OPERATIONS_ANALYTICS = '''"""
Generated Operations Analytics Script
Purpose: {purpose}
Generated: {timestamp}
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta


def analyze_operations_data(data: List[Dict]) -> Dict:
    """
    Analyze operations data and identify trends.

    Args:
        data: List of operations records with schema: {data_schema}

    Returns:
        Dictionary containing analytics and trends
    """
    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Parse dates if present
    if {date_column} in df.columns:
        df[{date_column}] = pd.to_datetime(df[{date_column}])

    # Ensure numeric columns
    for col in {numeric_columns}:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Initialize results
    results = {{}}

    {aggregation_code}

    {trend_analysis_code}

    {anomaly_detection_code}

    # Generate recommendations
    recommendations = []
    {recommendation_code}

    results['recommendations'] = recommendations

    return results


def calculate_trend(series: pd.Series) -> str:
    """Calculate trend direction from time series."""
    if len(series) < 2:
        return "insufficient_data"

    # Simple linear trend
    x = range(len(series))
    y = series.values
    slope = (len(x) * sum(x[i] * y[i] for i in range(len(x))) - sum(x) * sum(y)) / \\
            (len(x) * sum(x[i]**2 for i in range(len(x))) - sum(x)**2)

    if slope > 0.05:
        return "increasing"
    elif slope < -0.05:
        return "decreasing"
    else:
        return "stable"


def detect_anomalies(series: pd.Series, threshold: float = 2.0) -> List[int]:
    """Detect anomalies using standard deviation method."""
    mean = series.mean()
    std = series.std()

    anomalies = []
    for idx, value in enumerate(series):
        z_score = abs((value - mean) / std) if std > 0 else 0
        if z_score > threshold:
            anomalies.append(idx)

    return anomalies


# Main execution
if __name__ == "__main__":
    # Test with sample data
    sample_data = {sample_data}

    result = analyze_operations_data(sample_data)

    print("Operations Analytics Results:")
    print("=" * 50)
    for key, value in result.items():
        if key != 'recommendations':
            print(f"{{key}}: {{value}}")

    print("\\nRecommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"{{i}}. {{rec}}")
'''

    # ========================================================================
    # Template 3: SQL Report Generation (SQL)
    # ========================================================================
    SQL_REPORT = '''-- Generated SQL Report Query
-- Purpose: {purpose}
-- Generated: {timestamp}
-- Database: {database_type}

-- Safety Checks:
-- ✓ Read-only (SELECT only)
-- ✓ LIMIT clause present
-- ✓ No subqueries modifying data
-- ✓ No DELETE/UPDATE/DROP

{query_code}

-- Query Metadata:
-- Expected columns: {expected_columns}
-- Expected rows: {expected_row_count}
-- Execution time estimate: {estimated_duration}
'''

    # ========================================================================
    # Financial Calculation Snippets
    # ========================================================================
    FINANCIAL_CALCULATIONS = {
        "profit_margin": '''
    # Calculate profit margin: (Revenue - Cost) / Revenue * 100
    total_revenue = df[{revenue_col}].sum()
    total_cost = df[{cost_col}].sum()
    profit = total_revenue - total_cost
    profit_margin = safe_divide(profit, total_revenue) * 100

    results['total_revenue'] = format_currency(total_revenue)
    results['total_cost'] = format_currency(total_cost)
    results['profit'] = format_currency(profit)
    results['profit_margin'] = format_percentage(profit_margin)
''',

        "roi": '''
    # Calculate ROI: (Gain - Investment) / Investment * 100
    total_gain = df[{gain_col}].sum()
    total_investment = df[{investment_col}].sum()
    roi = safe_divide(total_gain - total_investment, total_investment) * 100

    results['total_gain'] = format_currency(total_gain)
    results['total_investment'] = format_currency(total_investment)
    results['roi'] = format_percentage(roi)
''',

        "growth_rate": '''
    # Calculate growth rate: (Current - Previous) / Previous * 100
    current_value = df[{value_col}].iloc[-1] if len(df) > 0 else 0
    previous_value = df[{value_col}].iloc[0] if len(df) > 0 else 0
    growth_rate = safe_divide(current_value - previous_value, previous_value) * 100

    results['current_value'] = format_currency(current_value)
    results['previous_value'] = format_currency(previous_value)
    results['growth_rate'] = format_percentage(growth_rate)
'''
    }

    # ========================================================================
    # Operations Analytics Snippets
    # ========================================================================
    OPERATIONS_AGGREGATIONS = {
        "daily_summary": '''
    # Group by date and calculate daily metrics
    if {date_column} in df.columns:
        daily = df.groupby(df[{date_column}].dt.date).agg({{
            {metric_column}: ['count', 'sum', 'mean']
        }}).round(2)

        results['daily_summary'] = daily.to_dict()
        results['total_days'] = len(daily)
        results['avg_daily_value'] = daily[{metric_column}]['sum'].mean()
''',

        "completion_rate": '''
    # Calculate completion rate
    total_tasks = len(df)
    completed_tasks = len(df[df[{status_column}] == {completed_status}])
    completion_rate = safe_divide(completed_tasks, total_tasks) * 100

    results['total_tasks'] = total_tasks
    results['completed_tasks'] = completed_tasks
    results['completion_rate'] = format_percentage(completion_rate)
''',

        "cycle_time": '''
    # Calculate average cycle time
    if {start_date_col} in df.columns and {end_date_col} in df.columns:
        df['cycle_time'] = (df[{end_date_col}] - df[{start_date_col}]).dt.days
        avg_cycle_time = df['cycle_time'].mean()

        results['avg_cycle_time_days'] = round(avg_cycle_time, 1)
        results['min_cycle_time_days'] = int(df['cycle_time'].min())
        results['max_cycle_time_days'] = int(df['cycle_time'].max())
'''
    }

    # ========================================================================
    # SQL Query Snippets
    # ========================================================================
    SQL_QUERIES = {
        "revenue_by_period": '''
SELECT
    DATE({date_column}) as period,
    COUNT(*) as transaction_count,
    SUM({revenue_column}) as total_revenue,
    AVG({revenue_column}) as avg_revenue,
    MIN({revenue_column}) as min_revenue,
    MAX({revenue_column}) as max_revenue
FROM {table_name}
WHERE {date_column} BETWEEN {start_date} AND {end_date}
GROUP BY DATE({date_column})
ORDER BY period DESC
LIMIT {limit};
''',

        "top_items": '''
SELECT
    {item_column} as item,
    COUNT(*) as frequency,
    SUM({value_column}) as total_value,
    AVG({value_column}) as avg_value
FROM {table_name}
WHERE {filter_condition}
GROUP BY {item_column}
ORDER BY total_value DESC
LIMIT {limit};
''',

        "comparison_report": '''
SELECT
    {category_column} as category,
    SUM(CASE WHEN {period_column} = {period1} THEN {value_column} ELSE 0 END) as period1_value,
    SUM(CASE WHEN {period_column} = {period2} THEN {value_column} ELSE 0 END) as period2_value,
    ROUND(
        (SUM(CASE WHEN {period_column} = {period2} THEN {value_column} ELSE 0 END) -
         SUM(CASE WHEN {period_column} = {period1} THEN {value_column} ELSE 0 END)) * 100.0 /
        NULLIF(SUM(CASE WHEN {period_column} = {period1} THEN {value_column} ELSE 0 END), 0),
        2
    ) as change_percentage
FROM {table_name}
WHERE {period_column} IN ({period1}, {period2})
GROUP BY {category_column}
ORDER BY period2_value DESC
LIMIT {limit};
'''
    }

    @classmethod
    def get_template(cls, template_type: TemplateType) -> str:
        """Get template string by type."""
        template_map = {
            TemplateType.FINANCIAL_ANALYSIS: cls.FINANCIAL_ANALYSIS,
            TemplateType.OPERATIONS_ANALYTICS: cls.OPERATIONS_ANALYTICS,
            TemplateType.SQL_REPORT: cls.SQL_REPORT,
        }
        return template_map.get(template_type, "")

    @classmethod
    def get_calculation_snippet(cls, calculation_type: str) -> str:
        """Get financial calculation code snippet."""
        return cls.FINANCIAL_CALCULATIONS.get(calculation_type, "")

    @classmethod
    def get_aggregation_snippet(cls, aggregation_type: str) -> str:
        """Get operations aggregation code snippet."""
        return cls.OPERATIONS_AGGREGATIONS.get(aggregation_type, "")

    @classmethod
    def get_sql_snippet(cls, query_type: str) -> str:
        """Get SQL query snippet."""
        return cls.SQL_QUERIES.get(query_type, "")
