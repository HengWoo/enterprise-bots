"""
Output Formatting System

Provides safe formatting functions for outputs with validation.
Ensures consistent formatting across all bots.
"""

import logging
from typing import Optional, Union
from datetime import datetime
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)


class FormatError(Exception):
    """Raised when formatting fails"""
    pass


def format_currency(
    amount: Union[int, float, Decimal],
    currency: str = "¥",
    decimals: int = 2,
    thousands_separator: str = ",",
) -> str:
    """
    Format number as currency.

    Args:
        amount: Amount to format
        currency: Currency symbol (default: ¥)
        decimals: Number of decimal places
        thousands_separator: Separator for thousands

    Returns:
        Formatted currency string

    Example:
        >>> format_currency(1234.56)
        "¥1,234.56"
        >>> format_currency(1234.56, currency="$")
        "$1,234.56"
    """
    try:
        # Convert to float and round
        value = round(float(amount), decimals)

        # Split into integer and decimal parts
        integer_part = int(abs(value))
        decimal_part = abs(value) - integer_part

        # Format integer part with thousands separator
        integer_str = f"{integer_part:,}".replace(",", thousands_separator)

        # Format decimal part
        if decimals > 0:
            decimal_str = f"{decimal_part:.{decimals}f}"[2:]  # Remove "0."
            result = f"{integer_str}.{decimal_str}"
        else:
            result = integer_str

        # Add currency symbol and sign
        if value < 0:
            return f"-{currency}{result}"
        else:
            return f"{currency}{result}"

    except (ValueError, TypeError) as e:
        logger.warning(f"[Format] ⚠️ Currency formatting failed: {e}")
        return f"{currency}{amount}"


def format_percentage(
    value: Union[int, float],
    decimals: int = 1,
    include_sign: bool = False,
) -> str:
    """
    Format number as percentage.

    Args:
        value: Value to format (0-1 or 0-100)
        decimals: Number of decimal places
        include_sign: Whether to include + for positive values

    Returns:
        Formatted percentage string

    Example:
        >>> format_percentage(0.234, decimals=1)
        "23.4%"
        >>> format_percentage(23.4, decimals=1)
        "23.4%"
        >>> format_percentage(0.1, include_sign=True)
        "+10.0%"
    """
    try:
        # Auto-detect if value is 0-1 or 0-100 range
        if 0 <= abs(value) <= 1:
            percentage = value * 100
        else:
            percentage = value

        formatted = f"{percentage:.{decimals}f}%"

        if include_sign and percentage > 0:
            return f"+{formatted}"

        return formatted

    except (ValueError, TypeError) as e:
        logger.warning(f"[Format] ⚠️ Percentage formatting failed: {e}")
        return f"{value}%"


def format_number(
    value: Union[int, float],
    decimals: int = 0,
    thousands_separator: str = ",",
) -> str:
    """
    Format number with thousands separator.

    Args:
        value: Value to format
        decimals: Number of decimal places
        thousands_separator: Separator for thousands

    Returns:
        Formatted number string

    Example:
        >>> format_number(1234567)
        "1,234,567"
        >>> format_number(1234.5678, decimals=2)
        "1,234.57"
    """
    try:
        if decimals > 0:
            formatted = f"{value:,.{decimals}f}"
        else:
            formatted = f"{int(value):,}"

        if thousands_separator != ",":
            formatted = formatted.replace(",", thousands_separator)

        return formatted

    except (ValueError, TypeError) as e:
        logger.warning(f"[Format] ⚠️ Number formatting failed: {e}")
        return str(value)


def format_date(
    date: Union[str, datetime],
    format_str: str = "%Y-%m-%d",
    output_format: str = "中文",  # "中文" or "English"
) -> str:
    """
    Format date in various formats.

    Args:
        date: Date to format (string or datetime)
        format_str: Input format string (if date is string)
        output_format: Output format ("中文" or "English")

    Returns:
        Formatted date string

    Example:
        >>> format_date("2025-10-29", output_format="中文")
        "2025年10月29日"
        >>> format_date("2025-10-29", output_format="English")
        "October 29, 2025"
    """
    try:
        # Convert string to datetime if needed
        if isinstance(date, str):
            dt = datetime.strptime(date, format_str)
        else:
            dt = date

        # Format based on output format
        if output_format == "中文":
            return f"{dt.year}年{dt.month}月{dt.day}日"
        elif output_format == "English":
            return dt.strftime("%B %d, %Y")
        else:
            return dt.strftime(format_str)

    except (ValueError, TypeError) as e:
        logger.warning(f"[Format] ⚠️ Date formatting failed: {e}")
        return str(date)


def format_change(
    current: Union[int, float],
    previous: Union[int, float],
    format_as: str = "percentage",  # "percentage", "absolute", "both"
    include_arrow: bool = True,
) -> str:
    """
    Format change between two values.

    Args:
        current: Current value
        previous: Previous value
        format_as: How to format ("percentage", "absolute", "both")
        include_arrow: Whether to include arrow indicator

    Returns:
        Formatted change string

    Example:
        >>> format_change(120, 100)
        "↑ +20.0%"
        >>> format_change(80, 100)
        "↓ -20.0%"
        >>> format_change(120, 100, format_as="both")
        "↑ +20 (+20.0%)"
    """
    try:
        change = current - previous
        percentage = (change / previous * 100) if previous != 0 else 0

        # Determine arrow
        if include_arrow:
            if change > 0:
                arrow = "↑ "
            elif change < 0:
                arrow = "↓ "
            else:
                arrow = "→ "
        else:
            arrow = ""

        # Format sign
        sign = "+" if change > 0 else ""

        # Format based on type
        if format_as == "percentage":
            return f"{arrow}{sign}{percentage:.1f}%"
        elif format_as == "absolute":
            return f"{arrow}{sign}{change:,.0f}"
        elif format_as == "both":
            return f"{arrow}{sign}{change:,.0f} ({sign}{percentage:.1f}%)"
        else:
            return f"{sign}{percentage:.1f}%"

    except (ValueError, TypeError, ZeroDivisionError) as e:
        logger.warning(f"[Format] ⚠️ Change formatting failed: {e}")
        return f"{current} vs {previous}"


def format_duration(
    days: Union[int, float],
    include_hours: bool = False,
    chinese: bool = True,
) -> str:
    """
    Format duration in days.

    Args:
        days: Duration in days
        include_hours: Whether to include hours
        chinese: Whether to use Chinese format

    Returns:
        Formatted duration string

    Example:
        >>> format_duration(3.5, chinese=True)
        "3.5天"
        >>> format_duration(3.5, include_hours=True, chinese=True)
        "3天12小时"
        >>> format_duration(3.5, chinese=False)
        "3.5 days"
    """
    try:
        if include_hours:
            whole_days = int(days)
            hours = int((days - whole_days) * 24)

            if chinese:
                if hours > 0:
                    return f"{whole_days}天{hours}小时"
                else:
                    return f"{whole_days}天"
            else:
                if hours > 0:
                    return f"{whole_days} days {hours} hours"
                else:
                    return f"{whole_days} days"
        else:
            if chinese:
                return f"{days:.1f}天"
            else:
                day_word = "day" if days == 1 else "days"
                return f"{days:.1f} {day_word}"

    except (ValueError, TypeError) as e:
        logger.warning(f"[Format] ⚠️ Duration formatting failed: {e}")
        return f"{days} days"


def format_ratio(
    numerator: Union[int, float],
    denominator: Union[int, float],
    format_as: str = "decimal",  # "decimal", "percentage", "ratio", "fraction"
) -> str:
    """
    Format ratio in various formats.

    Args:
        numerator: Top number
        denominator: Bottom number
        format_as: Output format

    Returns:
        Formatted ratio string

    Example:
        >>> format_ratio(1, 2, format_as="decimal")
        "0.50"
        >>> format_ratio(1, 2, format_as="percentage")
        "50.0%"
        >>> format_ratio(1, 2, format_as="ratio")
        "1:2"
        >>> format_ratio(1, 2, format_as="fraction")
        "1/2"
    """
    try:
        if format_as == "ratio":
            return f"{numerator}:{denominator}"
        elif format_as == "fraction":
            return f"{numerator}/{denominator}"
        elif format_as == "percentage":
            percentage = (numerator / denominator * 100) if denominator != 0 else 0
            return f"{percentage:.1f}%"
        else:  # decimal
            decimal = (numerator / denominator) if denominator != 0 else 0
            return f"{decimal:.2f}"

    except (ValueError, TypeError, ZeroDivisionError) as e:
        logger.warning(f"[Format] ⚠️ Ratio formatting failed: {e}")
        return f"{numerator}/{denominator}"


def format_html_metric_card(
    label: str,
    value: str,
    change: Optional[str] = None,
    color: str = "#2c5aa0",
) -> str:
    """
    Format metric as HTML card.

    Args:
        label: Metric label
        value: Metric value (pre-formatted)
        change: Change indicator (e.g., "↑ +10%")
        color: Color theme

    Returns:
        HTML string for metric card
    """
    change_html = ""
    if change:
        # Determine color based on arrow
        if "↑" in change:
            change_color = "#388e3c"  # Green
        elif "↓" in change:
            change_color = "#d32f2f"  # Red
        else:
            change_color = "#666"     # Gray

        change_html = f'<span style="color: {change_color}; margin-left: 8px;">{change}</span>'

    return f'''
<div style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
            color: white; padding: 15px; border-radius: 8px; margin: 10px 0;">
    <div style="font-size: 14px; opacity: 0.9;">{label}</div>
    <div style="font-size: 28px; font-weight: bold; margin: 5px 0;">
        {value}{change_html}
    </div>
</div>
'''
