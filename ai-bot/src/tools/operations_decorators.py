"""
Basic operations data CRUD tools
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
    name="query_operations_data",
    description="""Query operations data from Supabase tables.

Use this tool when:
- User asks for operations metrics or data
- Need to retrieve project information
- User wants to see task status or progress
- Looking up specific records in operations database

Supports filtering, sorting, and limiting results.

Returns: List of records matching query criteria with metadata.""",
    input_schema={
        "table": str,  # Required: table name (e.g., 'projects', 'tasks', 'operations_metrics')
        "filters": dict,  # Optional: column-value pairs to filter by
        "columns": str,  # Optional: columns to select (default "*")
        "limit": int,  # Optional: max records to return (default 100)
        "order_by": str  # Optional: column to order by (prefix '-' for descending)
    }
)
async def query_operations_data_tool(args):
    """Query operations data from Supabase"""
    if not _supabase_tools:
        return {
            "content": [{
                "type": "text",
                "text": "⚠️ **Supabase tools not available**\n\nSupabase credentials have not been configured. Please contact the administrator to set up SUPABASE_URL and SUPABASE_KEY environment variables."
            }]
        }

    try:
        # Extract parameters
        table = args.get('table', '')
        filters = args.get('filters', {})
        columns = args.get('columns', '*')
        limit = args.get('limit', 100)
        order_by = args.get('order_by')

        # Call underlying implementation
        result = _supabase_tools.query_operations_data(
            table=table,
            filters=filters,
            columns=columns,
            limit=limit,
            order_by=order_by
        )

        # Format response
        if result.get('success') and result.get('data'):
            records = result['data']
            response_text = f"**{table}** 表查询结果 ({len(records)} 条记录):\n\n"

            # Format records as a table
            for i, record in enumerate(records[:10], 1):  # Show first 10
                response_text += f"{i}. "
                for key, value in record.items():
                    response_text += f"{key}: {value}, "
                response_text = response_text.rstrip(', ') + "\n"

            if len(records) > 10:
                response_text += f"\n...还有 {len(records) - 10} 条记录\n"

        elif result.get('success') and not result.get('data'):
            response_text = f"未找到符合条件的记录（表：{table}）"

        else:
            response_text = f"查询失败：{result.get('error', '未知错误')}"

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
                "text": f"查询运营数据失败：{str(e)}"
            }]
        }


@tool(
    name="update_operations_data",
    description="""Update an operations data record in Supabase.

Use this tool when:
- User wants to update project status
- Need to mark a task as completed
- Updating operations metrics or records
- User says "update", "change", or "modify" operations data

Returns: Confirmation of update with updated record.""",
    input_schema={
        "table": str,  # Required: table name
        "record_id": int,  # Required: ID of record to update
        "data": dict,  # Required: column-value pairs to update
        "id_column": str  # Optional: ID column name (default "id")
    }
)
async def update_operations_data_tool(args):
    """Update operations data in Supabase"""
    if not _supabase_tools:
        return {
            "content": [{
                "type": "text",
                "text": "⚠️ **Supabase tools not available**\n\nSupabase credentials have not been configured."
            }]
        }

    try:
        # Extract parameters
        table = args.get('table', '')
        record_id = args.get('record_id')
        data = args.get('data', {})
        id_column = args.get('id_column', 'id')

        # Call underlying implementation
        result = _supabase_tools.update_operations_data(
            table=table,
            record_id=record_id,
            data=data,
            id_column=id_column
        )

        # Format response
        if result.get('success'):
            response_text = f"✅ 更新成功\n\n"
            response_text += f"表: {table}\n"
            response_text += f"记录ID: {record_id}\n"
            response_text += f"更新字段: {', '.join(data.keys())}\n"

            # Show updated record if available
            if result.get('data'):
                response_text += f"\n**更新后的记录:**\n"
                for key, value in result['data'].items():
                    response_text += f"- {key}: {value}\n"
        else:
            response_text = f"更新失败：{result.get('error', '未知错误')}"

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
                "text": f"更新运营数据失败：{str(e)}"
            }]
        }


@tool(
    name="get_operations_summary",
    description="""Generate a summary report of operations data for a date range.

Use this tool when:
- User asks for an operations summary or report
- User wants to see overall statistics
- Need to aggregate operations metrics
- User asks "what's the status of operations" or "give me a summary"

Generates summary with metrics grouped by category and status.

Returns: Comprehensive summary report with statistics and breakdowns.""",
    input_schema={
        "date_range": dict,  # Optional: {'start_date': 'YYYY-MM-DD', 'end_date': 'YYYY-MM-DD'}
        "metrics": list  # Optional: list of metrics to include (e.g., ['tasks', 'projects'])
    }
)
async def get_operations_summary_tool(args):
    """Generate operations summary report"""
    if not _supabase_tools:
        return {
            "content": [{
                "type": "text",
                "text": "⚠️ **Supabase tools not available**\n\nSupabase credentials have not been configured."
            }]
        }

    try:
        # Extract parameters
        date_range = args.get('date_range')
        metrics = args.get('metrics')

        # Call underlying implementation
        result = _supabase_tools.get_operations_summary(
            date_range=date_range,
            metrics=metrics
        )

        # Format response
        if result.get('success'):
            response_text = f"📊 **运营数据摘要**\n\n"

            # Date range
            if date_range:
                response_text += f"时间范围: {date_range.get('start_date', '')} 至 {date_range.get('end_date', '')}\n\n"

            # Summary data
            summary = result.get('summary', {})
            if summary:
                for metric_name, metric_data in summary.items():
                    response_text += f"**{metric_name}:**\n"

                    if isinstance(metric_data, dict):
                        for key, value in metric_data.items():
                            response_text += f"- {key}: {value}\n"
                    else:
                        response_text += f"- {metric_data}\n"

                    response_text += "\n"
            else:
                response_text += "暂无运营数据。\n"

        else:
            response_text = f"生成摘要失败：{result.get('error', '未知错误')}"

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
                "text": f"生成运营摘要失败：{str(e)}"
            }]
        }


