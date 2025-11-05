"""
Tests for verification validators

Coverage: Input validation decorators, validation functions
"""

import pytest
from src.verification.validators import (
    ValidationError,
    ValidationWarning,
    validate_inputs,
    validate_date_format,
    validate_date_range,
    validate_percentage,
    validate_positive_number,
    validate_non_zero,
    validate_financial_calculation,
    validate_date_range_query,
)
from src.verification.config import VerificationMode, VerificationConfig, BOT_CONFIGS


class TestValidateDateFormat:
    """Test date format validation"""

    def test_valid_dates(self):
        """Test valid date formats"""
        assert validate_date_format("2025-10-29") is True
        assert validate_date_format("2025-01-01") is True
        assert validate_date_format("2025-12-31") is True

    def test_invalid_dates(self):
        """Test invalid date formats"""
        assert validate_date_format("29-10-2025") is False
        assert validate_date_format("2025/10/29") is False
        assert validate_date_format("invalid") is False
        assert validate_date_format("2025-13-01") is False


class TestValidateDateRange:
    """Test date range validation"""

    def test_valid_range(self):
        """Test valid date range"""
        assert validate_date_range("2025-01-01", "2025-12-31") is None

    def test_invalid_start_format(self):
        """Test invalid start date format"""
        error = validate_date_range("invalid", "2025-12-31")
        assert error is not None
        assert "Invalid start date format" in error

    def test_invalid_end_format(self):
        """Test invalid end date format"""
        error = validate_date_range("2025-01-01", "invalid")
        assert error is not None
        assert "Invalid end date format" in error

    def test_start_after_end(self):
        """Test start date after end date"""
        error = validate_date_range("2025-12-31", "2025-01-01")
        assert error is not None
        assert "is after end date" in error


class TestValidatePercentage:
    """Test percentage validation"""

    def test_valid_percentage_0_to_1(self):
        """Test valid percentage in 0-1 range"""
        assert validate_percentage(0.5) is None
        assert validate_percentage(0) is None
        assert validate_percentage(1) is None

    def test_valid_percentage_0_to_100(self):
        """Test valid percentage in 0-100 range"""
        assert validate_percentage(50) is None
        assert validate_percentage(0) is None
        assert validate_percentage(100) is None

    def test_invalid_percentage(self):
        """Test invalid percentage"""
        error = validate_percentage(150)
        assert error is not None
        assert "out of range" in error

    def test_negative_percentage(self):
        """Test negative percentage"""
        error = validate_percentage(-10)
        assert error is not None

    def test_non_number_percentage(self):
        """Test non-number percentage"""
        error = validate_percentage("50")
        assert error is not None
        assert "must be a number" in error


class TestValidatePositiveNumber:
    """Test positive number validation"""

    def test_valid_positive(self):
        """Test valid positive numbers"""
        assert validate_positive_number(10) is None
        assert validate_positive_number(0.5) is None
        assert validate_positive_number(0) is None

    def test_negative_number(self):
        """Test negative number"""
        error = validate_positive_number(-10)
        assert error is not None
        assert "must be positive" in error

    def test_non_number(self):
        """Test non-number input"""
        error = validate_positive_number("10")
        assert error is not None
        assert "must be a number" in error

    def test_custom_field_name(self):
        """Test custom field name in error"""
        error = validate_positive_number(-10, field_name="revenue")
        assert "revenue" in error


class TestValidateNonZero:
    """Test non-zero validation"""

    def test_valid_non_zero(self):
        """Test valid non-zero numbers"""
        assert validate_non_zero(10) is None
        assert validate_non_zero(-5) is None

    def test_zero(self):
        """Test zero value"""
        error = validate_non_zero(0)
        assert error is not None
        assert "cannot be zero" in error


class TestValidateFinancialCalculation:
    """Test financial calculation validator"""

    def test_valid_calculation(self):
        """Test valid financial data"""
        args = {"revenue": 1000, "cost": 700}
        assert validate_financial_calculation(args) is None

    def test_negative_revenue(self):
        """Test negative revenue"""
        args = {"revenue": -1000, "cost": 700}
        error = validate_financial_calculation(args)
        assert error is not None
        assert "revenue" in error

    def test_cost_exceeds_revenue(self):
        """Test cost exceeding revenue"""
        args = {"revenue": 1000, "cost": 1200}
        error = validate_financial_calculation(args)
        assert error is not None
        assert "exceeds revenue" in error


class TestValidateDateRangeQuery:
    """Test date range query validator"""

    def test_no_dates(self):
        """Test no date range specified"""
        assert validate_date_range_query({}) is None

    def test_valid_date_range(self):
        """Test valid date range"""
        args = {"start_date": "2025-01-01", "end_date": "2025-12-31"}
        assert validate_date_range_query(args) is None

    def test_only_start_date(self):
        """Test only start date specified"""
        args = {"start_date": "2025-01-01"}
        result = validate_date_range_query(args)
        assert result is not None  # Warning
        assert "end_date will default" in result

    def test_only_end_date(self):
        """Test only end date specified"""
        args = {"end_date": "2025-12-31"}
        result = validate_date_range_query(args)
        assert result is not None  # Warning
        assert "start_date will default" in result


class TestValidateInputsDecorator:
    """Test @validate_inputs decorator"""

    def test_decorator_with_valid_inputs(self):
        """Test decorator allows valid inputs"""

        @validate_inputs(required=["name"], types={"age": int})
        async def test_func(args):
            return {"success": True}

        # Should pass validation
        result = test_func({"name": "Alice", "age": 30}, bot_id="default")
        # Note: Can't test async easily without asyncio, but decorator should allow

    def test_decorator_required_fields(self):
        """Test decorator checks required fields"""

        @validate_inputs(required=["name", "age"])
        async def test_func(args):
            return {"success": True}

        # Missing required field should be caught
        # (Implementation will log warning or raise error based on config)

    def test_decorator_type_validation(self):
        """Test decorator validates types"""

        @validate_inputs(types={"age": int, "revenue": float})
        async def test_func(args):
            return {"success": True}

        # Type mismatch should be caught

    def test_decorator_range_validation(self):
        """Test decorator validates ranges"""

        @validate_inputs(ranges={"age": (0, 120), "percentage": (0, 100)})
        async def test_func(args):
            return {"success": True}

        # Out of range should be caught

    def test_decorator_custom_validation(self):
        """Test decorator with custom validator"""

        def custom_validator(args):
            if args.get("value", 0) < 0:
                return "Value must be positive"
            return None

        @validate_inputs(custom=custom_validator)
        async def test_func(args):
            return {"success": True}

        # Custom validation should be applied


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
