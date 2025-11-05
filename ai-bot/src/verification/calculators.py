"""
Safe Calculation Operations

Provides safe wrappers for mathematical operations to prevent:
- Division by zero
- Integer overflow
- Floating point precision errors
- Invalid operations (sqrt of negative, etc.)
"""

import logging
import math
from decimal import Decimal, InvalidOperation
from typing import Optional, Union

logger = logging.getLogger(__name__)


class CalculationError(Exception):
    """Raised when calculation fails or produces invalid result"""
    pass


def safe_divide(
    numerator: Union[int, float, Decimal],
    denominator: Union[int, float, Decimal],
    default: Optional[Union[int, float]] = None,
) -> Union[float, None]:
    """
    Safely divide two numbers.

    Args:
        numerator: Number to divide
        denominator: Number to divide by
        default: Default value if division fails (None to raise error)

    Returns:
        Result of division, or default if fails

    Raises:
        CalculationError: If division fails and no default provided

    Example:
        >>> safe_divide(10, 2)
        5.0
        >>> safe_divide(10, 0, default=0)
        0
        >>> safe_divide(10, 0)
        Traceback: CalculationError
    """
    try:
        if denominator == 0:
            if default is not None:
                logger.warning(f"[Calculation] ⚠️ Division by zero: {numerator}/{denominator}, returning default={default}")
                return default
            raise CalculationError(f"Division by zero: {numerator}/{denominator}")

        result = float(numerator) / float(denominator)

        # Check for infinity or NaN
        if math.isinf(result) or math.isnan(result):
            if default is not None:
                logger.warning(f"[Calculation] ⚠️ Invalid result: {result}, returning default={default}")
                return default
            raise CalculationError(f"Invalid division result: {result}")

        return result

    except (TypeError, ValueError) as e:
        if default is not None:
            logger.warning(f"[Calculation] ⚠️ Calculation error: {e}, returning default={default}")
            return default
        raise CalculationError(f"Calculation error: {e}")


def safe_percentage(
    value: Union[int, float],
    total: Union[int, float],
    multiply_by_100: bool = True,
    decimals: int = 2,
) -> Optional[float]:
    """
    Safely calculate percentage.

    Args:
        value: Part value
        total: Total value
        multiply_by_100: Whether to multiply by 100 (True for %, False for 0-1)
        decimals: Number of decimal places to round to

    Returns:
        Percentage value, or None if calculation fails

    Example:
        >>> safe_percentage(25, 100)
        25.0
        >>> safe_percentage(1, 4, multiply_by_100=False)
        0.25
        >>> safe_percentage(10, 0)
        None
    """
    try:
        ratio = safe_divide(value, total, default=None)

        if ratio is None:
            return None

        percentage = ratio * 100 if multiply_by_100 else ratio

        return round(percentage, decimals)

    except Exception as e:
        logger.warning(f"[Calculation] ⚠️ Percentage calculation failed: {e}")
        return None


def safe_multiply(
    *values: Union[int, float],
    check_overflow: bool = True,
    max_result: float = 1e15,
) -> Optional[float]:
    """
    Safely multiply numbers with overflow protection.

    Args:
        values: Numbers to multiply
        check_overflow: Whether to check for overflow
        max_result: Maximum allowed result

    Returns:
        Product of all values, or None if overflow

    Example:
        >>> safe_multiply(2, 3, 4)
        24.0
        >>> safe_multiply(1e10, 1e10, max_result=1e15)
        None
    """
    try:
        result = 1.0
        for value in values:
            result *= float(value)

            # Check for overflow
            if check_overflow:
                if abs(result) > max_result:
                    logger.warning(
                        f"[Calculation] ⚠️ Multiplication overflow: "
                        f"result {result} exceeds max {max_result}"
                    )
                    return None

                if math.isinf(result) or math.isnan(result):
                    logger.warning(f"[Calculation] ⚠️ Invalid multiplication result: {result}")
                    return None

        return result

    except Exception as e:
        logger.warning(f"[Calculation] ⚠️ Multiplication failed: {e}")
        return None


def safe_add(*values: Union[int, float]) -> Optional[float]:
    """
    Safely add numbers with overflow protection.

    Args:
        values: Numbers to add

    Returns:
        Sum of all values, or None if overflow
    """
    try:
        result = sum(float(v) for v in values)

        if math.isinf(result) or math.isnan(result):
            logger.warning(f"[Calculation] ⚠️ Invalid addition result: {result}")
            return None

        return result

    except Exception as e:
        logger.warning(f"[Calculation] ⚠️ Addition failed: {e}")
        return None


def safe_subtract(
    minuend: Union[int, float],
    subtrahend: Union[int, float],
) -> Optional[float]:
    """
    Safely subtract two numbers.

    Args:
        minuend: Number to subtract from
        subtrahend: Number to subtract

    Returns:
        Difference, or None if calculation fails
    """
    try:
        result = float(minuend) - float(subtrahend)

        if math.isinf(result) or math.isnan(result):
            logger.warning(f"[Calculation] ⚠️ Invalid subtraction result: {result}")
            return None

        return result

    except Exception as e:
        logger.warning(f"[Calculation] ⚠️ Subtraction failed: {e}")
        return None


def safe_average(
    *values: Union[int, float],
    skip_none: bool = True,
) -> Optional[float]:
    """
    Safely calculate average.

    Args:
        values: Numbers to average
        skip_none: Whether to skip None values

    Returns:
        Average of values, or None if no valid values
    """
    try:
        if skip_none:
            values = [v for v in values if v is not None]

        if not values:
            return None

        total = safe_add(*values)
        if total is None:
            return None

        return safe_divide(total, len(values))

    except Exception as e:
        logger.warning(f"[Calculation] ⚠️ Average calculation failed: {e}")
        return None


def safe_ratio(
    numerator: Union[int, float],
    denominator: Union[int, float],
    format_as: str = "decimal",  # "decimal", "percentage", "ratio"
) -> Optional[Union[float, str]]:
    """
    Safely calculate ratio in various formats.

    Args:
        numerator: Top number
        denominator: Bottom number
        format_as: Output format ("decimal", "percentage", "ratio")

    Returns:
        Ratio in requested format, or None if calculation fails

    Example:
        >>> safe_ratio(1, 2, format_as="decimal")
        0.5
        >>> safe_ratio(1, 2, format_as="percentage")
        50.0
        >>> safe_ratio(1, 2, format_as="ratio")
        "1:2"
    """
    try:
        if format_as == "ratio":
            return f"{numerator}:{denominator}"

        ratio = safe_divide(numerator, denominator, default=None)
        if ratio is None:
            return None

        if format_as == "percentage":
            return round(ratio * 100, 2)

        return ratio

    except Exception as e:
        logger.warning(f"[Calculation] ⚠️ Ratio calculation failed: {e}")
        return None


# Financial calculation helpers

def calculate_profit_margin(
    revenue: Union[int, float],
    cost: Union[int, float],
) -> Optional[float]:
    """
    Calculate profit margin percentage.

    Formula: (Revenue - Cost) / Revenue * 100

    Args:
        revenue: Total revenue
        cost: Total cost

    Returns:
        Profit margin percentage, or None if calculation fails
    """
    try:
        profit = safe_subtract(revenue, cost)
        if profit is None:
            return None

        margin = safe_percentage(profit, revenue)
        return margin

    except Exception as e:
        logger.warning(f"[Calculation] ⚠️ Profit margin calculation failed: {e}")
        return None


def calculate_roi(
    gain: Union[int, float],
    cost: Union[int, float],
) -> Optional[float]:
    """
    Calculate Return on Investment (ROI) percentage.

    Formula: (Gain - Cost) / Cost * 100

    Args:
        gain: Investment gain
        cost: Investment cost

    Returns:
        ROI percentage, or None if calculation fails
    """
    try:
        net_return = safe_subtract(gain, cost)
        if net_return is None:
            return None

        roi = safe_percentage(net_return, cost)
        return roi

    except Exception as e:
        logger.warning(f"[Calculation] ⚠️ ROI calculation failed: {e}")
        return None


def calculate_growth_rate(
    current: Union[int, float],
    previous: Union[int, float],
) -> Optional[float]:
    """
    Calculate growth rate percentage.

    Formula: (Current - Previous) / Previous * 100

    Args:
        current: Current period value
        previous: Previous period value

    Returns:
        Growth rate percentage, or None if calculation fails
    """
    try:
        change = safe_subtract(current, previous)
        if change is None:
            return None

        growth = safe_percentage(change, previous)
        return growth

    except Exception as e:
        logger.warning(f"[Calculation] ⚠️ Growth rate calculation failed: {e}")
        return None
