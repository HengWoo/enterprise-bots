# Integrating Financial Report Agent MCP with Campfire Bot

## Overview

You have TWO separate MCP servers that can work together:

1. **Campfire MCP** (`campfire`) - Conversation search, user context, preferences
2. **Financial Report Agent MCP** (`fin-report-agent`) - Excel analysis, financial calculations, insights

Both can be used by the same Campfire bot simultaneously!

---

## Your Financial Report Agent MCP

**Location:** `/Users/heng/Development/campfire/` (different repo)

**Tools Available (15+ tools):**

### Simple Tools
- `read_excel_region` - Extract rectangular cell regions
- `search_in_excel` - Search for text/patterns in Excel
- `get_excel_info` - Get workbook structure (sheets, dimensions)
- `calculate` - Mathematical calculations
- `show_excel_visual` - Visual representation of Excel structure

### Navigation Tools
- `find_account` - Search for account names in financial reports
- `get_account_hierarchy` - Get parent/child account relationships
- `get_child_accounts` - Get all child accounts

### Thinking Tools
- `think_about_financial_data` - Reflect on collected data
- `suggest_next_steps` - Suggest analysis actions
- `ask_clarification_question` - Ask user for clarity

### Memory Tools
- `save_analysis_insight` - Store insights for session
- `recall_analysis_insights` - Retrieve saved insights
- `clear_session_memory` - Clear session data

### Complex Analysis
- `adaptive_financial_analysis` - Full AI-powered analysis
- `parse_excel` - Parse financial statements with column intelligence

---

## How to Connect Both MCP Servers

### Option 1: External MCP Server (stdio) - Recommended

Your financial MCP runs as separate process, Claude Code CLI connects to it:

```python
# src/campfire_agent.py

def _create_client(self):
    # Create Campfire MCP (SDK-based)
    campfire_mcp = create_sdk_mcp_server(
        name="campfire",
        version="1.0.0",
        tools=AGENT_TOOLS
    )

    # Connect to external Financial MCP (stdio)
    options = ClaudeAgentOptions(
        model=self.bot_config.model,
        system_prompt=self.bot_config.system_prompt,
        mcp_servers={
            # Local SDK MCP
            "campfire": campfire_mcp,

            # External stdio MCP
            "fin-report-agent": {
                "transport": "stdio",
                "command": "python",
                "args": ["/Users/heng/Development/campfire/run_mcp_server.py"]
            }
        },
        allowed_tools=[
            # Campfire tools
            "mcp__campfire__search_conversations",
            "mcp__campfire__get_user_context",
            "mcp__campfire__save_user_preference",

            # Financial tools
            "mcp__fin-report-agent__read_excel_region",
            "mcp__fin-report-agent__search_in_excel",
            "mcp__fin-report-agent__parse_excel",
            "mcp__fin-report-agent__find_account",
            "mcp__fin-report-agent__adaptive_financial_analysis",
            # ... all 15 tools available!
        ]
    )

    self.client = ClaudeSDKClient(options=options)
```

### Option 2: Import Financial Tools Directly

Copy financial tool handlers into your Campfire bot:

```python
# src/financial_tools.py (new file - copied from fin-report-agent)

from claude_agent_sdk import tool
from pathlib import Path
import openpyxl

@tool(
    name="read_excel_region",
    description="Extract rectangular region from Excel file",
    input_schema={
        "file_path": str,
        "start_row": int,
        "end_row": int,
        "start_col": int,
        "end_col": int
    }
)
async def read_excel_region_tool(args):
    # Implementation from fin-report-agent
    file_path = args["file_path"]
    # ... Excel reading logic ...
    return {"content": [{"type": "text", "text": result}]}

# ... copy other tools ...

FINANCIAL_TOOLS = [read_excel_region_tool, ...]
```

```python
# src/campfire_agent.py

from agent_tools import AGENT_TOOLS
from financial_tools import FINANCIAL_TOOLS

def _create_client(self):
    # Combine all tools
    all_tools = AGENT_TOOLS + FINANCIAL_TOOLS

    combined_mcp = create_sdk_mcp_server(
        name="campfire_financial",
        version="1.0.0",
        tools=all_tools
    )

    options = ClaudeAgentOptions(
        mcp_servers={"campfire_financial": combined_mcp},
        allowed_tools=[
            "mcp__campfire_financial__search_conversations",
            "mcp__campfire_financial__get_user_context",
            "mcp__campfire_financial__read_excel_region",
            # ... all tools
        ]
    )
```

---

## Example Usage in Campfire

### Scenario: User uploads Excel financial report

```
User in Campfire: "@财务分析师 帮我分析这份Q3财报"
[Attaches: Q3_财报.xlsx]

Campfire webhook → Flask → CampfireAgent → Claude Code CLI

Agent's Thought Process:
1. Get user context
   → uses mcp__campfire__get_user_context
   → "WU HENG, Finance Team room, prefers Chinese"

2. Parse uploaded Excel file
   → uses mcp__fin-report-agent__parse_excel
   → Returns: Revenue, expenses, accounts with column intelligence

3. Search for Q2 comparison context
   → uses mcp__campfire__search_conversations(query="Q2")
   → Finds: "Q2 revenue was $2M"

4. Perform financial analysis
   → uses mcp__fin-report-agent__adaptive_financial_analysis
   → Returns: Full insights

5. Respond in Chinese with comparison
   "Q3营收$2.3M，同比增长12%。相比Q2增长15%..."
```

---

## Recommended Integration Strategy

**For Financial Analyst Bot:**

Use **Option 1** (External MCP) because:

✅ Your financial MCP is already built and working
✅ Keeps code separation (easier to maintain)
✅ Can update financial MCP independently
✅ No code duplication
✅ Financial MCP has complex dependencies (parsers, validators, etc.)

**Steps:**

1. **Update CampfireAgent** to connect to external MCP (see Option 1 code)

2. **Configure allowed tools** based on bot type:
   ```python
   # financial_analyst bot gets ALL tools
   if self.bot_config.bot_id == "financial_analyst":
       allowed_tools = [
           "mcp__campfire__*",  # All Campfire tools
           "mcp__fin-report-agent__*"  # All financial tools
       ]
   else:
       # Other bots only get Campfire tools
       allowed_tools = ["mcp__campfire__*"]
   ```

3. **Handle file uploads** from Campfire:
   - Extract file path from webhook
   - Pass to financial tools

4. **Test integration** with real Excel file

---

## Bot-Specific Tool Access

Different bots can have different tool access:

```python
# src/campfire_agent.py

def _get_allowed_tools(self):
    """Get allowed tools based on bot configuration"""

    # Base tools (all bots)
    base_tools = [
        "mcp__campfire__search_conversations",
        "mcp__campfire__get_user_context",
        "mcp__campfire__save_user_preference"
    ]

    # Financial tools (only for financial_analyst bot)
    if self.bot_config.bot_id == "financial_analyst":
        financial_tools = [
            "mcp__fin-report-agent__read_excel_region",
            "mcp__fin-report-agent__search_in_excel",
            "mcp__fin-report-agent__parse_excel",
            "mcp__fin-report-agent__find_account",
            "mcp__fin-report-agent__adaptive_financial_analysis",
            "mcp__fin-report-agent__calculate",
            # ... all 15 tools
        ]
        return base_tools + financial_tools

    # Technical assistant could have different tools
    elif self.bot_config.bot_id == "technical_assistant":
        # Could add code analysis MCP tools here
        return base_tools

    # Default bots
    return base_tools
```

---

## File Attachment Handling

Campfire webhook includes file attachments. You need to:

1. **Extract attachment from webhook payload**
2. **Save to temporary location**
3. **Pass file path to financial tools**

```python
# src/app.py

@app.route('/webhook', methods=['POST'])
async def webhook(bot_id=None):
    payload = request.get_json()

    # Check for attachments
    attachments = payload.get('attachments', [])
    file_paths = []

    for attachment in attachments:
        # Download file from Campfire
        file_url = attachment['download_url']
        file_name = attachment['filename']

        # Save to temp location
        temp_path = f"/tmp/campfire_files/{file_name}"
        # Download and save...
        file_paths.append(temp_path)

    # Pass file paths to agent
    response = await agent.process_message(
        content=content,
        context={
            'user_id': user_id,
            'room_id': room_id,
            'file_paths': file_paths  # New!
        }
    )
```

---

## Next Steps

1. ✅ Test current Campfire MCP integration (Tests 1 & 2 passed)
2. ⏳ Add financial MCP connection to CampfireAgent
3. ⏳ Configure tool access per bot type
4. ⏳ Add file attachment handling
5. ⏳ Test with real Excel file upload

**Would you like me to implement Option 1 now?**

---

**Last Updated:** 2025-10-06
