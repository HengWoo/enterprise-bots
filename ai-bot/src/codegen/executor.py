"""
Safe Code Executor

Executes generated code in Docker sandbox via Bash tool with safety constraints.
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of code execution."""
    success: bool
    output: str
    errors: str
    exit_code: int
    execution_time_ms: float
    timeout: bool = False

    def get_summary(self) -> str:
        """Get human-readable summary."""
        if self.success:
            return f"✅ Execution successful ({self.execution_time_ms:.0f}ms)"
        elif self.timeout:
            return f"⏱️ Execution timeout"
        else:
            return f"❌ Execution failed (exit code: {self.exit_code})"


class CodeExecutor:
    """Execute generated code safely in Docker sandbox."""

    def __init__(
        self,
        bash_tool: Optional[Any] = None,
        working_dir: str = "/tmp/generated",
        default_timeout: int = 30
    ):
        """
        Initialize code executor.

        Args:
            bash_tool: Reference to Bash tool for execution
            working_dir: Working directory for execution
            default_timeout: Default timeout in seconds (max 30s)
        """
        self.bash_tool = bash_tool
        self.working_dir = Path(working_dir)
        self.default_timeout = min(default_timeout, 30)  # Cap at 30 seconds

    async def execute_python_script(
        self,
        code_file: str,
        input_data: Optional[Dict] = None,
        timeout: Optional[int] = None
    ) -> ExecutionResult:
        """
        Execute Python script via Bash tool.

        Args:
            code_file: Path to Python script file
            input_data: Optional input data (will be saved as JSON)
            timeout: Execution timeout in seconds (default: 30s)

        Returns:
            ExecutionResult with output and errors
        """
        import time
        start_time = time.time()

        # Prepare input data file if provided
        input_file = None
        if input_data:
            input_file = self.working_dir / "input_data.json"
            input_file.write_text(json.dumps(input_data, ensure_ascii=False, indent=2))

        # Build Python command
        cmd = f"python {code_file}"
        if input_file:
            cmd += f" < {input_file}"

        # Execute via Bash tool
        try:
            if self.bash_tool is None:
                # Fallback: direct subprocess execution (for testing)
                result = await self._execute_subprocess(
                    cmd,
                    cwd=str(self.working_dir),
                    timeout=timeout or self.default_timeout
                )
            else:
                # Production: execute via Bash tool (Docker sandbox)
                result = await self.bash_tool({
                    "command": cmd,
                    "cwd": str(self.working_dir),
                    "timeout": (timeout or self.default_timeout) * 1000  # Convert to ms
                })

            elapsed_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                success=result.get("exit_code", 1) == 0,
                output=result.get("stdout", ""),
                errors=result.get("stderr", ""),
                exit_code=result.get("exit_code", 1),
                execution_time_ms=elapsed_ms,
                timeout=False
            )

        except asyncio.TimeoutError:
            elapsed_ms = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=False,
                output="",
                errors="Execution timed out",
                exit_code=-1,
                execution_time_ms=elapsed_ms,
                timeout=True
            )
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"Error executing Python script: {e}")
            return ExecutionResult(
                success=False,
                output="",
                errors=str(e),
                exit_code=-1,
                execution_time_ms=elapsed_ms
            )

    async def execute_sql_query(
        self,
        query_file: str,
        database_path: str,
        timeout: Optional[int] = None
    ) -> ExecutionResult:
        """
        Execute SQL query via Bash tool.

        Args:
            query_file: Path to SQL query file
            database_path: Path to SQLite database
            timeout: Execution timeout in seconds (default: 30s)

        Returns:
            ExecutionResult with query results
        """
        import time
        start_time = time.time()

        # Build sqlite3 command (read-only mode)
        cmd = f"sqlite3 -readonly -json {database_path} < {query_file}"

        # Execute via Bash tool
        try:
            if self.bash_tool is None:
                # Fallback: direct subprocess execution
                result = await self._execute_subprocess(
                    cmd,
                    cwd=str(self.working_dir),
                    timeout=timeout or self.default_timeout
                )
            else:
                # Production: execute via Bash tool
                result = await self.bash_tool({
                    "command": cmd,
                    "cwd": str(self.working_dir),
                    "timeout": (timeout or self.default_timeout) * 1000
                })

            elapsed_ms = (time.time() - start_time) * 1000

            return ExecutionResult(
                success=result.get("exit_code", 1) == 0,
                output=result.get("stdout", ""),
                errors=result.get("stderr", ""),
                exit_code=result.get("exit_code", 1),
                execution_time_ms=elapsed_ms,
                timeout=False
            )

        except asyncio.TimeoutError:
            elapsed_ms = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=False,
                output="",
                errors="Query execution timed out",
                exit_code=-1,
                execution_time_ms=elapsed_ms,
                timeout=True
            )
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"Error executing SQL query: {e}")
            return ExecutionResult(
                success=False,
                output="",
                errors=str(e),
                exit_code=-1,
                execution_time_ms=elapsed_ms
            )

    async def _execute_subprocess(
        self,
        cmd: str,
        cwd: str,
        timeout: int
    ) -> Dict[str, Any]:
        """Fallback: Execute command via subprocess (for testing)."""
        import subprocess

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            raise asyncio.TimeoutError()
        except Exception as e:
            raise RuntimeError(f"Subprocess execution failed: {e}")


# ============================================================================
# High-Level Execution Function
# ============================================================================

async def execute_generated_code(
    code: str,
    language: str,
    input_data: Optional[Dict] = None,
    bash_tool: Optional[Any] = None,
    timeout: int = 30,
    database_path: Optional[str] = None
) -> ExecutionResult:
    """
    Execute generated code safely in Docker sandbox.

    Args:
        code: Source code to execute
        language: "python" or "sql"
        input_data: Optional input data for Python scripts
        bash_tool: Reference to Bash tool (if None, uses subprocess)
        timeout: Execution timeout in seconds (max 30s)
        database_path: Path to SQLite database (for SQL queries)

    Returns:
        ExecutionResult with output and errors

    Raises:
        ValueError: If language not supported or missing required args
    """
    executor = CodeExecutor(bash_tool=bash_tool, default_timeout=timeout)

    # Save code to temp file
    working_dir = Path("/tmp/generated")
    working_dir.mkdir(parents=True, exist_ok=True)

    if language == "python":
        # Save Python script
        script_file = working_dir / f"script_{hash(code) % 10000}.py"
        script_file.write_text(code)

        # Execute
        return await executor.execute_python_script(
            code_file=str(script_file),
            input_data=input_data,
            timeout=timeout
        )

    elif language == "sql":
        if not database_path:
            raise ValueError("database_path required for SQL execution")

        # Save SQL query
        query_file = working_dir / f"query_{hash(code) % 10000}.sql"
        query_file.write_text(code)

        # Execute
        return await executor.execute_sql_query(
            query_file=str(query_file),
            database_path=database_path,
            timeout=timeout
        )

    else:
        raise ValueError(f"Unsupported language: {language}")


# ============================================================================
# Execution Safety Wrapper
# ============================================================================

async def safe_execute_with_validation(
    code: str,
    language: str,
    validator: Optional[Any] = None,
    input_data: Optional[Dict] = None,
    bash_tool: Optional[Any] = None,
    timeout: int = 30,
    database_path: Optional[str] = None
) -> tuple[ExecutionResult, Optional[Any]]:
    """
    Validate code first, then execute if valid.

    Args:
        code: Source code to validate and execute
        language: "python" or "sql"
        validator: Optional validator function (from validators.py)
        input_data: Optional input data
        bash_tool: Bash tool reference
        timeout: Execution timeout
        database_path: Database path for SQL

    Returns:
        Tuple of (ExecutionResult, ValidationResult)
    """
    # Step 1: Validate code
    validation_result = None
    if validator:
        from .validators import validate_generated_code
        validation_result = validate_generated_code(code, language, auto_fix=True)

        if not validation_result.valid:
            logger.warning(f"Code validation failed: {validation_result.get_summary()}")

            # Return early if validation failed
            return ExecutionResult(
                success=False,
                output="",
                errors=f"Validation failed: {len(validation_result.errors)} error(s)",
                exit_code=-1,
                execution_time_ms=0
            ), validation_result

        logger.info(f"Code validation passed: {validation_result.get_summary()}")

    # Step 2: Execute validated code
    execution_result = await execute_generated_code(
        code=code,
        language=language,
        input_data=input_data,
        bash_tool=bash_tool,
        timeout=timeout,
        database_path=database_path
    )

    return execution_result, validation_result


# ============================================================================
# Result Formatting
# ============================================================================

def format_execution_report(
    execution_result: ExecutionResult,
    validation_result: Optional[Any] = None,
    include_output: bool = True
) -> str:
    """
    Format execution result as human-readable report.

    Args:
        execution_result: ExecutionResult to format
        validation_result: Optional ValidationResult
        include_output: Whether to include full output (default: True)

    Returns:
        Formatted report string
    """
    lines = []

    # Summary
    lines.append("=" * 60)
    lines.append("CODE EXECUTION REPORT")
    lines.append("=" * 60)

    # Validation status
    if validation_result:
        lines.append(f"\n📋 Validation: {validation_result.get_summary()}")

    # Execution status
    lines.append(f"\n⚡ Execution: {execution_result.get_summary()}")

    # Output
    if include_output and execution_result.output:
        lines.append("\n📤 OUTPUT:")
        lines.append("-" * 60)
        lines.append(execution_result.output)

    # Errors
    if execution_result.errors:
        lines.append("\n❌ ERRORS:")
        lines.append("-" * 60)
        lines.append(execution_result.errors)

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)
