"""
Code Generation Module for Campfire AI Bot

This module provides safe code generation capabilities for agents to create
Python scripts and SQL queries for data analysis and report generation.

Architecture:
- templates.py: Pre-defined code templates (Python, SQL)
- generators.py: Code generation logic with validation
- validators.py: Linting integration (ruff, mypy)
- executor.py: Safe execution via Bash tool in Docker sandbox

Usage:
    from src.codegen import CodeGenerator, execute_generated_code

    # Generate Python script
    generator = CodeGenerator()
    code = generator.generate_python_script(
        purpose="Analyze sales trends",
        template_type="financial_analysis",
        data_schema={"date": "datetime", "revenue": "float"}
    )

    # Execute safely
    result = await execute_generated_code(
        code=code["code"],
        language="python",
        input_data=sales_data
    )

Security:
- All code generated from pre-approved templates
- Linting validation before execution (ruff + mypy)
- Execution in Docker sandbox via Bash tool
- Timeout limits to prevent infinite loops
- No file system access beyond /tmp/generated/
"""

from .templates import CodeTemplate, TemplateType
from .generators import CodeGenerator, GeneratedCode
from .validators import lint_python_code, lint_sql_query, ValidationResult
from .executor import execute_generated_code, ExecutionResult

__all__ = [
    # Templates
    "CodeTemplate",
    "TemplateType",

    # Generators
    "CodeGenerator",
    "GeneratedCode",

    # Validators
    "lint_python_code",
    "lint_sql_query",
    "ValidationResult",

    # Executor
    "execute_generated_code",
    "ExecutionResult",
]
