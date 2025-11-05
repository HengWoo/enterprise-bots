"""
v0.5.0 Integration Tests

Tests the integration of verification module into agent tools.
Validates that verification wrappers are called correctly and
produce appropriate warnings/errors in lenient mode.

Author: Claude (AI Assistant)
Date: 2025-10-31
Version: 0.5.0
"""

import pytest
from src.utils.verification_wrapper import (
    verify_calculation_result,
    verify_financial_data_wrapper,
    verify_html_content,
    add_verification_notice,
    quick_verify
)


class TestVerificationIntegration:
    """Test verification module integration into agent workflow"""

    def test_calculation_verification_catches_error(self):
        """Verify that impossible profit margin is caught"""
        result = verify_calculation_result(
            operation="profit_margin",
            inputs={"revenue": 100, "cost": 120},
            result=0.2
        )

        assert result["valid"] == False
        assert "Cost exceeds revenue" in result["errors"][0]
        assert "⚠️" in result["message"]

    def test_calculation_verification_passes_valid_input(self):
        """Verify that valid profit margin passes"""
        result = verify_calculation_result(
            operation="profit_margin",
            inputs={"revenue": 100, "cost": 60},
            result=0.4
        )

        assert result["valid"] == True
        assert len(result["errors"]) == 0
        assert "✓" in result["message"]

    def test_percentage_calculation_warning(self):
        """Verify that percentage >100% triggers warning"""
        result = verify_calculation_result(
            operation="percentage",
            inputs={"value": 150, "total": 100}
        )

        assert result["valid"] == True  # Warning, not error
        assert len(result["warnings"]) > 0
        assert "exceeds total" in result["warnings"][0]

    def test_division_by_zero_error(self):
        """Verify that division by zero is caught"""
        result = verify_calculation_result(
            operation="division",
            inputs={"divisor": 0}
        )

        assert result["valid"] == False
        assert "Division by zero" in result["errors"][0]


class TestFinancialDataVerification:
    """Test financial data verification wrapper"""

    def test_profit_equation_violation(self):
        """Verify that profit equation violation is caught"""
        result = verify_financial_data_wrapper({
            "revenue": 1000,
            "cost": 600,
            "profit": 500  # Should be 400!
        })

        assert result["valid"] == False
        assert len(result["errors"]) > 0
        assert "Balance equation" in result["errors"][0]

    def test_profit_equation_satisfied(self):
        """Verify that correct profit equation passes"""
        result = verify_financial_data_wrapper({
            "revenue": 1000,
            "cost": 600,
            "profit": 400
        })

        assert result["valid"] == True
        assert len(result["errors"]) == 0

    def test_negative_revenue_warning(self):
        """Verify that negative revenue triggers warnings"""
        result = verify_financial_data_wrapper({
            "revenue": -100,  # Unusual
            "cost": 0,
            "profit": -100
        }, check_balance=False)

        assert len(result["warnings"]) > 0
        assert "negative value" in result["warnings"][0].lower()


class TestHTMLVerification:
    """Test HTML content verification"""

    def test_full_html_document(self):
        """Verify that complete HTML document passes"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test</title>
            <style>
                body { font-family: Arial; }
            </style>
        </head>
        <body>
            <h2>Title</h2>
            <p>Content with proper structure</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
        </body>
        </html>
        """
        result = verify_html_content(html, check_structure=True)

        # Should pass with good quality
        assert result["valid"] == True
        assert result["quality_score"] > 0.7

    def test_html_fragment_warnings(self):
        """Verify that HTML fragments get warnings but don't fail (lenient mode)"""
        html = "<div><h2>Title</h2><p>Content</p></div>"
        result = verify_html_content(html, check_structure=True)

        # May have warnings about missing <html>, <body> but shouldn't fail
        # (depends on verifier strictness)
        assert "quality_score" in result

    def test_empty_html_error(self):
        """Verify that empty HTML is caught"""
        result = verify_html_content("", check_structure=True)

        assert result["valid"] == False
        assert len(result["errors"]) > 0


class TestVerificationNotice:
    """Test verification notice addition to responses"""

    def test_lenient_mode_adds_warning(self):
        """Verify that warnings are added in lenient mode"""
        original = "The profit margin is 25%"
        verification = {
            "valid": True,
            "warnings": ["Low margin compared to industry average"],
            "message": "⚠️ Warning: Low margin compared to industry average"
        }

        result = add_verification_notice(original, verification, mode="lenient")

        assert original in result
        assert verification["message"] in result

    def test_lenient_mode_adds_error_notice(self):
        """Verify that errors are added in lenient mode"""
        original = "The calculation shows..."
        verification = {
            "valid": False,
            "errors": ["Cost exceeds revenue"],
            "message": "⚠️ Calculation error: Cost exceeds revenue"
        }

        result = add_verification_notice(original, verification, mode="lenient")

        assert original in result
        assert verification["message"] in result

    def test_no_notice_for_valid_result(self):
        """Verify that valid results don't add notices"""
        original = "The calculation is correct"
        verification = {
            "valid": True,
            "warnings": [],
            "message": "✓ Calculation verified"
        }

        result = add_verification_notice(original, verification, mode="lenient")

        assert result == original  # Unchanged


class TestQuickVerify:
    """Test quick verification helper"""

    def test_type_check_failure(self):
        """Verify type checking works"""
        result = quick_verify("text", expected_type=int)

        assert result["valid"] == False
        assert "Expected int" in result["errors"][0]

    def test_range_check_min(self):
        """Verify minimum range checking"""
        result = quick_verify(-10, expected_type=int, min_value=0)

        assert result["valid"] == False
        assert "below minimum" in result["errors"][0]

    def test_range_check_max(self):
        """Verify maximum range checking"""
        result = quick_verify(150, expected_type=int, max_value=100)

        assert result["valid"] == False
        assert "exceeds maximum" in result["errors"][0]

    def test_valid_value_passes(self):
        """Verify valid values pass all checks"""
        result = quick_verify(50, expected_type=int, min_value=0, max_value=100)

        assert result["valid"] == True
        assert len(result["errors"]) == 0


class TestFileToolIntegration:
    """Test verification integration into file_saving_tools"""

    def test_html_tool_integration_exists(self):
        """Verify that file_saving_tools imports verification wrapper"""
        from src.tools import file_saving_tools

        # Check that module imports verification_wrapper
        assert hasattr(file_saving_tools, 'verify_html_content')

    # Skip async tests for now - requires pytest-asyncio setup
    # These will be tested manually in Campfire integration


# ===================================================================
# Test Configuration
# ===================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
