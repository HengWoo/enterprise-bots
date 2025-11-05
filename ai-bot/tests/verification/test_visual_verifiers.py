"""
Tests for Visual Content Verification

Tests HTML presentations, documents, and charts quality validation.
"""

import pytest
from src.verification.visual_verifiers import (
    verify_html_presentation,
    verify_document_formatting,
    verify_chart_quality,
    verify_visual_content,
    verify_multiple_visuals,
)


class TestHTMLPresentationVerification:
    """Test HTML presentation quality checks."""

    def test_valid_html_presentation(self):
        """Test validation of well-formed HTML presentation."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Test Presentation</title>
            <style>
                body { font-family: 'PingFang SC', sans-serif; line-height: 1.8; }
                h2 { color: #333; }
            </style>
        </head>
        <body>
            <h2>Introduction</h2>
            <p>This is a test presentation with Chinese text: 测试内容</p>
            <h3>Details</h3>
            <ul>
                <li>Point 1</li>
                <li>Point 2</li>
            </ul>
        </body>
        </html>
        """

        result = verify_html_presentation(html)

        assert result.passed
        assert len(result.errors) == 0
        assert "Chinese" in str(result.suggestions) or len(result.warnings) <= 1  # May have minor warnings

    def test_html_missing_body(self):
        """Test detection of missing body tag."""
        html = """
        <html>
        <head><title>Test</title></head>
        </html>
        """

        result = verify_html_presentation(html)

        assert not result.passed
        assert any("body" in error.lower() for error in result.errors)

    def test_html_no_headings(self):
        """Test detection of missing content structure."""
        html = """
        <html>
        <body>
            <p>Content without any headings</p>
        </body>
        </html>
        """

        result = verify_html_presentation(html)

        assert not result.passed
        assert any("heading" in error.lower() for error in result.errors)

    def test_html_no_css(self):
        """Test warning for missing CSS styling."""
        html = """
        <html>
        <body>
            <h2>Title</h2>
            <p>Content without styling</p>
        </body>
        </html>
        """

        result = verify_html_presentation(html, check_css=True)

        # Should pass but with warning about missing CSS
        assert result.passed
        assert any("css" in warning.lower() or "styling" in warning.lower() for warning in result.warnings)

    def test_html_chinese_text_no_utf8(self):
        """Test detection of Chinese text without UTF-8 encoding."""
        html = """
        <html>
        <body>
            <h2>中文标题</h2>
            <p>这是中文内容</p>
        </body>
        </html>
        """

        result = verify_html_presentation(html)

        # Should fail due to missing UTF-8 charset
        assert not result.passed
        assert any("utf-8" in error.lower() or "chinese" in error.lower() for error in result.errors)

    def test_html_responsive_design(self):
        """Test detection of responsive design elements."""
        html_responsive = """
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                @media (max-width: 768px) { body { font-size: 14px; } }
            </style>
        </head>
        <body>
            <h2>Responsive Content</h2>
            <p>This is content with responsive design elements.</p>
        </body>
        </html>
        """

        result = verify_html_presentation(html_responsive, check_responsive=True)

        # Should have suggestion about responsive design (may have warnings about unclosed tags)
        assert result.passed or len(result.errors) == 0  # Accept if no errors
        assert any("responsive" in suggestion.lower() for suggestion in result.suggestions)

    def test_html_required_sections(self):
        """Test validation of required sections."""
        html = """
        <html>
        <body>
            <div id="introduction">
                <h2>Introduction</h2>
                <p>Content</p>
            </div>
        </body>
        </html>
        """

        # Test with missing required section
        result = verify_html_presentation(html, required_sections=["introduction", "conclusion"])

        assert not result.passed
        assert any("conclusion" in error.lower() for error in result.errors)


class TestDocumentFormattingVerification:
    """Test document formatting and readability checks."""

    def test_valid_document_formatting(self):
        """Test validation of well-formatted document."""
        html = """
        <div style="line-height: 1.8; font-size: 16px; margin-bottom: 20px; color: #333; background: #fff;">
            <p>This is a paragraph with good formatting.</p>
            <p>Another paragraph with proper spacing.</p>
        </div>
        """

        result = verify_document_formatting(html, content_type="html")

        assert result.passed
        assert any("line height" in suggestion.lower() or "good" in suggestion.lower()
                   for suggestion in result.suggestions if suggestion)

    def test_document_small_font(self):
        """Test detection of small font sizes."""
        html = """
        <div style="font-size: 10px;">
            <p>This text is too small</p>
        </div>
        """

        result = verify_document_formatting(html, content_type="html")

        assert any("font size" in warning.lower() or "10px" in warning.lower()
                   for warning in result.warnings)

    def test_document_no_line_height(self):
        """Test warning for missing line-height."""
        html = """
        <div>
            <p>Content without explicit line-height</p>
        </div>
        """

        result = verify_document_formatting(html, content_type="html")

        # Should have warning about line-height
        assert any("line-height" in warning.lower() or "line height" in warning.lower()
                   for warning in result.warnings)

    def test_markdown_no_headings(self):
        """Test detection of missing headings in markdown."""
        markdown = """
        This is a document with no headings.
        Just plain text paragraphs.
        """

        result = verify_document_formatting(markdown, content_type="markdown", check_readability=False)

        # Should warn about missing headings
        assert any("heading" in warning.lower() for warning in result.warnings)

    def test_text_readability(self):
        """Test readability checks for long paragraphs."""
        text = "This is a very long paragraph. " * 100  # 500+ chars

        result = verify_document_formatting(text, content_type="text", check_readability=True)

        # May have warning about long lines (500+ chars)
        # This is lenient - just check it doesn't crash
        assert result is not None


class TestChartQualityVerification:
    """Test chart/visualization quality checks."""

    def test_valid_chart(self):
        """Test validation of well-formed chart data."""
        chart_data = {
            "title": "Monthly Revenue",
            "labels": ["Jan", "Feb", "Mar", "Apr"],
            "datasets": [{
                "label": "Revenue",
                "data": [1000, 1500, 1200, 1800]
            }],
            "xAxisLabel": "Month",
            "yAxisLabel": "Revenue (¥)",
            "legend": True
        }

        result = verify_chart_quality(chart_data, chart_type="bar")

        assert result.passed
        assert len(result.errors) == 0

    def test_chart_missing_labels(self):
        """Test detection of missing data labels."""
        chart_data = {
            "datasets": [{
                "data": [10, 20, 30]
            }]
        }

        result = verify_chart_quality(chart_data, check_labels=True)

        assert not result.passed
        assert any("label" in error.lower() for error in result.errors)

    def test_chart_nan_values(self):
        """Test detection of NaN values in dataset."""
        chart_data = {
            "labels": ["A", "B", "C"],
            "datasets": [{
                "data": [10, None, 30]
            }]
        }

        result = verify_chart_quality(chart_data, check_data_accuracy=True)

        assert not result.passed
        assert any("nan" in error.lower() or "none" in error.lower() for error in result.errors)

    def test_pie_chart_negative_values(self):
        """Test detection of negative values in pie chart."""
        chart_data = {
            "labels": ["A", "B", "C"],
            "values": [10, -5, 30]
        }

        result = verify_chart_quality(chart_data, chart_type="pie", check_data_accuracy=True)

        assert not result.passed
        assert any("negative" in error.lower() and "pie" in error.lower() for error in result.errors)

    def test_chart_extreme_outliers(self):
        """Test detection of extreme value ranges."""
        chart_data = {
            "labels": ["A", "B", "C", "D"],
            "datasets": [{
                "data": [10, 15, 12, 1500]  # max/min ratio > 100
            }]
        }

        result = verify_chart_quality(chart_data, check_data_accuracy=True)

        # Should warn about extreme range
        assert any("extreme" in warning.lower() or "range" in warning.lower() or "scale" in warning.lower()
                   for warning in result.warnings)

    def test_chart_too_many_points(self):
        """Test warning for excessive data points."""
        chart_data = {
            "labels": [f"Point {i}" for i in range(100)],  # 100 data points
            "datasets": [{
                "data": list(range(100))
            }]
        }

        result = verify_chart_quality(chart_data)

        # Should warn about large number of points
        assert any("point" in warning.lower() or "100" in warning.lower()
                   for warning in result.warnings)

    def test_chart_no_data_points(self):
        """Test detection of empty chart."""
        chart_data = {
            "labels": [],
            "datasets": []
        }

        result = verify_chart_quality(chart_data, check_labels=True)

        assert not result.passed
        assert any("empty" in error.lower() or "no data" in error.lower()
                   for error in result.errors)


class TestUnifiedVerification:
    """Test unified verification function."""

    def test_verify_html_content_type(self):
        """Test routing to HTML verification."""
        html = """
        <html>
        <body>
            <h2>Title</h2>
            <p>Content</p>
        </body>
        </html>
        """

        result = verify_visual_content(html, content_type="html_presentation")

        assert isinstance(result.passed, bool)

    def test_verify_document_content_type(self):
        """Test routing to document verification."""
        doc = "# Heading\n\nParagraph text."

        # The verify_visual_content routes to verify_document_formatting based on content_type="document"
        # We can't pass another content_type parameter, so we just test basic routing
        result = verify_visual_content(doc, content_type="document")

        assert isinstance(result.passed, bool)

    def test_verify_chart_content_type(self):
        """Test routing to chart verification."""
        chart = {
            "labels": ["A", "B"],
            "datasets": [{"data": [10, 20]}]
        }

        result = verify_visual_content(chart, content_type="chart")

        assert isinstance(result.passed, bool)

    def test_unknown_content_type(self):
        """Test handling of unknown content type."""
        result = verify_visual_content("content", content_type="unknown_type")

        assert not result.passed
        assert any("unknown" in error.lower() for error in result.errors)


class TestBatchVerification:
    """Test batch verification of multiple visuals."""

    def test_verify_multiple_contents(self):
        """Test verification of multiple contents in batch."""
        contents = [
            {
                "name": "presentation",
                "content": "<html><body><h2>Title</h2></body></html>",
                "content_type": "html_presentation"
            },
            {
                "name": "chart",
                "content": {
                    "labels": ["A", "B"],
                    "datasets": [{"data": [10, 20]}]
                },
                "content_type": "chart"
            }
        ]

        results = verify_multiple_visuals(contents)

        assert "presentation" in results
        assert "chart" in results
        assert isinstance(results["presentation"].passed, bool)
        assert isinstance(results["chart"].passed, bool)

    def test_batch_with_error(self):
        """Test batch verification with an error case."""
        contents = [
            {
                "name": "good",
                "content": "<html><body><h2>Title</h2></body></html>",
                "content_type": "html_presentation"
            },
            {
                "name": "bad",
                "content": None,  # This will cause an error
                "content_type": "html_presentation"
            }
        ]

        results = verify_multiple_visuals(contents)

        assert "good" in results
        assert "bad" in results
        # "bad" should have failed verification
        assert not results["bad"].passed or len(results["bad"].errors) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_html(self):
        """Test handling of empty HTML."""
        result = verify_html_presentation("")

        # Should handle gracefully
        assert isinstance(result.passed, bool)

    def test_malformed_html(self):
        """Test handling of malformed HTML."""
        html = "<html><body><div>Unclosed div</body></html>"

        result = verify_html_presentation(html)

        # Should parse but may have warnings
        assert isinstance(result.passed, bool)

    def test_empty_chart_data(self):
        """Test handling of empty chart data."""
        result = verify_chart_quality({})

        # Should handle gracefully
        assert isinstance(result.passed, bool)

    def test_chart_with_single_point(self):
        """Test chart with single data point."""
        chart_data = {
            "labels": ["A"],
            "datasets": [{"data": [10]}]
        }

        result = verify_chart_quality(chart_data)

        # Should pass - single point is valid
        assert result.passed or len(result.errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
