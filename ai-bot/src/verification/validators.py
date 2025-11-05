"""
Input Validation System

Provides decorators for validating tool inputs with lenient/strict modes.
Follows principle: warn first, block only when necessary.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Type
from functools import wraps
from datetime import datetime
from .config import get_verification_config

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation fails in strict mode"""
    pass


class ValidationWarning(UserWarning):
    """Raised when validation fails in lenient mode"""
    pass


def validate_inputs(
    required: Optional[List[str]] = None,
    types: Optional[Dict[str, Type]] = None,
    ranges: Optional[Dict[str, tuple]] = None,
    custom: Optional[Callable[[Dict], Optional[str]]] = None,
) -> Callable:
    """
    Decorator for validating tool inputs.

    Args:
        required: List of required field names
        types: Dict mapping field names to expected types
        ranges: Dict mapping field names to (min, max) tuples
        custom: Custom validation function returning error message or None

    Example:
        @validate_inputs(
            required=["revenue", "cost"],
            types={"revenue": float, "cost": float},
            ranges={"revenue": (0, float('inf'))}
        )
        async def calculate_profit_tool(args):
            ...

    Behavior:
        - Lenient mode: Logs warning, allows request
        - Strict mode: Raises ValidationError, blocks request
        - Off mode: No validation
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(args: Dict, bot_id: str = "default", *func_args, **func_kwargs):
            # Get bot configuration
            config = get_verification_config(bot_id)

            if not config.is_enabled():
                # Verification disabled
                return await func(args, *func_args, **func_kwargs)

            # Collect validation errors
            errors = []

            # Validate required fields
            if required:
                for field in required:
                    if field not in args or args[field] is None:
                        errors.append(f"Missing required field: {field}")

            # Validate types
            if types:
                for field, expected_type in types.items():
                    if field in args and args[field] is not None:
                        if not isinstance(args[field], expected_type):
                            actual_type = type(args[field]).__name__
                            expected_name = expected_type.__name__
                            errors.append(
                                f"Invalid type for {field}: "
                                f"expected {expected_name}, got {actual_type}"
                            )

            # Validate ranges
            if ranges:
                for field, (min_val, max_val) in ranges.items():
                    if field in args and args[field] is not None:
                        value = args[field]
                        if isinstance(value, (int, float)):
                            if value < min_val or value > max_val:
                                errors.append(
                                    f"{field} out of range: "
                                    f"{value} not in [{min_val}, {max_val}]"
                                )

            # Custom validation
            if custom:
                custom_error = custom(args)
                if custom_error:
                    errors.append(custom_error)

            # Handle errors based on mode
            if errors:
                error_msg = "; ".join(errors)

                if config.should_block():
                    # Strict mode: block request
                    logger.error(f"[Verification] ❌ Blocking request: {error_msg}")
                    raise ValidationError(error_msg)
                elif config.should_warn():
                    # Lenient mode: warn but allow
                    logger.warning(f"[Verification] ⚠️ Input validation warning: {error_msg}")
                    # Continue execution despite warnings

            # Execute original function
            return await func(args, *func_args, **func_kwargs)

        return wrapper

    return decorator


def validate_date_format(date_str: str) -> bool:
    """
    Validate date string format (YYYY-MM-DD).

    Args:
        date_str: Date string to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def validate_date_range(start_date: str, end_date: str) -> Optional[str]:
    """
    Validate date range (start <= end).

    Args:
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD)

    Returns:
        Error message if invalid, None if valid
    """
    if not validate_date_format(start_date):
        return f"Invalid start date format: {start_date} (expected YYYY-MM-DD)"

    if not validate_date_format(end_date):
        return f"Invalid end date format: {end_date} (expected YYYY-MM-DD)"

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    if start > end:
        return f"Start date {start_date} is after end date {end_date}"

    return None


def validate_percentage(value: float) -> Optional[str]:
    """
    Validate percentage value (0 <= value <= 100 or 0 <= value <= 1).

    Args:
        value: Percentage value to validate

    Returns:
        Error message if invalid, None if valid
    """
    if not isinstance(value, (int, float)):
        return f"Percentage must be a number, got {type(value).__name__}"

    # Accept both 0-1 and 0-100 ranges
    if 0 <= value <= 1 or 0 <= value <= 100:
        return None

    return f"Percentage {value} out of range (expected 0-1 or 0-100)"


def validate_positive_number(value: Any, field_name: str = "value") -> Optional[str]:
    """
    Validate that a number is positive.

    Args:
        value: Value to validate
        field_name: Name of the field (for error messages)

    Returns:
        Error message if invalid, None if valid
    """
    if not isinstance(value, (int, float)):
        return f"{field_name} must be a number, got {type(value).__name__}"

    if value < 0:
        return f"{field_name} must be positive, got {value}"

    return None


def validate_non_zero(value: Any, field_name: str = "value") -> Optional[str]:
    """
    Validate that a number is non-zero.

    Args:
        value: Value to validate
        field_name: Name of the field (for error messages)

    Returns:
        Error message if invalid, None if valid
    """
    if not isinstance(value, (int, float)):
        return f"{field_name} must be a number, got {type(value).__name__}"

    if value == 0:
        return f"{field_name} cannot be zero"

    return None


# Example usage validators for common patterns

def validate_financial_calculation(args: Dict) -> Optional[str]:
    """
    Custom validator for financial calculations.

    Example:
        @validate_inputs(custom=validate_financial_calculation)
        async def calculate_profit_tool(args):
            ...
    """
    errors = []

    # Check required fields
    if "revenue" in args:
        if err := validate_positive_number(args["revenue"], "revenue"):
            errors.append(err)

    if "cost" in args:
        if err := validate_positive_number(args["cost"], "cost"):
            errors.append(err)

    # Check logic
    if "revenue" in args and "cost" in args:
        if args["cost"] > args["revenue"]:
            errors.append(
                f"Cost ({args['cost']}) exceeds revenue ({args['revenue']}). "
                "This results in negative profit."
            )

    return "; ".join(errors) if errors else None


def validate_date_range_query(args: Dict) -> Optional[str]:
    """
    Custom validator for date range queries.

    Example:
        @validate_inputs(custom=validate_date_range_query)
        async def query_data_tool(args):
            ...
    """
    if "start_date" not in args and "end_date" not in args:
        # No date range specified, OK
        return None

    if "start_date" in args and "end_date" in args:
        return validate_date_range(args["start_date"], args["end_date"])

    # Only one date specified - warn but allow
    if "start_date" in args:
        return "Only start_date specified, end_date will default to today"

    if "end_date" in args:
        return "Only end_date specified, start_date will default to beginning of period"

    return None
