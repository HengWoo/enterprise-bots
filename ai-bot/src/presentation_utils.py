"""
Presentation Utilities for v0.4.1 File Download System

Helper functions for generating download buttons and presentation-related HTML.
"""


def generate_download_button(
    token: str,
    title: str,
    base_url: str = "http://localhost:5000",
    additional_text: str = None
) -> str:
    """
    Generate styled download button HTML for Campfire.

    Args:
        token: UUID token from file_registry.register_file()
        title: Button text (e.g., "View Full Presentation", "Download Report")
        base_url: Base URL for the download endpoint (default: localhost for testing)
        additional_text: Optional text to display below the button (e.g., "7 slides with interactive charts")

    Returns:
        HTML string with styled download button

    Example:
        html = generate_download_button(
            token="abc123-uuid-456def",
            title="View Full Presentation",
            base_url="https://chat.smartice.ai",
            additional_text="7 slides with interactive charts"
        )

        # Result:
        # <div style="margin-top: 20px; ...">
        #     <a href="https://chat.smartice.ai/files/download/abc123-uuid-456def" ...>
        #         🎯 View Full Presentation
        #     </a>
        #     <p>7 slides with interactive charts • Link expires in 1 hour</p>
        # </div>
    """
    download_url = f"{base_url}/files/download/{token}"

    # Build additional text line
    if additional_text:
        info_text = f"{additional_text} • Link expires in 1 hour"
    else:
        info_text = "Link expires in 1 hour • Opens in new tab"

    return f"""
<div style="margin-top: 20px; padding: 15px; background: #f0f7ff; border-radius: 8px; text-align: center;">
    <a href="{download_url}"
       target="_blank"
       style="display: inline-block;
              padding: 12px 24px;
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              color: white;
              text-decoration: none;
              border-radius: 6px;
              font-weight: 600;
              box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
        🎯 {title}
    </a>
    <p style="color: #666; font-size: 0.9em; margin-top: 10px;">
        {info_text}
    </p>
</div>
"""


def generate_inline_preview(
    title: str,
    summary: str,
    metrics: list = None,
    download_token: str = None,
    base_url: str = "http://localhost:5000"
) -> str:
    """
    Generate inline preview HTML for presentations/reports.

    This creates a Campfire-safe preview (no JavaScript) that summarizes
    the main content and provides a download link for the full version.

    Args:
        title: Presentation/report title
        summary: Brief summary text
        metrics: List of metric dicts with keys: label, value, change (optional), color (optional)
        download_token: UUID token for download link (optional)
        base_url: Base URL for download endpoint

    Returns:
        HTML string with inline preview

    Example:
        html = generate_inline_preview(
            title="Q3 Financial Performance",
            summary="Analysis of revenue trends and profitability",
            metrics=[
                {"label": "Total Revenue", "value": "$1.2M", "change": "+23% YoY"},
                {"label": "Profit Margin", "value": "32%", "change": "+2%"}
            ],
            download_token="abc123-uuid-456def"
        )
    """
    html = f"""
<div style="background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
            padding: 25px;
            border-radius: 12px;
            border-left: 5px solid #667eea;
            margin: 15px 0;">
    <h2 style="color: #2c3e50; margin: 0 0 10px 0; font-size: 1.8em;">
        {title}
    </h2>
    <p style="color: #7f8c8d; margin: 0 0 20px 0; font-size: 1.1em;">
        {summary}
    </p>
"""

    # Add metrics if provided
    if metrics:
        html += """
    <div style="display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;">
"""
        for metric in metrics:
            color = metric.get('color', '#667eea')
            html += f"""
        <div style="background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    border-left: 4px solid {color};">
            <div style="font-size: 2em;
                        font-weight: 700;
                        color: {color};
                        margin-bottom: 8px;">
                {metric['value']}
            </div>
            <div style="color: #7f8c8d; font-size: 0.95em;">
                {metric['label']}
            </div>
"""
            if metric.get('change'):
                html += f"""
            <div style="color: #27ae60; margin-top: 8px; font-size: 0.9em;">
                {metric['change']}
            </div>
"""
            html += "        </div>\n"

        html += "    </div>\n"

    # Add download button if token provided
    if download_token:
        download_url = f"{base_url}/files/download/{download_token}"
        html += f"""
    <div style="margin-top: 25px; text-align: center;">
        <a href="{download_url}"
           target="_blank"
           style="display: inline-block;
                  padding: 14px 28px;
                  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                  color: white;
                  text-decoration: none;
                  border-radius: 8px;
                  font-weight: 600;
                  font-size: 1.1em;
                  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                  transition: transform 0.2s;">
            🎯 View Full Report
        </a>
        <p style="color: #95a5a6;
                  font-size: 0.9em;
                  margin-top: 12px;">
            Interactive charts and full analysis • Link expires in 1 hour
        </p>
    </div>
"""

    html += "</div>"
    return html
