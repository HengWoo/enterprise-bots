"""
Tests for verification verifiers

Coverage: Business rule verification, data quality checks
"""

import pytest
from src.verification.verifiers import (
    VerificationResult,
    verify_financial_balance,
    verify_percentage_sum,
    verify_date_range,
    verify_positive_number,
    verify_data_quality,
    verify_menu_profitability,
    verify_operations_metrics,
    verify_html_structure,
)


class TestVerificationResult:
    """Test VerificationResult dataclass"""

    def test_default_result(self):
        """Test default verification result"""
        result = VerificationResult(passed=True)
        assert result.passed is True
        assert len(result.warnings) == 0
        assert len(result.errors) == 0
        assert len(result.suggestions) == 0

    def test_add_warning(self):
        """Test adding warning"""
        result = VerificationResult(passed=True)
        result.add_warning("Test warning")
        assert len(result.warnings) == 1
        assert result.passed is True  # Warnings don't change pass status

    def test_add_error(self):
        """Test adding error"""
        result = VerificationResult(passed=True)
        result.add_error("Test error")
        assert len(result.errors) == 1
        assert result.passed is False  # Errors change pass status

    def test_has_issues(self):
        """Test has_issues check"""
        result = VerificationResult(passed=True)
        assert result.has_issues() is False

        result.add_warning("Warning")
        assert result.has_issues() is True

    def test_get_summary(self):
        """Test summary generation"""
        result = VerificationResult(passed=True)
        assert "All checks passed" in result.get_summary()

        result.add_error("Error")
        summary = result.get_summary()
        assert "❌ Errors: 1" in summary


class TestFinancialBalance:
    """Test financial balance verification"""

    def test_balanced_equation(self):
        """Test balanced financial equation"""
        result = verify_financial_balance(1000, 700, 300)
        assert result.passed is True
        assert len(result.errors) == 0

    def test_unbalanced_equation(self):
        """Test unbalanced equation"""
        result = verify_financial_balance(1000, 700, 400)
        assert result.passed is False
        assert len(result.errors) > 0

    def test_cost_exceeds_revenue(self):
        """Test cost exceeding revenue"""
        result = verify_financial_balance(1000, 1200, -200)
        assert len(result.warnings) > 0
        assert "exceeds revenue" in result.warnings[0]

    def test_negative_profit(self):
        """Test negative profit warning"""
        result = verify_financial_balance(1000, 1200, -200)
        assert "Negative profit" in str(result.warnings)


class TestPercentageSum:
    """Test percentage sum verification"""

    def test_valid_sum(self):
        """Test valid percentage sum"""
        result = verify_percentage_sum([25.0, 25.0, 25.0, 25.0])
        assert result.passed is True

    def test_invalid_sum(self):
        """Test invalid percentage sum"""
        result = verify_percentage_sum([30.0, 30.0, 30.0])
        assert result.passed is False

    def test_negative_percentages(self):
        """Test negative percentages"""
        result = verify_percentage_sum([50.0, 50.0, -10.0, 10.0])
        assert len(result.warnings) > 0


class TestDateRangeVerification:
    """Test date range verification"""

    def test_valid_date_range(self):
        """Test valid date range"""
        result = verify_date_range("2025-01-01", "2025-12-31")
        assert result.passed is True

    def test_invalid_start_after_end(self):
        """Test start after end"""
        result = verify_date_range("2025-12-31", "2025-01-01")
        assert result.passed is False

    def test_max_days_exceeded(self):
        """Test maximum days exceeded"""
        result = verify_date_range("2025-01-01", "2025-12-31", max_days=30)
        assert len(result.warnings) > 0


class TestDataQuality:
    """Test data quality verification"""

    def test_valid_data(self):
        """Test valid data"""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]
        result = verify_data_quality(data, required_fields=["name", "age"])
        assert result.passed is True

    def test_missing_fields(self):
        """Test missing required fields"""
        data = [
            {"name": "Alice"},
            {"name": "Bob", "age": 25},
        ]
        result = verify_data_quality(data, required_fields=["name", "age"])
        assert len(result.warnings) > 0 or len(result.errors) > 0

    def test_insufficient_records(self):
        """Test insufficient records"""
        data = []
        result = verify_data_quality(data, required_fields=["name"], min_records=1)
        assert result.passed is False


class TestMenuProfitability:
    """Test menu profitability verification"""

    def test_valid_profitable_dish(self):
        """Test valid profitable dish"""
        dish = {
            "revenue": 1000,
            "cost": 700,
            "margin": 30.0,
            "sales_count": 100,
        }
        result = verify_menu_profitability(dish)
        assert result.passed is True

    def test_low_margin(self):
        """Test low profit margin"""
        dish = {
            "revenue": 1000,
            "cost": 950,
            "margin": 5.0,
            "sales_count": 100,
        }
        result = verify_menu_profitability(dish, min_profit_margin=10.0)
        assert len(result.warnings) > 0

    def test_negative_margin(self):
        """Test negative profit margin"""
        dish = {
            "revenue": 1000,
            "cost": 1200,
            "margin": -20.0,
            "sales_count": 100,
        }
        result = verify_menu_profitability(dish)
        assert result.passed is False


class TestOperationsMetrics:
    """Test operations metrics verification"""

    def test_valid_metrics(self):
        """Test valid operations metrics"""
        metrics = {
            "completion_rate": 90.0,
            "cycle_time_days": 5,
            "on_time_rate": 95.0,
        }
        result = verify_operations_metrics(metrics)
        assert result.passed is True

    def test_low_completion_rate(self):
        """Test low completion rate"""
        metrics = {"completion_rate": 60.0}
        result = verify_operations_metrics(metrics)
        assert len(result.warnings) > 0

    def test_high_cycle_time(self):
        """Test high cycle time"""
        metrics = {"cycle_time_days": 45}
        result = verify_operations_metrics(metrics)
        assert len(result.warnings) > 0


class TestHTMLStructure:
    """Test HTML structure verification"""

    def test_valid_html(self):
        """Test valid HTML structure"""
        html = "<html><head></head><body><div>Content</div></body></html>"
        result = verify_html_structure(html)
        assert result.passed is True

    def test_missing_html_tag(self):
        """Test missing HTML tag"""
        html = "<body><div>Content</div></body>"
        result = verify_html_structure(html)
        assert len(result.warnings) > 0

    def test_empty_html(self):
        """Test empty HTML"""
        result = verify_html_structure("")
        assert result.passed is False


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
