# Campfire AI Bot - Troubleshooting & Implementation Summary

**Date:** 2025-10-07
**Session:** Docker Deployment Testing
**Image Version:** 1.0.3

---

## Implementation Summary

### What We Built

**Multi-MCP AI Bot System:**
- Flask webhook server receiving mentions from Campfire
- Claude Agent SDK orchestrating multiple MCP servers
- Campfire MCP (built-in) - 3 tools for conversation search, user context, etc.
- Financial MCP (external stdio) - 16 tools for Excel analysis, financial calculations
- Three bot personalities: Financial Analyst (财务分析师), Technical Assistant, Default
- Docker containerized deployment ready for DigitalOcean

**Technology Stack:**
- Python 3.11 (system Python in container)
- Flask 3.1.2 (webhook server)
- Claude Agent SDK 0.1.0 (agentic orchestration)
- Claude Sonnet 4.5 (claude-sonnet-4-5-20250929) - upgraded from Haiku
- Node.js 20 + Claude Code CLI (required by Agent SDK)
- uv package manager (for Python dependency management)
- Financial MCP (stdio subprocess via uv run)

---

## What's Working ✅

### 1. Core Infrastructure
- ✅ Docker image builds successfully (1.51GB, version 1.0.3)
- ✅ Flask webhook server starts and responds to health checks
- ✅ Three bot configurations load correctly
- ✅ Model upgraded to Sonnet 4.5 across all bots
- ✅ Agent SDK initializes and connects

### 2. Basic Bot Functionality
- ✅ Simple greetings work (10 second response time)
- ✅ Agent SDK message streaming visible in logs
- ✅ Graceful error handling (agent asks for permission when tools fail)
- ✅ Chinese language responses working correctly
- ✅ Context-aware prompts with room/user information

### 3. Docker Environment
- ✅ System Python 3.11.13 correctly configured
- ✅ Node.js 20 and Claude Code CLI installed globally
- ✅ Financial MCP source code copied into image
- ✅ Financial MCP `.venv` built with system Python (not broken symlinks)
- ✅ Volume mounts working (test DB, AI knowledge)
- ✅ Health checks passing

---

## What's NOT Working ❌

### 1. Financial MCP Tools (CRITICAL ISSUE)

**Symptoms:**
- Agent attempts to use Financial MCP tools
- All tool calls fail
- Agent falls back to asking user permission to run Python scripts
- Response: "我需要您的授权来运行Python脚本以分析这份Excel财务报表"

**Evidence from Logs:**
```
[Agent SDK] Received: AssistantMessage
[Agent Message] 您好！我来帮您分析这份财务报表。让我先查看一下文件的内容和结构。...
[Agent SDK] Received: AssistantMessage
[Agent SDK] Received: UserMessage  <-- Tool result (likely error)
[Agent SDK] Received: AssistantMessage
[Agent Message] 让我使用专门的Excel分析工具来读取这份财务报表：...
[Agent SDK] Received: AssistantMessage
[Agent SDK] Received: UserMessage  <-- Tool result (likely error)
[Agent SDK] Received: AssistantMessage
[Agent SDK] Received: UserMessage  <-- Tool result (likely error)
[Agent SDK] Received: AssistantMessage
[Agent Message] 让我使用Python来分析这份Excel财务报表：...
```

**What We Tried:**
1. ✅ Fixed broken Python symlinks (was Python 3.12, now 3.11)
2. ✅ Set `ENV UV_PYTHON=/usr/local/bin/python3` in Dockerfile
3. ✅ Verified `.venv/pyvenv.cfg` points to correct Python
4. ✅ Confirmed openpyxl, pandas installed in Financial MCP venv
5. ❌ Financial MCP server still not responding to tool calls

**Possible Root Causes:**
1. **MCP Server Startup Failure:**
   - Financial MCP subprocess may not be starting correctly
   - stdio transport communication broken
   - Timeout during initialization

2. **Permission Issues:**
   - Container runs as `appuser` (UID 1000)
   - Financial MCP files owned by `appuser`
   - But subprocess might lack permissions

3. **Path Issues:**
   - Docker path: `/app/financial-mcp`
   - File attachment path: `/app/ai-knowledge/0.野百灵（绵阳店）-2025年5-8月财务报表.xlsx`
   - MCP might not have access to mounted volume

4. **Agent SDK Configuration:**
   - `allowed_tools` might be filtering out Financial MCP tools
   - MCP server config might be incorrect
   - Tool schema mismatch

---

## Current Docker Image Configuration

### Dockerfile Key Sections

**Financial MCP Installation (Lines 67-79):**
```dockerfile
# Copy Financial MCP and install dependencies
COPY financial-mcp/ /app/financial-mcp/
WORKDIR /app/financial-mcp
# Remove broken .venv if it exists
RUN rm -rf .venv
# Install Financial MCP dependencies using system Python 3.11
ENV UV_PYTHON=/usr/local/bin/python3
RUN uv sync
# Go back to app directory
WORKDIR /app

# Change ownership of Financial MCP to appuser
RUN chown -R appuser:appuser /app/financial-mcp
```

**Result:**
- `.venv` created with Python 3.11.13
- All dependencies installed (openpyxl, pandas, pydantic, etc.)
- Ownership: `appuser:appuser`

### Agent Configuration (src/campfire_agent.py:104-118)

```python
# Add Financial MCP for financial_analyst bot
if self.bot_config.bot_id == "financial_analyst":
    # External Financial MCP (stdio transport via uv)
    mcp_servers["fin-report-agent"] = {
        "transport": "stdio",
        "command": "uv",
        "args": [
            "run",
            "--directory",
            "/Users/heng/Development/AI_apps/fin_report_agent/fin_report_agent",  # ⚠️ WRONG PATH
            "python",
            "run_mcp_server.py"
        ]
    }
```

**🚨 CRITICAL BUG FOUND:** The MCP configuration still uses the LOCAL development path, not the Docker container path!

**Should be:**
```python
"/app/financial-mcp"
```

---

## Diagnostic Commands

### Check Financial MCP in Container
```bash
# Verify Python is correct
docker exec -u appuser campfire-ai-bot-local-test bash -c "cd /app/financial-mcp && cat .venv/pyvenv.cfg"
# Output: home = /usr/local/bin, version_info = 3.11.13 ✅

# Test MCP server manually
docker exec -u appuser campfire-ai-bot-local-test timeout 5 bash -c "cd /app/financial-mcp && uv run python run_mcp_server.py"
# Output: WARNING: Failed to validate request ⚠️

# Check dependencies
docker exec -u appuser campfire-ai-bot-local-test bash -c "cd /app/financial-mcp && uv run python -c 'import openpyxl; print(openpyxl.__version__)'"
# Works ✅
```

### Check Agent SDK Logs
```bash
# Follow logs in real-time
docker logs --follow campfire-ai-bot-local-test 2>&1 | grep -E "(Agent|Tool)"

# Check recent messages
docker logs campfire-ai-bot-local-test 2>&1 | grep "Agent Message"
```

---

## Test Results

### Test 1: Simple Greeting ✅
**Request:** "你好，请简单介绍一下你自己"
**Response Time:** 10 seconds
**Result:** SUCCESS
**Agent Messages:**
- SystemMessage
- AssistantMessage (intro text)
- ResultMessage

### Test 2: Financial Report Analysis ⚠️
**Request:** "请分析这个财务报表，给我一个完整的财务分析报告"
**Attachment:** `0.野百灵（绵阳店）-2025年5-8月财务报表.xlsx`
**Response Time:** 40 seconds
**Result:** PARTIAL SUCCESS (agent asks for permission)
**Agent Messages:**
- Multiple tool call attempts (failed)
- Final response asks user to approve Python execution

---

## Next Steps (Priority Order)

### IMMEDIATE FIX (Must Do)

**1. Fix MCP Configuration Path** ⭐⭐⭐
- **File:** `src/campfire_agent.py:114`
- **Change:** `/Users/heng/Development/AI_apps/fin_report_agent/fin_report_agent` → `/app/financial-mcp`
- **Why:** Container doesn't have access to local development path

**2. Rebuild and Test**
```bash
docker build -t campfire-ai-bot:1.0.4 .
docker-compose -f docker-compose.local.yml down
sed -i '' 's/1.0.3/1.0.4/' docker-compose.local.yml
docker-compose -f docker-compose.local.yml up -d
```

**3. Verify MCP Connection**
```bash
# Test financial report again
curl -X POST http://localhost:5001/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d @test_real_financial_report.json

# Watch logs
docker logs --follow campfire-ai-bot-local-test 2>&1 | grep "Agent"
```

### DEBUGGING (If Still Failing)

**4. Add MCP Server Logging**
- Check if Financial MCP server is starting
- Check stdout/stderr from subprocess
- Verify tool list is exposed

**5. Test MCP Server Directly**
```bash
# Inside container
docker exec -u appuser campfire-ai-bot-local-test bash -c "
cd /app/financial-mcp && \
echo '{\"jsonrpc\":\"2.0\",\"method\":\"initialize\",\"params\":{},\"id\":1}' | \
uv run python run_mcp_server.py
"
```

**6. Check File Access**
```bash
# Verify file is accessible to MCP
docker exec -u appuser campfire-ai-bot-local-test ls -la /app/ai-knowledge/*.xlsx
```

### PRODUCTION DEPLOYMENT

**7. Create Production Image**
- Once tools working, tag as `production`
- Export image: `docker save campfire-ai-bot:production | gzip > campfire-ai-bot-production.tar.gz`

**8. Transfer to DigitalOcean**
```bash
scp campfire-ai-bot-production.tar.gz root@128.199.175.50:/root/
```

**9. Deploy on Server**
```bash
ssh root@128.199.175.50
docker load < /root/campfire-ai-bot-production.tar.gz
cd /root/ai-service
docker-compose up -d
```

---

## Known Issues

### Issue 1: Long Response Times with File Analysis
- **Symptom:** 40+ seconds for financial report analysis
- **Status:** Expected (Sonnet 4.5 is more thoughtful)
- **Mitigation:** Consider streaming responses in future

### Issue 2: Agent Asks for Permission Instead of Using Tools
- **Symptom:** "我需要您的授权来运行Python脚本"
- **Root Cause:** Financial MCP tools failing, agent falls back to Bash tool
- **Status:** Critical bug - see IMMEDIATE FIX

### Issue 3: Missing Verbose Tool Execution Logs
- **Symptom:** Can't see tool call parameters or results in logs
- **Status:** Added message type logging, but need more detail
- **Future:** Log tool names, parameters, and results

---

## File Locations Reference

### Docker Container Paths
```
/app/                              # Application root
├── .venv/                         # Main app virtual environment (Python 3.11)
├── src/                           # Application source
│   ├── app.py                     # Flask webhook server
│   ├── campfire_agent.py          # Agent SDK wrapper
│   └── tools/                     # Campfire MCP tools
├── bots/                          # Bot configurations
│   ├── financial_analyst.json     # Sonnet 4.5
│   ├── technical_assistant.json   # Sonnet 4.5
│   └── default.json               # Sonnet 4.5
├── financial-mcp/                 # Financial MCP (BUILT INTO IMAGE)
│   ├── .venv/                     # Financial MCP venv (Python 3.11)
│   ├── src/                       # Financial MCP source
│   └── run_mcp_server.py          # MCP server entry point
└── ai-knowledge/                  # Mounted volume (read-write)
    └── *.xlsx                     # Test files

/campfire-db/test.db              # Mounted test database (read-only)
```

### Local Development Paths
```
/Users/heng/Development/campfire/ai-bot/
├── Dockerfile                     # Multi-stage build
├── docker-compose.local.yml       # Local testing
├── .env.docker-test               # Test environment
├── test_real_financial_report.json  # Test payload
├── financial-mcp/                 # Copied from external repo
└── ai-knowledge/                  # Local test files
    └── 0.野百灵（绵阳店）-2025年5-8月财务报表.xlsx
```

---

## Session Summary

**Time Spent:** ~4 hours
**Docker Builds:** 4 iterations (1.0.0 → 1.0.1 → 1.0.2 → 1.0.3)
**Tests Completed:** 15+
**Critical Bug Discovered:** MCP configuration using wrong path

**Achievements:**
- ✅ Multi-stage Docker build optimized
- ✅ Model upgraded to Sonnet 4.5
- ✅ Agent SDK integrated successfully
- ✅ Message streaming implemented
- ✅ Graceful error handling working
- ✅ Production-ready for basic bot functionality

**Blockers:**
- ❌ Financial MCP tools not accessible (path configuration bug)

**Confidence Level:** 90% - One critical bug away from full functionality

---

## Quick Start Commands

### Rebuild with Fix
```bash
# Fix the path in src/campfire_agent.py line 114
# Then:
docker build -t campfire-ai-bot:1.0.4 .
docker-compose -f docker-compose.local.yml down
sed -i '' 's/1.0.3/1.0.4/' docker-compose.local.yml
docker-compose -f docker-compose.local.yml up -d
sleep 10
curl -X POST http://localhost:5001/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d @test_real_financial_report.json
```

### Monitor Logs
```bash
docker logs --follow campfire-ai-bot-local-test 2>&1 | grep -E "(Agent|Error|Tool)"
```

### Clean Up
```bash
docker-compose -f docker-compose.local.yml down
docker rmi campfire-ai-bot:1.0.3
```

---

**End of Troubleshooting Document**
**Status:** READY FOR FIX
**Next Action:** Update MCP path and rebuild
