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
                "text": "错误：Campfire工具未初始化。请检查数据库连接。"
            }]
        }

    try:
        # Extract parameters
        user_id = args.get('user_id')
        action = args.get('action', 'list')
        task_data = args.get('task_data', {})

        # Call underlying implementation
        result = _campfire_tools.manage_personal_tasks(
            user_id=user_id,
            action=action,
            task_data=task_data
        )

        # Format response based on action
        if action == 'list':
            tasks = result.get('tasks', [])
            if not tasks:
                response_text = "您当前没有待办任务。"
            else:
                response_text = f"**您的待办任务** ({len(tasks)} 个):\n\n"
                for i, task in enumerate(tasks, 1):
                    status_icon = "✅" if task.get('status') == 'completed' else "⭕"
                    priority = task.get('priority', 'medium')
                    priority_icon = "🔴" if priority == 'high' else ("🟡" if priority == 'medium' else "🟢")

                    response_text += f"{i}. {status_icon} {priority_icon} **{task.get('title', 'Untitled')}**\n"
                    if task.get('description'):
                        response_text += f"   {task.get('description')}\n"
                    if task.get('due_date'):
                        response_text += f"   📅 到期: {task.get('due_date')}\n"
                    response_text += "\n"

        elif action == 'create':
            response_text = f"✅ 任务已创建：{result.get('title', 'Untitled')}"
            if result.get('due_date'):
                response_text += f"\n📅 到期时间：{result.get('due_date')}"

        elif action == 'complete':
            response_text = f"✅ 任务已完成：{result.get('title', 'Task')}"

        elif action == 'delete':
            response_text = f"🗑️ 任务已删除"

        else:
            response_text = result.get('message', '操作完成')

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
                "text": f"管理任务失败：{str(e)}"
            }]
        }


@tool(
    name="set_reminder",
    description="""Set a personal reminder for a user with automated delivery (v0.5.1).

Use this tool when:
- User wants to be reminded about something ("提醒我" or "remind me")
- User says "set reminder" or "create reminder"
- User wants to schedule a notification

The bot will save the reminder and automatically send a notification at the scheduled time.
Supports natural language times like "明天上午10点", "2小时后", or standard formats like "2025-11-03 14:30".

Returns: Confirmation that reminder was saved and will be delivered automatically.""",
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
                "text": "错误：Campfire工具未初始化。请检查数据库连接。"
            }]
        }

    try:
        # Extract parameters
        user_id = args.get('user_id')
        reminder_text = args.get('reminder_text', '')
        remind_at = args.get('remind_at', '')

        # Call underlying implementation
        result = _campfire_tools.set_reminder(
            user_id=user_id,
            reminder_text=reminder_text,
            remind_at=remind_at
        )

        # Format response
        if result.get('success'):
            response_text = f"⏰ 提醒已设置\n\n"
            response_text += f"内容: {reminder_text}\n"
            response_text += f"时间: {remind_at}\n\n"
            response_text += "注意：提醒已保存，但自动通知功能尚未实现。您可以通过查看任务列表查看提醒。"
        else:
            response_text = f"设置提醒失败：{result.get('error', '未知错误')}"

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
                "text": f"设置提醒失败：{str(e)}"
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
                "text": "错误：Campfire工具未初始化。请检查数据库连接。"
            }]
        }

    try:
        # Extract parameters
        user_id = args.get('user_id')
        title = args.get('title', '')
        content = args.get('content', '')

        # Call underlying implementation
        result = _campfire_tools.save_personal_note(
            user_id=user_id,
            title=title,
            content=content
        )

        # Format response
        if result.get('success'):
            response_text = f"📝 笔记已保存\n\n"
            response_text += f"标题: {title}\n"
            response_text += f"路径: {result.get('path', 'N/A')}\n"
            if result.get('timestamp'):
                response_text += f"时间: {result.get('timestamp')}\n"
        else:
            response_text = f"保存笔记失败：{result.get('error', '未知错误')}"

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
                "text": f"保存笔记失败：{str(e)}"
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
                "text": "错误：Campfire工具未初始化。请检查数据库连接。"
            }]
        }

    try:
        # Extract parameters
        user_id = args.get('user_id')
        query = args.get('query', '')
        max_results = args.get('max_results', 10)

        # Call underlying implementation
        notes = _campfire_tools.search_personal_notes(
            user_id=user_id,
            query=query,
            max_results=max_results
        )

        # Format response
        if not notes:
            if query:
                response_text = f"未找到包含 '{query}' 的笔记。"
            else:
                response_text = "您还没有保存任何笔记。"
        else:
            if query:
                response_text = f"找到 {len(notes)} 条相关笔记：\n\n"
            else:
                response_text = f"**最近的笔记** ({len(notes)} 条):\n\n"

            for i, note in enumerate(notes, 1):
                response_text += f"**{i}. {note.get('title', 'Untitled')}**\n"
                response_text += f"📅 {note.get('timestamp', 'Unknown date')}\n"

                # Add excerpt if available
                excerpt = note.get('excerpt', note.get('content', ''))
                if excerpt:
                    response_text += f"{excerpt[:200]}...\n"

                response_text += f"路径: {note.get('path', 'N/A')}\n\n"

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
                "text": f"搜索笔记失败：{str(e)}"
            }]
        }


