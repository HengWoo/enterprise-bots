# Campfire AI Bot Project

## 📚 Essential Documentation

**For new Claude sessions, read these files:**

1. **@DESIGN.md** - System architecture and database structure
2. **@IMPLEMENTATION_PLAN.md** - Deployment guide and procedures
3. **This file (CLAUDE.md)** - Current status and infrastructure overview

---

## 🔥 Current Production Status

**Production Version:** v0.3.3.1 ✅
**Last Deployed:** 2025-10-25
**Status:** All systems operational

**v0.4.0 Status:** 🟢 Ready for Production Deployment
**Testing Complete:** 2025-10-25 (All 13 tests passed)
**Security Status:** ✅ Perfect (0 violations)

**Latest Version (v0.4.0 - Ready for Deployment):**
- ✅ **Multi-Bot Collaboration** via Task tool (peer-to-peer subagent architecture)
- ✅ **Critical Security Fixes** (all 8 bots read-only, no Write/Edit/Bash via webhooks)
- ✅ **Subagent Security** (dangerous tools excluded from subagent mappings)
- ✅ **System Prompt Guardrails** (all 8 bot configs updated with security restrictions)
- ✅ **Document Processing Architecture** (PDF via Read native, Images via Claude vision, DOCX via Skills MCP + pandoc, PPTX via Skills MCP + markitdown)
- ✅ **Bash Tool Re-enabled** for personal_assistant (safe in Docker sandbox for document processing)
- ✅ **PPTX Support Added** (text extraction, visual analysis, editing via Skills MCP)
- ✅ **Comprehensive Testing** (13 scenarios across 4 categories, all passed)
- ✅ **Test Infrastructure** (test_phase6_multibot.py created)
- ✅ **Documentation Complete** (V0.4.0_LOCAL_TEST_RESULTS.md, V0.4.0_DOCUMENT_PROCESSING_ARCHITECTURE.md)

**Previous Version (v0.3.3.1):**
- ✅ Image Processing (all bots via Claude API)
- ✅ Agent Tools Refactoring (46% code reduction)
- ✅ 8 specialized bots operational

**Working Features:**
- ✅ **NEW v0.4.0**: Multi-Bot Collaboration (Task tool + subagent coordination)
- ✅ **NEW v0.4.0**: Two-Layer Security Protection (code + prompt restrictions)
- ✅ FastAPI + Stateful Sessions (hot/warm/cold paths, 40% faster responses)
- ✅ Real-time Progress Milestones (50%+ perceived speed improvement)
- ✅ 8 Specialized Bots with Haiku 4.5 model
- ✅ AI-Powered Daily Briefing Generation
- ✅ Knowledge Base Integration (Claude Code tutorials)
- ✅ Financial MCP Server (Excel analysis)
- ✅ Skills MCP (progressive skill disclosure)
- ✅ Supabase Integration (Operations + Menu Engineering)
- ✅ Image Processing (all bots via Claude API)

---

## Project Overview

AI-powered intelligent bot system for Campfire group chat that transforms team communication into an AI-augmented collaborative workspace with context-aware assistants.

## Infrastructure

- **Server:** DigitalOcean Droplet at 128.199.175.50
- **Domain:** https://chat.smartice.ai
- **Platform:** Campfire (37signals ONCE) - auto-updates nightly at 2am
- **Database:** SQLite at `/var/once/campfire/db/production.sqlite3` (WAL mode)
- **AI Service:** `/root/ai-service/` (Docker: hengwoo/campfire-ai-bot:0.3.3.1)
- **Knowledge Base:** `/root/ai-knowledge/company_kb/`

## Bot Configuration

**All 8 bots are ACTIVE in production:**

1. **财务分析师 (Financial Analyst)** - Bot Key: `2-CsheovnLtzjM`
   - Model: `claude-haiku-4-5-20251001`
   - Capabilities: Financial analysis, Excel processing, knowledge base access

2. **技术助手 (Technical Assistant)** - Bot Key: `3-2cw4dPpVMk86`
   - Model: `claude-haiku-4-5-20251001`
   - Capabilities: Technical support, documentation, knowledge base access

3. **个人助手 (Personal Assistant)** - Bot Key: `4-GZfqGLxdULBM`
   - Model: `claude-haiku-4-5-20251001`
   - Capabilities: Personal task management, reminders, knowledge base access

4. **日报助手 (Briefing Assistant)** - Bot Key: `11-cLwvq6mLx4WV`
   - Model: `claude-haiku-4-5-20251001`
   - Capabilities: AI-powered daily briefing generation, historical briefing search

5. **AI Assistant (Default)** - Bot Key: `10-vWgb0YVbUSYs`
   - Model: `claude-haiku-4-5-20251001`
   - Capabilities: General-purpose AI assistance

6. **运营数据助手 (Operations Assistant)** - Bot Key: `TBD`
   - Model: `claude-haiku-4-5-20251001`
   - Capabilities: Supabase data queries, operational analytics (v0.3.0.1)

7. **Claude Code 导师 (CC Tutor)** - Bot Key: `TBD`
   - Model: `claude-haiku-4-5-20251001`
   - Capabilities: Claude Code education, troubleshooting, knowledge base (v0.3.0.1)

8. **菜单工程师 (Menu Engineer)** - Bot Key: `19-gawmDGiVGP4u`
   - Model: `claude-haiku-4-5-20251001`
   - Capabilities: Boston Matrix analysis, dish profitability, cost coverage (v0.3.2)

**Webhook Pattern:** `http://128.199.175.50:5000/webhook/{bot_id}`
**API Pattern:** `POST https://chat.smartice.ai/rooms/{room_id}/{bot_key}/messages`

## Architecture Summary

```
Campfire (Docker) → Webhook → AI Service (FastAPI) → Claude API
                        ↓           ↓
                   Campfire DB  Knowledge Base
                   (read-only)  (/root/ai-knowledge/)
```

## Key Technical Stack

- **AI Framework:** Claude Agent SDK 0.1.4
- **AI Model:** claude-haiku-4-5-20251001
- **Backend:** Python 3.11 + FastAPI + uvicorn
- **Database:** SQLite3 (read-only, WAL mode)
- **MCP Tools:** 9 total (3 conversations + 4 knowledge base + 2 briefing)
- **Progressive Skills:** Skills MCP server (custom implementation)
- **File Processing:** Financial MCP (Excel), openpyxl
- **Deployment:** Docker multi-stage build

## Data Locations

- **Campfire Database:** `/var/once/campfire/db/production.sqlite3`
- **Campfire Files:** `/var/once/campfire/files/{hash}/`
- **AI Service:** `/root/ai-service/` (Docker container)
- **Knowledge Base:** `/root/ai-knowledge/company_kb/`
- **Daily Briefings:** `/root/ai-knowledge/company_kb/briefings/YYYY/MM/`
- **User Contexts:** `/root/ai-knowledge/user_contexts/`

## Critical Constraints

- **No source code modification** - ONCE overwrites container nightly
- **Read-only database access** - Use `?mode=ro` URI parameter
- **External AI service** - Must live outside Campfire Docker
- **Persistent knowledge base** - Store at `/root/ai-knowledge/`
- **WAL mode compatibility** - Safe for concurrent reads

## Development Commands

```bash
# SSH to server (use DigitalOcean console - SSH blocked by Cloudflare VPN)
ssh root@128.199.175.50

# Test bot posting
curl -d 'Test message' https://chat.smartice.ai/rooms/1/{BOT_KEY}/messages

# View container logs
docker logs -f campfire-ai-bot

# Restart AI service
cd /root/ai-service && docker-compose restart

# Check database
sqlite3 /var/once/campfire/db/production.sqlite3 -readonly
```

## Deployment Commands

```bash
# Standard deployment
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:latest
docker-compose up -d
docker logs -f campfire-ai-bot
```

## 📋 Planned Improvements

**Issues to Address:**

1. **⚠️ Daily Briefing Cron Issue** (Priority: High)
   - **Problem:** Scheduled briefing automation not working - cron event not registering
   - **Investigation:** Check cron setup, verify script permissions, test cron execution
   - **Location:** `/root/ai-service/scripts/generate_daily_briefing.py`
   - **Expected Fix:** Proper cron job installation and verification

2. **🇨🇳 Chinese Progress Message** ✅ (Fixed in v0.3.0.1)
   - **Change:** Replace "🤔 Processing your request..." with "努力工作ing"
   - **File:** `app_fastapi.py` line 418
   - **Status:** Completed - now shows "努力工作ing" for better Chinese localization

3. **🚨 CRITICAL: Built-in SDK Tools Were Blocked** ✅ (Fixed in v0.3.0.1)
   - **Problem:** Built-in Agent SDK tools (WebSearch, WebFetch, Read, Write, Edit, Bash, Grep, Glob) were inadvertently blocked by `allowed_tools` whitelist
   - **Root Cause:** The `allowed_tools` parameter only included MCP tools, blocking all built-in SDK tools
   - **Impact:** Bots couldn't search the web, fetch URLs, or use other powerful built-in capabilities
   - **Fix:** Updated `campfire_agent.py:_get_allowed_tools_for_bot()` to include built-in SDK tools for all bots
   - **Result:** All 5 bots now have access to:
     - 🌐 WebSearch & WebFetch - Search and fetch web content
     - 📄 Read, Write, Edit - File operations
     - 💻 Bash - Shell command execution
     - 🔍 Grep, Glob - File and content searching
   - **File:** `src/campfire_agent.py` lines 48-140
   - **Reference:** https://docs.claude.com/en/api/agent-sdk/overview

4. **🔴 CRITICAL: PDF Infinite Loop Issue** ✅ (Fixed in v0.3.0.1)
   - **Problem:** Personal assistant bot gets stuck in infinite loop when user asks to analyze PDF files
   - **Symptoms:** 60+ Read tool calls with binary search pattern, 5+ minute hangs, queue blocking
   - **Root Cause:** Bot system prompt claimed PDF/Excel/PPT support but skills not installed
   - **Impact:** Bot becomes unresponsive, subsequent requests fail with "I'm overloaded"
   - **Fix:** Updated `bots/personal_assistant.json` with:
     - Removed false claims about xlsx/pptx/pdf support
     - Added explicit "暂不支持" messages for PDF/Excel/PPT
     - Added "CRITICAL: 工具使用限制" section with max 3 retries per tool
     - Added file type detection before processing
     - Updated capabilities flags to reflect reality (docx: true, pdf/xlsx/pptx: false)
   - **Result:** PDF requests now return clear "not supported" message within 10 seconds instead of 5+ minute hang
   - **Files:** `bots/personal_assistant.json` (fixed), `PDF_INFINITE_LOOP_ISSUE.md` (analysis), `PDF_FIX_DEPLOYMENT.md` (deployment guide)
   - **Status:** ✅ Fixed and tested locally, ready for production deployment

**New Features Completed:**

5. **📊 Operations Assistant Enhanced with Analytical Framework** ✅ (Completed in v0.3.0.1)
   - **Purpose:** Transform from data query tool to data analyst
   - **What was added:**
     - Created operations knowledge base: `knowledge-base/operations/llm.txt` (633 lines)
     - STAR analysis framework (Situation, Task, Analysis, Recommendation)
     - 4 common workflow templates (Daily, Weekly, Monthly, Ad-hoc reports)
     - KPI interpretation guides with thresholds
     - 7 best practices for analytical reporting
     - Enhanced system prompt (~2x longer with analytical focus)
   - **Tools added:**
     - `search_knowledge_base` - Search operations workflows
     - `read_knowledge_document` - Read full guides
     - `list_knowledge_documents` - List available docs
   - **Capabilities updated:**
     - `operations_analytics: true`
     - `response_style: "analytical"` (was "professional")
   - **Result:** Bot now provides context, trends, root cause analysis, and actionable recommendations instead of raw data dumps
   - **Files:** `bots/operations_assistant.json` (enhanced), `knowledge-base/operations/llm.txt` (new), `OPERATIONS_ASSISTANT_ENHANCEMENT.md` (documentation)
   - **Status:** ✅ Completed and tested locally, ready for production deployment

6. **🎓 Claude Code Tutor Bot** ✅ (Completed in v0.3.0.1)
   - **Purpose:** Help users learn and use Claude Code effectively
   - **Knowledge Base created:**
     - Claude Code documentation (4,752 lines across 10 files)
     - Getting started guides (installation, quickstart, basic workflow)
     - Tool usage guides (Read, Write, Edit, Bash, Grep, Glob, Task, WebSearch, WebFetch)
     - MCP server integration guides
     - Agent SDK patterns and examples
     - Troubleshooting guides
   - **Bot configuration:**
     - Created `bots/cc_tutor.json` (Claude Code 导师)
     - Specialized system prompt for teaching
     - Access to knowledge base tools
   - **Knowledge Categories:**
     - `claude-code/getting-started/` - Installation and first steps
     - `claude-code/tools/` - Comprehensive tool usage guides
     - `claude-code/mcp/` - MCP server creation and best practices
     - `claude-code/agent-sdk/` - Agent SDK patterns
     - `claude-code/troubleshooting/` - Common issues and solutions
   - **Result:** Bot can answer questions about Claude Code installation, usage, best practices, and troubleshooting
   - **Files:** `bots/cc_tutor.json` (new bot), `knowledge-base/claude-code/` (10 markdown files), deployment via GitHub Gist
   - **Status:** ✅ Completed and tested locally, ready for production deployment

**New Features Completed (v0.3.2):**

7. **📊 Menu Engineering Bot with Boston Matrix** ✅ (Completed in v0.3.2)
   - **Purpose:** Analyze dish profitability using Boston Matrix methodology
   - **What was added:**
     - 5 Supabase RPC functions: `get_menu_profitability`, `get_top_profitable_dishes`, `get_low_profit_dishes`, `get_cost_coverage_rate`, `get_dishes_missing_cost`
     - Boston Matrix categorization: ⭐ Stars, 🧩 Puzzles, 🐴 Plowhorses, 🐕 Dogs
     - Profitability analysis based on real sales data from `rsp_order_items` and cost data from `product_cost_analysis`
     - Data coverage tracking for missing cost information
   - **Bot configuration:**
     - Created `bots/menu_engineering.json` (菜单工程师)
     - Bot Key: `19-gawmDGiVGP4u`
     - Webhook: `/webhook/menu_engineer`
   - **Tools added:**
     - All 5 menu engineering tools registered in `agent_tools.py`
     - Python wrappers in `supabase_tools.py`
   - **Result:** Restaurant can now identify Stars (promote), Puzzles (market more), Plowhorses (raise prices), Dogs (remove)
   - **Status:** ✅ Deployed to production (v0.3.2)

**New Features Completed (v0.3.3):**

8. **🔧 Agent Tools Refactoring** ✅ (Completed in v0.3.3)
   - **Problem:** `agent_tools.py` had grown to 2,418 lines (difficult to maintain and navigate)
   - **Solution:** Split into 7 modular decorator files by functional domain
   - **Structure created:**
     ```
     src/tools/
     ├── campfire_decorators.py       # 7 tools (224 lines)
     ├── briefing_decorators.py       # 2 tools (84 lines)
     ├── personal_decorators.py       # 4 tools (143 lines)
     ├── operations_decorators.py     # 3 tools (110 lines)
     ├── analytics_decorators.py      # 10 tools (360 lines)
     ├── menu_engineering_decorators.py  # 5 tools (176 lines)
     └── image_decorators.py          # 1 tool (54 lines)
     ```
   - **Results:**
     - agent_tools.py: 2,418 lines → 154 lines (94% reduction)
     - Total codebase: 2,418 lines → 1,305 lines (46% reduction)
     - All 32 tools verified working
     - Zero behavior changes (pure structural refactoring)
   - **Bug Fixed:** Added missing `AGENT_TOOLS` export that was accidentally omitted during initial refactoring
   - **Status:** ✅ Deployed to production (v0.3.3)

**Features Still Planned:**

9. **⏰ Daily Briefing Cron Automation** (Priority: Medium - Future)
   - **Problem:** Scheduled briefing automation not working
   - **Investigation:** Check cron setup, verify script permissions
   - **Location:** `/root/ai-service/scripts/generate_daily_briefing.py`

---

**Current Version:** v0.4.0 (Ready for Production)
**Status:** 🟢 Testing complete, approved for deployment

**v0.3.3.1 Status:** ✅ DEPLOYED to production on 2025-10-25

**v0.4.0 Completion Status:**
- ✅ Multi-Bot Collaboration Architecture (Task tool + subagent coordination)
- ✅ Critical Security Fixes (all 8 bots read-only, no Write/Edit/Bash via webhooks)
- ✅ Subagent Tool Mapping Bug Fix (dangerous tools excluded)
- ✅ System Prompt Guardrails (all 8 bot configs updated)
- ✅ Test Infrastructure Created (test_phase6_multibot.py with 13 scenarios)
- ✅ Comprehensive Local Testing Complete (All 13 tests passed)
- ✅ Security Verification Perfect (0 violations)
- ✅ Documentation Complete (test results, deployment guide)

**Completed in v0.4.0:**
- Multi-bot collaboration via Task tool (peer-to-peer architecture)
- Distributed subagent system (all 8 bots can spawn other bots)
- Two-layer security protection (code + prompt restrictions)
- Subagent security verification (safe tools only)
- Context isolation between main bot and subagents
- Document processing architecture validated (PDF/Image/DOCX/PPTX workflows)
- Bash re-enabled for personal_assistant (safe in Docker sandbox)
- PPTX support via Skills MCP (text extraction, visual analysis, editing)
- Dependencies added (markitdown, libreoffice, poppler-utils)
- Comprehensive test suite (13 Phase 6 scenarios)
- Full local testing execution (Phases 1-6)

**Ready for v0.4.0 Deployment:**
- Build Docker image (v0.4.0)
- Push to Docker Hub
- Deploy to production
- Monitor for 24-48 hours

**Deferred to Future Versions:**
- ⏰ Daily Briefing Cron Automation (v0.4.1 or later)

---

## Version History

| Version | Date | Changes | Status |
|---------|------|---------|--------|
| 1.0.x | 2025-10-07 | Initial deployment (Flask) | Superseded |
| 0.2.0 | 2025-10-14 | FastAPI + stateful sessions | Deployed |
| 0.2.1 | 2025-10-15 | Real-time progress milestones | Deployed |
| 0.2.2 | 2025-10-15 | Knowledge base integration | Deployed |
| 0.2.4.2 | 2025-10-16 | AI briefing automation | Deployed |
| 0.3.0 | 2025-10-20 | Haiku 4.5 + Enhanced HTML formatting | Deployed |
| 0.3.0.1 | 2025-10-21 | Bug fixes + Operations bot + CC Tutor | Deployed |
| 0.3.2 | 2025-10-23 | Menu Engineering bot + Boston Matrix | Deployed |
| 0.3.3 | 2025-10-25 | Agent Tools Refactoring (46% code reduction) | Deployed |
| 0.3.3.1 | 2025-10-25 | Image processing fix | ✅ IN PRODUCTION |
| **0.4.0** | **2025-10-25** | **Multi-Bot Collaboration + Security Fixes** | **🟢 READY FOR DEPLOYMENT** |

## Key Features by Version

**v0.2.0:** FastAPI backend, stateful sessions (40% faster)
**v0.2.1:** Real-time progress milestones (50%+ perceived speed improvement)
**v0.2.2:** Knowledge base tools (4 new MCP tools)
**v0.2.4.2:** AI-powered daily briefing automation
**v0.3.0:** Haiku 4.5 model upgrade + blog-style HTML formatting (5 bots)
**v0.3.0.1:** Fixed built-in SDK tools, Chinese progress message, Operations + CC Tutor bots (7 bots)
**v0.3.2:** Menu Engineering bot with 5 profitability analysis tools (8 bots)
**v0.3.3:** Agent Tools Refactoring - 2,418 → 154 lines (94% reduction), 7 modular decorator files
**v0.3.3.1:** Image processing bug fix - implemented missing process_image_tool body (97 lines), enables image analysis for all bots
**v0.4.0:** Multi-bot collaboration via Task tool + Critical security fixes (all bots read-only) + Document processing (PDF/Images/DOCX/PPTX via Skills MCP) + 13 test scenarios passed

## Project File Reference

### Documentation (Root `/campfire/`)
- **CLAUDE.md** - This file, project overview and status
- **DESIGN.md** - System architecture and database schema
- **IMPLEMENTATION_PLAN.md** - Deployment procedures

### Code (`/ai-bot/src/`)
- **app_fastapi.py** - FastAPI webhook server (main entry point)
- **campfire_agent.py** - Claude Agent SDK wrapper
- **bot_manager.py** - Multi-bot configuration loader
- **tools/campfire_tools.py** - Database queries and MCP tool implementations

### Configuration (`/ai-bot/`)
- **bots/*.json** - Bot configurations (8 bots)
- **Dockerfile** - Multi-stage Docker build
- **docker-compose.yml** - Production deployment config
- **pyproject.toml** - Python dependencies (uv)

---

**Last Updated:** 2025-10-25
**Current Status:** v0.3.3 Deployed to Production ✅
**Model:** claude-haiku-4-5-20251001 (all 8 bots)
**Key Achievement:** Agent Tools Refactoring - 46% code reduction with modular architecture
