"""
Daily briefing generation and search tools
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
    name="generate_daily_briefing",
    description="""Generate a daily briefing document from Campfire conversations and files.

Use this tool when:
- User asks to generate today's briefing or daily report
- User wants a summary of today's activity
- User says "生成今天的日报" or "generate daily briefing"
- Need to compile daily activity for archival/review

The briefing includes:
- Executive summary of the day
- By-room activity breakdown
- Files uploaded
- Participant summary

Returns: Confirmation with path to generated briefing document.""",
    input_schema={
        "date": str,  # Optional: YYYY-MM-DD format, defaults to today
        "room_ids": list,  # Optional: list of room IDs, defaults to all
        "include_files": bool,  # Optional: default True
        "summary_length": str  # Optional: "concise" or "detailed", default "concise"
    }
)
async def generate_daily_briefing_tool(args):
    """Generate daily briefing document"""
    if not _campfire_tools:
        return {
            "content": [{
                "type": "text",
                "text": "Error: CampfireTools not initialized"
            }]
        }


@tool(
    name="search_briefings",
    description="""Search historical daily briefings by date range or keywords.

Use this tool when:
- User asks "show me briefings from last week"
- User wants to find briefings containing specific topics
- User asks "搜索日报" or "search briefings"
- Need to review past activity

Returns: List of matching briefings with excerpts and metadata.""",
    input_schema={
        "query": str,  # Optional: search keywords
        "start_date": str,  # Optional: YYYY-MM-DD
        "end_date": str,  # Optional: YYYY-MM-DD
        "max_results": int  # Optional: default 5
    }
)
async def search_briefings_tool(args):
    """Search historical briefings"""
    if not _campfire_tools:
        return {
            "content": [{
                "type": "text",
                "text": "Error: CampfireTools not initialized"
            }]
        }


