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
                "text": "错误：Campfire工具未初始化。请检查数据库连接。"
            }]
        }

    try:
        # Extract parameters
        date = args.get('date')
        room_ids = args.get('room_ids')
        include_files = args.get('include_files', True)
        summary_length = args.get('summary_length', 'concise')

        # Call underlying implementation
        result = _campfire_tools.generate_daily_briefing(
            date=date,
            room_ids=room_ids,
            include_files=include_files,
            summary_length=summary_length
        )

        # Format response
        if result.get('success'):
            response_text = f"📊 日报生成成功\n\n"
            response_text += f"日期: {result.get('date', 'N/A')}\n"
            response_text += f"路径: {result.get('path', 'N/A')}\n"

            # Add statistics if available
            stats = result.get('statistics', {})
            if stats:
                response_text += f"\n**统计信息:**\n"
                response_text += f"- 消息数量: {stats.get('message_count', 0)}\n"
                response_text += f"- 房间数量: {stats.get('room_count', 0)}\n"
                if include_files:
                    response_text += f"- 文件数量: {stats.get('file_count', 0)}\n"
        else:
            response_text = f"生成日报失败：{result.get('error', '未知错误')}"

        return {
            "content": [{
                "type": "text",
                "text": response_text
            }]
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"生成日报失败：{str(e)}"
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
                "text": "错误：Campfire工具未初始化。请检查数据库连接。"
            }]
        }

    try:
        # Extract parameters
        query = args.get('query', '')
        start_date = args.get('start_date')
        end_date = args.get('end_date')
        max_results = args.get('max_results', 5)

        # Call underlying implementation
        briefings = _campfire_tools.search_briefings(
            query=query,
            start_date=start_date,
            end_date=end_date,
            max_results=max_results
        )

        # Format response
        if not briefings:
            response_text = "✅ **搜索完成**\n\n"
            if query:
                response_text += f"未找到包含 '{query}' 的日报。\n\n"
            elif start_date or end_date:
                date_range = f"{start_date or '起始'} 到 {end_date or '结束'}"
                response_text += f"未找到 {date_range} 期间的日报。\n\n"
            else:
                response_text += "未找到历史日报。\n\n"

            response_text += "📝 **可能原因：**\n"
            response_text += "- 该时间段内尚未生成日报文档\n"
            response_text += "- 日报文件不存在于系统中\n"
        else:
            response_text = f"找到 {len(briefings)} 份日报：\n\n"

            for i, briefing in enumerate(briefings, 1):
                response_text += f"**{i}. {briefing.get('date', 'Unknown date')} 日报**\n"
                response_text += f"路径: {briefing.get('path', 'N/A')}\n"

                # Add statistics if available
                stats = briefing.get('statistics', {})
                if stats:
                    response_text += f"统计: "
                    response_text += f"{stats.get('message_count', 0)} 条消息, "
                    response_text += f"{stats.get('room_count', 0)} 个房间"
                    if stats.get('file_count'):
                        response_text += f", {stats.get('file_count')} 个文件"
                    response_text += "\n"

                # Add excerpt if available
                excerpt = briefing.get('excerpt', '')
                if excerpt:
                    response_text += f"摘要: {excerpt[:200]}...\n"

                response_text += "\n"

        return {
            "content": [{
                "type": "text",
                "text": response_text
            }]
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"搜索日报失败：{str(e)}"
            }]
        }


