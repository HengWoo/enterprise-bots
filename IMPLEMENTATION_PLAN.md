# Campfire AI Bot - Implementation Guide

**Current Production:** v0.3.3 - Agent Tools Refactoring
**Status:** ✅ All 8 bots active and operational
**Last Deployed:** October 25, 2025

---

## 🔥 Current Status

**Production (v0.3.3):**
- ✅ claude-haiku-4-5-20251001 model across all 8 bots
- ✅ Agent Tools Refactoring: 2,418 → 154 lines (94% reduction)
- ✅ 7 modular decorator files by functional domain (46% total code reduction)
- ✅ Bug fix: Added missing AGENT_TOOLS export for SDK MCP server
- ✅ Supabase integration for operations and menu data
- ✅ FastAPI with stateful sessions (hot/warm/cold paths)
- ✅ Real-time progress milestones
- ✅ Knowledge base integration (Claude Code tutorials)
- ✅ Daily briefing automation
- ✅ Financial MCP server for Excel analysis

**Active Bots:**
1. 财务分析师 (Financial Analyst) - `2-CsheovnLtzjM`
2. 技术助手 (Technical Assistant) - `3-2cw4dPpVMk86`
3. 个人助手 (Personal Assistant) - `4-GZfqGLxdULBM`
4. 日报助手 (Briefing Assistant) - `11-cLwvq6mLx4WV`
5. AI Assistant (Default) - `10-vWgb0YVbUSYs`
6. 运营数据助手 (Operations Assistant) - `TBD`
7. Claude Code 导师 (CC Tutor) - `TBD`
8. 菜单工程师 (Menu Engineer) - `19-gawmDGiVGP4u`

---

## Quick Reference

### Local Development

```bash
# Test locally (from ai-bot directory)
cd /Users/heng/Development/campfire/ai-bot
PYTHONPATH=/Users/heng/Development/campfire/ai-bot \
  TESTING=true \
  CAMPFIRE_URL=https://chat.smartice.ai \
  uv run python src/app_fastapi.py

# Test webhook
curl -X POST http://localhost:8000/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":1,"name":"Test"},"room":{"id":1,"name":"Test"},"content":"介绍一下你的功能"}'
```

### Docker Deployment

```bash
# Build (local machine)
docker buildx build --platform linux/amd64 \
  -t hengwoo/campfire-ai-bot:0.3.0 \
  -t hengwoo/campfire-ai-bot:latest .

# Push to Docker Hub
docker push hengwoo/campfire-ai-bot:0.3.0
docker push hengwoo/campfire-ai-bot:latest

# Deploy on server (via DigitalOcean console)
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:latest
docker-compose up -d
docker logs -f campfire-ai-bot
```

### Health Checks

```bash
# Service health
curl http://localhost:5000/health

# Test bot posting
curl -d 'Test message' \
  https://chat.smartice.ai/rooms/1/2-CsheovnLtzjM/messages
```

### Database Access

```bash
# Query Campfire database (read-only)
sqlite3 /var/once/campfire/db/production.sqlite3 -readonly
> SELECT * FROM users WHERE role = 1;  -- List bots
> SELECT COUNT(*) FROM messages;
> .quit
```

---

## Infrastructure

**Server:** DigitalOcean Droplet (128.199.175.50)
- Domain: https://chat.smartice.ai
- OS: Ubuntu 25.04 x64 (2GB RAM, 1 vCPU)

**AI Service:** `/root/ai-service/`
- Framework: FastAPI + Claude Agent SDK
- Model: claude-haiku-4-5-20251001
- Port: 8000 (internal), 5000 (external)
- Deployment: Docker Hub → hengwoo/campfire-ai-bot:0.3.0

**File Locations:**
```
/root/ai-service/               # FastAPI app
/root/ai-service/.env           # API keys
/root/ai-knowledge/user_contexts/  # User preferences
/root/ai-knowledge/company_kb/     # Knowledge base
/var/once/campfire/db/production.sqlite3  # Campfire DB (read-only)
```

---

## Key Learnings

### Response Formatting

**Campfire renders HTML:**
- Use `<h2>`, `<h3>` for headings
- Use `<strong>`, `<code>` for emphasis
- Use `<ul><li>`, `<table>` for structure
- Blog-style layout: line-height 1.8-2.0, proper margins
- Configure bot system prompts to generate HTML

### Deployment Best Practices

1. Test locally first
2. Get user confirmation before Docker build
3. Build & push to Docker Hub
4. Deploy to production
5. Monitor logs for verification

**Anti-Pattern:** Deploying without local testing

### Version History

| Version | Changes | Status |
|---------|---------|--------|
| v1.0.x | Flask-based MVP | ✅ Deprecated |
| v0.2.0-0.2.2 | FastAPI + Sessions + Knowledge Base | ✅ Deployed |
| v0.2.3-0.2.4 | Briefing Bot + Multi-Bot System | ✅ Deployed |
| v0.3.0-0.3.2 | Haiku 4.5 + HTML + Menu Engineering | ✅ Deployed |
| **v0.3.3** | **Agent Tools Refactoring (46% code reduction)** | **✅ IN PRODUCTION** 🔥 |

---

## Deployment Checklist

**Pre-Deployment:**
- [ ] Local testing complete
- [ ] User confirmation received
- [ ] Version numbers updated in code

**Docker Build:**
- [ ] Build with correct version tag
- [ ] Push to Docker Hub
- [ ] Verify images on Docker Hub

**Production Deployment:**
- [ ] Stop existing container
- [ ] Pull latest image
- [ ] Start container
- [ ] Check logs for errors
- [ ] Verify bots respond correctly

**Post-Deployment:**
- [ ] Test each bot via @mention
- [ ] Verify knowledge base access
- [ ] Check daily briefing generation
- [ ] Monitor logs for 24 hours

---

## Troubleshooting

### Bot Not Responding

1. Check container status: `docker ps`
2. Check logs: `docker logs campfire-ai-bot`
3. Verify webhook URL in Campfire bot settings
4. Test health endpoint: `curl http://localhost:5000/health`

### Slow Responses

1. Check session cache: `curl http://localhost:5000/cache/stats`
2. Review progress milestones in logs
3. Verify database access (read-only mode)
4. Check API rate limits

### Knowledge Base Issues

1. Verify file structure: `ls -la /root/ai-knowledge/company_kb/`
2. Check file permissions
3. Test tool: `@财务分析师 列出所有知识库文档`

---

## 📋 Planned for v0.3.0.1

### Bug Fixes

**1. Daily Briefing Cron Not Working** (Priority: High)

**Problem:** Scheduled briefing automation not triggering
**Investigation Steps:**
```bash
# Check if cron job exists
crontab -l

# Test script manually
docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py --date 2025-10-20

# Check cron logs
tail -f /var/log/syslog | grep CRON
```

**Expected Solution:**
- Install cron in Docker container OR
- Use external cron on host that calls into container OR
- Use systemd timer as alternative

**2. Localize Progress Message to Chinese** (Priority: Low)

**Change Required:**
```python
# app_fastapi.py line ~400
# Before:
await post_acknowledgment(room_id, bot_key, "🤔 Processing your request...")

# After:
await post_acknowledgment(room_id, bot_key, "努力工作ing")
```

**Files to Update:**
- `src/app_fastapi.py` (main acknowledgment)
- Consider bot-specific messages in bot configs

**3. Bot Tool Access Audit and Fix** (Priority: High)

**Problem:** Personal assistant bot claims WebFetch tool not available when user requests web translation

**Investigation:**

Current `tools_enabled` in bot configs only includes custom MCP tools, not built-in Claude Code tools:

```bash
# Personal Assistant current tools:
- search_conversations
- get_user_context
- save_user_preference
- manage_personal_tasks
- set_reminder
- save_personal_note
- search_personal_notes
# Missing: WebFetch, process_file
```

**Required Tool Audit Matrix:**

| Bot | Current Tools | Should Add |
|-----|--------------|------------|
| Financial Analyst | 3 base + Financial MCP | WebFetch?, query_knowledge_base |
| Technical Assistant | 3 base | WebFetch, process_file, query_knowledge_base |
| Personal Assistant | 7 custom | **WebFetch**, process_file, query_knowledge_base |
| Briefing Assistant | 5 base + 2 briefing | query_knowledge_base, read_knowledge_document |
| Default | 2 base | WebFetch, query_knowledge_base |

**Implementation Steps:**

1. **Review Each Bot's Intended Capabilities:**
   ```bash
   # Check system prompts for claimed capabilities
   grep -A 5 "专业能力" bots/*.json
   grep -A 5 "capabilities" bots/*.json
   ```

2. **Add Missing Tools to Bot Configs:**
   ```json
   // Example for personal_assistant.json
   "tools_enabled": [
     "search_conversations",
     "get_user_context",
     "save_user_preference",
     "manage_personal_tasks",
     "set_reminder",
     "save_personal_note",
     "search_personal_notes",
     "WebFetch",              // ADD: For web content
     "process_file",          // ADD: For file analysis
     "query_knowledge_base"   // ADD: For KB access
   ]
   ```

3. **Verify Tool Registration in campfire_agent.py:**
   ```python
   # Ensure all listed tools are properly registered
   # Check allowed_tools parameter passed to Agent SDK
   ```

4. **Update System Prompts:**
   - Remove claims about capabilities if tools not enabled
   - OR add tools and update prompts to guide proper usage

**Testing:**
```bash
# Test each bot with tool-specific requests
curl -X POST http://localhost:8000/webhook/personal_assistant \
  -d '{"content": "Please translate this article: https://example.com/article"}'

# Verify bot can use WebFetch
# Check logs for tool usage confirmation
```

### New Features

**4. Operations Data Bot with Supabase Integration** (Priority: Medium)

**Implementation Plan:**

1. **Add Supabase Dependency**
   ```bash
   # Add to pyproject.toml
   dependencies = [
       "supabase>=2.0.0",
       # ... existing deps
   ]
   ```

2. **Create Bot Configuration**
   ```bash
   # Create bots/operations_assistant.json
   {
     "bot_id": "operations_assistant",
     "bot_key": "TBD",  # Create bot in Campfire first
     "name": "运营数据助手",
     "model": "claude-haiku-4-5-20251001",
     "tools_enabled": [
       "query_operations_data",
       "update_operations_data",
       "get_operations_summary"
     ]
   }
   ```

3. **Implement Supabase MCP Tools**
   ```bash
   # Create src/tools/supabase_tools.py
   # Implement:
   # - query_operations_data(table, filters, limit)
   # - update_operations_data(table, id, data)
   # - get_operations_summary(date_range)
   ```

4. **Environment Configuration**
   ```bash
   # Add to .env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-service-role-key
   ```

**Testing:**
- Local testing with test Supabase project
- Verify CRUD operations
- Test with real operations data schema

**5. Claude Code Tutor Bot** (Priority: Medium)

**Implementation Plan:**

1. **Build Knowledge Base**
   ```bash
   # Create directory structure
   /root/ai-knowledge/company_kb/claude-code/
   ├── getting-started/
   │   ├── installation.md
   │   ├── first-steps.md
   │   └── basic-workflow.md
   ├── tools/
   │   ├── read-tool.md
   │   ├── write-tool.md
   │   ├── edit-tool.md
   │   ├── bash-tool.md
   │   └── agent-tool.md
   ├── mcp/
   │   ├── what-is-mcp.md
   │   ├── creating-mcp-servers.md
   │   └── best-practices.md
   ├── agent-sdk/
   │   ├── overview.md
   │   ├── patterns.md
   │   └── examples.md
   └── troubleshooting/
       ├── common-issues.md
       └── debugging-tips.md
   ```

2. **Curate Content**
   - Scrape/download Claude Code docs from docs.claude.com
   - Add examples from GitHub repos
   - Document common patterns and workflows
   - Create step-by-step guides

3. **Create Bot Configuration**
   ```bash
   # Create bots/claude_code_tutor.json
   {
     "bot_id": "claude_code_tutor",
     "bot_key": "TBD",
     "name": "Claude Code 导师",
     "model": "claude-haiku-4-5-20251001",
     "system_prompt": "You are an expert Claude Code tutor...",
     "tools_enabled": [
       "search_conversations",
       "query_knowledge_base",
       "read_knowledge_document"
     ]
   }
   ```

4. **Testing:**
   - Test with common user questions
   - Verify knowledge base retrieval
   - Ensure accurate, helpful responses

**Deployment Checklist for v0.3.0.1:**

**Bug Fixes:**
- [ ] Fix daily briefing cron issue
- [ ] Update progress message to Chinese ("努力工作ing")
- [ ] Audit all 5 bot configurations for tool access
- [ ] Add missing tools to bot configs (WebFetch, process_file, query_knowledge_base)
- [ ] Test each bot with tool-specific requests
- [ ] Update system prompts to match actual capabilities

**New Features:**
- [ ] Add supabase-py dependency
- [ ] Implement Supabase MCP tools (query, update, summary)
- [ ] Create operations_assistant bot config
- [ ] Test Supabase integration locally
- [ ] Build Claude Code knowledge base structure
- [ ] Curate Claude Code documentation content
- [ ] Create claude_code_tutor bot config
- [ ] Test tutor bot responses

**Deployment:**
- [ ] Update documentation (CLAUDE.md, IMPLEMENTATION_PLAN.md)
- [ ] Build Docker image: v0.3.0.1
- [ ] Push to Docker Hub
- [ ] Deploy to production
- [ ] Verify all 7 bots working (5 current + 2 new)
- [ ] Monitor logs for 24-48 hours

**Estimated Timeline:** 1-2 weeks
**Target Completion:** Early November 2025

---

## Emergency Rollback

If deployment fails:

```bash
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:0.2.4  # Previous stable version
docker-compose up -d
docker logs -f campfire-ai-bot
```

---

**Document Version:** 7.0 (v0.3.3 Deployment Guide)
**Last Updated:** October 25, 2025
**Production Status:** v0.3.3 deployed ✅
**For Details:** See CLAUDE.md (project memory), DESIGN.md (architecture)
