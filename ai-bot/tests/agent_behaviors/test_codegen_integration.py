"""
Critical Path Test 2: Code Generation System Integration

Tests that code generation module works end-to-end:
generate → validate → execute
"""

import pytest
import asyncio
from pathlib import Path
from src.codegen import (
    CodeGenerator,
    TemplateType,
    lint_python_code,
    lint_sql_query,
    execute_generated_code,
)


class TestCodeGenerationIntegration:
    """Test code generation system integration."""

    def test_generate_python_script(self):
        """Test Python script generation from template."""

        generator = CodeGenerator(output_dir="/tmp/test_generated")

        # Generate financial analysis script
        code = generator.generate_python_script(
            purpose="Test profit margin calculation",
            template_type=TemplateType.FINANCIAL_ANALYSIS,
            data_schema={
                "revenue": "float",
                "cost": "float",
                "date": "datetime"
            },
            calculation_types=["profit_margin"]
        )

        # Verify code object created
        assert code.code is not None
        assert code.language == "python"
        assert code.template_type == TemplateType.FINANCIAL_ANALYSIS
        assert "def analyze_financial_data" in code.code
        assert "profit_margin" in code.code

        # Verify file saved
        assert Path(code.file_path).exists()

    def test_generate_sql_query(self):
        """Test SQL query generation from template."""

        generator = CodeGenerator(output_dir="/tmp/test_generated")

        # Generate revenue by period query
        query = generator.generate_sql_query(
            purpose="Test revenue report",
            query_type="revenue_by_period",
            table_name="transactions",
            columns={
                "date_column": "created_at",
                "revenue_column": "amount"
            },
            filters={
                "start_date": "'2025-01-01'",
                "end_date": "'2025-01-31'"
            },
            limit=100
        )

        # Verify query generated
        assert query.code is not None
        assert query.language == "sql"
        assert "SELECT" in query.code
        assert "transactions" in query.code
        assert "LIMIT 100" in query.code

    def test_python_linting_validation(self):
        """Test that Python linting catches errors."""

        # Valid Python code
        valid_code = '''
def test():
    x = 1 + 1
    return x
'''
        validation = lint_python_code(valid_code, check_types=False)
        assert validation.valid is True

        # Invalid Python code (syntax error)
        invalid_code = '''
def test()  # Missing colon
    x = 1 + 1
    return x
'''
        validation = lint_python_code(invalid_code, check_types=False)
        assert validation.valid is False
        assert len(validation.errors) > 0

    def test_sql_safety_validation(self):
        """Test that SQL validation catches dangerous operations."""

        # Safe query (SELECT only)
        safe_query = "SELECT * FROM users LIMIT 10;"
        validation = lint_sql_query(safe_query)
        assert validation.valid is True

        # Dangerous query (DELETE)
        dangerous_query = "DELETE FROM users WHERE id = 1;"
        validation = lint_sql_query(dangerous_query)
        assert validation.valid is False
        assert any("delete" in e.message.lower() for e in validation.errors)

        # Dangerous query (UPDATE)
        dangerous_query2 = "UPDATE users SET role = 'admin' WHERE id = 1;"
        validation = lint_sql_query(dangerous_query2)
        assert validation.valid is False

    @pytest.mark.asyncio
    async def test_code_execution_sandbox(self):
        """Test that code execution works in sandbox."""

        # Simple Python code that returns JSON
        code = '''
import json
result = {"test": "success", "value": 42}
print(json.dumps(result))
'''

        # Execute (without bash_tool, uses subprocess fallback)
        result = await execute_generated_code(
            code=code,
            language="python",
            input_data=None,
            bash_tool=None,  # Subprocess fallback for testing
            timeout=5
        )

        # Verify execution succeeded
        assert result.success is True
        assert result.exit_code == 0
        assert "test" in result.output
        assert "success" in result.output

    @pytest.mark.asyncio
    async def test_code_execution_timeout(self):
        """Test that code execution respects timeout."""

        # Code that runs forever
        infinite_loop_code = '''
while True:
    pass
'''

        # Execute with 2 second timeout
        result = await execute_generated_code(
            code=infinite_loop_code,
            language="python",
            input_data=None,
            bash_tool=None,
            timeout=2
        )

        # Verify timeout occurred
        assert result.success is False
        assert result.timeout is True

    def test_quick_generator_profit_margin(self):
        """Test quick generator: profit margin calculator."""

        generator = CodeGenerator(output_dir="/tmp/test_generated")

        code = generator.generate_profit_margin_calculator(
            revenue_col="sales",
            cost_col="expenses"
        )

        # Verify generated
        assert "sales" in code.code
        assert "expenses" in code.code
        assert "profit_margin" in code.code


# This test validates the ENTIRE code generation pipeline:
# Template → Generation → Validation → Execution
# If this passes, code generation system works end-to-end
