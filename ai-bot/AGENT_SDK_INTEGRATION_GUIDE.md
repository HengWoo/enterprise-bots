# Claude Agent SDK Integration Guide
## Subagents & MCP Servers for Campfire Bots

**Date:** 2025-10-06
**Status:** Planning / Research

---

## Table of Contents

1. [What is the Claude Agent SDK?](#what-is-the-claude-agent-sdk)
2. [Subagents Explained](#subagents-explained)
3. [MCP Servers Explained](#mcp-servers-explained)
4. [Integration Roadmap](#integration-roadmap)
5. [Example Implementation](#example-implementation)

---

## What is the Claude Agent SDK?

The **Claude Agent SDK** (formerly Claude Code SDK) is Anthropic's framework for building autonomous AI agents. It provides:

### Core Capabilities

1. **Agentic Search** - Built-in file system and semantic search
2. **Subagents** - Parallel task processing with isolated contexts
3. **Auto Context Management** - Handles token limits automatically
4. **Tool Framework** - Standardized tool interface
5. **MCP Integration** - Connect to external services via Model Context Protocol

### Current State vs. Agent SDK

**What we're using now:**
```python
from anthropic import Anthropic

agent = Anthropic(api_key=api_key)
response = agent.messages.create(
    model="claude-3-5-haiku-20241022",
    messages=[{"role": "user", "content": "..."}]
)
```

**With Agent SDK:**
```python
from claude_agent_sdk import Agent, Tool

agent = Agent(
    model="claude-3-5-haiku-20241022",
    tools=[search_tool, context_tool],
    enable_subagents=True,
    mcp_servers=["slack", "github"]
)

result = await agent.run("Analyze Q3 revenue trends")
```

---

## Subagents Explained

### What Are Subagents?

**Subagents** are specialized AI assistants that operate **in parallel** within the main agent. Each subagent has:

- ✅ **Isolated context window** - Doesn't pollute main agent's context
- ✅ **Custom system prompt** - Specialized for specific tasks
- ✅ **Specific tool permissions** - Only access tools it needs
- ✅ **Independent execution** - Runs in parallel with other subagents

### Why Use Subagents?

**Parallelization:**
```
Without Subagents (Sequential):
Task 1 → Task 2 → Task 3 → Task 4
(10s)    (10s)    (10s)    (10s)
Total: 40 seconds

With Subagents (Parallel):
Task 1 ┐
Task 2 ├→ All run simultaneously
Task 3 │
Task 4 ┘
Total: ~10 seconds (fastest task)
```

**Context Efficiency:**
- Each subagent maintains its own focused conversation
- Only sends relevant results back to orchestrator
- Main agent doesn't get overwhelmed with details

**Specialization:**
- Different subagents can have different personalities
- One subagent for data extraction, another for analysis, another for visualization

### Real-World Example: Financial Analysis

**User asks:** "Analyze Q3 revenue by region and create a summary report"

**Without Subagents:**
```
Main Agent:
1. Search conversation history for Q3 data
2. Extract revenue numbers
3. Calculate regional breakdowns
4. Analyze trends
5. Format report
6. Generate charts
Time: ~60 seconds, 15K tokens
```

**With Subagents:**
```
Main Agent (Orchestrator):
├─ Subagent 1: "Search for Q3 revenue data"
│  └─ Returns: Raw data (2K tokens)
│
├─ Subagent 2: "Analyze regional trends"
│  └─ Returns: Analysis (1K tokens)
│
├─ Subagent 3: "Generate visualizations"
│  └─ Returns: Chart data (500 tokens)
│
└─ Main Agent: Synthesize into final report

Time: ~20 seconds, 8K tokens
Savings: 67% faster, 50% fewer tokens
```

### How Subagents Work

```python
from claude_agent_sdk import Agent

# Create main agent
main_agent = Agent(
    model="claude-3-5-haiku-20241022",
    system_prompt="You are a financial analyst orchestrator",
    enable_subagents=True
)

# Agent automatically spawns subagents as needed
result = await main_agent.run(
    "Analyze Q3 revenue by region and create report",
    tools=[
        search_conversations_tool,
        process_excel_tool,
        chart_generator_tool
    ]
)

# Behind the scenes:
# 1. Main agent decides: "I need 3 subagents"
# 2. Subagent 1: Search for Q3 data
# 3. Subagent 2: Process Excel files
# 4. Subagent 3: Generate charts
# 5. All run in parallel
# 6. Main agent synthesizes results
```

### Subagent Limits

- **Max parallelism:** 10 concurrent subagents
- **Batching:** Processes in batches if > 10 tasks
- **Token budget:** Each subagent has its own token limit
- **Models:** Subagents can use different models than main agent

---

## MCP Servers Explained

### What is MCP?

**Model Context Protocol (MCP)** is an open standard for connecting AI agents to external tools and services.

Think of MCP as **"USB ports for AI"** - a universal connector.

### How MCP Works

```
┌──────────────┐
│ Claude Agent │
└──────┬───────┘
       │
       ├─ MCP Server 1: Slack
       ├─ MCP Server 2: GitHub
       ├─ MCP Server 3: PostgreSQL
       ├─ MCP Server 4: Google Drive
       └─ MCP Server 5: Custom API
```

**Benefits:**
- ✅ **Standardized interface** - All integrations use same protocol
- ✅ **Automatic authentication** - Handles OAuth, API keys, etc.
- ✅ **Type safety** - Validated inputs/outputs
- ✅ **Community servers** - 100+ pre-built integrations

### MCP Server Types

**1. Stdio Servers** (Local processes)
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://localhost/mydb"
      }
    }
  }
}
```

**2. HTTP/SSE Servers** (Remote services)
```json
{
  "mcpServers": {
    "slack": {
      "url": "https://mcp.slack.com",
      "apiKey": "xoxb-your-token"
    }
  }
}
```

### Available MCP Servers (Examples)

**Enterprise Systems:**
- **Slack** - Read/send messages, search channels
- **GitHub** - Manage repos, issues, PRs
- **Google Drive** - Search, read, write documents
- **PostgreSQL** - Query databases
- **Puppeteer** - Web scraping and automation

**Developer Tools:**
- **Git** - Repository operations
- **Docker** - Container management
- **Redis** - Cache operations
- **Sentry** - Error tracking

**Custom:**
- **Your API** - Build custom MCP server for your services

### MCP for Campfire Bots

**Use Case 1: Campfire as MCP Server**
```python
# Create MCP server that exposes Campfire data
# Other AI agents can then query Campfire

mcp_server = MCPServer(
    name="campfire",
    tools=[
        "search_messages",
        "get_user_info",
        "post_message"
    ]
)

# Now any Claude agent can access Campfire:
agent.run("Check what was discussed in Finance room yesterday",
          mcp_servers=["campfire"])
```

**Use Case 2: Campfire Bot Uses MCP Servers**
```python
# Your Campfire bot can use external MCP servers

financial_bot = Agent(
    system_prompt="You are a financial analyst",
    mcp_servers=[
        "postgres",     # Query financial database
        "slack",        # Check Slack discussions
        "google-drive"  # Access financial reports
    ]
)

# Bot can now:
# - Query PostgreSQL for latest numbers
# - Check Slack for context
# - Read Google Drive spreadsheets
# All through standardized MCP protocol
```

---

## Integration Roadmap

### Phase 1: Direct API (Current) ✅

**Status:** Implemented
- Using `anthropic` library directly
- Manual context building
- Custom tool implementations
- Works but limited

**Pros:**
- ✅ Simple and direct
- ✅ Full control
- ✅ No additional dependencies

**Cons:**
- ❌ No subagents
- ❌ No MCP integration
- ❌ Manual context management
- ❌ No auto-optimization

### Phase 2: Agent SDK Basic (Next Step)

**Goal:** Switch to Agent SDK with tools

**Changes needed:**
```python
# Install Agent SDK
pip install claude-agent-sdk

# Update app.py
from claude_agent_sdk import Agent, Tool

# Wrap existing tools
campfire_tools = [
    Tool(
        name="search_conversations",
        description="Search Campfire message history",
        function=tools.search_conversations
    ),
    Tool(
        name="get_user_context",
        description="Get user preferences and history",
        function=tools.get_user_context
    )
]

# Create agent
agent = Agent(
    model=bot_config.model,
    system_prompt=bot_config.system_prompt,
    tools=campfire_tools
)

# Run (agent decides which tools to use)
result = await agent.run(user_message)
```

**Benefits:**
- ✅ Better tool orchestration
- ✅ Auto context management
- ✅ Foundation for subagents

### Phase 3: Enable Subagents

**Goal:** Add parallel processing for complex tasks

**Example: Multi-step financial analysis**

```python
agent = Agent(
    model="claude-3-5-haiku-20241022",
    system_prompt=bot_config.system_prompt,
    tools=campfire_tools,
    enable_subagents=True,  # ← Enable parallel processing
    max_subagents=5         # ← Limit concurrent subagents
)

# For complex queries, agent automatically spawns subagents
# User: "Analyze Q3 vs Q2 revenue by region and create report"
#
# Main Agent orchestrates:
# ├─ Subagent 1: Search Q3 data
# ├─ Subagent 2: Search Q2 data
# ├─ Subagent 3: Calculate regional breakdowns
# ├─ Subagent 4: Identify trends
# └─ Subagent 5: Generate visualizations
#
# All run in parallel, results synthesized by main agent
```

**Use Cases:**
- 📊 **Financial reports** - Parallel data extraction and analysis
- 📄 **Document processing** - Process multiple files simultaneously
- 🔍 **Research tasks** - Search multiple sources in parallel
- 📈 **Trend analysis** - Compare multiple time periods

### Phase 4: Add MCP Servers

**Goal:** Integrate external services

**Option A: Campfire Bot Uses MCP Servers**
```python
# Your financial analyst bot can access external data

financial_bot = Agent(
    model="claude-3-5-haiku-20241022",
    system_prompt=bot_config.system_prompt,
    tools=campfire_tools,
    enable_subagents=True,
    mcp_servers=[
        {
            "name": "postgres",
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-postgres"],
            "env": {"DATABASE_URL": "postgresql://..."}
        },
        {
            "name": "google-drive",
            "type": "http",
            "url": "https://mcp.google.com/drive",
            "auth": {"type": "oauth", "token": "..."}
        }
    ]
)

# Now bot can:
# - Query your PostgreSQL financial database
# - Read Google Drive spreadsheets
# - All automatically via MCP
```

**Option B: Build Campfire MCP Server**
```python
# Create MCP server so other AI agents can access Campfire

from mcp_sdk import MCPServer, Tool

campfire_mcp = MCPServer(
    name="campfire",
    version="1.0.0",
    description="Access Campfire chat data"
)

@campfire_mcp.tool()
def search_messages(query: str, room_id: int = None):
    """Search Campfire messages"""
    db = CampfireDBReader()
    return db.search_messages(query, room_id=room_id)

@campfire_mcp.tool()
def get_user_context(user_id: int):
    """Get user information"""
    return tools.get_user_context(user_id)

# Start MCP server (stdio or HTTP)
campfire_mcp.serve(transport="stdio")
```

**Use Cases:**
- 🗄️ **Database integration** - Query financial databases directly
- 📁 **File storage** - Access Google Drive, Dropbox, S3
- 💬 **Chat platforms** - Cross-reference Slack, Teams
- 🌐 **Web scraping** - Fetch data from websites
- 🔧 **Custom APIs** - Connect to your internal services

---

## Example Implementation

### Complete Agent SDK Example

```python
# ai-bot/src/app_with_agent_sdk.py

from claude_agent_sdk import Agent, Tool, MCPServer
from tools.campfire_tools import CampfireTools
from bot_manager import BotManager

# Initialize tools
campfire_tools = CampfireTools(
    db_path=config['CAMPFIRE_DB_PATH'],
    context_dir=config['CONTEXT_DIR']
)

# Define tools for Agent SDK
def create_agent_tools():
    """Create tools compatible with Agent SDK"""

    return [
        Tool(
            name="search_conversations",
            description="""Search through Campfire conversation history.
            Use this when user asks about past discussions, previous decisions,
            or references to earlier conversations.""",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search keywords or phrase"
                },
                "room_id": {
                    "type": "integer",
                    "description": "Optional: Limit search to specific room",
                    "optional": True
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of results to return (default: 10)",
                    "optional": True,
                    "default": 10
                }
            },
            function=campfire_tools.search_conversations
        ),

        Tool(
            name="get_user_context",
            description="""Get comprehensive information about a user including
            their preferences, room memberships, and conversation history.
            Use this to personalize responses.""",
            parameters={
                "user_id": {
                    "type": "integer",
                    "description": "User ID to look up"
                }
            },
            function=campfire_tools.get_user_context
        ),

        # More tools...
    ]


# Create agent with subagents enabled
async def create_agent(bot_config):
    """Create Agent SDK instance with bot configuration"""

    return Agent(
        model=bot_config.model,
        temperature=bot_config.temperature,
        max_tokens=bot_config.max_tokens,
        system_prompt=bot_config.system_prompt,

        # Enable subagents for complex multi-step tasks
        enable_subagents=True,
        max_subagents=5,

        # Provide tools
        tools=create_agent_tools(),

        # Auto context management
        auto_context_management=True,
        max_context_tokens=180000  # Leave buffer under 200K limit
    )


# Webhook handler
@app.route('/webhook/<bot_id>', methods=['POST'])
async def webhook(bot_id=None):
    """Process webhook with Agent SDK"""

    # ... validate payload ...

    # Get bot configuration
    bot_config = bot_manager.get_bot_by_id(bot_id) or bot_manager.get_default_bot()

    # Create agent
    agent = await create_agent(bot_config)

    # Run agent (it will autonomously decide which tools to use)
    result = await agent.run(
        message=content,
        context={
            'user_id': user_id,
            'room_id': room_id,
            'user_name': user_name,
            'room_name': room_name
        }
    )

    # Post response
    post_to_campfire(room_id, result.response)

    return jsonify({'status': 'success', 'response': result.response})
```

### With MCP Servers

```python
# Add PostgreSQL MCP server for financial data

agent = Agent(
    model="claude-3-5-haiku-20241022",
    system_prompt="You are a financial analyst with access to the company database",
    tools=create_agent_tools(),
    enable_subagents=True,

    # Add MCP servers
    mcp_servers=[
        MCPServer(
            name="postgres",
            transport="stdio",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-postgres"],
            env={
                "DATABASE_URL": "postgresql://localhost/financial_db"
            }
        ),
        MCPServer(
            name="google-drive",
            transport="http",
            url="https://mcp-server.company.com/google-drive",
            auth={"type": "bearer", "token": os.getenv("GDRIVE_TOKEN")}
        )
    ]
)

# Now when user asks: "What were our Q3 revenues?"
# Agent can:
# 1. Use search_conversations to check if it was discussed
# 2. Use postgres MCP to query financial_db directly
# 3. Use google-drive MCP to read Q3 report spreadsheet
# 4. Synthesize answer from all sources
```

---

## Decision Matrix

### Should We Migrate to Agent SDK?

| Factor | Direct API | Agent SDK | Winner |
|--------|-----------|-----------|--------|
| **Setup Complexity** | ⭐⭐⭐⭐⭐ Simple | ⭐⭐⭐ Moderate | Direct API |
| **Context Management** | ⭐⭐ Manual | ⭐⭐⭐⭐⭐ Auto | Agent SDK |
| **Parallel Processing** | ❌ None | ⭐⭐⭐⭐⭐ Subagents | Agent SDK |
| **Tool Framework** | ⭐⭐ Custom | ⭐⭐⭐⭐⭐ Built-in | Agent SDK |
| **MCP Integration** | ❌ None | ⭐⭐⭐⭐⭐ Native | Agent SDK |
| **Cost per Request** | ⭐⭐⭐⭐⭐ Lower | ⭐⭐⭐⭐ Slightly higher | Direct API |
| **Future Scalability** | ⭐⭐⭐ Limited | ⭐⭐⭐⭐⭐ Excellent | Agent SDK |
| **Development Speed** | ⭐⭐⭐ Slower | ⭐⭐⭐⭐⭐ Faster | Agent SDK |

### Recommendation

**Now:** Keep Direct API (it's working)
**Soon:** Migrate to Agent SDK when you need:
- Multi-step complex workflows
- Parallel processing
- External service integrations
- Advanced context management

---

## Next Steps

1. **Test current system in production** - Validate basic functionality works
2. **Identify complex use cases** - Which tasks would benefit from subagents?
3. **Evaluate MCP needs** - What external services do you want to integrate?
4. **Plan migration** - Create phased rollout plan
5. **Implement Agent SDK** - Start with one bot, expand gradually

---

## Resources

- [Agent SDK Documentation](https://docs.claude.com/en/api/agent-sdk/overview)
- [MCP Protocol Spec](https://modelcontextprotocol.io)
- [MCP Server Repository](https://github.com/modelcontextprotocol/servers)
- [Agent SDK Examples](https://github.com/anthropics/claude-agent-sdk/examples)

---

**Last Updated:** 2025-10-06
