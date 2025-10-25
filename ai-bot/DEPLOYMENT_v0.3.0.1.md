# Campfire AI Bot v0.3.0.1 Deployment Guide

**Version:** v0.3.0.1
**Release Date:** 2025-10-20
**Status:** Ready for Deployment

---

## 🎉 What's New in v0.3.0.1

### Critical Bug Fixes

#### 1. ✅ Built-in SDK Tools Now Available (CRITICAL FIX)

**Problem:** All built-in Agent SDK tools (WebSearch, WebFetch, Read, Write, Edit, Bash, Grep, Glob) were inadvertently blocked by the `allowed_tools` whitelist.

**Impact:** Bots couldn't:
- Search the web for information
- Fetch web page content
- Perform many file operations
- Execute shell commands

**Solution:** Updated `campfire_agent.py:_get_allowed_tools_for_bot()` to include all 8 built-in SDK tools for all bots.

**Result:** All 7 bots now have full access to built-in tools.

**Files Changed:**
- `src/campfire_agent.py` (lines 48-149)

---

#### 2. ✅ Chinese Progress Message

**Change:** Progress message now shows "努力工作ing" instead of "🤔 Processing your request..."

**Impact:** Better localization for Chinese users.

**Files Changed:**
- `src/app_fastapi.py` (line 418)

---

### New Features

#### 3. 📊 Operations Assistant Bot (NEW)

**Purpose:** Manage operations data via Supabase integration

**Capabilities:**
- Query operations data from Supabase tables
- Update project status, task progress, metrics
- Generate operations summary reports
- Access company knowledge base

**Implementation:**
- **New Module:** `src/tools/supabase_tools.py` (3 tools: query, update, summary)
- **New Agent Tools:** Registered in `src/agent_tools.py` (lines 975-1203)
- **New Bot Config:** `bots/operations_assistant.json`
- **Agent Integration:** `src/campfire_agent.py` (lines 138-146)

**Dependencies Added:**
- `supabase>=2.0.0` in `pyproject.toml`

**⚠️ BEFORE DEPLOYMENT:**
1. Create bot in Campfire web UI
2. Update `bot_key` in `bots/operations_assistant.json`
3. Set environment variables:
   ```bash
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-service-role-key
   ```

---

#### 4. 🎓 Claude Code Tutor Bot (NEW)

**Purpose:** Educational assistant for learning Claude Code

**Capabilities:**
- Getting started guides
- Tool usage tutorials
- MCP server integration help
- Agent SDK best practices
- Troubleshooting support

**Implementation:**
- **New Bot Config:** `bots/claude_code_tutor.json`
- **No code changes needed** (uses existing knowledge base tools)

**⚠️ BEFORE DEPLOYMENT:**
1. Create bot in Campfire web UI
2. Update `bot_key` in `bots/claude_code_tutor.json`
3. Build knowledge base content at `/root/ai-knowledge/company_kb/claude-code/`

**Knowledge Base Structure:**
```
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
│   ├── websearch-tool.md
│   └── webfetch-tool.md
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

---

### Documentation Updates

- **CLAUDE.md:** Added v0.3.0.1 status, documented bug fixes
- **DESIGN.md:** Added comprehensive tool access matrix
- **This file:** Complete deployment guide

---

## 📋 Pre-Deployment Checklist

### 1. Create New Bots in Campfire

Log into Campfire web UI and create 2 new bots:

**Operations Assistant:**
- Name: 运营数据助手
- Description: Operations data management with Supabase
- Copy the bot key → Update `bots/operations_assistant.json`

**Claude Code Tutor:**
- Name: Claude Code导师
- Description: Educational assistant for Claude Code
- Copy the bot key → Update `bots/claude_code_tutor.json`

### 2. Prepare Knowledge Base Content

Create Claude Code documentation:

```bash
# On production server
ssh root@128.199.175.50

# Create directory structure
mkdir -p /root/ai-knowledge/company_kb/claude-code/{getting-started,tools,mcp,agent-sdk,troubleshooting}

# TODO: Copy markdown files to these directories
# You can do this manually or use a script
```

**Content Sources:**
- https://docs.claude.com/en/docs/claude-code/
- Claude Code GitHub repository
- Community best practices

**Estimated time:** 2-3 hours to curate quality content

### 3. Set Up Supabase (Optional - for Operations Bot)

If deploying Operations Assistant:

1. Create Supabase project or use existing
2. Create tables: `projects`, `tasks`, `operations_metrics`
3. Get connection credentials:
   - Project URL: `https://xxx.supabase.co`
   - Service role key (from project settings)

### 4. Configure Daily Briefing Cron

**Option A: Host-Level Cron (Recommended)**

```bash
# On production server
crontab -e

# Add this line (generates briefing at 9am daily)
0 9 * * * docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py >> /root/ai-service/logs/briefing-cron.log 2>&1
```

**Option B: Docker Container Cron**

Install cron in Dockerfile (requires more changes - not recommended for this release)

---

## 🚀 Deployment Steps

### Step 1: Local Testing

```bash
cd /Users/heng/Development/campfire/ai-bot

# Update bot keys in configs
# Edit bots/operations_assistant.json → add bot_key
# Edit bots/claude_code_tutor.json → add bot_key

# Test locally (optional - requires local Supabase for ops bot)
PYTHONPATH=$(pwd) TESTING=true CAMPFIRE_URL=https://chat.smartice.ai uv run python src/app_fastapi.py
```

### Step 2: Build Docker Image

```bash
# Build for linux/amd64 platform
docker buildx build --platform linux/amd64 \
  -t hengwoo/campfire-ai-bot:0.3.0.1 \
  -t hengwoo/campfire-ai-bot:latest \
  .
```

### Step 3: Push to Docker Hub

```bash
docker push hengwoo/campfire-ai-bot:0.3.0.1
docker push hengwoo/campfire-ai-bot:latest
```

### Step 4: Update Production Environment Variables

```bash
# SSH to server
ssh root@128.199.175.50

# Edit .env file
cd /root/ai-service
nano .env

# Add these lines (if using Operations Assistant):
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
```

### Step 5: Deploy to Production

```bash
# On production server
cd /root/ai-service

# Stop current container
docker-compose down

# Pull new image
docker pull hengwoo/campfire-ai-bot:0.3.0.1

# Start container
docker-compose up -d

# Check logs
docker logs -f campfire-ai-bot
```

### Step 6: Verify Deployment

```bash
# Check health endpoint
curl http://localhost:5000/health
# Should return: {"status":"healthy","version":"0.3.0.1",...}

# Check bot list in startup logs
docker logs campfire-ai-bot | grep "BotManager"
# Should show 7 bots loaded

# Test a bot
curl -d 'Test message' https://chat.smartice.ai/rooms/1/<BOT_KEY>/messages
```

### Step 7: Configure Cron (if not done yet)

```bash
# Add cron job for daily briefing
crontab -e

# Add:
0 9 * * * docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py >> /root/ai-service/logs/briefing-cron.log 2>&1

# Verify cron is scheduled
crontab -l
```

### Step 8: Post-Deployment Testing

Test each bot via @mention in Campfire:

**Existing Bots (verify no regression):**
1. @财务分析师 - Test with "介绍一下你的功能"
2. @技术助手 - Test with "How do I...?"
3. @个人助手 - Test with "创建任务：测试"
4. @日报助手 - Test with "生成今天的日报"
5. AI Assistant - Test with general query

**New Bots:**
6. @运营数据助手 - Test with "查询项目列表" (requires Supabase)
7. @Claude Code导师 - Test with "How do I use the Read tool?"

**Built-in Tools (NEW - test across bots):**
- Test WebSearch: "@技术助手 Search for Claude Code documentation"
- Test WebFetch: "@个人助手 Fetch this webpage: https://example.com"
- Test Read: (Upload a file) "@财务分析师 Read this file"

---

## 🔍 Troubleshooting

### Issue: Bot not responding

```bash
# Check container status
docker ps

# Check logs for errors
docker logs campfire-ai-bot | tail -100

# Verify webhook URL in Campfire bot settings
```

### Issue: Operations bot says "Supabase tools not available"

```bash
# Check env vars are set
docker exec campfire-ai-bot env | grep SUPABASE

# Check logs for Supabase initialization
docker logs campfire-ai-bot | grep Supabase

# Should see: "[Supabase] ✅ Supabase tools initialized"
```

### Issue: Claude Code Tutor has no knowledge

```bash
# Check knowledge base exists
ls -la /root/ai-knowledge/company_kb/claude-code/

# Add content if missing
# Create markdown files with Claude Code documentation
```

### Issue: Daily briefing not generating

```bash
# Check cron is running
systemctl status cron

# Check cron logs
tail -f /root/ai-service/logs/briefing-cron.log

# Test manually
docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py --date 2025-10-20
```

---

## 📊 Summary of Changes

### Files Modified:
- `src/campfire_agent.py` - Added built-in tools + operations tools
- `src/app_fastapi.py` - Progress message + version updates
- `src/agent_tools.py` - Added Supabase tool wrappers
- `pyproject.toml` - Version + supabase dependency
- `Dockerfile` - Version update
- `CLAUDE.md` - Documentation updates
- `DESIGN.md` - Tool access matrix

### Files Created:
- `src/tools/supabase_tools.py` - Supabase integration (3 tools)
- `bots/operations_assistant.json` - Operations bot config
- `bots/claude_code_tutor.json` - Tutor bot config
- `DEPLOYMENT_v0.3.0.1.md` - This file

### Bot Count:
- Before: 5 bots
- After: 7 bots (+40% increase)

### Tool Count per Bot:
- Financial Analyst: 35 tools (8 built-in + 27 MCP)
- Technical Assistant: 15 tools (8 built-in + 7 MCP)
- Personal Assistant: 22 tools (8 built-in + 14 MCP)
- Briefing Assistant: 17 tools (8 built-in + 9 MCP)
- AI Assistant: 15 tools (8 built-in + 7 MCP)
- **Operations Assistant: 18 tools** (8 built-in + 10 MCP) ✨ NEW
- **Claude Code Tutor: 15 tools** (8 built-in + 7 MCP) ✨ NEW

---

## 🎯 Success Metrics

After deployment, verify:

- [ ] All 7 bots respond to @mentions
- [ ] Built-in tools work (WebSearch, WebFetch, Read, etc.)
- [ ] Progress message shows "努力工作ing"
- [ ] Operations bot can query Supabase (if configured)
- [ ] Claude Code Tutor provides helpful responses
- [ ] Daily briefing generates automatically at 9am
- [ ] No errors in logs for 24 hours
- [ ] Health endpoint returns v0.3.0.1

---

## 📝 Rollback Plan

If deployment fails:

```bash
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:0.3.0
docker-compose up -d
```

---

## 📅 Next Steps (v0.3.1+)

Potential future improvements:
- Enhanced Supabase schema for richer operations data
- More Claude Code tutorials and examples
- Advanced analytics and reporting features
- Integration with additional data sources
- Performance optimizations

---

**Deployment Prepared By:** Claude (Sonnet 4.5)
**Date:** 2025-10-20
**Deployment Window:** 1-2 hours
**Risk Level:** Low (backward compatible, new features are additive)

Ready for production deployment! 🚀
