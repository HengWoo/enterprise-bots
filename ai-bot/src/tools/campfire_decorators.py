"""
Campfire conversation and knowledge base tools
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
    name="search_conversations",
    description="""Search through Campfire conversation history for relevant context.

Use this tool when:
- User asks about past discussions or decisions
- Need to reference previous conversations
- Looking for specific information mentioned before
- Understanding conversation context

Returns: List of relevant messages with user names, room names, and message content.""",
    input_schema={
        "query": str,
        "room_id": int,  # Optional - will handle None in function
        "limit": int
    }
)
async def search_conversations_tool(args):
    """Search Campfire message history"""
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
        room_id = args.get('room_id')
        limit = args.get('limit', 10)

        # Call underlying implementation
        results = _campfire_tools.search_conversations(
            query=query,
            room_id=room_id,
            limit=limit
        )

        # Format response
        if not results:
            response_text = f"未找到包含 '{query}' 的消息。" if query else "未找到消息。"
        else:
            response_text = f"找到 {len(results)} 条相关消息：\n\n"
            for i, msg in enumerate(results, 1):
                response_text += f"{i}. [{msg.get('created_at', 'Unknown time')}] "
                response_text += f"{msg.get('creator_name', 'Unknown')}: "
                response_text += f"{msg.get('body', '')[:200]}...\n"
                response_text += f"   (Room: {msg.get('room_name', 'Unknown')})\n\n"

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
                "text": f"搜索失败：{str(e)}"
            }]
        }


@tool(
    name="get_user_context",
    description="""Get comprehensive information about a user including preferences, room memberships, and conversation history.

Use this tool when:
- Need to personalize responses based on user preferences
- Want to know user's expertise or interests
- Need to see what rooms user is member of
- Understanding user's context and background

Returns: User information including name, email, room memberships, preferences, and expertise areas.""",
    input_schema={
        "user_id": int
    }
)
async def get_user_context_tool(args):
    """Get user context and preferences"""
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

        # Call underlying implementation
        user_context = _campfire_tools.get_user_context(user_id=user_id)

        # Format response
        if not user_context:
            response_text = f"未找到用户 ID {user_id} 的上下文信息。"
        else:
            response_text = f"**用户信息** (ID: {user_context.get('id')})\n\n"
            response_text += f"姓名: {user_context.get('name', 'Unknown')}\n"
            response_text += f"邮箱: {user_context.get('email', 'N/A')}\n\n"

            # Room memberships
            rooms = user_context.get('rooms', [])
            if rooms:
                response_text += f"**房间成员** ({len(rooms)} 个):\n"
                for room in rooms[:10]:  # Limit to first 10
                    response_text += f"- {room.get('name', 'Unknown')}\n"
                if len(rooms) > 10:
                    response_text += f"- ...还有 {len(rooms) - 10} 个房间\n"
                response_text += "\n"

            # Preferences
            prefs = user_context.get('preferences', {})
            if prefs:
                response_text += f"**用户偏好:**\n"
                for key, value in prefs.items():
                    response_text += f"- {key}: {value}\n"
                response_text += "\n"

            # Expertise
            expertise = user_context.get('expertise', [])
            if expertise:
                response_text += f"**专业领域:** {', '.join(expertise)}\n"

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
                "text": f"获取用户上下文失败：{str(e)}"
            }]
        }


@tool(
    name="save_user_preference",
    description="""Save a user preference or setting for future reference.

Use this tool when:
- User expresses a preference (e.g., "I prefer YoY comparisons")
- User mentions their expertise or interests
- Need to remember user-specific settings
- Personalizing future interactions

Returns: Confirmation that preference was saved.""",
    input_schema={
        "user_id": int,
        "preference_key": str,
        "preference_value": str
    }
)
async def save_user_preference_tool(args):
    """Save user preference"""
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
        preference_key = args.get('preference_key')
        preference_value = args.get('preference_value')

        # Call underlying implementation
        # save_user_context expects preferences as a dict
        preferences = {preference_key: preference_value}
        _campfire_tools.save_user_context(
            user_id=user_id,
            preferences=preferences
        )

        return {
            "content": [{
                "type": "text",
                "text": f"✅ 已保存用户偏好：{preference_key} = {preference_value}"
            }]
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"保存用户偏好失败：{str(e)}"
            }]
        }


@tool(
    name="search_knowledge_base",
    description="""Search the company knowledge base for relevant documents and information.

Use this tool when:
- User asks about company policies or procedures
- Need to reference official documentation
- Looking for technical standards or guidelines
- User asks "what's our policy on..." or "how do we handle..."
- Need to verify company-specific information

The knowledge base contains:
- Financial reporting standards and policies
- Expense reimbursement procedures
- Account classification standards
- Approval workflows
- Technical guidelines

Returns: List of relevant documents with excerpts showing where the search term appears.""",
    input_schema={
        "query": str,
        "category": str,  # Optional: 'policies', 'procedures', 'technical', 'financial', or 'all'
        "max_results": int  # Optional: default 3
    }
)
async def search_knowledge_base_tool(args):
    """Search company knowledge base"""
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
        category = args.get('category')
        max_results = args.get('max_results', 3)

        # Call underlying implementation
        results = _campfire_tools.search_knowledge_base(
            query=query,
            category=category,
            max_results=max_results
        )

        # Format response
        if not results:
            response_text = f"未找到与 '{query}' 相关的知识库文档。"
        else:
            response_text = f"找到 {len(results)} 个相关文档：\n\n"
            for i, doc in enumerate(results, 1):
                response_text += f"**{i}. {doc.get('title', 'Untitled')}**\n"
                response_text += f"路径: {doc.get('path', 'N/A')}\n"
                response_text += f"分类: {doc.get('category', 'N/A')}\n"

                # Add excerpt if available
                excerpt = doc.get('excerpt', '')
                if excerpt:
                    response_text += f"摘要: {excerpt[:300]}...\n"

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
                "text": f"搜索知识库失败：{str(e)}"
            }]
        }


@tool(
    name="read_knowledge_document",
    description="""Read the full content of a specific knowledge base document.

Use this tool when:
- User asks for complete details from a policy or procedure
- Need to read the full document after finding it via search
- User asks "what does the [document name] say about..."
- Need to reference the complete document content

Returns: Full document content in markdown format with metadata.""",
    input_schema={
        "path": str  # Relative path like 'policies/financial-reporting-standards.md'
    }
)
async def read_knowledge_document_tool(args):
    """Read full knowledge base document"""
    if not _campfire_tools:
        return {
            "content": [{
                "type": "text",
                "text": "错误：Campfire工具未初始化。请检查数据库连接。"
            }]
        }

    try:
        # Extract parameters
        path = args.get('path', '')

        # Call underlying implementation
        doc = _campfire_tools.read_knowledge_document(path=path)

        # Format response
        if not doc:
            response_text = f"未找到文档：{path}"
        else:
            response_text = f"**{doc.get('title', 'Untitled')}**\n\n"
            response_text += f"路径: {doc.get('path', 'N/A')}\n"
            response_text += f"分类: {doc.get('category', 'N/A')}\n"

            # Add metadata if available
            if doc.get('author'):
                response_text += f"作者: {doc.get('author')}\n"
            if doc.get('created_at'):
                response_text += f"创建时间: {doc.get('created_at')}\n"

            response_text += "\n---\n\n"

            # Add content
            content = doc.get('content', '')
            if content:
                response_text += content
            else:
                response_text += "（文档内容为空）"

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
                "text": f"读取文档失败：{str(e)}"
            }]
        }


@tool(
    name="list_knowledge_documents",
    description="""List all available documents in the knowledge base.

Use this tool when:
- User asks "what policies do we have?"
- Need to see what documentation is available
- User wants to browse available resources
- Starting a research task and need to know what's available

Returns: List of all documents organized by category with metadata.""",
    input_schema={
        "category": str  # Optional: filter by 'policies', 'procedures', 'technical', 'financial'
    }
)
async def list_knowledge_documents_tool(args):
    """List available knowledge base documents"""
    if not _campfire_tools:
        return {
            "content": [{
                "type": "text",
                "text": "错误：Campfire工具未初始化。请检查数据库连接。"
            }]
        }

    try:
        # Extract parameters
        category = args.get('category')

        # Call underlying implementation
        docs = _campfire_tools.list_knowledge_documents(category=category)

        # Format response
        if not docs:
            if category:
                response_text = f"未找到 '{category}' 分类下的文档。"
            else:
                response_text = "知识库中没有文档。"
        else:
            if category:
                response_text = f"**{category}** 分类下的文档 ({len(docs)} 个):\n\n"
            else:
                response_text = f"**知识库文档** ({len(docs)} 个):\n\n"

            # Group by category
            by_category = {}
            for doc in docs:
                cat = doc.get('category', 'uncategorized')
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(doc)

            # Display by category
            for cat, cat_docs in sorted(by_category.items()):
                response_text += f"**{cat.upper()}**\n"
                for doc in cat_docs:
                    response_text += f"- {doc.get('title', 'Untitled')}\n"
                    response_text += f"  路径: {doc.get('path', 'N/A')}\n"
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
                "text": f"列出文档失败：{str(e)}"
            }]
        }


@tool(
    name="store_knowledge_document",
    description="""Create and store a new document in the knowledge base.

Use this tool when:
- User wants to document a new policy or procedure
- Creating official company documentation
- User says "let's document this" or "we should record this policy"
- Storing important decisions or standards

IMPORTANT: This creates official company documentation. Only use when:
- User explicitly requests to create documentation
- The information is meant to be preserved as official policy
- You have verified the content with the user

Returns: Confirmation with the path to the new document.""",
    input_schema={
        "category": str,  # Must be: 'policies', 'procedures', 'technical', or 'financial'
        "title": str,
        "content": str,  # Markdown formatted content
        "author": str  # Optional: author name
    }
)
async def store_knowledge_document_tool(args):
    """Store new document to knowledge base"""
    if not _campfire_tools:
        return {
            "content": [{
                "type": "text",
                "text": "错误：Campfire工具未初始化。请检查数据库连接。"
            }]
        }

    try:
        # Extract parameters
        category = args.get('category', '')
        title = args.get('title', '')
        content = args.get('content', '')
        author = args.get('author')

        # Call underlying implementation
        result = _campfire_tools.store_knowledge_document(
            category=category,
            title=title,
            content=content,
            author=author
        )

        # Format response
        if result and result.get('success'):
            response_text = f"✅ 文档已保存到知识库\n\n"
            response_text += f"标题: {title}\n"
            response_text += f"分类: {category}\n"
            response_text += f"路径: {result.get('path', 'N/A')}\n"
            if author:
                response_text += f"作者: {author}\n"
        else:
            response_text = f"保存文档失败：{result.get('error', '未知错误')}"

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
                "text": f"保存文档失败：{str(e)}"
            }]
        }


