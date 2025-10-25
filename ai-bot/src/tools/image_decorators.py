"""
Image processing tools
Agent SDK Tool Decorators
"""

from claude_agent_sdk import tool
from typing import Optional

# Global instances (will be initialized by app)
_campfire_tools: Optional = None
_supabase_tools: Optional = None


def set_tools(campfire_tools, supabase_tools):
    """Set the global tool instances"""
    global _campfire_tools, _supabase_tools
    _campfire_tools = campfire_tools
    _supabase_tools = supabase_tools


async def _process_image_impl(args):
    """Internal implementation of image processing"""
    import anthropic
    import base64
    import os
    from pathlib import Path

    file_path = args.get("file_path", "")
    question = args.get("question", "What's in this image? Please provide a detailed analysis.")

    # Validate inputs
    if not file_path:
        return "❌ Error: file_path is required"

    # Convert relative path to absolute if needed
    if not file_path.startswith("/"):
        file_path = f"/{file_path}"

    # Check if file exists
    if not os.path.exists(file_path):
        return f"❌ Error: File not found at path: {file_path}\n\nPlease verify the file path is correct."

    # Determine file type from extension and content_type
    file_ext = Path(file_path).suffix.lower()
    supported_formats = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }

    if file_ext not in supported_formats:
        return f"❌ Error: Unsupported file format: {file_ext}\n\nSupported formats: PNG, JPG, JPEG, GIF, WEBP"

    media_type = supported_formats[file_ext]

    # Read and encode image
    try:
        with open(file_path, 'rb') as f:
            image_data = f.read()

        # Check file size (Claude has limits, ~5MB is safe)
        file_size_mb = len(image_data) / (1024 * 1024)
        if file_size_mb > 5:
            return f"❌ Error: Image file too large ({file_size_mb:.1f}MB). Maximum supported size is 5MB.\n\nPlease compress the image or upload a smaller version."

        # Encode to base64
        image_base64 = base64.standard_b64encode(image_data).decode('utf-8')

    except Exception as e:
        return f"❌ Error reading image file: {str(e)}"

    # Call Claude Vision API
    try:
        # Get API key from environment
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return "❌ Error: ANTHROPIC_API_KEY not found in environment"

        # Create Anthropic client
        client = anthropic.Anthropic(api_key=api_key)

        # Call Vision API
        response = client.messages.create(
            model="claude-sonnet-4-20250514",  # Use Claude 4 Sonnet for vision tasks
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                    ]
                }
            ]
        )

        # Extract text from response
        result_text = ""
        for block in response.content:
            if hasattr(block, 'text'):
                result_text += block.text

        return result_text if result_text else "❌ Error: No response from Vision API"

    except Exception as e:
        return f"❌ Error calling Vision API: {str(e)}"


@tool(
    name="process_image",
    description="""Analyze an image file using Claude's vision capabilities.

Use this tool when:
- User uploads a screenshot or photo
- User asks to analyze an image
- User references an image file in their message
- You need to extract text or information from an image

This tool reads image files (PNG, JPG, JPEG, GIF, WEBP) from /campfire-files/
and uses Claude's vision API to analyze them.

Returns: Detailed analysis of the image content.

Example queries:
- "请分析这张截图"
- "这张图片里有什么？"
- "帮我读取图片中的文字"

IMPORTANT: Use this instead of Read tool for image files.""",
    input_schema={
        "file_path": str,  # Path to image file (e.g., "/campfire-files/xx/yy/hash")
        "question": str    # Optional: Specific question about the image (default: "What's in this image?")
    }
)
async def process_image_tool(args):
    """Process and analyze image files using Claude's vision API - wrapper for SDK tool"""
    return await _process_image_impl(args)


