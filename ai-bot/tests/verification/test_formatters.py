"""
Tests for verification formatters

Coverage: Output formatting functions, currency, percentage, date formatting
"""

import pytest
from src.verification.formatters import (
    FormatError,
    format_currency,
    format_percentage,
    format_number,
    format_date,
    format_change,
    format_duration,
    format_ratio,
    format_html_metric_card,
)


class TestFormatCurrency:
    """Test currency formatting"""

    def test_basic_currency(self):
        """Test basic currency formatting"""
        assert format_currency(1234.56) == "¥1,234.56"

    def test_currency_with_custom_symbol(self):
        """Test currency with custom symbol"""
        assert format_currency(1234.56, currency="$") == "$1,234.56"

    def test_currency_no_decimals(self):
        """Test currency with no decimals"""
        assert format_currency(1234, decimals=0) == "¥1,234"

    def test_negative_currency(self):
        """Test negative amount"""
        assert format_currency(-1234.56) == "-¥1,234.56"

    def test_zero_currency(self):
        """Test zero amount"""
        assert format_currency(0) == "¥0.00"


class TestFormatPercentage:
    """Test percentage formatting"""

    def test_percentage_from_decimal(self):
        """Test percentage from 0-1 range"""
        assert format_percentage(0.234, decimals=1) == "23.4%"

    def test_percentage_from_integer(self):
        """Test percentage from 0-100 range"""
        assert format_percentage(23.4, decimals=1) == "23.4%"

    def test_percentage_with_sign(self):
        """Test percentage with + sign"""
        assert format_percentage(0.1, include_sign=True) == "+10.0%"

    def test_negative_percentage(self):
        """Test negative percentage"""
        assert format_percentage(-0.1) == "-10.0%"


class TestFormatNumber:
    """Test number formatting"""

    def test_integer_number(self):
        """Test integer formatting"""
        assert format_number(1234567) == "1,234,567"

    def test_float_number(self):
        """Test float formatting"""
        assert format_number(1234.5678, decimals=2) == "1,234.57"

    def test_custom_separator(self):
        """Test custom thousands separator"""
        result = format_number(1234567, thousands_separator=" ")
        assert "1 234 567" in result


class TestFormatDate:
    """Test date formatting"""

    def test_chinese_format(self):
        """Test Chinese date format"""
        result = format_date("2025-10-29", output_format="中文")
        assert "2025年10月29日" == result

    def test_english_format(self):
        """Test English date format"""
        result = format_date("2025-10-29", output_format="English")
        assert "October 29, 2025" == result


class TestFormatChange:
    """Test change formatting"""

    def test_positive_change(self):
        """Test positive change"""
        result = format_change(120, 100)
        assert "↑" in result
        assert "+20.0%" in result

    def test_negative_change(self):
        """Test negative change"""
        result = format_change(80, 100)
        assert "↓" in result
        assert "-20.0%" in result

    def test_no_change(self):
        """Test no change"""
        result = format_change(100, 100)
        assert "→" in result
        assert "0.0%" in result

    def test_change_absolute(self):
        """Test absolute change format"""
        result = format_change(120, 100, format_as="absolute")
        assert "+20" in result

    def test_change_both(self):
        """Test both absolute and percentage"""
        result = format_change(120, 100, format_as="both")
        assert "+20" in result
        assert "+20.0%" in result


class TestFormatDuration:
    """Test duration formatting"""

    def test_duration_chinese(self):
        """Test Chinese duration"""
        assert format_duration(3.5, chinese=True) == "3.5天"

    def test_duration_english(self):
        """Test English duration"""
        result = format_duration(3.5, chinese=False)
        assert "3.5 days" in result

    def test_duration_with_hours(self):
        """Test duration with hours"""
        result = format_duration(3.5, include_hours=True, chinese=True)
        assert "3天12小时" == result


class TestFormatRatio:
    """Test ratio formatting"""

    def test_ratio_decimal(self):
        """Test ratio as decimal"""
        assert format_ratio(1, 2, format_as="decimal") == "0.50"

    def test_ratio_percentage(self):
        """Test ratio as percentage"""
        assert format_ratio(1, 2, format_as="percentage") == "50.0%"

    def test_ratio_string(self):
        """Test ratio as string"""
        assert format_ratio(1, 2, format_as="ratio") == "1:2"

    def test_ratio_fraction(self):
        """Test ratio as fraction"""
        assert format_ratio(1, 2, format_as="fraction") == "1/2"


class TestFormatHTMLMetricCard:
    """Test HTML metric card formatting"""

    def test_basic_metric_card(self):
        """Test basic metric card"""
        html = format_html_metric_card("Revenue", "¥1,234")
        assert "Revenue" in html
        assert "¥1,234" in html
        assert "<div" in html

    def test_metric_card_with_change(self):
        """Test metric card with change indicator"""
        html = format_html_metric_card("Revenue", "¥1,234", change="↑ +10%")
        assert "Revenue" in html
        assert "¥1,234" in html
        assert "↑ +10%" in html

    def test_metric_card_custom_color(self):
        """Test metric card with custom color"""
        html = format_html_metric_card("Revenue", "¥1,234", color="#ff0000")
        assert "#ff0000" in html


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
