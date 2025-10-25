# Claude Agent SDK - Practical Integration Guide (Updated)
## Based on Official Documentation

**Date:** 2025-10-06
**Status:** Research Complete
**Official Docs:** https://docs.claude.com/en/api/agent-sdk/python

---

## Important Discovery

The **actual Agent SDK API** is different from our initial analysis. Here's what the real API looks like:

### Real Agent SDK API

```python
from claude_agent_sdk import query, ClaudeSDKClient, tool, create_sdk_mcp_server

# Option 1: One-off query (stateless)
async for message in query(
    prompt="Your question here",
    options=ClaudeAgentOptions(allowed_tools=["Read", "Write"])
):
    print(message)

# Option 2: Continuous session (stateful)
client = ClaudeSDKClient(options=ClaudeAgentOptions(...))
async for message in client.query("Your question"):
    print(message)
```

**vs. What we thought it was:**
```python
# THIS DOESN'T EXIST - this was conceptual
from claude_agent_sdk import Agent, Tool

agent = Agent(model="...", tools=[...])
result = await agent.run("question")
```

---

## How the Agent SDK Actually Works

### 1. Installation

```bash
pip install claude-agent-sdk
```

### 2. Basic Usage - One-off Query

```python
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    # Simple query with default options
    async for message in query("Create a Python hello world script"):
        print(message)

# Or with options
async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        permission_mode='acceptEdits'
    )

    async for message in query(
        prompt="Create a Python project structure",
        options=options
    ):
        print(message)
```

**Note:** `query()` is **streaming** - it yields messages as they come.

### 3. Continuous Session

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

# Create client for multi-turn conversation
client = ClaudeSDKClient(
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Write"],
        permission_mode='default'
    )
)

# First query
async for message in client.query("Create a file called test.py"):
    print(message)

# Follow-up query (maintains context)
async for message in client.query("Now add a main function to it"):
    print(message)

# Context is maintained between queries!
```

### 4. Custom Tools

**Define a custom tool:**

```python
from claude_agent_sdk import tool

@tool(
    name="calculate",
    description="Perform mathematical calculations",
    input_schema={
        "expression": str  # Parameter type
    }
)
async def calculate(args):
    """Calculate mathematical expression"""
    result = eval(args["expression"])  # DON'T actually use eval in production!

    return {
        "content": [{
            "type": "text",
            "text": f"Result: {result}"
        }]
    }

# Use tool in query
options = ClaudeAgentOptions(
    custom_tools=[calculate],
    allowed_tools=["calculate"]
)

async for message in query("What is 25 * 4?", options=options):
    print(message)
```

### 5. MCP Server Creation

**Create an MCP server from your tools:**

```python
from claude_agent_sdk import create_sdk_mcp_server, tool

@tool("get_time", "Get current time", {})
async def get_time(args):
    from datetime import datetime
    return {"content": [{"type": "text", "text": str(datetime.now())}]}

@tool("calculate", "Calculate expression", {"expression": str})
async def calculate(args):
    result = eval(args["expression"])
    return {"content": [{"type": "text", "text": f"Result: {result}"}]}

# Create MCP server from tools
my_server = create_sdk_mcp_server(
    name="utilities",
    version="1.0.0",
    tools=[calculate, get_time]
)

# Use MCP server in agent
options = ClaudeAgentOptions(
    mcp_servers={"utils": my_server},
    allowed_tools=["mcp__utils__calculate", "mcp__utils__get_time"]
)

async for message in query("What time is it?", options=options):
    print(message)
```

**Note:** MCP tools are prefixed with `mcp__<server_name>__<tool_name>`

---

## How to Integrate with Campfire

### Current Implementation (Direct API)

```python
# src/app.py (current)
from anthropic import Anthropic

agent = Anthropic(api_key=api_key)
response = agent.messages.create(
    model="claude-3-5-haiku-20241022",
    messages=[{"role": "user", "content": context_message}]
)
```

### Option A: Simple Agent SDK Integration

```python
# src/app.py (with Agent SDK - simple)
from claude_agent_sdk import query, ClaudeAgentOptions

async def process_webhook(content: str, bot_config):
    """Process webhook with Agent SDK"""

    options = ClaudeAgentOptions(
        model=bot_config.model,
        system_prompt=bot_config.system_prompt,
        allowed_tools=[],  # No custom tools yet
        permission_mode='default'
    )

    # Stream response
    response_text = ""
    async for message in query(prompt=content, options=options):
        response_text += message  # Accumulate streaming response

    return response_text
```

### Option B: Agent SDK with Custom Campfire Tools

```python
# src/campfire_agent.py (new file)
from claude_agent_sdk import tool, ClaudeSDKClient, ClaudeAgentOptions
from tools.campfire_tools import CampfireTools

# Initialize Campfire tools
campfire_tools_instance = CampfireTools(
    db_path="./tests/fixtures/test.db",
    context_dir="./user_contexts"
)

# Define custom tools for Agent SDK
@tool(
    name="search_conversations",
    description="Search through Campfire conversation history. Use this when user asks about past discussions or previous decisions.",
    input_schema={
        "query": str,
        "room_id": int,  # Optional will be handled in function
        "limit": int
    }
)
async def search_conversations_tool(args):
    """Search Campfire conversations"""
    results = campfire_tools_instance.search_conversations(
        query=args["query"],
        room_id=args.get("room_id"),
        limit=args.get("limit", 10)
    )

    # Format results for Claude
    formatted = "Found conversations:\n"
    for msg in results:
        formatted += f"- [{msg['creator_name']}] in {msg['room_name']}: {msg['body']}\n"

    return {
        "content": [{
            "type": "text",
            "text": formatted
        }]
    }


@tool(
    name="get_user_context",
    description="Get user preferences, room memberships, and conversation history",
    input_schema={"user_id": int}
)
async def get_user_context_tool(args):
    """Get user context"""
    context = campfire_tools_instance.get_user_context(args["user_id"])

    formatted = f"User: {context.get('user_name')}\n"
    formatted += f"Email: {context.get('email')}\n"
    formatted += f"Rooms: {', '.join([r['room_name'] for r in context.get('rooms', [])])}\n"

    if context.get('preferences'):
        formatted += f"Preferences: {context['preferences']}\n"

    return {
        "content": [{
            "type": "text",
            "text": formatted
        }]
    }


# Create Campfire Agent class
class CampfireAgent:
    """Agent SDK wrapper for Campfire bots"""

    def __init__(self, bot_config):
        self.bot_config = bot_config
        self.client = None

    def _create_client(self):
        """Create Agent SDK client"""
        options = ClaudeAgentOptions(
            model=self.bot_config.model,
            system_prompt=self.bot_config.system_prompt,
            custom_tools=[
                search_conversations_tool,
                get_user_context_tool
            ],
            allowed_tools=[
                "search_conversations",
                "get_user_context"
            ],
            permission_mode='default'
        )

        return ClaudeSDKClient(options=options)

    async def process_message(self, content: str, context: dict):
        """Process a message with context"""

        # Create client if needed
        if not self.client:
            self.client = self._create_client()

        # Build prompt with context
        prompt = f"""User: {context['user_name']} (ID: {context['user_id']})
Room: {context['room_name']} (ID: {context['room_id']})

Message: {content}"""

        # Query agent (streaming)
        response_text = ""
        async for message in self.client.query(prompt):
            response_text += message

        return response_text


# Usage in app.py
@app.route('/webhook', methods=['POST'])
async def webhook():
    # ... validate payload ...

    # Get bot config
    bot_config = bot_manager.get_bot_by_id(bot_id) or bot_manager.get_default_bot()

    # Create agent
    agent = CampfireAgent(bot_config)

    # Process message
    response = await agent.process_message(
        content=content,
        context={
            'user_id': user_id,
            'user_name': user_name,
            'room_id': room_id,
            'room_name': room_name
        }
    )

    # Post response
    post_to_campfire(room_id, response)

    return jsonify({'status': 'success'})
```

---

## Subagents in Agent SDK

**Key Finding:** The official docs don't explicitly show subagent API.

However, based on research:
- Subagents are enabled through the `Task` tool
- They're part of Claude Code's built-in tool set
- They're automatically available when using full Agent SDK

**Theoretical usage:**
```python
options = ClaudeAgentOptions(
    allowed_tools=["Task"],  # Enable subagents
    # Task tool allows agent to spawn parallel sub-tasks
)

# Agent can now say: "I'll use the Task tool to process this in parallel"
```

**In Campfire context:**
User asks: "Analyze Q3 revenue by region and create report"

Agent thinks:
1. "I need to search for Q3 data" → spawns Task 1
2. "I need to analyze by region" → spawns Task 2
3. "I need to create visualizations" → spawns Task 3
4. Tasks run in parallel
5. Main agent synthesizes results

---

## MCP Servers in Campfire

### Option 1: Create Campfire MCP Server

**Allow other AI agents to access Campfire data:**

```python
# campfire_mcp_server.py
from claude_agent_sdk import create_sdk_mcp_server, tool
from tools.campfire_tools import CampfireTools

tools_instance = CampfireTools(...)

@tool("campfire_search", "Search Campfire messages", {"query": str})
async def search(args):
    results = tools_instance.search_conversations(args["query"])
    return {"content": [{"type": "text", "text": str(results)}]}

@tool("campfire_user_info", "Get user information", {"user_id": int})
async def user_info(args):
    context = tools_instance.get_user_context(args["user_id"])
    return {"content": [{"type": "text", "text": str(context)}]}

# Create MCP server
campfire_mcp = create_sdk_mcp_server(
    name="campfire",
    version="1.0.0",
    tools=[search, user_info]
)

# Now any Claude agent can use:
# mcp__campfire__campfire_search
# mcp__campfire__campfire_user_info
```

### Option 2: Use External MCP Servers in Campfire Bot

**Let your bot access external services:**

```python
from claude_agent_sdk import ClaudeAgentOptions

# Configure external MCP servers
options = ClaudeAgentOptions(
    mcp_servers={
        "postgres": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-postgres"],
            "env": {"DATABASE_URL": "postgresql://..."}
        },
        "slack": {
            "transport": "http",
            "url": "https://mcp.slack.com",
            "auth": {"token": "xoxb-..."}
        }
    },
    allowed_tools=[
        "mcp__postgres__query",
        "mcp__slack__search_messages"
    ]
)

# Now your financial bot can:
# - Query PostgreSQL financial database
# - Search Slack for context
# All through standardized MCP protocol
```

---

## Comparison: What We Have vs. What We Could Have

### Current (Direct API)

**Pros:**
- ✅ Simple and working
- ✅ Full control
- ✅ Lower cost per request
- ✅ No additional dependencies

**Cons:**
- ❌ Manual context management
- ❌ No tool framework
- ❌ No subagents
- ❌ No MCP integration
- ❌ More code to maintain

### With Agent SDK

**Pros:**
- ✅ Built-in tool framework
- ✅ Streaming responses
- ✅ Potential subagent support
- ✅ MCP integration ready
- ✅ Context management handled
- ✅ Less code to maintain

**Cons:**
- ❌ Additional dependency
- ❌ Slightly higher cost (tool use overhead)
- ❌ Less direct control
- ❌ API not as documented in our initial analysis

---

## Recommendation

### For Now: Keep Direct API ✅

**Reasons:**
1. Current implementation works well
2. Agent SDK API is different from what we planned
3. Simple use case doesn't need complex framework
4. Lower cost

### Migrate to Agent SDK When:

1. **Need custom tools** - When you want agent to autonomously search/retrieve data
2. **Complex workflows** - Multi-step tasks that benefit from agent reasoning
3. **External integrations** - Want to connect to databases, Slack, etc via MCP
4. **Parallel processing** - Tasks that can be split and run simultaneously

### Migration Path

**Phase 1:** Add one simple custom tool
```python
@tool("search_conversations", "...", {...})
async def search(args): ...
```

**Phase 2:** Switch webhook handler to Agent SDK
```python
agent = CampfireAgent(bot_config)
response = await agent.process_message(content, context)
```

**Phase 3:** Add more tools as needed
**Phase 4:** Enable MCP servers for external integrations
**Phase 5:** Explore subagents for complex tasks

---

## Practical Next Steps

1. **Test current system in production** - Validate it works reliably
2. **Identify bottlenecks** - Where is manual work painful?
3. **Prototype one tool** - Try Agent SDK with `search_conversations` tool
4. **Measure performance** - Compare Direct API vs. Agent SDK
5. **Decide on migration** - Based on real needs, not theory

---

## Code Examples Repository

Create `/examples/agent_sdk/` directory with:
- `01_basic_query.py` - Simple Agent SDK usage
- `02_custom_tool.py` - Custom tool definition
- `03_mcp_server.py` - MCP server creation
- `04_campfire_integration.py` - Full Campfire integration

This allows experimentation without affecting production code.

---

**Last Updated:** 2025-10-06
**Based On:** Official Agent SDK Python Documentation
