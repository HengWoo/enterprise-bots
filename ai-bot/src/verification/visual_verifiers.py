"""
Visual Content Verification

Verifies HTML presentations, documents, and charts for quality and correctness.
Used to validate generated visual content before displaying to users.
"""

import re
import logging
from typing import Dict, List, Optional, Any
from html.parser import HTMLParser

from .verifiers import VerificationResult

logger = logging.getLogger(__name__)


# ============================================================================
# HTML Structure Parser
# ============================================================================

class HTMLStructureParser(HTMLParser):
    """Parse HTML to extract structure information."""

    def __init__(self):
        super().__init__()
        self.tags = []
        self.tag_counts = {}
        self.unclosed_tags = []
        self.has_doctype = False
        self.has_title = False
        self.has_body = False
        self.current_tag_stack = []

    def handle_starttag(self, tag, attrs):
        """Handle opening tags."""
        self.tags.append(tag)
        self.tag_counts[tag] = self.tag_counts.get(tag, 0) + 1
        self.current_tag_stack.append(tag)

        # Track important tags
        if tag == 'html':
            pass  # Root tag
        elif tag == 'title':
            self.has_title = True
        elif tag == 'body':
            self.has_body = True

    def handle_endtag(self, tag):
        """Handle closing tags."""
        if self.current_tag_stack and self.current_tag_stack[-1] == tag:
            self.current_tag_stack.pop()
        else:
            self.unclosed_tags.append(tag)

    def handle_decl(self, decl):
        """Handle DOCTYPE declaration."""
        if 'doctype' in decl.lower():
            self.has_doctype = True


# ============================================================================
# HTML Presentation Verification
# ============================================================================

def verify_html_presentation(
    html_content: str,
    required_sections: Optional[List[str]] = None,
    check_css: bool = True,
    check_responsive: bool = True
) -> VerificationResult:
    """
    Verify HTML presentation quality and structure.

    Checks:
    - Valid HTML structure (balanced tags, proper nesting)
    - Required sections present (title, headings, content)
    - CSS styling present
    - Responsive design elements
    - Content hierarchy (h2 > h3 structure)
    - Chinese text support (UTF-8, proper fonts)

    Args:
        html_content: HTML content to verify
        required_sections: List of required section IDs or classes
        check_css: Whether to check for CSS styling
        check_responsive: Whether to check responsive design elements

    Returns:
        VerificationResult with validation details
    """
    result = VerificationResult(passed=True)

    # Parse HTML structure
    parser = HTMLStructureParser()
    try:
        parser.feed(html_content)
    except Exception as e:
        result.add_error(f"HTML parsing failed: {str(e)}")
        return result

    # Check 1: Basic HTML structure
    if not parser.has_body:
        result.add_error("Missing <body> tag")

    if parser.unclosed_tags:
        result.add_warning(f"Potentially unclosed tags: {', '.join(set(parser.unclosed_tags))}")

    # Check 2: Content hierarchy
    h1_count = parser.tag_counts.get('h1', 0)
    h2_count = parser.tag_counts.get('h2', 0)
    h3_count = parser.tag_counts.get('h3', 0)

    if h1_count == 0 and h2_count == 0:
        result.add_error("No headings found (h1 or h2) - content needs structure")
    elif h1_count > 1:
        result.add_warning(f"Multiple h1 tags ({h1_count}) - recommend using h2 for sections")

    if h2_count > 0 and h3_count > h2_count * 3:
        result.add_warning(f"Too many h3 tags ({h3_count}) relative to h2 ({h2_count}) - check hierarchy")

    # Check 3: Required sections
    if required_sections:
        html_lower = html_content.lower()
        for section in required_sections:
            if section.lower() not in html_lower:
                result.add_error(f"Required section missing: {section}")

    # Check 4: CSS styling
    if check_css:
        has_inline_css = 'style=' in html_content
        has_style_tag = '<style' in html_content.lower()
        has_external_css = '<link' in html_content.lower() and 'stylesheet' in html_content.lower()

        if not (has_inline_css or has_style_tag or has_external_css):
            result.add_warning("No CSS styling detected - presentation may look unstyled")
        else:
            result.add_suggestion("✅ CSS styling present")

    # Check 5: Responsive design
    if check_responsive:
        has_viewport = 'viewport' in html_content.lower()
        has_media_queries = '@media' in html_content.lower()
        has_flex_grid = any(keyword in html_content.lower() for keyword in ['display: flex', 'display: grid'])

        if not has_viewport:
            result.add_warning("No viewport meta tag - may not display correctly on mobile")

        if has_media_queries or has_flex_grid:
            result.add_suggestion("✅ Responsive design elements detected")

    # Check 6: Chinese text support
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', html_content))
    if has_chinese:
        has_utf8 = 'utf-8' in html_content.lower() or 'charset="utf-8"' in html_content.lower()
        has_chinese_fonts = any(font in html_content.lower() for font in [
            'pingfang', 'hiragino', 'microsoft yahei', 'sans-serif'
        ])

        if not has_utf8:
            result.add_error("Chinese text detected but no UTF-8 charset declaration")

        if not has_chinese_fonts:
            result.add_suggestion("Consider adding Chinese-friendly fonts (PingFang SC, Microsoft YaHei)")

    # Check 7: Content density
    div_count = parser.tag_counts.get('div', 0)
    p_count = parser.tag_counts.get('p', 0)
    text_elements = p_count + parser.tag_counts.get('li', 0) + parser.tag_counts.get('span', 0)

    if div_count > 50 and text_elements < 10:
        result.add_warning(f"High div count ({div_count}) with low text content - check for over-structuring")

    if text_elements == 0:
        result.add_error("No text content found (no p, li, or span tags)")

    # Summary
    if result.passed:
        result.add_suggestion(f"✅ HTML presentation structure validated ({len(parser.tags)} total tags)")

    return result


# ============================================================================
# Document Formatting Verification
# ============================================================================

def verify_document_formatting(
    content: str,
    content_type: str = "html",
    check_readability: bool = True,
    min_line_height: float = 1.5
) -> VerificationResult:
    """
    Verify document formatting and readability.

    Checks:
    - Line height for readability (1.5+ recommended)
    - Paragraph spacing
    - Font size (not too small)
    - Text contrast
    - Content length (not too long without breaks)

    Args:
        content: Document content (HTML or text)
        content_type: Type of content ("html", "text", "markdown")
        check_readability: Whether to check readability metrics
        min_line_height: Minimum recommended line height

    Returns:
        VerificationResult with formatting validation
    """
    result = VerificationResult(passed=True)

    if content_type == "html":
        # Check line height
        line_height_match = re.search(r'line-height:\s*([0-9.]+)', content)
        if line_height_match:
            line_height = float(line_height_match.group(1))
            if line_height < min_line_height:
                result.add_warning(f"Line height {line_height} is below recommended {min_line_height} - may affect readability")
            else:
                result.add_suggestion(f"✅ Good line height ({line_height})")
        else:
            result.add_warning("No explicit line-height set - browser default may vary")

        # Check font size
        font_sizes = re.findall(r'font-size:\s*(\d+)px', content)
        if font_sizes:
            min_font_size = min(int(size) for size in font_sizes)
            if min_font_size < 14:
                result.add_warning(f"Small font size detected ({min_font_size}px) - recommend 14px+ for body text")

        # Check paragraph spacing
        has_margin = 'margin:' in content or 'margin-bottom:' in content
        has_padding = 'padding:' in content or 'padding-bottom:' in content

        if not (has_margin or has_padding):
            result.add_suggestion("Consider adding margin/padding between paragraphs for better readability")

        # Check text contrast
        has_dark_text_light_bg = bool(re.search(r'color:\s*#(?:000|333|222|111)|black', content)) and \
                                 bool(re.search(r'background(?:-color)?:\s*#(?:fff|f[0-9a-f]{3})|white', content))

        if not has_dark_text_light_bg:
            result.add_suggestion("Ensure sufficient text contrast (dark text on light background recommended)")

    elif content_type == "text" or content_type == "markdown":
        # Check paragraph breaks
        lines = content.split('\n')
        long_paragraphs = [i for i, line in enumerate(lines) if len(line) > 500]

        if long_paragraphs:
            result.add_warning(f"Found {len(long_paragraphs)} very long lines (>500 chars) - consider breaking up")

        # Check heading structure (markdown)
        if content_type == "markdown":
            h1_count = content.count('\n# ')
            h2_count = content.count('\n## ')

            if h1_count == 0 and h2_count == 0:
                result.add_warning("No markdown headings found - add structure with # headers")

    # Check readability
    if check_readability:
        # Count sentences
        sentences = re.split(r'[.!?。！？]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) > 0:
            avg_sentence_length = len(content) / len(sentences)

            if avg_sentence_length > 200:
                result.add_warning("Average sentence length is very long - consider shorter sentences for readability")

    return result


# ============================================================================
# Chart/Data Visualization Verification
# ============================================================================

def verify_chart_quality(
    chart_data: Dict[str, Any],
    chart_type: str = "bar",
    check_labels: bool = True,
    check_data_accuracy: bool = True
) -> VerificationResult:
    """
    Verify chart/visualization quality.

    Checks:
    - Data labels present
    - Axis labels present
    - Data values make sense (no NaN, no extreme outliers)
    - Color contrast
    - Legend present (if multiple series)

    Args:
        chart_data: Chart data dictionary with keys like 'labels', 'datasets', 'values'
        chart_type: Type of chart ("bar", "line", "pie", etc.)
        check_labels: Whether to check for labels
        check_data_accuracy: Whether to validate data values

    Returns:
        VerificationResult with chart validation
    """
    result = VerificationResult(passed=True)

    # Check 1: Labels present
    if check_labels:
        if 'labels' not in chart_data or not chart_data['labels']:
            result.add_error("Chart missing data labels")
        elif len(chart_data['labels']) == 0:
            result.add_error("Chart has empty labels array")
        else:
            result.add_suggestion(f"✅ Chart has {len(chart_data['labels'])} data labels")

        # Check axis labels
        if 'xAxisLabel' not in chart_data and 'yAxisLabel' not in chart_data:
            result.add_warning("Chart missing axis labels - recommend adding for clarity")

    # Check 2: Data values
    if check_data_accuracy:
        datasets = chart_data.get('datasets', [chart_data.get('values', [])])

        for i, dataset in enumerate(datasets):
            if isinstance(dataset, dict):
                data_values = dataset.get('data', [])
            else:
                data_values = dataset

            # Check for NaN or None
            if any(v is None or (isinstance(v, float) and str(v) == 'nan') for v in data_values):
                result.add_error(f"Dataset {i} contains NaN or None values")

            # Check for negative values in pie charts
            if chart_type == "pie" and any(isinstance(v, (int, float)) and v < 0 for v in data_values):
                result.add_error("Pie chart cannot have negative values")

            # Check for extreme outliers
            numeric_values = [v for v in data_values if isinstance(v, (int, float))]
            if len(numeric_values) > 2:
                max_val = max(numeric_values)
                min_val = min(numeric_values)
                if max_val > min_val * 100:
                    result.add_warning(f"Extreme value range detected (max/min ratio > 100) - consider log scale")

    # Check 3: Legend (for multi-series charts)
    if 'datasets' in chart_data and len(chart_data['datasets']) > 1:
        if 'legend' not in chart_data:
            result.add_warning("Multiple datasets but no legend - add legend for clarity")

    # Check 4: Chart title
    if 'title' not in chart_data or not chart_data['title']:
        result.add_suggestion("Consider adding a chart title for context")

    # Check 5: Data point count
    if 'labels' in chart_data:
        point_count = len(chart_data['labels'])
        if point_count > 50:
            result.add_warning(f"Large number of data points ({point_count}) - consider aggregation or filtering")
        elif point_count == 0:
            result.add_error("Chart has no data points")

    return result


# ============================================================================
# Combined Visual Content Verification
# ============================================================================

def verify_visual_content(
    content: Any,
    content_type: str,
    **kwargs
) -> VerificationResult:
    """
    Unified verification function for all visual content types.

    Args:
        content: Content to verify (HTML string, chart data dict, etc.)
        content_type: Type of content ("html_presentation", "document", "chart")
        **kwargs: Additional arguments passed to specific verifiers

    Returns:
        VerificationResult from appropriate verifier

    Example:
        result = verify_visual_content(
            html_string,
            content_type="html_presentation",
            required_sections=["summary", "details"]
        )
    """
    if content_type == "html_presentation":
        return verify_html_presentation(content, **kwargs)

    elif content_type == "document":
        return verify_document_formatting(content, **kwargs)

    elif content_type == "chart":
        return verify_chart_quality(content, **kwargs)

    else:
        result = VerificationResult(passed=False)
        result.add_error(f"Unknown content type: {content_type}")
        return result


# ============================================================================
# Batch Verification
# ============================================================================

def verify_multiple_visuals(
    contents: List[Dict[str, Any]]
) -> Dict[str, VerificationResult]:
    """
    Verify multiple visual contents in batch.

    Args:
        contents: List of dicts with keys 'content', 'content_type', 'name', and optional kwargs

    Returns:
        Dict mapping content names to VerificationResults

    Example:
        results = verify_multiple_visuals([
            {
                "name": "main_presentation",
                "content": html_string,
                "content_type": "html_presentation"
            },
            {
                "name": "revenue_chart",
                "content": chart_data,
                "content_type": "chart"
            }
        ])
    """
    results = {}

    for item in contents:
        name = item.get('name', f'item_{len(results)}')
        content = item.get('content')
        content_type = item.get('content_type')

        # Extract kwargs (everything except name, content, content_type)
        kwargs = {k: v for k, v in item.items() if k not in ('name', 'content', 'content_type')}

        try:
            result = verify_visual_content(content, content_type, **kwargs)
            results[name] = result
        except Exception as e:
            error_result = VerificationResult(passed=False)
            error_result.add_error(f"Verification failed: {str(e)}")
            results[name] = error_result

    return results


# ============================================================================
# Reporting
# ============================================================================

def format_visual_verification_report(
    results: Dict[str, VerificationResult],
    include_suggestions: bool = True
) -> str:
    """
    Format verification results as human-readable report.

    Args:
        results: Dict of verification results
        include_suggestions: Whether to include suggestions in report

    Returns:
        Formatted report string
    """
    lines = []

    lines.append("=" * 70)
    lines.append("VISUAL CONTENT VERIFICATION REPORT")
    lines.append("=" * 70)

    overall_passed = all(r.passed for r in results.values())
    lines.append(f"\n📊 Overall Status: {'✅ PASSED' if overall_passed else '❌ FAILED'}")
    lines.append(f"   Items Verified: {len(results)}")

    for name, result in results.items():
        lines.append(f"\n{'─' * 70}")
        lines.append(f"📄 {name}")
        lines.append(f"{'─' * 70}")
        lines.append(f"Status: {result.get_summary()}")

        if result.errors:
            lines.append("\n❌ ERRORS:")
            for i, error in enumerate(result.errors, 1):
                lines.append(f"  {i}. {error}")

        if result.warnings:
            lines.append("\n⚠️  WARNINGS:")
            for i, warning in enumerate(result.warnings, 1):
                lines.append(f"  {i}. {warning}")

        if include_suggestions and result.suggestions:
            lines.append("\n💡 SUGGESTIONS:")
            for i, suggestion in enumerate(result.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")

    lines.append("\n" + "=" * 70)

    return "\n".join(lines)
