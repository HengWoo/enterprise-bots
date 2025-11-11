"""
File Saving Tools for v0.4.1 Integration
Provides bot-facing tools to save generated files and create download links

v0.5.0: Added HTML verification before saving
"""

import os
from claude_agent_sdk import tool
from src.file_registry import file_registry
from src.presentation_utils import generate_download_button
from src.utils.verification_wrapper import verify_html_content


async def _save_html_presentation_impl(args):
    """
    Implementation of save_html_presentation_tool (testable).

    Args:
        html_content: Full HTML code
        filename: File name (e.g., "Q3_Report.html")
        title: Display title for download button

    Returns:
        Formatted response with download button HTML
    """
    try:
        # Get temp directory from environment variable
        temp_dir = os.getenv('FILE_TEMP_DIR', '/tmp')

        # Extract parameters
        html_content = args.get('html_content')
        filename = args.get('filename', 'presentation.html')
        title = args.get('title', '生成的报告')

        # Validate inputs
        if not html_content:
            return {
                "content": [{
                    "type": "text",
                    "text": "错误：HTML内容不能为空"
                }]
            }

        # v0.5.0: Verify HTML quality before saving
        verification_result = verify_html_content(html_content, check_structure=True)

        # In lenient mode, log warnings but don't block
        if not verification_result.get("valid"):
            print(f"[Verification] ⚠️  HTML validation errors: {verification_result.get('errors')}")
        elif verification_result.get("warnings"):
            print(f"[Verification] ℹ️  HTML validation warnings: {verification_result.get('warnings')}")

        # Quality score logging (for monitoring)
        quality_score = verification_result.get("quality_score", 0.0)
        print(f"[Verification] HTML quality score: {quality_score:.0%}")

        # Ensure filename ends with .html
        if not filename.endswith('.html'):
            filename = f"{filename}.html"

        # Create full file path
        file_path = os.path.join(temp_dir, filename)

        # Save HTML content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Register with FileRegistry (1-hour expiry)
        token = file_registry.register_file(
            file_path=file_path,
            filename=filename,
            expiry_hours=1,
            mime_type='text/html'
        )

        # Get base URL for file downloads (external, browser-accessible)
        # Production: http://files.smartice.ai:5000 (DNS-only mode via FILE_DOWNLOAD_BASE_URL env var)
        # Local dev: http://localhost:8000 (default)
        base_url = os.getenv('FILE_DOWNLOAD_BASE_URL', 'http://localhost:8000')

        # Extract file size for additional info
        file_size = os.path.getsize(file_path)
        size_kb = file_size / 1024

        # Generate download button HTML
        download_html = generate_download_button(
            token=token,
            title=title,
            base_url=base_url,
            additional_text=f"HTML文件 • {size_kb:.1f}KB"
        )

        # v0.5.0: Add verification notice if there are warnings/errors (lenient mode)
        if not verification_result.get("valid") or verification_result.get("warnings"):
            verification_message = verification_result.get("message", "")
            download_html = f"{download_html}\n\n{verification_message}"

        # Add clickable URL as fallback (in case HTML doesn't render)
        download_url = f"{base_url}/files/download/{token}"
        download_html_with_url = f"""{download_html}

<hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">

<p>📥 <strong>文件下载地址：</strong></p>
<p><a href="{download_url}" target="_blank" style="color: #667eea; text-decoration: underline;">{download_url}</a></p>

<p style="color: #999; font-size: 0.9em;">⏱️ 链接有效期：1小时</p>
"""

        # Log for debugging
        print(f"[save_html_presentation] Download URL: {download_url}")
        print(f"[save_html_presentation] Returning HTML with download button")

        # Return formatted response
        return {
            "content": [{
                "type": "text",
                "text": download_html_with_url
            }]
        }

    except Exception as e:
        # Handle any errors gracefully
        return {
            "content": [{
                "type": "text",
                "text": f"保存文件时出错：{str(e)}\n\n请检查FILE_TEMP_DIR环境变量是否配置正确。"
            }]
        }


@tool(
    name="save_html_presentation",
    description="""Save an HTML presentation/report and generate a download link.

Use this tool when:
- User requests an HTML presentation ("创建HTML演示文稿" or "create HTML presentation")
- User asks for an HTML report ("生成HTML报告" or "generate HTML report")
- User wants a downloadable HTML file ("HTML格式下载" or "downloadable HTML")
- You've generated complex HTML content that should be downloadable

This tool will:
1. Save the HTML content to a temporary file
2. Register it with FileRegistry (1-hour expiring token)
3. Generate a styled download button for Campfire
4. Return formatted HTML with inline preview + download link

Returns: HTML with download button and expiry notice.

Example:
User: "创建一个关于餐饮运营流程的HTML幻灯片"
Bot calls this tool with:
{
    "html_content": "<完整HTML代码>",
    "filename": "餐饮运营流程.html",
    "title": "餐饮运营流程演示文稿"
}
Bot receives download button HTML to post to Campfire.
User clicks button, downloads file.
After 1 hour, link expires and file is auto-deleted.
""",
    input_schema={
        "html_content": str,  # Full HTML code to save
        "filename": str,      # File name (e.g., "Report_Q3.html")
        "title": str          # Display title for download button
    }
)
async def save_html_presentation_tool(args):
    """
    Save HTML presentation and return download button (SDK tool wrapper).
    """
    return await _save_html_presentation_impl(args)


# MIME type mapping for common file extensions
MIME_TYPES = {
    '.html': 'text/html',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.pdf': 'application/pdf',
    '.txt': 'text/plain',
    '.md': 'text/markdown',
    '.json': 'application/json',
    '.csv': 'text/csv',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.zip': 'application/zip',
}


async def _save_file_impl(args):
    """
    Implementation of save_file_tool (testable).

    Args:
        file_path: Absolute path to the file to register (e.g., "/tmp/report.pptx")
        filename: User-facing filename for download (e.g., "Q3_Report.pptx")
        title: Display title for download button

    Returns:
        Formatted response with download button HTML
    """
    try:
        # Extract parameters
        file_path = args.get('file_path')
        filename = args.get('filename')
        title = args.get('title', '生成的文件')

        # Validate inputs
        if not file_path:
            return {
                "content": [{
                    "type": "text",
                    "text": "错误：file_path参数不能为空"
                }]
            }

        if not filename:
            # Use basename from file_path if filename not provided
            filename = os.path.basename(file_path)

        if not os.path.exists(file_path):
            return {
                "content": [{
                    "type": "text",
                    "text": f"错误：文件不存在：{file_path}"
                }]
            }

        # Determine MIME type from file extension
        _, ext = os.path.splitext(filename)
        mime_type = MIME_TYPES.get(ext.lower(), 'application/octet-stream')

        # Register with FileRegistry (1-hour expiry)
        token = file_registry.register_file(
            file_path=file_path,
            filename=filename,
            expiry_hours=1,
            mime_type=mime_type
        )

        # Get base URL for file downloads (external, browser-accessible)
        # Production: http://files.smartice.ai:5000 (DNS-only mode via FILE_DOWNLOAD_BASE_URL env var)
        # Local dev: http://localhost:8000 (default)
        base_url = os.getenv('FILE_DOWNLOAD_BASE_URL', 'http://localhost:8000')

        # Extract file size for additional info
        file_size = os.path.getsize(file_path)
        size_kb = file_size / 1024

        # Determine file type description
        file_type_desc = {
            '.html': 'HTML文件',
            '.pptx': 'PowerPoint文件',
            '.docx': 'Word文档',
            '.xlsx': 'Excel文件',
            '.pdf': 'PDF文件',
            '.txt': '文本文件',
            '.md': 'Markdown文件',
            '.json': 'JSON文件',
            '.csv': 'CSV文件',
            '.png': 'PNG图片',
            '.jpg': 'JPG图片',
            '.jpeg': 'JPEG图片',
            '.gif': 'GIF图片',
            '.svg': 'SVG图片',
            '.zip': 'ZIP压缩文件',
        }.get(ext.lower(), '文件')

        # Generate download button HTML
        download_html = generate_download_button(
            token=token,
            title=title,
            base_url=base_url,
            additional_text=f"{file_type_desc} • {size_kb:.1f}KB"
        )

        # Add clickable URL as fallback (in case HTML doesn't render)
        download_url = f"{base_url}/files/download/{token}"
        download_html_with_url = f"""{download_html}

<hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">

<p>📥 <strong>文件下载地址：</strong></p>
<p><a href="{download_url}" target="_blank" style="color: #667eea; text-decoration: underline;">{download_url}</a></p>

<p style="color: #999; font-size: 0.9em;">⏱️ 链接有效期：1小时</p>
"""

        # Log for debugging
        print(f"[save_file] File: {filename}")
        print(f"[save_file] Type: {file_type_desc} ({mime_type})")
        print(f"[save_file] Size: {size_kb:.1f} KB")
        print(f"[save_file] Download URL: {download_url}")

        # Return formatted response
        return {
            "content": [{
                "type": "text",
                "text": download_html_with_url
            }]
        }

    except Exception as e:
        # Handle any errors gracefully
        return {
            "content": [{
                "type": "text",
                "text": f"保存文件时出错：{str(e)}"
            }]
        }


@tool(
    name="save_file",
    description="""Universal file saving tool - Register any file type and generate a download link.

Use this tool AFTER you've generated a file using Bash or other tools.

Supported file types:
- Office: PPTX, DOCX, XLSX
- Documents: PDF, TXT, MD, JSON, CSV
- Images: PNG, JPG, JPEG, GIF, SVG
- Archives: ZIP
- Web: HTML

Workflow:
1. Generate file using appropriate tool (e.g., Bash + python-pptx for PPTX)
2. Call this tool to register the file and create download link
3. Return the download button HTML to user

This tool will:
1. Verify the file exists at the given path
2. Auto-detect MIME type from file extension
3. Register with FileRegistry (1-hour expiring token)
4. Generate a styled download button for Campfire
5. Return formatted HTML with download link

Returns: HTML with download button and expiry notice.

Example 1 - PPTX:
User: "生成一个关于前厅风险点的PPT"
Bot:
1. Uses Bash to run python-pptx script → saves to /tmp/前厅风险点.pptx
2. Calls save_file with:
{
    "file_path": "/tmp/前厅风险点.pptx",
    "filename": "前厅风险点分析.pptx",
    "title": "前厅风险点分析报告"
}
3. Bot receives download button HTML → user clicks to download

Example 2 - Excel:
User: "导出财务数据为Excel"
Bot:
1. Creates Excel file → /tmp/financial_data.xlsx
2. Calls save_file with:
{
    "file_path": "/tmp/financial_data.xlsx",
    "filename": "财务数据.xlsx",
    "title": "财务数据导出"
}

Example 3 - PDF:
User: "生成PDF报告"
Bot:
1. Creates PDF → /tmp/report.pdf
2. Calls save_file with:
{
    "file_path": "/tmp/report.pdf",
    "filename": "季度报告.pdf",
    "title": "Q3季度报告"
}

IMPORTANT: The file must already exist at file_path before calling this tool.
""",
    input_schema={
        "file_path": str,  # Absolute path to existing file (e.g., "/tmp/report.pptx")
        "filename": str,    # User-facing filename (optional, defaults to basename of file_path)
        "title": str        # Display title for download button
    }
)
async def save_file_tool(args):
    """
    Universal file saving tool - Register any file and return download button.
    """
    return await _save_file_impl(args)
