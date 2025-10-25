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
                "text": "Error: CampfireTools not initialized"
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
                "text": "Error: CampfireTools not initialized"
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
                "text": "Error: CampfireTools not initialized"
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
                "text": "Error: CampfireTools not initialized"
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
                "text": "Error: CampfireTools not initialized"
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
                "text": "Error: CampfireTools not initialized"
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
                "text": "Error: CampfireTools not initialized"
            }]
        }


