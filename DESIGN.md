# Campfire AI Bot System - Architecture Design

**Platform:** Campfire (37signals ONCE)
**Current Version:** v0.4.0.2 (Production), v0.5.0 (Native Skills - Local Validated)
**Status:** ✅ All 8 bots active with Haiku 4.5, personal_assistant upgraded to native skills

---

## System Architecture

### High-Level Diagram

```
User → Campfire (Rails) → Webhook → AI Service (FastAPI) → Claude API
                              ↓           ↓
                         Campfire DB  Knowledge Base
                         (read-only)  (/root/ai-knowledge/)
```

### Infrastructure

**Server:** DigitalOcean Droplet (128.199.175.50)
- **Domain:** https://chat.smartice.ai
- **Campfire:** Docker container (auto-updates nightly at 2am)
- **AI Service:** /root/ai-service/ (Docker: hengwoo/campfire-ai-bot:latest)

### Request Flow

```
1. User @mentions bot in Campfire
2. Campfire POSTs webhook to http://128.199.175.50:5000/webhook/{bot_id}
3. FastAPI spawns background task, returns 200 OK immediately
4. SessionManager loads session (hot/warm/cold paths)
5. Claude Agent SDK executes with max_turns=30
6. MCP tools execute (Campfire MCP, Financial MCP, Operations MCP, etc.)
7. Progress milestones posted during execution
8. Final response POSTed to Campfire API
9. Session cached for next request (40% faster)
```

---

## Database Schema (Key Tables)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `messages` | Message metadata | id, room_id, creator_id, created_at |
| `action_text_rich_texts` | Message body (HTML) | record_id, body |
| `users` | User accounts | id, name, role (0=user, 1=bot) |
| `rooms` | Rooms | id, name, kind (Open/Closed/Direct) |
| `active_storage_blobs` | File metadata | id, key, filename, byte_size |
| `active_storage_attachments` | File links | record_id, blob_id |
| `message_search_index` | FTS5 full-text search | content |

**Access:** Read-only with `PRAGMA query_only = ON` (WAL mode safe for concurrent reads)

---

## Tool Categories & MCP Servers

| Category | MCP Prefix | Tools | Used By |
|----------|------------|-------|---------|
| Built-in SDK | (none) | 8 | All bots (WebSearch, WebFetch, Read, Grep, Glob, Task, Bash, **Skill** ⭐) |
| Campfire Base | `mcp__campfire__` | 7 | All bots (conversations, user context, knowledge base) |
| Financial | `mcp__fin-report-agent__` | 17 | financial_analyst (Excel, financial calculations) |
| Operations | `mcp__operations__` | 3 | operations_assistant (Supabase queries) |
| Analytics RPC | `mcp__analytics__` | 10 | operations_assistant (RPC functions) |
| Menu Engineering | `mcp__menu_engineering__` | 5 | menu_engineer (Boston Matrix analysis) |

**Implementation:** `src/campfire_agent.py:_get_allowed_tools_for_bot()`

**⭐ Native Skills System (v0.5.0):**

The "Skill" built-in tool enables access to two types of skills:

**1. Anthropic Plugin Skills** (Official Document Processing)
- `document-skills-docx` - Word document creation/editing
- `document-skills-pdf` - PDF manipulation
- `document-skills-pptx` - PowerPoint presentations
- `document-skills-xlsx` - Excel spreadsheets
- **Source:** Anthropic's official skills plugins (https://github.com/anthropics/skills)
- **Status:** Point-in-time snapshots (stable, production-ready)

**2. Custom Project Skills** (Campfire-Specific Workflows)
- `code-generation` - Template-based code generation
- `conversation-search` - Advanced conversation search
- `daily-briefing` - Briefing generation workflows
- `financial-analysis` - Financial analysis patterns
- `knowledge-base` - Knowledge base query workflows
- `personal-productivity` - Task/reminder/note management
- `presentation-generation` - HTML presentation creation
- **Source:** Project-maintained (`.claude/skills/` directory)

**Discovery Mechanism:**
- Both types auto-discovered via `setting_sources=["user", "project"]`
- Agent SDK scans `.claude/skills/` on startup
- Skills loaded on-demand when bot invokes `Skill("skill-name")`
- Token efficient: Only loads when explicitly requested

**Migration Note:** Skills MCP server deprecated (v0.5.0). All skills now use native Agent SDK pattern. All other MCP servers remain fully operational:
- Campfire MCP (7 tools) ✅ Active
- Financial MCP (17 tools) ✅ Active
- Operations MCP (3 tools) ✅ Active
- Analytics RPC MCP (10 tools) ✅ Active
- Menu Engineering MCP (5 tools) ✅ Active

---

## 8 Active Bots

| Bot | Tools | Key Features |
|-----|-------|--------------|
| 财务分析师 (Financial Analyst) | 35 | Excel analysis, Financial MCP (17 tools) |
| 技术助手 (Technical Assistant) | 15 | Web research, knowledge base |
| 个人助手 (Personal Assistant) | 16 | Tasks, reminders, native skills ✅ |
| 日报助手 (Briefing Assistant) | 17 | AI-powered daily briefings |
| AI Assistant (Default) | 15 | General-purpose assistance |
| 运营数据助手 (Operations Assistant) | 28 | Supabase analytics, STAR framework |
| Claude Code导师 (CC Tutor) | 15 | 4.7K line knowledge base |
| 菜单工程师 (Menu Engineer) | 20 | Boston Matrix profitability analysis |

**All bots use:** claude-haiku-4-5-20251001 model

---

## Multi-Bot Collaboration (v0.4.0)

**Architecture:** Peer-to-peer subagent spawning via Task tool

```
User → Primary Bot (e.g., Financial Analyst)
          ├─ Analyzes with own tools
          └─ Spawns Subagent (e.g., Personal Assistant for PDF creation)
                ├─ Executes specialized task
                └─ Returns result
       ← Combines results and responds
```

**Security:** Subagents limited to safe tools (Read, Grep, Glob, WebSearch, WebFetch, Task only)

---

## Native Agent SDK Skills (v0.5.0) ⭐

### Architecture: Filesystem-Based Auto-Discovery

**Pattern:** Uses Anthropic's native Agent SDK skills system (not external MCP server)

```
Agent SDK
  ↓ setting_sources=["user", "project"]
  ↓ Scans filesystem on startup
  ↓
.claude/skills/
  ├── code-generation/SKILL.md          (custom)
  ├── conversation-search/SKILL.md      (custom)
  ├── daily-briefing/SKILL.md           (custom)
  ├── financial-analysis/SKILL.md       (custom)
  ├── knowledge-base/SKILL.md           (custom)
  ├── personal-productivity/SKILL.md    (custom)
  └── presentation-generation/SKILL.md  (custom)
  ↓
Bot invokes: Skill("presentation-generation")  OR  Skill("document-skills-pptx")
  ↓ Loads skill on-demand (either custom or plugin)
  ↓ Follows workflow in SKILL.md
  ✓ Executes task
```

**Two Types of Skills:**

**1. Anthropic Plugin Skills** (Document Processing)
- **Available:** document-skills-docx, document-skills-pptx, document-skills-pdf, document-skills-xlsx
- **Source:** Anthropic's official plugin repository
- **Status:** NOT currently installed in `.claude/skills/` directory
- **How to use:** Bots reference them in prompts (e.g., "load_skill('document-skills-pptx')")
- **Note:** Agent SDK auto-provides these if available in plugin system

**2. Custom Project Skills** (Campfire Workflows)
- **Installed:** 7 custom skills in `.claude/skills/` directory
- **Purpose:** Project-specific workflows (code generation, briefings, presentations, etc.)
- **Maintained:** By project team

**Key Components:**
- **Skill Tool:** Built-in Agent SDK tool (replaces `mcp__skills__load_skill`)
- **Auto-Discovery:** Skills found automatically from `.claude/skills/` directory
- **On-Demand Loading:** Skills loaded only when needed (token efficient)
- **YAML Frontmatter:** Metadata in SKILL.md files (name, description, version)

**Implementation:**
```python
# campfire_agent.py:609 - Enables native skills globally
"setting_sources": ["user", "project"]

# campfire_agent.py:107 - Default builtin tools include Skill
builtin_tools = [..., "Skill"]

# .claude/skills/ directory structure (Anthropic standard)
```

**Benefits:**
- ✓ No external MCP server process
- ✓ Follows Anthropic best practices
- ✓ Automatic skill discovery
- ✓ Better tool access control
- ✓ Simpler architecture
- ✓ Both plugin and custom skills use same mechanism

**Migration Status:**
- ✅ personal_assistant - Native skills enabled (validated Nov 2, 2025)
- ✅ cc_tutor - File-based prompts (native skills being added)
- ⏳ 6 other bots - Pending native skills enablement

**Real-World Test:** 22MB Chinese PPTX → Text extraction → English translation → File saved ✅

---

## File-Based Prompt System (v0.4.1)

### Three-Layer Architecture

| Layer | Purpose | Size | When Loaded |
|-------|---------|------|-------------|
| **Layer 1:** Bot Personality | Identity, capabilities, HTML formatting | ~200 lines | Always |
| **Layer 2:** Skills | Domain expertise, detailed workflows | 400-600 lines each | **On-demand via Skill tool** ⭐ |
| **Layer 3:** Dynamic Context | Template variables ($current_date, $user_name, $room_name) | N/A | Runtime injection |

**Implementation:**
- **PromptLoader** (280 lines) - Loads `.md` files with `string.Template` substitution
- **Native Skills** ⭐ - Agent SDK auto-discovers from `.claude/skills/` (replaces SkillsManager)
- **BotManager** - YAML + JSON dual format support (backwards compatible)

**Token Efficiency:**
- Simple queries (70%): **20% savings** (no Skills loaded)
- Complex workflows (30%): 13-33% overhead (Skills loaded on-demand)

**Migration Status:** 1/8 bots (personal_assistant - file-based prompts + native skills)

---

## Technical Stack

**Runtime:** Python 3.11, FastAPI, Uvicorn
**AI:** Claude Agent SDK 0.1.4, claude-haiku-4-5-20251001
**Database:** SQLite3 (read-only, WAL mode), Supabase (Postgres)
**Storage:** JSON (sessions, contexts), Filesystem (documents)
**Infrastructure:** Docker, DigitalOcean, Cloudflare DNS

---

## Critical Constraints

1. **No source code modification** - ONCE overwrites container nightly
2. **Read-only database access** - Use `?mode=ro` URI parameter
3. **External AI service** - Must live outside Campfire Docker
4. **Persistent knowledge base** - Store at `/root/ai-knowledge/`
5. **WAL mode compatibility** - Safe for concurrent reads

---

## System Improvements (v0.5.0)

**Status:** ✅ NATIVE SKILLS COMPLETE - Local validation successful (Nov 2, 2025)
**Foundation:** Anthropic's native Agent SDK skills pattern

### Native Skills Migration ⭐

**Architecture Change:**
```
External Skills MCP (deprecated) → Native Agent SDK Skills
```

**Implementation:**
- Added `setting_sources=["user", "project"]` to enable filesystem skills
- Added `"Skill"` builtin tool (replaces `mcp__skills__load_skill`)
- Consolidated 9 skills to `.claude/skills/` (Anthropic standard)
- Deprecated Skills MCP server (commented out for 2-4 week transition)

**Validation (Nov 2, 2025):**
- ✅ Skills auto-discovered from `.claude/skills/`
- ✅ Bot autonomously invoked Skill tool
- ✅ Real test: 22MB PPTX file → extracted Chinese text → translated to English → saved result
- ✅ All 9 skills working: docx, pptx, presentation-generation, code-generation, personal-productivity, etc.

**Status:** Ready for production deployment (personal_assistant pilot)

---

### Other Modules (Paused)

**1. Verification Module** (src/verification/)
- Status: Implementation complete, testing pending
- 170+ test cases created, 77% coverage

**2. Code Generation Module** (src/codegen/)
- Status: Implementation complete, integration with native skills pending
- Template-based generation ready

**3. Test Infrastructure** (tests/agent_behaviors/)
- Status: 3 critical path tests created
- Will be activated after native skills production validation

---

## Cost Estimates

| Item | Monthly Cost |
|------|--------------|
| DigitalOcean Droplet | $18 |
| Claude API (Haiku 4.5) | $30-100 |
| Supabase | Free tier |
| **Total** | **$50-120** |

---

**Document Version:** 10.0 (Condensed Architecture Reference)
**Last Updated:** November 2, 2025
**Production Status:** v0.4.0.2 ✅

**For Details:**
- Tool matrix and detailed workflows → See CLAUDE.md
- Complete version history → @docs/reference/VERSION_HISTORY.md
- Document processing architecture → @docs/reference/V0.4.0_DOCUMENT_PROCESSING_ARCHITECTURE.md
- Deployment procedures → IMPLEMENTATION_PLAN.md
