"""
Personal task and note management tools
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
    name="manage_personal_tasks",
    description="""Manage personal tasks and to-do items for a user.

Use this tool when:
- User wants to create a new task ("创建任务" or "add task")
- User wants to see their tasks ("显示待办" or "show my tasks")
- User wants to mark a task as complete ("完成任务" or "complete task")
- User wants to delete a task ("删除任务" or "delete task")

Actions supported:
- create: Create a new task with title, description, priority, and due date
- list: List all tasks (or filter by status: pending/completed)
- complete: Mark a task as completed
- delete: Remove a task from the list

Returns: Confirmation message or list of tasks with details.""",
    input_schema={
        "user_id": int,
        "action": str,  # "create", "list", "complete", "delete"
        "task_data": dict  # Task details (varies by action)
    }
)
async def manage_personal_tasks_tool(args):
    """Manage personal tasks"""
    if not _campfire_tools:
        return {
            "content": [{
                "type": "text",
                "text": "Error: CampfireTools not initialized"
            }]
        }


@tool(
    name="set_reminder",
    description="""Set a personal reminder for a user.

Use this tool when:
- User wants to be reminded about something ("提醒我" or "remind me")
- User says "set reminder" or "create reminder"
- User wants to schedule a notification

NOTE: This stores the reminder but automated delivery is not yet implemented.
The bot will save the reminder for manual review by the user.

Returns: Confirmation that reminder was saved with details.""",
    input_schema={
        "user_id": int,
        "reminder_text": str,
        "remind_at": str  # Natural language or YYYY-MM-DD HH:MM format
    }
)
async def set_reminder_tool(args):
    """Set personal reminder"""
    if not _campfire_tools:
        return {
            "content": [{
                "type": "text",
                "text": "Error: CampfireTools not initialized"
            }]
        }


@tool(
    name="save_personal_note",
    description="""Save a personal note for a user.

Use this tool when:
- User wants to save information ("记录笔记" or "save note")
- User wants to document something for later reference
- User says "take a note" or "save this"

Notes are stored as Markdown files with timestamps and searchable.

Returns: Confirmation that note was saved with path.""",
    input_schema={
        "user_id": int,
        "title": str,
        "content": str  # Markdown formatted content
    }
)
async def save_personal_note_tool(args):
    """Save personal note"""
    if not _campfire_tools:
        return {
            "content": [{
                "type": "text",
                "text": "Error: CampfireTools not initialized"
            }]
        }


@tool(
    name="search_personal_notes",
    description="""Search a user's personal notes.

Use this tool when:
- User wants to find notes ("搜索笔记" or "search my notes")
- User asks "what did I write about..."
- User wants to see recent notes
- User says "find my note about..."

If no query is provided, returns the most recent notes.

Returns: List of matching notes with excerpts and metadata.""",
    input_schema={
        "user_id": int,
        "query": str,  # Optional: search keywords
        "max_results": int  # Optional: default 10
    }
)
async def search_personal_notes_tool(args):
    """Search personal notes"""
    if not _campfire_tools:
        return {
            "content": [{
                "type": "text",
                "text": "Error: CampfireTools not initialized"
            }]
        }


