"""
Code Generators for Financial and Operations Analytics

Generates Python scripts and SQL queries from templates with validation.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import uuid4
from pathlib import Path

from .templates import CodeTemplate, TemplateType


@dataclass
class GeneratedCode:
    """Container for generated code with metadata."""
    code: str
    language: str
    template_type: TemplateType
    purpose: str
    file_path: str
    validated: bool
    validation_errors: List[str] = None

    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []


class CodeGenerator:
    """Generate safe, validated code from templates."""

    def __init__(self, output_dir: str = "/tmp/generated"):
        """
        Initialize code generator.

        Args:
            output_dir: Directory to save generated code files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # Main Generation Methods
    # ========================================================================

    def generate_python_script(
        self,
        purpose: str,
        template_type: TemplateType,
        data_schema: Dict[str, str],
        calculation_types: Optional[List[str]] = None,
        sample_data: Optional[List[Dict]] = None
    ) -> GeneratedCode:
        """
        Generate Python analysis script.

        Args:
            purpose: Description of what the script does
            template_type: FINANCIAL_ANALYSIS or OPERATIONS_ANALYTICS
            data_schema: Dict mapping column names to types (e.g., {"revenue": "float"})
            calculation_types: List of calculation types to include (e.g., ["profit_margin", "roi"])
            sample_data: Optional sample data for testing

        Returns:
            GeneratedCode object with the script and metadata
        """
        # Get base template
        template = CodeTemplate.get_template(template_type)

        # Extract numeric columns from schema
        numeric_columns = [
            col for col, dtype in data_schema.items()
            if dtype in ("int", "float", "Decimal")
        ]

        # Build calculation code
        calculation_code = ""
        insight_code = ""

        if template_type == TemplateType.FINANCIAL_ANALYSIS:
            calculation_code, insight_code = self._build_financial_calculations(
                calculation_types or ["profit_margin"],
                data_schema
            )
        elif template_type == TemplateType.OPERATIONS_ANALYTICS:
            calculation_code, insight_code = self._build_operations_analytics(
                calculation_types or ["completion_rate"],
                data_schema
            )

        # Generate sample data if not provided
        if sample_data is None:
            sample_data = self._generate_sample_data(data_schema, num_rows=5)

        # Format template
        code = template.format(
            purpose=purpose,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_schema=str(data_schema),
            numeric_columns=repr(numeric_columns),
            calculation_code=calculation_code,
            insight_code=insight_code,
            sample_data=repr(sample_data)
        )

        # Save to file
        file_path = self.output_dir / f"analysis_{uuid4().hex[:8]}.py"
        file_path.write_text(code)

        return GeneratedCode(
            code=code,
            language="python",
            template_type=template_type,
            purpose=purpose,
            file_path=str(file_path),
            validated=False  # Will be validated by validators.py
        )

    def generate_sql_query(
        self,
        purpose: str,
        query_type: str,
        table_name: str,
        columns: Dict[str, str],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> GeneratedCode:
        """
        Generate SQL report query.

        Args:
            purpose: Description of what the query does
            query_type: Type of query (e.g., "revenue_by_period", "top_items")
            table_name: Name of the table to query
            columns: Dict mapping column roles to column names
                     (e.g., {"date_column": "created_at", "revenue_column": "amount"})
            filters: Optional filter conditions
            limit: Maximum rows to return (default: 100)

        Returns:
            GeneratedCode object with the SQL query
        """
        # Get query snippet
        query_snippet = CodeTemplate.get_sql_snippet(query_type)

        if not query_snippet:
            raise ValueError(f"Unknown query type: {query_type}")

        # Build query code
        query_code = query_snippet.format(
            table_name=table_name,
            limit=limit,
            **columns,
            **(filters or {})
        )

        # Get template
        template = CodeTemplate.get_template(TemplateType.SQL_REPORT)

        # Format full SQL file
        code = template.format(
            purpose=purpose,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            database_type="SQLite3",
            query_code=query_code,
            expected_columns=list(columns.values()),
            expected_row_count=f"≤{limit}",
            estimated_duration="<1 second"
        )

        # Save to file
        file_path = self.output_dir / f"query_{uuid4().hex[:8]}.sql"
        file_path.write_text(code)

        return GeneratedCode(
            code=code,
            language="sql",
            template_type=TemplateType.SQL_REPORT,
            purpose=purpose,
            file_path=str(file_path),
            validated=False
        )

    # ========================================================================
    # Financial Calculations Builder
    # ========================================================================

    def _build_financial_calculations(
        self,
        calculation_types: List[str],
        data_schema: Dict[str, str]
    ) -> tuple[str, str]:
        """
        Build financial calculation code from snippets.

        Returns:
            Tuple of (calculation_code, insight_code)
        """
        calculations = []
        insights = []

        # Infer column names from schema
        revenue_col = self._find_column(data_schema, ["revenue", "sales", "income"])
        cost_col = self._find_column(data_schema, ["cost", "expense"])

        for calc_type in calculation_types:
            snippet = CodeTemplate.get_calculation_snippet(calc_type)
            if snippet:
                # Format snippet with column names
                formatted = snippet.format(
                    revenue_col=repr(revenue_col),
                    cost_col=repr(cost_col),
                    gain_col=repr(revenue_col),
                    investment_col=repr(cost_col),
                    value_col=repr(revenue_col)
                )
                calculations.append(formatted)

                # Add corresponding insight
                if calc_type == "profit_margin":
                    insights.append('''
    if profit_margin > 30:
        insights.append("Strong profit margin (>30%)")
    elif profit_margin < 10:
        insights.append("Low profit margin (<10%) - consider cost reduction")
''')
                elif calc_type == "roi":
                    insights.append('''
    if roi > 20:
        insights.append("Excellent ROI (>20%)")
    elif roi < 0:
        insights.append("Negative ROI - investment not profitable")
''')
                elif calc_type == "growth_rate":
                    insights.append('''
    if growth_rate > 10:
        insights.append(f"Strong growth trend (+{growth_rate:.1f}%)")
    elif growth_rate < -10:
        insights.append(f"Concerning decline (-{abs(growth_rate):.1f}%)")
''')

        calculation_code = "\n".join(calculations)
        insight_code = "\n".join(insights)

        return calculation_code, insight_code

    # ========================================================================
    # Operations Analytics Builder
    # ========================================================================

    def _build_operations_analytics(
        self,
        calculation_types: List[str],
        data_schema: Dict[str, str]
    ) -> tuple[str, str]:
        """
        Build operations analytics code from snippets.

        Returns:
            Tuple of (aggregation_code, recommendation_code)
        """
        aggregations = []
        recommendations = []

        # Infer column names
        date_col = self._find_column(data_schema, ["date", "created_at", "timestamp"])
        status_col = self._find_column(data_schema, ["status", "state"])
        metric_col = self._find_column(data_schema, ["value", "count", "amount"])

        for calc_type in calculation_types:
            snippet = CodeTemplate.get_aggregation_snippet(calc_type)
            if snippet:
                # Format snippet
                formatted = snippet.format(
                    date_column=repr(date_col),
                    status_column=repr(status_col),
                    completed_status=repr("completed"),
                    metric_column=repr(metric_col),
                    start_date_col=repr("start_date"),
                    end_date_col=repr("end_date")
                )
                aggregations.append(formatted)

                # Add recommendation logic
                if calc_type == "completion_rate":
                    recommendations.append('''
    if completion_rate < 70:
        recommendations.append("Completion rate below target (70%) - investigate bottlenecks")
''')
                elif calc_type == "cycle_time":
                    recommendations.append('''
    if avg_cycle_time > 7:
        recommendations.append("Average cycle time >1 week - consider process optimization")
''')

        # Add trend analysis section
        trend_analysis = '''
    # Analyze trends over time
    if {date_column} in df.columns:
        df_sorted = df.sort_values({date_column})
        recent_trend = calculate_trend(df_sorted[{metric_column}].tail(7))
        results['trend'] = recent_trend
'''.format(date_column=repr(date_col), metric_column=repr(metric_col))

        # Add anomaly detection section
        anomaly_detection = '''
    # Detect anomalies
    if len(df) > 10:
        anomaly_indices = detect_anomalies(df[{metric_column}])
        results['anomaly_count'] = len(anomaly_indices)
        if anomaly_indices:
            results['anomaly_values'] = df.iloc[anomaly_indices][{metric_column}].tolist()
'''.format(metric_column=repr(metric_col))

        aggregation_code = "\n".join(aggregations)
        recommendation_code = "\n".join(recommendations)

        return aggregation_code + trend_analysis + anomaly_detection, recommendation_code

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _find_column(self, schema: Dict[str, str], candidates: List[str]) -> str:
        """Find column name from schema by matching candidates."""
        for col in schema.keys():
            if any(candidate in col.lower() for candidate in candidates):
                return col
        # Return first column if no match
        return list(schema.keys())[0] if schema else "value"

    def _generate_sample_data(self, schema: Dict[str, str], num_rows: int = 5) -> List[Dict]:
        """Generate sample data matching the schema."""
        import random
        from datetime import date, timedelta

        sample = []
        for i in range(num_rows):
            row = {}
            for col, dtype in schema.items():
                if dtype == "str":
                    row[col] = f"item_{i+1}"
                elif dtype == "int":
                    row[col] = random.randint(1, 100)
                elif dtype == "float" or dtype == "Decimal":
                    row[col] = round(random.uniform(10, 1000), 2)
                elif dtype == "datetime" or dtype == "date":
                    row[col] = (date.today() - timedelta(days=i)).isoformat()
                elif dtype == "bool":
                    row[col] = random.choice([True, False])
                else:
                    row[col] = None
            sample.append(row)

        return sample

    # ========================================================================
    # Quick Generation Methods
    # ========================================================================

    def generate_profit_margin_calculator(
        self,
        revenue_col: str = "revenue",
        cost_col: str = "cost"
    ) -> GeneratedCode:
        """Quick generator: Profit margin calculator."""
        return self.generate_python_script(
            purpose="Calculate profit margin from revenue and cost data",
            template_type=TemplateType.FINANCIAL_ANALYSIS,
            data_schema={
                revenue_col: "float",
                cost_col: "float",
                "date": "datetime"
            },
            calculation_types=["profit_margin"]
        )

    def generate_operations_dashboard(
        self,
        status_col: str = "status",
        date_col: str = "created_at"
    ) -> GeneratedCode:
        """Quick generator: Operations dashboard metrics."""
        return self.generate_python_script(
            purpose="Generate operations dashboard metrics",
            template_type=TemplateType.OPERATIONS_ANALYTICS,
            data_schema={
                "id": "int",
                status_col: "str",
                date_col: "datetime",
                "value": "float"
            },
            calculation_types=["completion_rate", "daily_summary"]
        )

    def generate_revenue_report_query(
        self,
        table: str = "transactions",
        date_col: str = "created_at",
        revenue_col: str = "amount"
    ) -> GeneratedCode:
        """Quick generator: Revenue report SQL query."""
        return self.generate_sql_query(
            purpose="Generate revenue report by time period",
            query_type="revenue_by_period",
            table_name=table,
            columns={
                "date_column": date_col,
                "revenue_column": revenue_col
            },
            filters={
                "start_date": "'2025-01-01'",
                "end_date": "'2025-12-31'"
            },
            limit=365
        )
