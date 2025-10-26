# Campfire AI Bot System - Architecture Design

**Project:** AI-Powered Group Chat Intelligence
**Platform:** Campfire (37signals ONCE)
**Current Version:** v0.4.0 (Ready for Deployment)
**Production Status:** v0.3.3.1 (All 8 bots active with Haiku 4.5)

---

## 🔥 Current Status

**Production:** v0.3.3.1 with claude-haiku-4-5-20251001 model
**Ready for Deployment:** v0.4.0 with Multi-Bot Collaboration + Security Fixes
**Architecture:** FastAPI + Stateful Sessions + Multi-Bot Collaboration + Progress Milestones + Knowledge Base + Skills MCP + Supabase + Modular Tools
**Bots:** 8 specialized assistants (Financial, Technical, Personal, Briefing, Default, Operations, CC Tutor, Menu Engineering)
**Key Features:** Multi-bot collaboration via Task tool + Two-layer security protection (all bots read-only)

---

## Vision & Principles

### Core Objective
Transform Campfire into an **AI-augmented collaborative workspace** with intelligent agents providing:
- Context-aware responses based on conversation history
- Access to company knowledge base
- Personalized interactions per user
- File analysis (Excel, PDF, documents)

### Guiding Principles

**1. Non-Invasive Integration**
- Campfire managed by ONCE (auto-updates nightly at 2am)
- AI system external to Docker container
- No source code modifications

**2. Data Sovereignty**
- Read-only database access (WAL mode, safe concurrent reads)
- AI knowledge base stored separately at `/root/ai-knowledge/`
- User data privacy and isolation

**3. Scalability**
- Multiple specialized bots
- Efficient context management
- Horizontal scaling capability

---

## System Architecture

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  DigitalOcean Droplet (128.199.175.50)                         │
│  Domain: https://chat.smartice.ai                               │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Docker Container: campfire                             │   │
│  │  ├─ Campfire Rails App (managed by ONCE)               │   │
│  │  ├─ Port 80/443 (HTTPS with auto SSL)                 │   │
│  │  └─ Volume: /rails/storage → /var/once/campfire       │   │
│  └───────────────────────┬────────────────────────────────┘   │
│                           │                                     │
│                           │ Webhook POST (on @bot mention)     │
│                           ↓                                     │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  AI Webhook Service (/root/ai-service/)                │   │
│  │  ├─ FastAPI HTTP server (port 8000)                   │   │
│  │  ├─ POST /webhook (receives from Campfire)            │   │
│  │  ├─ Claude Agent SDK (max_turns=10)                   │   │
│  │  ├─ Stateful SessionManager (hot/warm/cold paths)    │   │
│  │  ├─ Progress Milestones (smart broadcasting)          │   │
│  │  ├─ Financial MCP Server (Excel analysis)             │   │
│  │  ├─ BackgroundTasks (immediate 200 response)          │   │
│  │  └─ uvicorn (ASGI production server)                  │   │
│  └───────┬───────────────┬────────────────────────────────┘   │
│          │               │                                      │
│          │ reads         │ reads/writes                         │
│          ↓               ↓                                      │
│  ┌──────────────┐   ┌─────────────────────────────────┐       │
│  │ Campfire DB  │   │  AI Knowledge Base               │       │
│  │ (read-only)  │   │  (/root/ai-knowledge/)           │       │
│  │              │   │  ├─ user_contexts/               │       │
│  │ SQLite3 WAL  │   │  │  └─ user_{id}.json           │       │
│  │ production   │   │  ├─ company_kb/                  │       │
│  │ .sqlite3     │   │  │  ├─ briefings/               │       │
│  │              │   │  │  ├─ policies/                │       │
│  │              │   │  │  ├─ procedures/              │       │
│  │              │   │  │  ├─ financial/               │       │
│  │              │   │  │  └─ technical/               │       │
│  └──────────────┘   └─────────────────────────────────┘       │
│          │                           │                          │
│          │                           │                          │
└──────────┼───────────────────────────┼──────────────────────────┘
           │                           │
           │                           ↓
           │               ┌─────────────────────────────────┐
           │               │  Anthropic Claude API            │
           │               │  Model: claude-haiku-4.5         │
           │               │  (cloud service)                 │
           │               └─────────────────────────────────┘
           │                           │
           │                           │ Response
           │                           ↓
           │               POST https://chat.smartice.ai/
           └───────────────rooms/{id}/{bot_key}/messages
```

### Request Flow Sequence

```
┌─────────┐
│  User   │  @财务分析师 分析野百灵5-8月报表
└────┬────┘
     │
     ↓
┌─────────────────────────────────────────────────────────┐
│  Campfire                                                │
│  1. Detects @bot mention                                │
│  2. POSTs webhook to http://128.199.175.50:5000/webhook│
│     Payload: {user, room, message}                      │
└────┬────────────────────────────────────────────────────┘
     │
     ↓
┌─────────────────────────────────────────────────────────┐
│  FastAPI Webhook Handler (app_fastapi.py)               │
│  3. Receives webhook                                     │
│  4. Spawns background task                              │
│  5. Returns 200 OK immediately (<1 second)              │
└────┬────────────────────────────────────────────────────┘
     │
     ↓
┌─────────────────────────────────────────────────────────┐
│  Background Processing Task                             │
│  6. Posts acknowledgment: "🤔 Processing..."            │
│  7. Loads session from cache (if exists)                │
└────┬────────────────────────────────────────────────────┘
     │
     ↓
┌─────────────────────────────────────────────────────────┐
│  Claude Agent SDK (campfire_agent.py)                   │
│  8. Loads conversation context (last 10 messages)       │
│  9. Loads room files (checks for attachments)           │
│  10. Calls Claude API with ClaudeAgentOptions:          │
│      - model: claude-haiku-4-5-20251001                 │
│      - mcp_servers: [Financial MCP]                     │
│      - max_turns: 10                                    │
└────┬────────────────────────────────────────────────────┘
     │
     ↓
┌─────────────────────────────────────────────────────────┐
│  Claude API Processing (Turn 1)                         │
│  11. Receives prompt + context                          │
│  12. Decides to call MCP tools                          │
│      - get_excel_info()                                 │
│      - show_excel_visual()                              │
│  13. Returns ToolUseBlock                               │
└────┬────────────────────────────────────────────────────┘
     │
     ↓
┌─────────────────────────────────────────────────────────┐
│  MCP Tool Execution (Financial MCP Server)              │
│  14. Executes get_excel_info()                          │
│      → Returns: Sheet structure, column names           │
│  15. Executes show_excel_visual()                       │
│      → Returns: Data preview, summaries                 │
│  16. Progress milestone posted: "📊 Reading Excel..."   │
└────┬────────────────────────────────────────────────────┘
     │
     ↓
┌─────────────────────────────────────────────────────────┐
│  Claude API Processing (Turn 2) ← ENABLED BY max_turns │
│  17. Receives tool results                              │
│  18. Synthesizes findings into text                     │
│  19. Returns AssistantMessage with full analysis        │
└────┬────────────────────────────────────────────────────┘
     │
     ↓
┌─────────────────────────────────────────────────────────┐
│  Response Streaming (app_fastapi.py)                    │
│  20. Extracts text blocks from AssistantMessage         │
│  21. POSTs to Campfire API:                             │
│      POST https://chat.smartice.ai/rooms/{id}/{bot_key}/│
│      messages                                            │
│      Body: "根据Excel文件分析，我发现..."               │
│  22. Saves session to cache for future requests         │
└────┬────────────────────────────────────────────────────┘
     │
     ↓
┌─────────────────────────────────────────────────────────┐
│  Campfire                                                │
│  23. Receives bot message                               │
│  24. Renders HTML formatting                            │
│  25. Displays to user                                   │
└─────────────────────────────────────────────────────────┘
     │
     ↓
┌─────────┐
│  User   │  Sees full financial analysis with formatting
└─────────┘
```

### Infrastructure

**Server:** DigitalOcean Droplet (128.199.175.50)
- **Domain:** https://chat.smartice.ai
- **OS:** Ubuntu 25.04 x64 (2GB RAM, 1 vCPU)
- **Campfire:** Docker container (auto-updates nightly)

**AI Service:** `/root/ai-service/`
- **Framework:** FastAPI + Claude Agent SDK
- **Model:** claude-haiku-4-5-20251001 (all bots)
- **Port:** 8000 (internal), 5000 (external)
- **Deployment:** Docker Hub → hengwoo/campfire-ai-bot:0.3.2

**8 Active Bots:**
1. 财务分析师 (Financial Analyst) - `2-CsheovnLtzjM`
2. 技术助手 (Technical Assistant) - `3-2cw4dPpVMk86`
3. 个人助手 (Personal Assistant) - `4-GZfqGLxdULBM`
4. 日报助手 (Briefing Assistant) - `11-cLwvq6mLx4WV`
5. AI Assistant (Default) - `10-vWgb0YVbUSYs`
6. 运营数据助手 (Operations Assistant) - `TBD`
7. Claude Code 导师 (CC Tutor) - `TBD`
8. 菜单工程师 (Menu Engineer) - `19-gawmDGiVGP4u`

### File Structure

```
/root/ai-service/
├── src/
│   ├── app_fastapi.py           # FastAPI webhook server
│   ├── campfire_agent.py        # Agent SDK wrapper
│   ├── bot_manager.py           # Bot configuration
│   ├── session_manager.py       # Session caching
│   ├── progress_classifier.py   # Milestone detection
│   └── tools/campfire_tools.py  # Database queries
├── bots/
│   ├── financial_analyst.json
│   ├── technical_assistant.json
│   ├── personal_assistant.json
│   ├── briefing_assistant.json
│   ├── default.json
│   ├── operations_assistant.json
│   ├── claude_code_tutor.json
│   └── menu_engineering.json
└── .env                         # API keys

/root/ai-knowledge/
├── user_contexts/               # User preferences
├── company_kb/
│   ├── briefings/              # Daily briefings
│   ├── policies/               # Company policies
│   ├── procedures/             # Process docs
│   ├── financial/              # Financial standards
│   └── technical/              # Technical guides
└── logs/                       # Application logs
```

---

## Tool Access Matrix

### Overview

Each bot has access to different tool combinations based on their role:
- **Built-in SDK Tools:** Provided by Claude Agent SDK (WebSearch, WebFetch, Read, Write, etc.)
- **MCP Tools:** Custom tools via Model Context Protocol (Campfire tools, Financial tools, Skills tools)

**Key Fix (v0.3.0.1):** Previously, the `allowed_tools` whitelist inadvertently blocked all built-in SDK tools. This has been fixed - all bots now have access to built-in tools.

### Built-in SDK Tools (All Bots)

These tools are now available to **all 5 bots**:

| Tool | Purpose | Use Cases |
|------|---------|-----------|
| 🌐 **WebSearch** | Search the web for information | Research, fact-checking, current events |
| 🌐 **WebFetch** | Fetch web page content | Read documentation, articles, online resources |
| 📄 **Read** | Read file contents | View uploaded files, analyze documents |
| 📝 **Write** | Create new files | Generate reports, save outputs |
| ✏️ **Edit** | Modify existing files | Update documents, fix files |
| 💻 **Bash** | Execute shell commands | File system operations, data processing |
| 🔍 **Grep** | Search within files | Find content in documents |
| 🗂️ **Glob** | Find files by pattern | Locate files matching criteria |

### MCP Tools by Bot Type

#### Base MCP Tools (All Bots)

| Tool | Purpose |
|------|---------|
| `search_conversations` | Search Campfire message history |
| `get_user_context` | Get user preferences and info |
| `save_user_preference` | Save user preferences |
| `search_knowledge_base` | Search company knowledge base |
| `read_knowledge_document` | Read full knowledge base documents |
| `list_knowledge_documents` | List available documents |
| `store_knowledge_document` | Create new knowledge base documents |

#### 1. Financial Analyst

**Additional Tools:**
- **Financial MCP** (17 tools): Excel analysis, account validation, financial thinking tools
- **Skills MCP** (3 tools): Progressive skill disclosure for document creation

**Total:** 8 built-in + 7 base MCP + 17 financial MCP + 3 skills MCP = **35 tools**

**Key Capabilities:**
- Analyze Excel financial reports
- Validate account structures
- Calculate financial ratios
- Create financial documents (via Skills)
- Search web for financial data (WebSearch)

#### 2. Technical Assistant

**Additional Tools:** None (base only)

**Total:** 8 built-in + 7 base MCP = **15 tools**

**Key Capabilities:**
- Search web for documentation (WebSearch, WebFetch)
- Read/edit code files (Read, Write, Edit)
- Execute shell commands (Bash)
- Search company knowledge base
- Access conversation history

#### 3. Personal Assistant

**Additional Tools:**
- `manage_personal_tasks` - Create, list, complete, delete tasks
- `set_reminder` - Set personal reminders
- `save_personal_note` - Save private notes
- `search_personal_notes` - Search user's notes
- **Skills MCP** (3 tools): Progressive skill disclosure

**Total:** 8 built-in + 7 base MCP + 4 personal MCP + 3 skills MCP = **22 tools**

**Key Capabilities:**
- Task and reminder management
- Personal note-taking
- Web translation (WebFetch + WebSearch)
- Document creation (via Skills)
- File handling (Read, Write, Edit)

#### 4. Briefing Assistant

**Additional Tools:**
- `generate_daily_briefing` - Generate daily summaries
- `search_briefings` - Search historical briefings

**Total:** 8 built-in + 7 base MCP + 2 briefing MCP = **17 tools**

**Key Capabilities:**
- Generate AI-powered daily briefings
- Search historical briefings
- Access conversation history
- Web research for news (WebSearch)

#### 5. AI Assistant (Default)

**Additional Tools:** None (base only)

**Total:** 8 built-in + 7 base MCP = **15 tools**

**Key Capabilities:**
- General-purpose assistance
- Web search and fetch
- File operations
- Conversation history access
- Knowledge base queries

### Tool Access Implementation

**Code Location:** `src/campfire_agent.py:_get_allowed_tools_for_bot()`

```python
# Built-in tools added to all bots (v0.3.0.1)
builtin_tools = ["WebSearch", "WebFetch", "Read", "Write", "Edit", "Bash", "Grep", "Glob"]

# Base MCP tools added to all bots
base_tools = ["mcp__campfire__*"] # 7 knowledge base and conversation tools

# Bot-specific tools added based on bot_id
# financial_analyst → Financial MCP + Skills MCP
# personal_assistant → Personal productivity + Skills MCP
# briefing_assistant → Briefing tools
# technical_assistant, default → Base only
```

**Reference:** https://docs.claude.com/en/api/agent-sdk/overview

---

## Database & Storage

### Campfire Database

**Location:** `/var/once/campfire/db/production.sqlite3`
**Technology:** SQLite3 with WAL mode

**Key Tables:**
- `messages` - Message metadata
- `action_text_rich_texts` - Message body (HTML)
- `users` - User accounts (role: 0=user, 1=bot)
- `rooms` - Rooms (Open, Closed, Direct)
- `active_storage_blobs` - File metadata
- `active_storage_attachments` - File links
- `message_search_index` - FTS5 full-text search

**Access Pattern:**
- Read-only with `PRAGMA query_only = ON`
- WAL mode allows concurrent reads
- No locking conflicts with Campfire

### File Storage

**Location:** `/var/once/campfire/files/`
**Structure:** Hash-based partitioning (e.g., `4j/ab/xyz123...`)

### Technical Constraints

1. **No Source Modifications** - ONCE overwrites container nightly
2. **Read-Only DB** - Must use WAL mode safely
3. **Update Resilience** - AI service survives Campfire updates
4. **External Storage** - Knowledge base outside Docker

---

## Key Learnings

### Response Formatting

**Campfire renders HTML:**
- Use `<h2>`, `<h3>` for headings
- Use `<strong>`, `<code>` for emphasis
- Use `<ul><li>`, `<table>` for structure
- Blog-style layout with proper spacing (line-height: 1.8-2.0)
- Configure bot system prompts to generate HTML

### Deployment Best Practices

1. Test locally first
2. Get user confirmation before Docker build
3. Build & push to Docker Hub
4. Deploy to production
5. Monitor logs for verification

**Anti-Pattern:** Rapid deploy without local testing

### Version History

| Version | Changes | Status |
|---------|---------|--------|
| v1.0.x | Flask-based MVP | ✅ Deprecated |
| v0.2.0 | FastAPI + Stateful Sessions | ✅ Deployed |
| v0.2.1 | Progress Milestones | ✅ Deployed |
| v0.2.2 | Knowledge Base (4 tools) | ✅ Deployed |
| v0.2.3 | Briefing Bot | ✅ Deployed |
| v0.2.4 | 3 New Bots + API Fallback | ✅ Deployed |
| v0.3.0 | Haiku 4.5 + Enhanced HTML | ✅ Deployed |
| v0.3.0.1 | Operations + CC Tutor bots | ✅ Deployed |
| v0.3.2 | Menu Engineering + Boston Matrix | ✅ Deployed |
| **v0.3.3** | **Agent Tools Refactoring (46% code reduction)** | **✅ IN PRODUCTION** 🔥 |

---

## Technology Stack

**Runtime:** Python 3.11+, FastAPI, Uvicorn
**AI:** Anthropic Claude Haiku 4.5, Claude Agent SDK
**Database:** SQLite3 (read-only, WAL mode), Supabase (Postgres)
**Storage:** JSON (sessions, contexts), Filesystem (documents)
**Infrastructure:** Docker, DigitalOcean, Cloudflare DNS

---

## Cost Estimates

**DigitalOcean:** $18/month
**Claude API:** $30-100/month (Haiku 4.5 is cost-efficient)
**Supabase:** Free tier (sufficient for current usage)
**Total:** $50-120/month

---

**Document Version:** 7.0 (v0.3.3 - Agent Tools Refactoring)
**Last Updated:** October 25, 2025
**Production Status:** v0.3.3 deployed ✅
**For Details:** See CLAUDE.md (project memory), IMPLEMENTATION_PLAN.md (deployment)
