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


