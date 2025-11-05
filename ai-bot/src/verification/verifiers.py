"""
Result Verification System

Verifies business logic and data quality after calculations/operations.
Used to check that results make sense before returning to users.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """Result of verification check"""
    passed: bool
    warnings: List[str] = None
    errors: List[str] = None
    suggestions: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []
        if self.suggestions is None:
            self.suggestions = []

    def add_warning(self, message: str):
        """Add a warning message"""
        self.warnings.append(message)

    def add_error(self, message: str):
        """Add an error message"""
        self.errors.append(message)
        self.passed = False

    def add_suggestion(self, message: str):
        """Add a suggestion"""
        self.suggestions.append(message)

    def has_issues(self) -> bool:
        """Check if there are any issues"""
        return len(self.warnings) > 0 or len(self.errors) > 0

    def get_summary(self) -> str:
        """Get human-readable summary"""
        parts = []

        if self.errors:
            parts.append(f"❌ Errors: {len(self.errors)}")
        if self.warnings:
            parts.append(f"⚠️ Warnings: {len(self.warnings)}")
        if self.suggestions:
            parts.append(f"💡 Suggestions: {len(self.suggestions)}")

        if not parts:
            return "✅ All checks passed"

        return " | ".join(parts)


def verify_financial_balance(
    revenue: Union[int, float],
    cost: Union[int, float],
    profit: Union[int, float],
    tolerance: float = 0.01,
) -> VerificationResult:
    """
    Verify financial balance equation: Revenue - Cost = Profit

    Args:
        revenue: Total revenue
        cost: Total cost
        profit: Reported profit
        tolerance: Allowed difference (default 0.01 for rounding)

    Returns:
        VerificationResult with any issues found
    """
    result = VerificationResult(passed=True)

    # Check equation balance
    expected_profit = revenue - cost
    difference = abs(expected_profit - profit)

    if difference > tolerance:
        result.add_error(
            f"Balance equation violated: "
            f"Revenue ({revenue}) - Cost ({cost}) = {expected_profit}, "
            f"but profit reported as {profit} (difference: {difference})"
        )

    # Check logical constraints
    if cost > revenue:
        result.add_warning(
            f"Cost ({cost}) exceeds revenue ({revenue}). "
            f"This results in negative profit ({profit})."
        )

    if profit < 0:
        result.add_warning(f"Negative profit: {profit}")

    return result


def verify_percentage_sum(
    percentages: List[float],
    expected_total: float = 100.0,
    tolerance: float = 0.1,
) -> VerificationResult:
    """
    Verify that percentages sum to expected total (usually 100%).

    Args:
        percentages: List of percentage values
        expected_total: Expected sum (default 100)
        tolerance: Allowed difference (default 0.1%)

    Returns:
        VerificationResult with any issues found
    """
    result = VerificationResult(passed=True)

    total = sum(percentages)
    difference = abs(total - expected_total)

    if difference > tolerance:
        result.add_error(
            f"Percentages do not sum to {expected_total}%: "
            f"got {total}% (difference: {difference}%)"
        )

    # Check for negative percentages
    negative = [p for p in percentages if p < 0]
    if negative:
        result.add_warning(f"Found {len(negative)} negative percentages: {negative}")

    return result


def verify_date_range(
    start_date: str,
    end_date: str,
    max_days: Optional[int] = None,
) -> VerificationResult:
    """
    Verify date range is valid and reasonable.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        max_days: Maximum allowed days (None for no limit)

    Returns:
        VerificationResult with any issues found
    """
    result = VerificationResult(passed=True)

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        # Check order
        if start > end:
            result.add_error(f"Start date {start_date} is after end date {end_date}")
            return result

        # Check range
        days = (end - start).days
        if max_days and days > max_days:
            result.add_warning(
                f"Date range is {days} days, which exceeds limit of {max_days} days"
            )

        # Check for future dates
        today = datetime.now()
        if end > today:
            result.add_warning(f"End date {end_date} is in the future")

    except ValueError as e:
        result.add_error(f"Invalid date format: {e}")

    return result


def verify_positive_number(
    value: Union[int, float],
    field_name: str = "value",
    allow_zero: bool = True,
) -> VerificationResult:
    """
    Verify that a number is positive (or non-negative if allow_zero).

    Args:
        value: Value to verify
        field_name: Name of the field (for error messages)
        allow_zero: Whether zero is allowed

    Returns:
        VerificationResult with any issues found
    """
    result = VerificationResult(passed=True)

    if not isinstance(value, (int, float)):
        result.add_error(f"{field_name} must be a number, got {type(value).__name__}")
        return result

    if allow_zero:
        if value < 0:
            result.add_error(f"{field_name} must be non-negative, got {value}")
    else:
        if value <= 0:
            result.add_error(f"{field_name} must be positive, got {value}")

    return result


def verify_data_quality(
    data: List[Dict],
    required_fields: List[str],
    min_records: int = 1,
) -> VerificationResult:
    """
    Verify data quality (completeness, required fields).

    Args:
        data: List of data records
        required_fields: Fields that must be present
        min_records: Minimum number of records required

    Returns:
        VerificationResult with any issues found
    """
    result = VerificationResult(passed=True)

    # Check record count
    if len(data) < min_records:
        result.add_error(
            f"Insufficient data: got {len(data)} records, "
            f"minimum {min_records} required"
        )
        return result

    # Check for missing fields
    missing_fields = {}
    for i, record in enumerate(data):
        for field in required_fields:
            if field not in record or record[field] is None:
                if field not in missing_fields:
                    missing_fields[field] = []
                missing_fields[field].append(i)

    # Report missing fields
    for field, indices in missing_fields.items():
        count = len(indices)
        percentage = (count / len(data)) * 100
        if percentage > 50:
            result.add_error(
                f"Field '{field}' missing in {count}/{len(data)} records ({percentage:.1f}%)"
            )
        elif percentage > 10:
            result.add_warning(
                f"Field '{field}' missing in {count}/{len(data)} records ({percentage:.1f}%)"
            )
        else:
            result.add_suggestion(
                f"Field '{field}' missing in {count} records"
            )

    return result


def verify_menu_profitability(
    dish_data: Dict,
    min_profit_margin: float = 0.0,
) -> VerificationResult:
    """
    Verify menu item profitability data.

    Args:
        dish_data: Dict with keys: revenue, cost, margin, sales_count
        min_profit_margin: Minimum acceptable margin (default 0)

    Returns:
        VerificationResult with any issues found
    """
    result = VerificationResult(passed=True)

    # Check required fields
    required = ["revenue", "cost", "margin", "sales_count"]
    for field in required:
        if field not in dish_data:
            result.add_error(f"Missing required field: {field}")
            return result

    revenue = dish_data["revenue"]
    cost = dish_data["cost"]
    margin = dish_data["margin"]
    sales = dish_data["sales_count"]

    # Verify calculations
    expected_profit = revenue - cost
    expected_margin = (expected_profit / revenue) * 100 if revenue > 0 else 0

    if abs(expected_margin - margin) > 0.1:
        result.add_warning(
            f"Margin calculation mismatch: "
            f"expected {expected_margin:.1f}%, got {margin:.1f}%"
        )

    # Check profitability
    if margin < min_profit_margin:
        result.add_warning(
            f"Low profit margin: {margin:.1f}% "
            f"(minimum: {min_profit_margin:.1f}%)"
        )

    # Check for negative profit
    if margin < 0:
        result.add_error(f"Negative profit margin: {margin:.1f}%")

    # Check sales volume
    if sales == 0:
        result.add_warning("No sales recorded for this item")
    elif sales < 5:
        result.add_suggestion(
            f"Low sales volume: {sales} (may not be statistically significant)"
        )

    return result


def verify_operations_metrics(
    metrics: Dict,
) -> VerificationResult:
    """
    Verify operations metrics (completion rate, cycle time, etc.).

    Args:
        metrics: Dict with metrics to verify

    Returns:
        VerificationResult with any issues found
    """
    result = VerificationResult(passed=True)

    # Check completion rate
    if "completion_rate" in metrics:
        rate = metrics["completion_rate"]
        if rate < 0 or rate > 100:
            result.add_error(f"Invalid completion rate: {rate}% (must be 0-100)")
        elif rate < 70:
            result.add_warning(f"Low completion rate: {rate}% (target: >85%)")
        elif rate >= 85:
            result.add_suggestion(f"Good completion rate: {rate}%")

    # Check cycle time
    if "cycle_time_days" in metrics:
        days = metrics["cycle_time_days"]
        if days < 0:
            result.add_error(f"Invalid cycle time: {days} days (must be positive)")
        elif days > 30:
            result.add_warning(f"High cycle time: {days} days (investigate bottlenecks)")

    # Check on-time delivery
    if "on_time_rate" in metrics:
        rate = metrics["on_time_rate"]
        if rate < 0 or rate > 100:
            result.add_error(f"Invalid on-time rate: {rate}% (must be 0-100)")
        elif rate < 80:
            result.add_warning(f"Low on-time delivery: {rate}% (target: >90%)")

    return result


def verify_html_structure(html: str) -> VerificationResult:
    """
    Verify HTML structure (basic checks, not full validation).

    Args:
        html: HTML content to verify

    Returns:
        VerificationResult with any issues found
    """
    result = VerificationResult(passed=True)

    # Check for empty content
    if not html or len(html.strip()) < 10:
        result.add_error("HTML content is empty or too short")
        return result

    # Check for basic structure
    html_lower = html.lower()

    if "<html" not in html_lower:
        result.add_warning("Missing <html> tag")

    if "<body" not in html_lower:
        result.add_warning("Missing <body> tag")

    if "<head" not in html_lower:
        result.add_warning("Missing <head> tag")

    # Check for unclosed tags (basic check)
    open_tags = html.count("<div")
    close_tags = html.count("</div>")
    if open_tags != close_tags:
        result.add_warning(
            f"Mismatched <div> tags: {open_tags} opening, {close_tags} closing"
        )

    return result
