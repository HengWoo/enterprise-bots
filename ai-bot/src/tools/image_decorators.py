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
    """Process and analyze image files using Claude's vision API"""
    import anthropic
    import base64
    import os
    from pathlib import Path


