"""
Progress Classifier - Detect significant milestone messages from agent thinking

Filters agent text blocks to identify major progress steps worth showing to users,
preventing message spam while keeping users informed during long analyses.
"""

import re
from typing import Optional


class ProgressClassifier:
    """
    Classify agent messages as milestones worth showing to users.

    Distinguishes between:
    - Major milestones (e.g., "Step 1: 初步探索", "📊 正在读取Excel...")
    - Minor internal thoughts (skip these to avoid spam)
    """

    # Chinese action verbs indicating progress
    MILESTONE_KEYWORDS = [
        "让我", "现在", "完美", "很好", "太好了", "好的",
        "接下来", "然后", "开始", "正在",
        "Step 1", "Step 2", "Step 3", "Step 4", "Step 5",
        "📊", "🔍", "📈", "💰", "✅", "🎯", "📋", "🤔"
    ]

    # Tool names that indicate major milestones
    MAJOR_TOOLS = [
        "get_excel_info",           # Reading Excel structure
        "validate_account_structure", # Validating financial accounts
        "read_excel_region",         # Extracting data
        "calculate",                 # Performing calculations
        "show_excel_visual",         # Generating visualizations
        "think_about_financial_data", # Analyzing data
        "think_about_assumptions",   # Validating assumptions
        "save_analysis_insight",     # Saving results
        "write_memory_note"          # Documenting insights
    ]

    @staticmethod
    def is_milestone(text: str, last_tool: Optional[str] = None) -> bool:
        """
        Determine if a message is a significant milestone worth posting.

        Args:
            text: Message text from agent
            last_tool: Name of tool that was just called (if any)

        Returns:
            True if this should be posted as a progress update

        Examples:
            >>> ProgressClassifier.is_milestone("让我先查看一下这个文件...")
            True
            >>> ProgressClassifier.is_milestone("The file contains...")  # Too generic
            False
            >>> ProgressClassifier.is_milestone("很好！我看到这个文件包含139行数据")
            True
        """
        # Skip very short messages (likely not meaningful)
        if len(text.strip()) < 20:
            return False

        # Skip messages that are mostly HTML tags (internal formatting)
        html_tag_ratio = len(re.findall(r'<[^>]+>', text)) / max(len(text), 1)
        if html_tag_ratio > 0.3:  # More than 30% HTML tags
            return False

        # Check for explicit milestone keywords
        for keyword in ProgressClassifier.MILESTONE_KEYWORDS:
            if keyword in text:
                return True

        # Check if this message follows a major tool call
        # (likely explaining what the tool found)
        if last_tool:
            tool_name = last_tool.replace("mcp__fin-report-agent__", "")
            if tool_name in ProgressClassifier.MAJOR_TOOLS:
                return True

        # Check for headings (likely section markers)
        if re.search(r'<h[1-6]>', text) or re.search(r'##\s+', text):
            return True

        return False

    @staticmethod
    def get_tool_milestone(tool_name: str) -> Optional[str]:
        """
        Get user-friendly milestone message for a tool call.

        Args:
            tool_name: MCP tool name (e.g., "mcp__fin-report-agent__get_excel_info")

        Returns:
            User-friendly progress message, or None if not a major tool

        Examples:
            >>> ProgressClassifier.get_tool_milestone("mcp__fin-report-agent__get_excel_info")
            '📊 正在读取Excel文件结构...'
            >>> ProgressClassifier.get_tool_milestone("mcp__campfire__search_conversations")
            None  # Not a major financial analysis tool
        """
        milestones = {
            "get_excel_info": "📊 正在读取Excel文件结构...",
            "validate_account_structure": "🔍 正在验证账户层级...",
            "read_excel_region": "📈 正在提取财务数据...",
            "calculate": "💰 正在计算核心指标...",
            "show_excel_visual": "📊 正在生成数据可视化...",
            "think_about_financial_data": "🤔 正在分析财务数据...",
            "think_about_assumptions": "✅ 正在验证分析假设...",
            "save_analysis_insight": "💾 正在保存分析结果...",
            "write_memory_note": "📝 正在记录分析洞察..."
        }

        # Clean MCP prefix from tool name
        clean_name = tool_name.replace("mcp__fin-report-agent__", "")

        # Return milestone message if it's a major tool
        return milestones.get(clean_name)

    @staticmethod
    def truncate_for_preview(text: str, max_length: int = 150) -> str:
        """
        Truncate text for preview while preserving meaning.

        Args:
            text: Full text
            max_length: Maximum characters to include

        Returns:
            Truncated text with ellipsis if needed

        Examples:
            >>> ProgressClassifier.truncate_for_preview("Very long text here...", 20)
            'Very long text he...'
        """
        # Strip HTML tags for preview
        clean_text = re.sub(r'<[^>]+>', '', text)

        # Remove excessive whitespace
        clean_text = ' '.join(clean_text.split())

        if len(clean_text) <= max_length:
            return clean_text

        # Truncate at word boundary
        truncated = clean_text[:max_length].rsplit(' ', 1)[0]
        return f"{truncated}..."
