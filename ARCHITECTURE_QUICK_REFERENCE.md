# Campfire AI Bot - Architecture Quick Reference

**Production Version:** v0.5.2.2 ✅
**Development Version:** v0.5.3 🔄 (Code Execution with MCP - 85-95% token savings)
**Last Updated:** 2025-11-09

---

## System Overview

| Component | Value |
|-----------|-------|
| **Server** | DigitalOcean Droplet (128.199.175.50) |
| **Domain** | https://chat.smartice.ai |
| **Platform** | Campfire (37signals ONCE) - auto-updates nightly |
| **Framework** | FastAPI + Claude Agent SDK 0.1.4 |
| **Model** | claude-haiku-4-5-20251001 (all 7 bots) |
| **Database** | SQLite3 (WAL mode, read-only access) |
| **Deployment** | Docker (hengwoo/campfire-ai-bot:latest) |

---

## 7 Active Bots - 100% Migrated ✅

| Bot | Bot Key | Total Tools | Special Capabilities |
|-----|---------|-------------|---------------------|
| 财务分析师 (Financial Analyst) | `2-CsheovnLtzjM` | 35 | Excel analysis, Financial MCP (17 tools), file-based prompts ✅, native skills ✅ |
| 技术助手 (Technical Assistant) | `3-2cw4dPpVMk86` | 15 | Web research, knowledge base, file-based prompts ✅, native skills ✅ |
| 个人助手 (Personal Assistant) | `10-vWgb0YVbUSYs` | 21 | Tasks, reminders, automated reminders ✅, file-based prompts ✅, native skills ✅ |
| 日报助手 (Briefing Assistant) | `11-cLwvq6mLx4WV` | 17 | AI-powered daily briefings, file-based prompts ✅, native skills ✅ |
| 运营数据助手 (Operations Assistant) | `17-9bsKCPyVKUQC` | 28 | Supabase analytics, STAR framework, file-based prompts ✅, native skills ✅ |
| Claude Code 导师 (CC Tutor) | `18-7anfEpcAxCyV` | 15 | Claude Code education, 4.7K KB, file-based prompts ✅, native skills ✅ |
| 菜单工程师 (Menu Engineer) | `19-gawmDGiVGP4u` | 20 | Boston Matrix profitability, file-based prompts ✅, native skills ✅ |

**Migration:** All 7/7 bots now use file-based prompts (.md) + YAML configs + native Agent SDK skills

---

## Key File Locations

### Server Paths
```
/root/ai-service/               # AI Service (Docker)
├── .env                        # API keys (ANTHROPIC_API_KEY)
├── docker-compose.yml          # Production config
└── src/                        # Application code

/root/ai-knowledge/             # Knowledge Base
├── user_contexts/              # User preferences
├── company_kb/                 # Company documents
│   ├── briefings/             # Daily briefings
│   ├── claude-code/           # Claude Code tutorials (4.8K lines)
│   └── operations/            # Operations workflows (633 lines)
└── logs/                       # Application logs

/var/once/campfire/             # Campfire (managed by ONCE)
├── db/production.sqlite3       # Database (read-only mount)
└── files/                      # File attachments
```

### Local Development Paths
```
/Users/heng/Development/campfire/ai-bot/
├── src/                        # Source code
│   ├── app_fastapi.py         # FastAPI webhook server
│   ├── campfire_agent.py      # Agent SDK wrapper
│   ├── bot_manager.py         # Bot config loader
│   ├── prompt_loader.py       # File-based prompts (v0.4.1)
│   └── tools/                 # MCP tool implementations
├── bots/                       # Bot configs (JSON - legacy)
├── prompts/                    # File-based prompts (v0.4.1)
│   ├── bots/                  # Bot personalities (*.md)
│   ├── configs/               # Bot metadata (*.yaml)
│   └── skills/                # On-demand skills (*/SKILL.md)
└── knowledge-base/             # Knowledge base content
```

---

## Tool Categories & MCP Prefixes

| Category | MCP Prefix | Tool Count | Used By |
|----------|------------|------------|---------|
| Built-in SDK | (none) | 8 | All bots (WebSearch, WebFetch, Read, Grep, Glob, Task, Bash, **Skill** ⭐) |
| Campfire Base | `mcp__campfire__` | 7 | All bots (conversations, user context, knowledge base) |
| Native Skills | (builtin Skill tool) | 7+ custom | **All 7 bots** - Filesystem-based auto-discovery (v0.5.0) ✅ |
| Financial | `mcp__fin-report-agent__` | 17 | financial_analyst (Excel, financial calculations) |
| Operations | `mcp__operations__` | 3 | operations_assistant (Supabase queries) |
| Analytics | `mcp__analytics__` | 10 | operations_assistant (RPC functions) |
| Menu Engineering | `mcp__menu_engineering__` | 5 | menu_engineer (Boston Matrix analysis) |

**Note:** Skills MCP deprecated (v0.5.0) - All bots now use native Agent SDK Skill tool instead

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

**Access Mode:** Read-only with `PRAGMA query_only = ON` (WAL mode safe for concurrent reads)

---

## Common Operations

### Service Management
```bash
# Restart service
cd /root/ai-service && docker-compose restart

# View logs (live)
docker logs -f campfire-ai-bot

# View logs (last 50 lines)
docker logs --tail 50 campfire-ai-bot

# Health check
curl http://localhost:5000/health

# Stop service
cd /root/ai-service && docker-compose down

# Start service
cd /root/ai-service && docker-compose up -d
```

### Testing
```bash
# Test bot posting (via Campfire API)
curl -d 'Test message' \
  https://chat.smartice.ai/rooms/1/{BOT_KEY}/messages

# Test webhook (local)
curl -X POST http://localhost:8000/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":1,"name":"Test"},"room":{"id":1,"name":"Test"},"content":"你好"}'
```

### Database Queries
```bash
# Query Campfire database (read-only)
sqlite3 /var/once/campfire/db/production.sqlite3 -readonly

# List bots
SELECT id, name, bot_token FROM users WHERE role = 1;

# Recent messages
SELECT COUNT(*) FROM messages WHERE created_at > datetime('now', '-1 day');
```

---

## Architecture Patterns

### Request Flow
```
User @mention → Campfire webhook → FastAPI background task →
→ SessionManager (hot/warm/cold) → Claude Agent SDK →
→ MCP tools execution → Progress milestones →
→ Response streaming → Post to Campfire API
```

### Session Management (3 Tiers)
- **Tier 1 (Hot):** Reuse existing session (40% faster, <60s old)
- **Tier 2 (Warm):** Load from disk cache (20% faster, <15min old)
- **Tier 3 (Cold):** Create fresh session (full initialization)

### Multi-Bot Collaboration (v0.4.0)
- Any bot can spawn other bots as "subagents" via Task tool
- Peer-to-peer architecture (no central coordinator)
- Security: Subagents limited to safe tools (Read, Grep, Glob, WebSearch, WebFetch, Task)

### File-Based Prompts (v0.4.1)
- **Layer 1:** Bot personality (always loaded, ~200 lines)
- **Layer 2:** Skills (on-demand via load_skill(), 400-600 lines each)
- **Layer 3:** Dynamic context (runtime template variables: $current_date, $user_name, $room_name)

---

## Version Status

| Version | Status | Key Features |
|---------|--------|--------------|
| **v0.4.1** | ✅ COMPLETE | File-based prompts (PromptLoader), 3-layer architecture |
| **v0.5.0** | ✅ COMPLETE | Native Agent SDK skills (filesystem-based) |
| **v0.5.1** | ✅ COMPLETE | Automated reminders, cc_tutor migration |
| **v0.5.2** | ✅ COMPLETE | **Bot migration sprint - 100% completion** (5 bots migrated) |
| **v0.5.2.2** | ✅ **IN PRODUCTION** | Memory leak fix, file download URL fix, CI/CD pipeline |
| **v0.5.3** | 🔄 **IN DEVELOPMENT** | **Code execution with MCP - 85-95% token savings, 4 helper functions** |

### v0.5.3 - Code Execution with MCP ⚡

**Innovation:** Filter large documents in execution environment BEFORE returning to model

**Problem → Solution:**
```
Before: read_knowledge_document("claude-code/llm.txt")
        → 4,800 tokens to model (wasteful!)

After:  search_and_extract(query="MCP", category="claude-code")
        → 200-300 tokens to model (95% savings!)
```

**Helper Functions:**
1. `search_and_extract()` - High-level entry point (recommended)
2. `extract_section()` - Keyword-based filtering
3. `extract_by_headings()` - Structure-based extraction
4. `get_document_outline()` - Minimal token overview (~50 tokens)

**Performance:**
- Claude Code docs: 4,787 lines → ~200 tokens (**94% savings**)
- Operations docs: 633 lines → ~100 tokens (76-84% savings)
- Response time: **90% faster** (2.0s → 0.2s)

**Status:** Implementation complete, ready for pilot on personal_assistant bot

---

## Key Technical Constraints

1. **No source code modification** - Campfire managed by ONCE (nightly auto-updates)
2. **Read-only database access** - Use `?mode=ro` URI parameter
3. **External AI service** - Must live outside Campfire Docker
4. **Persistent knowledge base** - Store at `/root/ai-knowledge/`
5. **WAL mode compatibility** - Safe for concurrent reads

---

## Cost Estimates

| Item | Monthly Cost |
|------|--------------|
| DigitalOcean Droplet | $18 |
| Claude API (Haiku 4.5) | $30-100 |
| Supabase | Free tier |
| **Total** | **$50-120** |

---

## Emergency Procedures

### Rollback to Previous Version
```bash
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:0.4.0.2  # Last stable
docker-compose up -d
docker logs -f campfire-ai-bot
```

### Check System Health
```bash
# Container status
docker ps | grep campfire-ai-bot

# Health endpoint
curl http://localhost:5000/health

# Recent errors
docker logs campfire-ai-bot 2>&1 | grep -i error | tail -20
```

---

## See Also

- **DESIGN.md** - Full architecture and design decisions
- **CLAUDE.md** - Project memory and current status
- **IMPLEMENTATION_PLAN.md** - Deployment procedures and CI/CD
- **TROUBLESHOOTING.md** - Common issues and solutions
- **prompts/MIGRATION_SUMMARY.md** - File-based prompt architecture guide
- **ANTHROPIC_BEST_PRACTICES_ROADMAP.md** - v0.5.0 3-phase plan

---

---

## 🔍 Finding More Information

**Need detailed docs?** See this decision tree:

```
User asks about...                    → Load this file
├─ "What changed in v0.3.2?"         → @docs/reference/VERSION_HISTORY.md
├─ "Bot not responding"               → @docs/reference/TROUBLESHOOTING.md
├─ "How to deploy?"                   → @docs/reference/PRODUCTION_DEPLOYMENT_GUIDE.md
├─ "Test locally"                     → @docs/reference/LOCAL_TESTING_GUIDE.md
├─ "Document processing"              → @docs/reference/V0.4.0_DOCUMENT_PROCESSING_ARCHITECTURE.md
├─ "Operations assistant details"     → @ai-bot/archive/OPERATIONS_ASSISTANT_ENHANCEMENT.md
├─ "Menu engineering details"         → @ai-bot/archive/MENU_ENGINEERING_TECHNICAL_SUMMARY.md
└─ "Historical versions"              → @ai-bot/archive/README.md (66 files catalog)
```

**Default:** Only use this doc + CLAUDE.md + DESIGN.md + IMPLEMENTATION_PLAN.md unless user needs details.

---

**Quick Reference Version:** 3.0 (Updated with v0.5.3 Code Execution with MCP)
**Last Updated:** 2025-11-09
**Maintained By:** Development team
