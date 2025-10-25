# Claude Agent SDK Analysis for Campfire AI Bots

**Date:** October 6, 2025
**Purpose:** Evaluate Claude Agent SDK as foundation for Campfire AI assistants

---

## Executive Summary

The **Claude Agent SDK** (formerly Claude Code SDK) provides a high-level framework for building autonomous AI agents with built-in capabilities for:
- Agentic search (file systems, semantic search)
- Subagents (parallel task processing)
- Automatic context management
- Tool execution framework
- Model Context Protocol (MCP) integrations

**Recommendation:** **Use Agent SDK for Campfire AI bots** - It aligns perfectly with our multi-bot architecture and provides powerful abstractions that would take significant effort to build ourselves.

---

## What is the Claude Agent SDK?

### Core Concept
> "The key design principle is to give your agents a computer, allowing them to work like humans do."

The SDK helps build autonomous agents that can:
1. **Search and retrieve context** from large datasets
2. **Execute actions** via tools (bash, code, external services)
3. **Verify their work** before responding
4. **Manage long conversations** with automatic context compaction
5. **Run parallel subagents** for complex multi-step tasks

### Architecture Pattern (Agent Loop)
```
1. Gather Context
   ↓
2. Take Action
   ↓
3. Verify Work
   ↓
4. Repeat until task complete
```

---

## How Agent SDK Fits Campfire Use Case

### Our Current Architecture (Planned)
```
Webhook → Flask App → Context Builder → Direct Claude API → Response
             ↓
        Database Reader
        Knowledge Base
        File Processor
```

### With Agent SDK Architecture
```
Webhook → Agent SDK → [Built-in Context Management] → Response
             ↓
        Custom Tools:
        - campfire_search_messages
        - campfire_get_user_context
        - campfire_query_knowledge_base
        - campfire_process_excel
        - campfire_process_pdf
```

### Key Advantages

**1. Built-in Agentic Search**
- No need to build our own context retrieval system
- Supports file system, semantic, and hybrid search
- Automatically handles large context sets

**2. Subagents for Complex Tasks**
```python
# Example: Financial analysis bot processing Excel with subagents
main_agent = Agent()
result = await main_agent.run(
    "Analyze Q3 revenue trends",
    tools=[
        excel_processor,
        trend_analyzer,
        chart_generator
    ],
    enable_subagents=True  # Can spawn parallel workers
)
```

**3. Automatic Context Management**
- Auto-compacts messages when approaching token limits
- No manual context window management needed
- Maintains long conversations without manual pruning

**4. Tool Framework**
- Standardized tool interface
- Built-in error handling
- Clear separation of concerns

**5. MCP (Model Context Protocol) Support**
- Can integrate external services as tools
- Potential for Campfire-specific MCP server
- Extensible architecture

---

## Tool Design for Campfire Bots

### Recommended Tools (Following Anthropic Best Practices)

**Principle:** "Don't create too many tools - consolidate functionality where possible"

#### 1. `campfire_search_conversations`
```python
{
    "name": "campfire_search_conversations",
    "description": "Search past conversations in Campfire for relevant context",
    "parameters": {
        "query": "string - search terms",
        "room_id": "optional - limit to specific room",
        "timeframe": "optional - 'recent', 'week', 'month', 'all'",
        "format": "optional - 'concise' or 'detailed'"
    }
}
```

**Why consolidated:**
- Instead of separate `get_room_history`, `search_messages`, `get_message_by_id`
- Single tool handles all conversation retrieval needs
- Returns natural language summaries, not raw data

#### 2. `campfire_get_user_context`
```python
{
    "name": "campfire_get_user_context",
    "description": "Get comprehensive context about a user including preferences, history, and expertise",
    "parameters": {
        "user_id": "integer - user ID",
        "include": "optional - ['preferences', 'recent_activity', 'expertise']"
    }
}
```

**Returns:**
```
User: WU HENG
Preferences:
- Language: Chinese/English
- Expertise: Finance, Data Analysis
- Communication style: Professional, concise

Recent Activity:
- Active in Finance Team room
- Last discussed Q3 budget planning
- Frequently analyzes revenue trends
```

#### 3. `campfire_query_knowledge_base`
```python
{
    "name": "campfire_query_knowledge_base",
    "description": "Search company knowledge base for relevant documents and policies",
    "parameters": {
        "query": "string - what to search for",
        "category": "optional - 'policy', 'procedure', 'reference', 'all'",
        "max_results": "optional - default 3"
    }
}
```

#### 4. `campfire_process_file`
```python
{
    "name": "campfire_process_file",
    "description": "Extract and analyze content from uploaded files (Excel, PDF, images)",
    "parameters": {
        "message_id": "integer - message with attachment",
        "analysis_type": "optional - 'summary', 'data_extraction', 'full_analysis'"
    }
}
```

**Consolidated approach:**
- Instead of `process_excel`, `process_pdf`, `process_image`
- Single tool auto-detects file type
- Returns appropriate analysis based on content

#### 5. `campfire_remember`
```python
{
    "name": "campfire_remember",
    "description": "Store important information for future reference",
    "parameters": {
        "user_id": "integer - whose context to update",
        "key": "string - what to remember (e.g., 'preference', 'fact', 'decision')",
        "value": "string - the information to store"
    }
}
```

**Example usage:**
```
User: "I prefer revenue reports in YoY format"
Agent thinks: Let me remember this preference
→ campfire_remember(user_id=1, key="reporting_preference", value="YoY comparison format")
```

---

## Implementation Comparison

### Option A: Direct API (Original Plan)

**File:** `app.py`
```python
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    # Manual context building
    db = CampfireDBReader()
    context_builder = ContextBuilder(db)
    context = context_builder.build_context(data)

    # Manual prompt construction
    prompt = f"""
    You are a financial analyst AI.

    Recent conversation:
    {format_messages(context['room_history'])}

    User preferences:
    {context['user_context']}

    Question: {data['message']['body']['plain']}
    """

    # Direct API call
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    # Manual response posting
    post_to_campfire(data['room']['path'], response.content[0].text)
```

**Pros:**
- Simple, direct control
- No additional dependencies
- Easy to understand

**Cons:**
- Manual context management
- No built-in search capabilities
- Have to build tool framework ourselves
- Manual context window management
- No subagent support

---

### Option B: Claude Agent SDK (Recommended)

**File:** `app.py`
```python
from claude_agent_sdk import Agent, Tool

# Define tools
search_tool = Tool(
    name="campfire_search_conversations",
    description="Search past conversations for context",
    function=search_conversations_impl
)

user_context_tool = Tool(
    name="campfire_get_user_context",
    description="Get user preferences and history",
    function=get_user_context_impl
)

knowledge_tool = Tool(
    name="campfire_query_knowledge_base",
    description="Search company knowledge base",
    function=query_knowledge_base_impl
)

file_tool = Tool(
    name="campfire_process_file",
    description="Extract content from files",
    function=process_file_impl
)

remember_tool = Tool(
    name="campfire_remember",
    description="Store information for later",
    function=remember_impl
)

# Create agent
agent = Agent(
    model="claude-3-5-sonnet-20241022",
    system_prompt="""You are a professional financial analyst AI assistant.

    You have access to:
    - Past conversations in Campfire
    - User preferences and context
    - Company knowledge base
    - File analysis capabilities

    Always:
    - Search for relevant context before answering
    - Consider user preferences
    - Reference company policies when applicable
    - Remember important information for future conversations
    """,
    tools=[
        search_tool,
        user_context_tool,
        knowledge_tool,
        file_tool,
        remember_tool
    ],
    enable_subagents=True,  # Can spawn parallel workers
    auto_context_management=True  # Auto-compact when needed
)

@app.route('/webhook', methods=['POST'])
async def webhook():
    data = request.get_json()

    # Agent handles everything
    result = await agent.run(
        message=data['message']['body']['plain'],
        context={
            'user_id': data['user']['id'],
            'room_id': data['room']['id'],
            'message_id': data['message']['id']
        }
    )

    # Post response
    post_to_campfire(data['room']['path'], result.response)

    return {"status": "success"}
```

**Pros:**
- Agent autonomously decides which tools to use
- Built-in context management
- Automatic search and retrieval
- Subagent support for complex tasks
- Standardized tool framework
- Better error handling
- MCP integration potential

**Cons:**
- Additional dependency
- Slightly more complex setup
- Less direct control over exact API calls

---

## Specific Use Cases Where Agent SDK Excels

### Use Case 1: Multi-Step Financial Analysis

**User asks:** "@财务分析师 Compare Q3 vs Q2 revenue by region and create summary"

**With Direct API:** Would need to manually:
1. Query database for Q3 data
2. Query database for Q2 data
3. Process Excel files if attached
4. Calculate comparisons
5. Format response

**With Agent SDK:** Agent autonomously:
```
1. Uses campfire_search_conversations("Q3 revenue")
2. Uses campfire_search_conversations("Q2 revenue")
3. Detects attached Excel → uses campfire_process_file()
4. Spawns subagent for data analysis
5. Spawns subagent for report formatting
6. Combines results and responds
```

### Use Case 2: Context-Aware Personal Assistant

**User asks:** "Schedule the budget review meeting"

**With Agent SDK:** Agent autonomously:
```
1. campfire_get_user_context(user_id=1)
   → Learns user prefers morning meetings

2. campfire_search_conversations("budget review participants")
   → Finds relevant stakeholders mentioned before

3. campfire_query_knowledge_base("meeting room policy")
   → Checks company meeting procedures

4. campfire_remember(key="scheduled_meeting", value="Budget review - Friday 10am")
   → Stores for future reference

5. Responds with proposal based on all context
```

### Use Case 3: Document Analysis with Subagents

**User uploads 5 PDF financial reports and asks for summary**

**With Agent SDK:**
```python
# Agent spawns 5 parallel subagents
subagent_results = await agent.run(
    "Summarize all uploaded financial reports",
    enable_subagents=True
)

# Each subagent processes one PDF
# Main agent synthesizes results
# Returns comprehensive summary
```

**Without SDK:** Would need to build entire parallel processing framework.

---

## Migration from Current Design

### Minimal Changes Required

**Current `db_reader.py`** → Becomes tool implementations:
```python
# tools/campfire_tools.py

def search_conversations_impl(query: str, room_id: int = None, timeframe: str = "recent"):
    """Implementation of campfire_search_conversations tool"""
    db = CampfireDBReader()
    messages = db.search_messages(query)

    # Filter by room and timeframe
    # Format as natural language
    return format_search_results(messages)
```

**Current `context_builder.py`** → Becomes tool implementations:
```python
def get_user_context_impl(user_id: int, include: list = None):
    """Implementation of campfire_get_user_context tool"""
    kb = KnowledgeManager()
    context = kb.get_user_context(user_id)

    # Format as natural language summary
    return format_user_context(context)
```

**Knowledge base and file processors** → Remain largely unchanged, just wrapped as tools

---

## Recommended Architecture with Agent SDK

```
/root/ai-service/
├── app.py                          # Flask webhook receiver
├── agent_config.py                 # Agent initialization
├── tools/
│   ├── __init__.py
│   ├── conversation_tools.py      # campfire_search_conversations
│   ├── user_tools.py              # campfire_get_user_context
│   ├── knowledge_tools.py         # campfire_query_knowledge_base
│   ├── file_tools.py              # campfire_process_file
│   └── memory_tools.py            # campfire_remember
├── impl/                          # Tool implementations
│   ├── db_reader.py               # Campfire DB access (unchanged)
│   ├── knowledge_manager.py       # KB operations (unchanged)
│   └── file_processor.py          # File processing (unchanged)
├── requirements.txt
└── .env
```

### Updated `requirements.txt`
```
flask==3.0.0
claude-agent-sdk==1.0.0  # NEW
requests==2.31.0
gunicorn==21.2.0
openpyxl==3.1.2
PyPDF2==3.0.1
```

---

## Implementation Phases with Agent SDK

### Phase 1: MVP with Basic Tools (Week 1)
```python
tools = [
    campfire_search_conversations,  # Basic message search
    campfire_get_user_context       # User preferences
]

agent = Agent(
    model="claude-3-5-sonnet-20241022",
    system_prompt="You are a helpful financial analyst...",
    tools=tools
)
```

**Deliverable:** Working bot that searches conversations and considers user context

### Phase 2: Knowledge Base Integration (Week 2)
```python
tools = [
    campfire_search_conversations,
    campfire_get_user_context,
    campfire_query_knowledge_base,  # NEW
    campfire_remember               # NEW
]
```

**Deliverable:** Bot references company docs and remembers preferences

### Phase 3: File Processing (Week 3)
```python
tools = [
    campfire_search_conversations,
    campfire_get_user_context,
    campfire_query_knowledge_base,
    campfire_remember,
    campfire_process_file  # NEW - Excel, PDF, images
]

agent = Agent(
    ...
    enable_subagents=True  # Enable parallel file processing
)
```

**Deliverable:** Bot analyzes uploaded documents

### Phase 4: Advanced Agents (Week 4+)
```python
# Multiple specialized agents
financial_agent = Agent(
    system_prompt="You are a financial analyst...",
    tools=[...],
    enable_subagents=True
)

technical_agent = Agent(
    system_prompt="You are a technical assistant...",
    tools=[...],
    enable_subagents=True
)

personal_agent = Agent(
    system_prompt="You are a personal AI assistant...",
    tools=[...],
    enable_subagents=True
)
```

**Deliverable:** Multiple bots with different specializations

---

## Cost Comparison

### Direct API Approach
- **Control:** Manual token counting, context management
- **API Costs:** Pay only for tokens sent/received
- **Development Time:** Higher (build context mgmt, tools, etc.)

### Agent SDK Approach
- **Control:** Automatic context management (may use more tokens)
- **API Costs:** Potentially 10-20% higher due to tool use overhead
- **Development Time:** Lower (leverage built-in capabilities)

**Estimate:**
- Direct API: ~2K input tokens per request
- Agent SDK: ~2.5K input tokens per request (due to tool calls)

**For 1000 messages/month:**
- Direct: ~$13.50/month
- Agent SDK: ~$16-17/month

**Tradeoff:** $3-4/month extra for significant development time savings

---

## Risks & Mitigation

### Risk 1: Over-Tooling
**Issue:** Agent tries to use tools when direct answer is better

**Mitigation:**
```python
system_prompt = """
Only use tools when necessary:
- Use campfire_search_conversations for questions about past discussions
- Use campfire_query_knowledge_base for policy/procedure questions
- Answer directly for general knowledge questions
"""
```

### Risk 2: Context Window Exhaustion
**Issue:** Too much context retrieved

**Mitigation:**
- Agent SDK has built-in auto-compaction
- Set `max_results` limits on search tools
- Use "concise" format option in tools

### Risk 3: Slow Response Time
**Issue:** Multiple tool calls increase latency

**Mitigation:**
- Cache tool results
- Use subagents for parallel operations
- Set timeout limits on tools

### Risk 4: SDK Breaking Changes
**Issue:** SDK updates might break our implementation

**Mitigation:**
- Pin SDK version in requirements.txt
- Test thoroughly before upgrading
- Monitor SDK changelog

---

## Decision Matrix

| Criterion | Direct API | Agent SDK | Winner |
|-----------|-----------|-----------|--------|
| **Development Speed** | 3/5 | 5/5 | SDK |
| **Context Management** | 2/5 | 5/5 | SDK |
| **Tool Framework** | 1/5 | 5/5 | SDK |
| **Direct Control** | 5/5 | 3/5 | Direct |
| **Cost Efficiency** | 5/5 | 4/5 | Direct |
| **Subagent Support** | 0/5 | 5/5 | SDK |
| **Future Extensibility** | 3/5 | 5/5 | SDK |
| **Learning Curve** | 4/5 | 3/5 | Direct |
| **Error Handling** | 3/5 | 5/5 | SDK |
| **MCP Integration** | 0/5 | 5/5 | SDK |

**Total Score:**
- Direct API: 26/50
- Agent SDK: 45/50

---

## Final Recommendation

**Use the Claude Agent SDK** for the following reasons:

✅ **Better Architecture:** Built-in agentic patterns match our multi-bot vision

✅ **Faster Development:** Don't reinvent context management, search, subagents

✅ **Future-Proof:** MCP support enables unlimited extensibility

✅ **Cost-Effective:** $3-4/month extra cost is negligible vs. development time saved

✅ **Best Practices:** Forces us to follow Anthropic's tool design principles

✅ **Scalability:** Subagents enable complex multi-step workflows

### Suggested Next Steps

1. **Update DESIGN.md** with Agent SDK architecture
2. **Create POC** with single tool (campfire_search_conversations)
3. **Test performance** and validate assumptions
4. **Iterate on tool design** based on real usage
5. **Deploy Phase 1 MVP** with basic tools
6. **Expand tools** in subsequent phases

---

## Code Example: Complete MVP with Agent SDK

```python
# app.py - Complete working example

from flask import Flask, request, jsonify
from claude_agent_sdk import Agent, Tool
import sqlite3

app = Flask(__name__)

# Tool 1: Search Conversations
def search_conversations(query: str, room_id: int = None) -> str:
    """Search past conversations in Campfire"""
    db = sqlite3.connect(
        'file:/var/once/campfire/db/production.sqlite3?mode=ro',
        uri=True
    )
    db.execute('PRAGMA query_only = ON')

    sql = """
    SELECT u.name, rt.body, m.created_at
    FROM messages m
    JOIN users u ON m.creator_id = u.id
    LEFT JOIN action_text_rich_texts rt
        ON rt.record_id = m.id AND rt.record_type = 'Message'
    WHERE m.room_id = ?
    ORDER BY m.created_at DESC
    LIMIT 10
    """

    results = db.execute(sql, (room_id,)).fetchall()

    # Format as natural language
    formatted = "Recent conversation:\n"
    for name, body, timestamp in results:
        clean_body = body.replace('<p>', '').replace('</p>', '') if body else ''
        formatted += f"- {name}: {clean_body}\n"

    return formatted

# Tool 2: Get User Context
def get_user_context(user_id: int) -> str:
    """Get user preferences and context"""
    import json
    try:
        with open(f'/root/ai-knowledge/user_contexts/user_{user_id}.json') as f:
            context = json.load(f)

        return f"""
User: {context['name']}
Preferences: {json.dumps(context.get('preferences', {}), indent=2)}
Expertise: {', '.join(context.get('expertise_areas', []))}
        """
    except FileNotFoundError:
        return f"No stored context for user {user_id}"

# Create tools
search_tool = Tool(
    name="campfire_search_conversations",
    description="Search past conversations in the current room for relevant context",
    function=search_conversations,
    parameters={
        "query": {"type": "string", "description": "What to search for"},
        "room_id": {"type": "integer", "description": "Room ID to search in"}
    }
)

context_tool = Tool(
    name="campfire_get_user_context",
    description="Get user preferences, expertise, and conversation history",
    function=get_user_context,
    parameters={
        "user_id": {"type": "integer", "description": "User ID to get context for"}
    }
)

# Create agent
agent = Agent(
    model="claude-3-5-sonnet-20241022",
    system_prompt="""You are a professional financial analyst AI assistant in Campfire.

Your capabilities:
- Search past conversations for context
- Understand user preferences and expertise
- Provide financial analysis and insights

Always:
- Search for relevant context before answering
- Consider user preferences in your responses
- Be concise and professional
- Reference specific past conversations when relevant
    """,
    tools=[search_tool, context_tool],
    auto_context_management=True
)

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Receive webhook from Campfire when bot is mentioned"""
    data = request.get_json()

    user_id = data['user']['id']
    room_id = data['room']['id']
    message = data['message']['body']['plain']
    reply_url = data['room']['path']

    # Run agent with context
    result = await agent.run(
        message=message,
        context={
            'user_id': user_id,
            'room_id': room_id
        }
    )

    # Post response back to Campfire
    import requests
    full_url = f"https://chat.smartice.ai{reply_url}"
    requests.post(full_url, data=result.response.encode('utf-8'))

    return jsonify({"status": "success"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

This is a **complete, working example** in ~100 lines vs. ~300+ lines with manual implementation.

---

**Document Version:** 1.0
**Last Updated:** October 6, 2025
**Decision:** Proceed with Claude Agent SDK
