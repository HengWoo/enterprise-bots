"""
Verification Wrapper Utilities for v0.5.0

Helper functions to integrate verification module into agent tool outputs.
Provides simple interfaces for validating calculations, data, and content.

Author: Claude (AI Assistant)
Date: 2025-10-31
Version: 0.5.0
"""

from typing import Dict, Any, List, Optional, Union
from src.verification import (
    verify_financial_balance,
    verify_positive_number,
    verify_date_range,
    verify_html_presentation,
    safe_divide,
    safe_percentage,
    ValidationWarning,
    VerificationResult
)


def verify_calculation_result(
    operation: str,
    inputs: Dict[str, Union[int, float]],
    result: Union[int, float, None] = None
) -> Dict[str, Any]:
    """
    Verify a calculation result is mathematically sound.

    Use this after performing calculations in tools to validate the math
    before returning to the user.

    Args:
        operation: Type of calculation (e.g., "profit_margin", "percentage", "division")
        inputs: Input values used in calculation
        result: Calculated result to verify (optional)

    Returns:
        {
            "valid": bool,
            "warnings": list[str],
            "errors": list[str],
            "message": str  # Human-readable summary
        }

    Example:
        >>> verify_calculation_result(
        ...     operation="profit_margin",
        ...     inputs={"revenue": 100, "cost": 120},
        ...     result=-0.2
        ... )
        {'valid': False, 'errors': ['Cost exceeds revenue'], 'message': '⚠️ ...'}
    """
    warnings: List[str] = []
    errors: List[str] = []

    try:
        # Operation-specific validation
        if operation == "profit_margin":
            revenue = inputs.get("revenue", 0)
            cost = inputs.get("cost", 0)

            # Check for impossible scenarios
            if cost > revenue:
                errors.append("Cost exceeds revenue - impossible profit margin")

            # Verify inputs are positive
            if revenue < 0 or cost < 0:
                errors.append("Revenue and cost must be positive numbers")

            # If result provided, verify it matches calculation
            if result is not None and revenue > 0:
                expected = (revenue - cost) / revenue
                if abs(expected - result) > 0.01:  # 1% tolerance
                    warnings.append(f"Result {result:.2%} differs from expected {expected:.2%}")

        elif operation == "percentage":
            value = inputs.get("value", 0)
            total = inputs.get("total", 0)

            if total == 0:
                errors.append("Cannot calculate percentage with zero total")
            elif value > total:
                warnings.append(f"Value ({value}) exceeds total ({total}) - percentage will be >100%")

        elif operation == "division":
            divisor = inputs.get("divisor", 0)
            if divisor == 0:
                errors.append("Division by zero is undefined")

        # Build human-readable message
        if errors:
            message = f"⚠️ Calculation error: {'; '.join(errors)}"
        elif warnings:
            message = f"⚠️ Warning: {'; '.join(warnings)}"
        else:
            message = "✓ Calculation verified"

        return {
            "valid": len(errors) == 0,
            "warnings": warnings,
            "errors": errors,
            "message": message
        }

    except Exception as e:
        return {
            "valid": False,
            "warnings": [],
            "errors": [f"Verification error: {str(e)}"],
            "message": f"⚠️ Verification failed: {str(e)}"
        }


def verify_financial_data_wrapper(
    data: Dict[str, float],
    check_balance: bool = True
) -> Dict[str, Any]:
    """
    Verify financial data follows accounting principles.

    Use this when processing profit calculations and financial statements.

    Args:
        data: Financial data (e.g., {"revenue": 1000, "cost": 600, "profit": 400})
        check_balance: Whether to verify balance equation (Revenue - Cost = Profit)

    Returns:
        {
            "valid": bool,
            "warnings": list[str],
            "errors": list[str],
            "message": str
        }

    Example:
        >>> verify_financial_data_wrapper({
        ...     "revenue": 1000,
        ...     "cost": 600,
        ...     "profit": 500  # Should be 400!
        ... })
        {'valid': False, 'errors': ['Balance equation violated...'], ...}
    """
    warnings: List[str] = []
    errors: List[str] = []

    try:
        # Check for negative values
        for key, value in data.items():
            if value < 0 and key not in ["net_income", "profit", "loss", "deficit"]:
                warnings.append(f"{key.replace('_', ' ').title()} has negative value: ${value:,.2f}")

        # Verify balance equation if requested (Revenue - Cost = Profit)
        if check_balance and all(k in data for k in ["revenue", "cost", "profit"]):
            result = verify_financial_balance(
                revenue=data["revenue"],
                cost=data["cost"],
                profit=data["profit"]
            )

            if not result.passed:
                errors.extend(result.errors)
            warnings.extend(result.warnings)

        # Build message
        if errors:
            message = f"⚠️ Financial data error: {'; '.join(errors)}"
        elif warnings:
            message = f"⚠️ Financial data warning: {'; '.join(warnings)}"
        else:
            message = "✓ Financial data verified"

        return {
            "valid": len(errors) == 0,
            "warnings": warnings,
            "errors": errors,
            "message": message
        }

    except Exception as e:
        return {
            "valid": False,
            "warnings": [],
            "errors": [f"Verification error: {str(e)}"],
            "message": f"⚠️ Financial verification failed: {str(e)}"
        }


def verify_html_content(
    html: str,
    check_structure: bool = True
) -> Dict[str, Any]:
    """
    Verify HTML content quality and structure.

    Use this before presenting HTML presentations or formatted
    content to users.

    Args:
        html: HTML string to verify
        check_structure: Whether to check HTML structure

    Returns:
        {
            "valid": bool,
            "warnings": list[str],
            "errors": list[str],
            "message": str,
            "quality_score": float  # 0.0 to 1.0
        }

    Example:
        >>> verify_html_content("<div><h2>Title</h2><p>Content</p></div>")
        {'valid': True, 'quality_score': 0.85, ...}
    """
    try:
        # Use visual verifier from verification module
        result = verify_html_presentation(html)

        # Calculate quality score from result
        quality_score = 1.0 if result.passed else 0.5
        if result.warnings:
            quality_score -= len(result.warnings) * 0.1

        # Build message
        if not result.passed:
            message = f"⚠️ HTML issues: {'; '.join(result.errors)}"
        elif result.warnings:
            message = f"⚠️ HTML warnings: {'; '.join(result.warnings)}"
        else:
            message = f"✓ HTML verified (quality: {quality_score:.0%})"

        return {
            "valid": result.passed,
            "warnings": result.warnings,
            "errors": result.errors,
            "message": message,
            "quality_score": max(0.0, min(1.0, quality_score))
        }

    except Exception as e:
        return {
            "valid": False,
            "warnings": [],
            "errors": [f"Verification error: {str(e)}"],
            "message": f"⚠️ HTML verification failed: {str(e)}",
            "quality_score": 0.0
        }


def add_verification_notice(
    original_message: str,
    verification_result: Dict[str, Any],
    mode: str = "lenient"
) -> str:
    """
    Add verification notice to an agent response message.

    In lenient mode: Only adds warning if there are issues
    In strict mode: Would block response (not implemented yet)

    Args:
        original_message: The original agent response
        verification_result: Result from verification functions
        mode: "lenient" or "strict"

    Returns:
        Modified message with verification notice if needed

    Example:
        >>> msg = "The profit margin is 25%"
        >>> result = {"valid": True, "warnings": ["Low margin"], "message": "..."}
        >>> add_verification_notice(msg, result)
        'The profit margin is 25%\n\n⚠️ Warning: Low margin'
    """
    if mode == "lenient":
        # Only add notice if there are warnings or errors
        if not verification_result.get("valid", True):
            # Has errors
            return f"{original_message}\n\n{verification_result.get('message', '')}"
        elif verification_result.get("warnings"):
            # Has warnings
            return f"{original_message}\n\n{verification_result.get('message', '')}"
        else:
            # All good, no notice needed
            return original_message

    elif mode == "strict":
        # TODO: In strict mode, would block response entirely if invalid
        # For now, same as lenient
        return add_verification_notice(original_message, verification_result, mode="lenient")

    return original_message


# Convenience function for quick validation
def quick_verify(
    value: Any,
    expected_type: type = None,
    min_value: float = None,
    max_value: float = None
) -> Dict[str, Any]:
    """
    Quick verification of a single value.

    Useful for simple checks without creating full validation context.

    Args:
        value: Value to verify
        expected_type: Expected type (int, float, str, etc.)
        min_value: Minimum allowed value (for numbers)
        max_value: Maximum allowed value (for numbers)

    Returns:
        {"valid": bool, "warnings": [], "errors": [], "message": str}

    Example:
        >>> quick_verify(150, expected_type=int, min_value=0, max_value=100)
        {'valid': False, 'errors': ['Value exceeds maximum'], ...}
    """
    errors: List[str] = []
    warnings: List[str] = []

    # Type check
    if expected_type is not None and not isinstance(value, expected_type):
        errors.append(f"Expected {expected_type.__name__}, got {type(value).__name__}")

    # Range check for numbers
    if isinstance(value, (int, float)):
        if min_value is not None and value < min_value:
            errors.append(f"Value {value} is below minimum {min_value}")
        if max_value is not None and value > max_value:
            errors.append(f"Value {value} exceeds maximum {max_value}")

    # Build message
    if errors:
        message = f"⚠️ Validation failed: {'; '.join(errors)}"
    elif warnings:
        message = f"⚠️ Warning: {'; '.join(warnings)}"
    else:
        message = "✓ Value verified"

    return {
        "valid": len(errors) == 0,
        "warnings": warnings,
        "errors": errors,
        "message": message
    }
