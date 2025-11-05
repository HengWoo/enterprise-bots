# Campfire AI Bot - Architecture Quick Reference

**Version:** v0.4.1 (Production: v0.4.0.2)
**Last Updated:** 2025-10-30

---

## System Overview

| Component | Value |
|-----------|-------|
| **Server** | DigitalOcean Droplet (128.199.175.50) |
| **Domain** | https://chat.smartice.ai |
| **Platform** | Campfire (37signals ONCE) - auto-updates nightly |
| **Framework** | FastAPI + Claude Agent SDK 0.1.4 |
| **Model** | claude-haiku-4-5-20251001 (all 8 bots) |
| **Database** | SQLite3 (WAL mode, read-only access) |
| **Deployment** | Docker (hengwoo/campfire-ai-bot:latest) |

---

## 8 Active Bots

| Bot | Bot Key | Total Tools | Special Capabilities |
|-----|---------|-------------|---------------------|
| 财务分析师 (Financial Analyst) | `2-CsheovnLtzjM` | 35 | Excel analysis, Financial MCP (17 tools) |
| 技术助手 (Technical Assistant) | `3-2cw4dPpVMk86` | 15 | Knowledge base, web research |
| 个人助手 (Personal Assistant) | `4-GZfqGLxdULBM` | 22 | Tasks, reminders, Skills MCP (file-based prompts) |
| 日报助手 (Briefing Assistant) | `11-cLwvq6mLx4WV` | 17 | AI-powered daily briefings, historical search |
| AI Assistant (Default) | `10-vWgb0YVbUSYs` | 15 | General-purpose assistance |
| 运营数据助手 (Operations Assistant) | TBD | 28 | Supabase, STAR analytics (10 RPC functions) |
| Claude Code 导师 (CC Tutor) | TBD | 15 | Claude Code education, 4.7K line knowledge base |
| 菜单工程师 (Menu Engineer) | `19-gawmDGiVGP4u` | 20 | Boston Matrix profitability analysis (5 tools) |

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
│   ├── claude-code/           # Claude Code tutorials (4.7K lines)
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
| Built-in SDK | (none) | 8 | All bots (WebSearch, WebFetch, Read, Write, Edit, Bash, Grep, Glob) |
| Campfire Base | `mcp__campfire__` | 7 | All bots (conversations, user context, knowledge base) |
| Skills | `mcp__skills__` | 2 | personal_assistant, financial_analyst (progressive disclosure) |
| Financial | `mcp__fin-report-agent__` | 17 | financial_analyst (Excel, financial calculations) |
| Operations | `mcp__operations__` | 3 | operations_assistant (Supabase queries) |
| Analytics | `mcp__analytics__` | 10 | operations_assistant (RPC functions) |
| Menu Engineering | `mcp__menu_engineering__` | 5 | menu_engineer (Boston Matrix analysis) |

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
| **v0.4.0.2** | ✅ **IN PRODUCTION** | Config-driven tools, documentation consolidation |
| **v0.4.1** | ✅ READY (not deployed) | File-based prompts (PromptLoader + SkillsManager), 3-layer architecture |
| **v0.4.2** | 📋 PLANNED | Web presentation generation (reveal.js + Chart.js) |
| **v0.5.0** | 🔄 IN PROGRESS (84%) | Verification + Code generation + Testing |

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

**Quick Reference Version:** 1.0
**Last Updated:** 2025-10-30
**Maintained By:** Development team
