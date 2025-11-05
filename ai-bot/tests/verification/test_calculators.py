"""
Tests for verification calculators

Coverage: Safe math operations, overflow protection, financial calculations
"""

import pytest
import math
from src.verification.calculators import (
    CalculationError,
    safe_divide,
    safe_percentage,
    safe_multiply,
    safe_add,
    safe_subtract,
    safe_average,
    safe_ratio,
    calculate_profit_margin,
    calculate_roi,
    calculate_growth_rate,
)


class TestSafeDivide:
    """Test safe division operation"""

    def test_normal_division(self):
        """Test normal division"""
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(15, 3) == 5.0
        assert safe_divide(1, 2) == 0.5

    def test_division_by_zero_with_default(self):
        """Test division by zero with default value"""
        assert safe_divide(10, 0, default=0) == 0
        assert safe_divide(100, 0, default=-1) == -1

    def test_division_by_zero_no_default(self):
        """Test division by zero raises error"""
        with pytest.raises(CalculationError, match="Division by zero"):
            safe_divide(10, 0)

    def test_negative_division(self):
        """Test division with negative numbers"""
        assert safe_divide(-10, 2) == -5.0
        assert safe_divide(10, -2) == -5.0
        assert safe_divide(-10, -2) == 5.0

    def test_float_division(self):
        """Test division with floats"""
        assert abs(safe_divide(10.5, 2.5) - 4.2) < 0.01
        assert abs(safe_divide(1.0, 3.0) - 0.333) < 0.01

    def test_invalid_types_with_default(self):
        """Test division with invalid types returns default"""
        assert safe_divide("abc", 2, default=0) == 0
        assert safe_divide(10, "xyz", default=0) == 0
        assert safe_divide(None, 5, default=0) == 0


class TestSafePercentage:
    """Test safe percentage calculation"""

    def test_normal_percentage(self):
        """Test normal percentage calculation"""
        assert safe_percentage(25, 100) == 25.0
        assert safe_percentage(1, 4) == 25.0
        assert safe_percentage(50, 200) == 25.0

    def test_percentage_without_multiplication(self):
        """Test percentage as 0-1 ratio"""
        assert safe_percentage(1, 4, multiply_by_100=False) == 0.25
        assert safe_percentage(1, 2, multiply_by_100=False) == 0.5

    def test_percentage_decimals(self):
        """Test decimal rounding"""
        assert safe_percentage(1, 3, decimals=2) == 33.33
        assert safe_percentage(2, 3, decimals=1) == 66.7

    def test_percentage_division_by_zero(self):
        """Test percentage with zero denominator"""
        assert safe_percentage(10, 0) is None

    def test_percentage_greater_than_100(self):
        """Test percentage over 100%"""
        assert safe_percentage(150, 100) == 150.0


class TestSafeMultiply:
    """Test safe multiplication with overflow protection"""

    def test_normal_multiplication(self):
        """Test normal multiplication"""
        assert safe_multiply(2, 3, 4) == 24.0
        assert safe_multiply(5, 2) == 10.0

    def test_single_value(self):
        """Test multiplication with single value"""
        assert safe_multiply(5) == 5.0

    def test_overflow_protection(self):
        """Test overflow protection"""
        result = safe_multiply(1e10, 1e10, max_result=1e15)
        assert result is None

    def test_large_numbers_allowed(self):
        """Test large numbers within limit"""
        result = safe_multiply(1e5, 1e5, max_result=1e15)
        assert result == 1e10

    def test_negative_multiplication(self):
        """Test multiplication with negative numbers"""
        assert safe_multiply(-2, 3) == -6.0
        assert safe_multiply(-2, -3) == 6.0


class TestSafeAdd:
    """Test safe addition"""

    def test_normal_addition(self):
        """Test normal addition"""
        assert safe_add(1, 2, 3) == 6.0
        assert safe_add(10, 20) == 30.0

    def test_single_value(self):
        """Test addition with single value"""
        assert safe_add(5) == 5.0

    def test_negative_addition(self):
        """Test addition with negative numbers"""
        assert safe_add(-5, 10) == 5.0
        assert safe_add(-5, -10) == -15.0


class TestSafeSubtract:
    """Test safe subtraction"""

    def test_normal_subtraction(self):
        """Test normal subtraction"""
        assert safe_subtract(10, 3) == 7.0
        assert safe_subtract(100, 50) == 50.0

    def test_negative_result(self):
        """Test subtraction resulting in negative"""
        assert safe_subtract(5, 10) == -5.0

    def test_negative_numbers(self):
        """Test subtraction with negative numbers"""
        assert safe_subtract(-5, 10) == -15.0
        assert safe_subtract(-5, -10) == 5.0


class TestSafeAverage:
    """Test safe average calculation"""

    def test_normal_average(self):
        """Test normal average"""
        assert safe_average(10, 20, 30) == 20.0
        assert safe_average(5, 15) == 10.0

    def test_single_value(self):
        """Test average of single value"""
        assert safe_average(42) == 42.0

    def test_skip_none_values(self):
        """Test skipping None values"""
        assert safe_average(10, None, 20, skip_none=True) == 15.0

    def test_all_none_values(self):
        """Test all None values"""
        assert safe_average(None, None, skip_none=True) is None

    def test_empty_values(self):
        """Test empty values"""
        assert safe_average() is None


class TestSafeRatio:
    """Test safe ratio calculation"""

    def test_ratio_as_decimal(self):
        """Test ratio as decimal"""
        assert safe_ratio(1, 2, format_as="decimal") == 0.5
        assert safe_ratio(3, 4, format_as="decimal") == 0.75

    def test_ratio_as_percentage(self):
        """Test ratio as percentage"""
        assert safe_ratio(1, 2, format_as="percentage") == 50.0
        assert safe_ratio(3, 4, format_as="percentage") == 75.0

    def test_ratio_as_ratio_string(self):
        """Test ratio as ratio string"""
        assert safe_ratio(1, 2, format_as="ratio") == "1:2"
        assert safe_ratio(3, 4, format_as="ratio") == "3:4"

    def test_ratio_division_by_zero(self):
        """Test ratio with zero denominator"""
        assert safe_ratio(10, 0, format_as="decimal") is None
        assert safe_ratio(10, 0, format_as="ratio") == "10:0"


class TestFinancialCalculations:
    """Test financial calculation helpers"""

    def test_profit_margin_positive(self):
        """Test profit margin calculation - positive"""
        # Profit margin = (Revenue - Cost) / Revenue * 100
        margin = calculate_profit_margin(1000, 700)
        assert margin == 30.0  # (1000 - 700) / 1000 * 100 = 30%

    def test_profit_margin_zero(self):
        """Test profit margin with zero profit"""
        margin = calculate_profit_margin(1000, 1000)
        assert margin == 0.0

    def test_profit_margin_negative(self):
        """Test profit margin with loss"""
        margin = calculate_profit_margin(1000, 1200)
        assert margin == -20.0  # Loss of 20%

    def test_profit_margin_zero_revenue(self):
        """Test profit margin with zero revenue"""
        margin = calculate_profit_margin(0, 100)
        assert margin is None

    def test_roi_positive(self):
        """Test ROI calculation - positive"""
        # ROI = (Gain - Cost) / Cost * 100
        roi = calculate_roi(1200, 1000)
        assert roi == 20.0  # (1200 - 1000) / 1000 * 100 = 20%

    def test_roi_zero(self):
        """Test ROI with breakeven"""
        roi = calculate_roi(1000, 1000)
        assert roi == 0.0

    def test_roi_negative(self):
        """Test ROI with loss"""
        roi = calculate_roi(800, 1000)
        assert roi == -20.0

    def test_roi_zero_cost(self):
        """Test ROI with zero cost"""
        roi = calculate_roi(1000, 0)
        assert roi is None

    def test_growth_rate_positive(self):
        """Test growth rate calculation - positive"""
        # Growth = (Current - Previous) / Previous * 100
        growth = calculate_growth_rate(120, 100)
        assert growth == 20.0  # 20% growth

    def test_growth_rate_negative(self):
        """Test growth rate - negative (decline)"""
        growth = calculate_growth_rate(80, 100)
        assert growth == -20.0  # 20% decline

    def test_growth_rate_zero(self):
        """Test growth rate with no change"""
        growth = calculate_growth_rate(100, 100)
        assert growth == 0.0

    def test_growth_rate_zero_previous(self):
        """Test growth rate with zero previous value"""
        growth = calculate_growth_rate(100, 0)
        assert growth is None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
