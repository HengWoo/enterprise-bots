"""
Code Validators with Linting Integration

Validates generated code using ruff (Python linter) and mypy (type checker)
before allowing execution.
"""

import subprocess
import json
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path
import tempfile
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """A single validation issue from linting."""
    line: int
    column: int
    severity: str  # error, warning
    message: str
    rule_id: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of code validation."""
    valid: bool
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
    linter_output: Dict
    auto_fixable: bool = False

    @property
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0

    def get_summary(self) -> str:
        """Get human-readable summary."""
        if self.valid:
            if self.has_warnings:
                return f"✅ Valid with {len(self.warnings)} warning(s)"
            return "✅ Valid - all checks passed"
        else:
            return f"❌ Invalid - {len(self.errors)} error(s), {len(self.warnings)} warning(s)"


# ============================================================================
# Python Code Validation
# ============================================================================

def lint_python_code(code: str, check_types: bool = True) -> ValidationResult:
    """
    Lint Python code using ruff and optionally mypy.

    Args:
        code: Python source code to validate
        check_types: Whether to run mypy type checking (default: True)

    Returns:
        ValidationResult with errors and warnings
    """
    errors = []
    warnings = []
    linter_output = {}

    # Create temporary file for linting
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        temp_file = Path(f.name)
        temp_file.write_text(code)

    try:
        # Run ruff linter
        ruff_result = _run_ruff(temp_file)
        linter_output['ruff'] = ruff_result

        # Parse ruff output
        for issue in ruff_result.get('issues', []):
            # Ruff doesn't provide severity, so we determine it by rule code
            # Syntax errors (E999, invalid-syntax) should be errors, not warnings
            code = issue.get('code', '')
            is_syntax_error = code in ['E999', 'invalid-syntax', 'syntax-error']

            validation_issue = ValidationIssue(
                line=issue.get('location', {}).get('row', 0),
                column=issue.get('location', {}).get('column', 0),
                severity='error' if is_syntax_error else 'warning',
                message=issue.get('message', ''),
                rule_id=code
            )

            if validation_issue.severity == 'error':
                errors.append(validation_issue)
            else:
                warnings.append(validation_issue)

        # Run mypy type checker (optional)
        if check_types:
            mypy_result = _run_mypy(temp_file)
            linter_output['mypy'] = mypy_result

            # Parse mypy output
            for issue in mypy_result.get('issues', []):
                validation_issue = ValidationIssue(
                    line=issue.get('line', 0),
                    column=issue.get('column', 0),
                    severity='error',
                    message=issue.get('message', ''),
                    rule_id='mypy'
                )
                errors.append(validation_issue)

    finally:
        # Cleanup temp file
        if temp_file.exists():
            temp_file.unlink()

    # Determine if auto-fixable
    auto_fixable = all(
        issue.rule_id in ('F401', 'W291', 'W293', 'E501')  # Import unused, trailing whitespace, line too long
        for issue in errors
    )

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        linter_output=linter_output,
        auto_fixable=auto_fixable
    )


def _run_ruff(file_path: Path) -> Dict:
    """Run ruff linter on Python file."""
    try:
        result = subprocess.run(
            ['ruff', 'check', '--output-format=json', str(file_path)],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.stdout:
            return {'issues': json.loads(result.stdout)}
        else:
            return {'issues': []}

    except subprocess.TimeoutExpired:
        logger.error("Ruff linting timed out")
        return {'issues': [], 'error': 'timeout'}
    except FileNotFoundError:
        logger.warning("Ruff not installed - skipping Python linting")
        return {'issues': [], 'error': 'ruff_not_found'}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse ruff output: {e}")
        return {'issues': [], 'error': 'parse_error'}
    except Exception as e:
        logger.error(f"Unexpected error running ruff: {e}")
        return {'issues': [], 'error': str(e)}


def _run_mypy(file_path: Path) -> Dict:
    """Run mypy type checker on Python file."""
    try:
        result = subprocess.run(
            ['mypy', '--output=json', str(file_path)],
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.stdout:
            # Parse mypy JSON output (one JSON object per line)
            issues = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        issue = json.loads(line)
                        issues.append(issue)
                    except json.JSONDecodeError:
                        continue

            return {'issues': issues}
        else:
            return {'issues': []}

    except subprocess.TimeoutExpired:
        logger.error("Mypy type checking timed out")
        return {'issues': [], 'error': 'timeout'}
    except FileNotFoundError:
        logger.warning("Mypy not installed - skipping type checking")
        return {'issues': [], 'error': 'mypy_not_found'}
    except Exception as e:
        logger.error(f"Unexpected error running mypy: {e}")
        return {'issues': [], 'error': str(e)}


def auto_fix_python_code(code: str) -> str:
    """
    Attempt to auto-fix common Python linting issues using ruff.

    Args:
        code: Python source code with linting issues

    Returns:
        Fixed code (or original if auto-fix fails)
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        temp_file = Path(f.name)
        temp_file.write_text(code)

    try:
        # Run ruff with --fix flag
        result = subprocess.run(
            ['ruff', 'check', '--fix', str(temp_file)],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Read fixed code
        if result.returncode == 0 or temp_file.exists():
            fixed_code = temp_file.read_text()
            return fixed_code
        else:
            logger.warning("Ruff auto-fix failed")
            return code

    except Exception as e:
        logger.error(f"Error during auto-fix: {e}")
        return code
    finally:
        if temp_file.exists():
            temp_file.unlink()


# ============================================================================
# SQL Query Validation
# ============================================================================

def lint_sql_query(query: str) -> ValidationResult:
    """
    Validate SQL query for safety and correctness.

    Args:
        query: SQL query string

    Returns:
        ValidationResult with errors and warnings
    """
    errors = []
    warnings = []

    # Normalize query (lowercase for checks)
    query_lower = query.lower().strip()

    # Safety checks: Ensure read-only
    dangerous_keywords = ['delete', 'update', 'drop', 'alter', 'create', 'insert', 'truncate']
    for keyword in dangerous_keywords:
        if keyword in query_lower:
            errors.append(ValidationIssue(
                line=0,
                column=0,
                severity='error',
                message=f"Dangerous keyword '{keyword}' not allowed - queries must be read-only (SELECT only)",
                rule_id='SQL001'
            ))

    # Check for LIMIT clause (required for safety)
    if 'limit' not in query_lower:
        warnings.append(ValidationIssue(
            line=0,
            column=0,
            severity='warning',
            message="No LIMIT clause found - consider adding to prevent large result sets",
            rule_id='SQL002'
        ))

    # Check for SELECT keyword
    if 'select' not in query_lower:
        errors.append(ValidationIssue(
            line=0,
            column=0,
            severity='error',
            message="Query must contain SELECT statement",
            rule_id='SQL003'
        ))

    # Check for potential SQL injection patterns
    suspicious_patterns = ["';", "--", "/*", "*/", "union", "exec(", "execute("]
    for pattern in suspicious_patterns:
        if pattern in query_lower:
            warnings.append(ValidationIssue(
                line=0,
                column=0,
                severity='warning',
                message=f"Suspicious pattern '{pattern}' detected - verify query safety",
                rule_id='SQL004'
            ))

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        linter_output={'sql_validation': 'basic_safety_checks'}
    )


# ============================================================================
# Combined Validation
# ============================================================================

def validate_generated_code(
    code: str,
    language: str,
    auto_fix: bool = True
) -> ValidationResult:
    """
    Validate generated code based on language.

    Args:
        code: Source code to validate
        language: "python" or "sql"
        auto_fix: Whether to attempt auto-fixing issues (Python only)

    Returns:
        ValidationResult

    Raises:
        ValueError: If language not supported
    """
    if language == "python":
        # First attempt: lint as-is
        result = lint_python_code(code)

        # Auto-fix if requested and fixable
        if auto_fix and result.auto_fixable and result.has_errors:
            logger.info("Attempting to auto-fix Python code...")
            fixed_code = auto_fix_python_code(code)

            # Re-validate fixed code
            result = lint_python_code(fixed_code)

            if result.valid:
                logger.info("✅ Auto-fix successful")
            else:
                logger.warning("⚠️ Auto-fix did not resolve all issues")

        return result

    elif language == "sql":
        return lint_sql_query(code)

    else:
        raise ValueError(f"Unsupported language: {language}")


# ============================================================================
# Validation Report Formatting
# ============================================================================

def format_validation_report(result: ValidationResult) -> str:
    """
    Format validation result as human-readable report.

    Args:
        result: ValidationResult to format

    Returns:
        Formatted report string
    """
    lines = []

    # Summary
    lines.append("=" * 60)
    lines.append(result.get_summary())
    lines.append("=" * 60)

    # Errors
    if result.has_errors:
        lines.append("\n❌ ERRORS:")
        for i, error in enumerate(result.errors, 1):
            lines.append(f"  {i}. Line {error.line}, Col {error.column} [{error.rule_id}]")
            lines.append(f"     {error.message}")

    # Warnings
    if result.has_warnings:
        lines.append("\n⚠️  WARNINGS:")
        for i, warning in enumerate(result.warnings, 1):
            lines.append(f"  {i}. Line {warning.line}, Col {warning.column} [{warning.rule_id}]")
            lines.append(f"     {warning.message}")

    # Auto-fixable notice
    if result.auto_fixable and result.has_errors:
        lines.append("\n💡 TIP: These errors can be auto-fixed. Rerun with auto_fix=True")

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)
