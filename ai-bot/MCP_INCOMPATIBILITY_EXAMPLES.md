# MCP Incompatibility: Agent SDK vs Direct Messages API

**Concrete Code Examples Showing Why They Can't Work Together**

---

## The Fundamental Architecture Difference

### How Agent SDK Uses MCPs (What We Have)

**Our Current Code (src/campfire_agent.py:118-143):**

```python
# Agent SDK MCP Configuration
mcp_servers = {
    # SDK-based MCP (in-process)
    "campfire": campfire_mcp_server,  # Already running in our process

    # External MCP (subprocess)
    "fin-report-agent": {
        "transport": "stdio",
        "command": "uv",
        "args": [
            "run",
            "--directory",
            "/app/financial-mcp",
            "python",
            "run_mcp_server.py"
        ]
    }
}

# SDK spawns and manages these
options = ClaudeAgentOptions(
    mcp_servers=mcp_servers,  # SDK handles everything
    ...
)

client = ClaudeSDKClient(options=options)
```

**What Happens Under the Hood:**

```python
# Inside ClaudeSDKClient (conceptual - actual code is in SDK)
class ClaudeSDKClient:
    def __init__(self, options):
        # 1. Spawn Claude CLI subprocess
        self.cli_process = subprocess.Popen([
            options.cli_path or "claude",
            "--model", options.model,
            "--mcp-servers", json.dumps(options.mcp_servers),  # Pass to CLI
            ...
        ])

        # 2. CLI subprocess starts MCP server subprocesses
        # For "fin-report-agent":
        #   - CLI runs: uv run --directory /app/financial-mcp python run_mcp_server.py
        #   - Creates stdin/stdout pipes for JSON-RPC communication
        #   - MCP server starts listening

        # 3. CLI queries each MCP server
        for server_name, server_config in options.mcp_servers.items():
            # CLI sends JSON-RPC request to MCP server via stdin:
            mcp_stdin.write(json.dumps({
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 1
            }))

            # MCP server responds via stdout with tool list:
            response = json.loads(mcp_stdout.readline())
            # {
            #   "jsonrpc": "2.0",
            #   "result": {
            #     "tools": [
            #       {"name": "get_excel_info", "description": "...", "inputSchema": {...}},
            #       {"name": "analyze_excel", "description": "...", "inputSchema": {...}}
            #     ]
            #   }
            # }

            # CLI registers these tools with Claude API
            self.available_tools.extend(response["result"]["tools"])

    async def send_message(self, user_message):
        # 4. When Claude calls a tool
        # Claude API returns: {"type": "tool_use", "name": "get_excel_info", "input": {...}}

        # 5. CLI routes to appropriate MCP server via stdin:
        mcp_stdin.write(json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_excel_info",
                "arguments": {...}
            }
        }))

        # 6. MCP server executes and responds via stdout:
        result = json.loads(mcp_stdout.readline())
        # {"jsonrpc": "2.0", "result": {"content": [{"type": "text", "text": "..."}]}}

        # 7. CLI sends result back to Claude API
        return result
```

**Key Point:** MCPs are **live subprocess connections** managed by CLI. The CLI maintains stdin/stdout pipes to each MCP server for bidirectional JSON-RPC communication.

---

### How Direct Messages API Uses Tools (Incompatible)

**What Direct API Expects:**

```python
import anthropic

client = anthropic.Anthropic(api_key=API_KEY)

# Direct API needs STATIC tool definitions (no subprocesses)
tools = [
    {
        "name": "get_excel_info",
        "description": "Get Excel file structure and metadata",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to Excel file"}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "analyze_excel",
        "description": "Analyze Excel data and calculate metrics",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "metrics": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["file_path", "metrics"]
        }
    }
]

# API call with static tool definitions
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    tools=tools,  # Static JSON schemas
    messages=[{"role": "user", "content": "Analyze this Excel file"}]
)

# When Claude calls a tool:
if response.stop_reason == "tool_use":
    tool_use = response.content[0]

    # WE must implement the tool execution ourselves
    if tool_use.name == "get_excel_info":
        result = get_excel_info_implementation(tool_use.input["file_path"])
    elif tool_use.name == "analyze_excel":
        result = analyze_excel_implementation(
            tool_use.input["file_path"],
            tool_use.input["metrics"]
        )

    # Send result back in next API call
    response2 = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        tools=tools,
        messages=[
            {"role": "user", "content": "Analyze this Excel file"},
            {"role": "assistant", "content": response.content},
            {
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result
                }]
            }
        ]
    )
```

**Key Point:** Direct API requires **static tool schemas** and **manual tool execution** in Python. There are no subprocesses, no stdin/stdout pipes, no JSON-RPC.

---

## The Incompatibility in Detail

### Problem 1: Tool Definition Format

**Agent SDK (MCP Servers):**
```python
# MCP server defines tools via JSON-RPC protocol
# The server is a RUNNING PROCESS

# Example: financial-mcp/run_mcp_server.py
from mcp.server import Server
from mcp import StdioServerTransport

server = Server("fin-report-agent")

@server.call_tool()
async def get_excel_info(arguments: dict) -> list[TextContent]:
    """Tool implementation in MCP server process"""
    file_path = arguments["file_path"]
    # Read Excel file
    info = extract_excel_info(file_path)
    return [TextContent(type="text", text=json.dumps(info))]

# Server runs continuously, waiting for JSON-RPC calls
async def main():
    async with StdioServerTransport() as transport:
        await server.run(transport)
```

**Direct Messages API:**
```python
# Tools are just JSON schemas (no implementation)
tools = [
    {
        "name": "get_excel_info",
        "description": "...",
        "input_schema": {...}
        # NO implementation - that's YOUR job!
    }
]

# You must implement execution separately
def execute_tool(tool_name, arguments):
    if tool_name == "get_excel_info":
        return extract_excel_info(arguments["file_path"])
    # Manual routing
```

**Why Incompatible:** MCP servers are processes with implementations. Direct API tools are schemas without implementations. Can't convert between them automatically.

---

### Problem 2: Communication Channel

**Agent SDK (MCP via CLI):**
```
Your Python Code
    ↓
ClaudeSDKClient (Python)
    ↓
Claude CLI subprocess (Rust binary)
    ↓ JSON-RPC via stdin/stdout
MCP Server subprocess (Python/Node/etc)
    ↓ Tool execution
Result via stdout → CLI → SDK → Your code
```

**Direct Messages API:**
```
Your Python Code
    ↓
HTTP POST to api.anthropic.com
    ↓
Claude API (Anthropic's servers)
    ↓ Returns tool_use
Your Python Code (YOU execute tool)
    ↓
HTTP POST result back to API
```

**Why Incompatible:** SDK uses local subprocesses with stdin/stdout. Direct API uses HTTP requests to cloud. Can't mix these communication channels.

---

### Problem 3: Tool Execution Location

**Agent SDK MCP:**
```python
# Tool runs in MCP server subprocess
# Example: fin-report-agent runs in its own process

Process Tree:
python app_fastapi.py (PID 1000)
  └─ ClaudeSDKClient spawns:
      └─ claude CLI (PID 1001)
          ├─ MCP: campfire (in-process, PID 1001)
          └─ MCP: fin-report-agent (PID 1002)
              └─ Executes get_excel_info()
```

**Direct Messages API:**
```python
# Tools run in YOUR Python process
# No subprocesses involved

Process Tree:
python app_fastapi.py (PID 1000)
  └─ Makes HTTP request to api.anthropic.com
  └─ Receives tool_use response
  └─ Executes tool in same process (PID 1000)
  └─ Makes another HTTP request with result
```

**Why Incompatible:** SDK MCPs run in separate processes. Direct API tools run in your process. Can't have the same tool implementation run in both locations simultaneously.

---

## Concrete Example: Why Hybrid Fails

### Attempt 1: Use SDK MCPs with Direct API

```python
import anthropic
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

# Try to use SDK MCPs
sdk_options = ClaudeAgentOptions(
    mcp_servers={
        "campfire": campfire_mcp_server,
        "fin-report-agent": {...}
    }
)
sdk_client = ClaudeSDKClient(options=sdk_options)
# SDK spawns MCP subprocesses managed by CLI

# Now try to use Direct API
direct_client = anthropic.Anthropic(api_key=API_KEY)

# ❌ PROBLEM: Direct API has no access to SDK's MCP subprocesses!
response = direct_client.messages.create(
    model="claude-sonnet-4-5-20250929",
    tools=[???],  # How do we reference SDK's MCP tools here?
    messages=[...]
)
```

**The Problem:**
- SDK's MCP servers are running in CLI subprocess (PID 1001, 1002)
- Direct API client only knows how to make HTTP requests
- Direct API has no way to communicate with SDK's MCP subprocesses
- **They're in different processes with no shared communication channel**

---

### Attempt 2: Convert MCP to Direct API Tools

```python
# Extract tool schemas from MCP
def extract_mcp_tools(mcp_servers):
    """Try to convert MCP servers to Direct API tool format"""
    tools = []

    for server_name, server_config in mcp_servers.items():
        # ❌ PROBLEM 1: How do we query MCP server for tool list?
        # We'd need to:
        # 1. Spawn the MCP server subprocess ourselves
        # 2. Set up stdin/stdout pipes
        # 3. Send JSON-RPC tools/list request
        # 4. Parse response
        # This is duplicating what SDK CLI already does!

        mcp_tools = query_mcp_server_for_tools(server_config)  # Complex!

        for mcp_tool in mcp_tools:
            tools.append({
                "name": mcp_tool["name"],
                "description": mcp_tool["description"],
                "input_schema": mcp_tool["inputSchema"]
            })

    return tools

# Now use Direct API
tools = extract_mcp_tools(mcp_servers)

response = direct_client.messages.create(
    model="claude-sonnet-4-5-20250929",
    tools=tools,  # ✅ We have schemas
    messages=[...]
)

# ❌ PROBLEM 2: When Claude calls a tool, how do we execute it?
if response.stop_reason == "tool_use":
    tool_use = response.content[0]

    # We need to:
    # 1. Figure out which MCP server has this tool
    # 2. Send JSON-RPC tools/call request to that server
    # 3. Wait for response
    # 4. Extract result

    # But the MCP server is running in SDK's CLI subprocess!
    # We have no pipe to communicate with it!

    # Would need to DUPLICATE the MCP server:
    # - Spawn our own instance
    # - Manage our own pipes
    # - Implement our own JSON-RPC client
    # This is 2-3 weeks of work!
```

---

### Attempt 3: Reimplement All MCPs as Native Functions

**What Would Be Required:**

```python
# Current: MCP server (separate process)
# financial-mcp/run_mcp_server.py
@server.call_tool()
async def get_excel_info(arguments: dict):
    file_path = arguments["file_path"]
    return extract_excel_info(file_path)

# Would need: Native Python implementation
async def get_excel_info_native(file_path: str) -> dict:
    """Reimplemented for Direct API"""
    # Copy-paste all MCP server logic here
    # Lose benefits of MCP architecture (external servers, hot reload, etc.)
    return extract_excel_info(file_path)

# Then register with Direct API
tools = [
    {
        "name": "get_excel_info",
        "description": "...",
        "input_schema": {...}
    },
    # ... all 9 MCP tools reimplemented
]

# Manual tool execution
def execute_tool(name, arguments):
    if name == "get_excel_info":
        return await get_excel_info_native(arguments["file_path"])
    elif name == "search_conversations":
        return await search_conversations_native(arguments["query"])
    # ... 9 tools × manual routing = lots of code
```

**Effort Estimate:**
- Reimplement 9 MCP tools as native functions: ~1 week
- Build tool execution router: ~2 days
- Handle tool execution errors: ~2 days
- Test all tools: ~3 days
- **Total: 2-3 weeks**

**What We Lose:**
- MCP architecture benefits (external servers, hot reload)
- Separation of concerns (tools in dedicated servers)
- stdio transport (simple, reliable)
- Community MCP servers (can't reuse)

---

## Why This Matters for Skills

**If we use Direct API for skills:**

```python
# Upload skills
skill_ids = upload_skills_to_api()

# Use Direct API
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    skills=skill_ids,  # ✅ Skills work
    tools=[???],       # ❌ No MCPs - must reimplement all 9 tools
    messages=[...]
)
```

**The Tradeoff:**
- ✅ Get skills support (progressive disclosure, token optimization)
- ❌ Lose all MCPs (must reimplement 9 tools as native functions)
- ❌ 2-3 weeks of work
- ❌ Lose SDK benefits (sessions, hooks, permissions)

**Not worth it!**

---

## Summary: The Fundamental Incompatibility

| Aspect | Agent SDK MCPs | Direct API Tools |
|--------|---------------|------------------|
| **Format** | Live subprocess processes | Static JSON schemas |
| **Communication** | stdin/stdout pipes (local) | HTTP requests (cloud) |
| **Execution** | In MCP server subprocess | In your Python process |
| **Management** | Claude CLI manages lifecycle | You manage everything |
| **Implementation** | Server code with @decorators | Manual routing function |
| **Architecture** | Distributed (multiple processes) | Monolithic (one process) |

**Conclusion:** They're fundamentally different architectures. Like trying to plug a USB-C cable into a lightning port - they just don't fit together.

---

## The Only Way to Mix Them

**Reimplement everything as native functions:**

```python
# Before (SDK + MCPs): Clean architecture
mcp_servers = {"campfire": ..., "financial": ...}
options = ClaudeAgentOptions(mcp_servers=mcp_servers)
# SDK handles everything

# After (Direct API): Manual everything
tools = [...]  # 9 tool schemas
response = client.messages.create(tools=tools, ...)
if response.stop_reason == "tool_use":
    result = manual_tool_router(response.content[0])  # Your code
    # Continue conversation with result
```

**Effort:** 2-3 weeks
**Maintenance:** Ongoing (can't use MCP updates)
**Benefit:** Skills support (progressive disclosure)

**Is it worth it?** NO - better to use manual skill content (+$7.50/month, 2-3 hours work).
