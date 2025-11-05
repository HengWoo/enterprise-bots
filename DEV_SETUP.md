# Local Development Environment Setup

**Version:** 1.0
**Date:** 2025-10-27
**Status:** ✅ Production-Faithful Local Testing Environment

---

## Overview

This setup runs a **complete local Campfire + AI Bot environment** for testing with **100% production fidelity**. Unlike mock environments, this uses the actual Campfire Rails application, providing true integration testing.

### What You Get

✅ **Real Campfire UI** - Actual chat interface, not a simulation
✅ **Real Webhooks** - Campfire → AI Bot integration
✅ **Real API Posting** - AI Bot → Campfire responses
✅ **File Uploads** - Test Excel, PDF, DOCX, images
✅ **All 8 Bots** - Test every bot's capabilities
✅ **Multi-turn Conversations** - Test conversation memory
✅ **HTML Rendering** - See formatting exactly as in production

---

## Quick Start (5 Minutes)

```bash
# 1. Create .env.local file with production-faithful configuration
cd /Users/heng/Development/campfire/ai-bot
cp .env.local.example .env.local
# Edit .env.local and verify HusanAI endpoint is set
# (HusanAI API key already included in template)

# 2. Start the environment
cd /Users/heng/Development/campfire
docker-compose -f docker-compose.dev.yml up

# 3. Wait for services to be healthy (~30 seconds)
# Look for: "Listening on http://0.0.0.0:80"

# 4. Open browser
open http://localhost:3000

# 5. Create account and start chatting!
```

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│  Browser: http://localhost:3000                        │
│  ├─ Campfire Rails App                                 │
│  ├─ Real chat UI                                       │
│  ├─ File uploads                                       │
│  └─ Bot mentions trigger webhooks                      │
└──────────────┬─────────────────────────────────────────┘
               │ Webhook: http://ai-bot:8000/webhook
               ↓
┌────────────────────────────────────────────────────────┐
│  AI Bot Service: http://localhost:8000                 │
│  ├─ FastAPI webhook handler                            │
│  ├─ Claude Agent SDK                                   │
│  ├─ Session management (hot/warm/cold)                 │
│  └─ Response posts to http://campfire:80/rooms/...    │
└────────────────────────────────────────────────────────┘
               │
               ↓
┌────────────────────────────────────────────────────────┐
│  Redis: localhost:6379                                 │
│  ├─ ActionCable (WebSocket) backend                    │
│  └─ Background job queue (Resque)                      │
└────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Required

- **Docker Desktop** installed and running
- **2GB+ RAM** available for Docker
- **5GB+ disk space** for images
- **Anthropic API Key** (from https://console.anthropic.com/)

### Optional

- **Supabase credentials** (for Operations/Menu Engineering bots)
- **VS Code** with Docker extension (for easier container management)

---

## Detailed Setup

### Step 1: Environment Variables (Production-Faithful Setup)

Create `.env.local` file in `ai-bot/` directory with **exact production configuration**:

```bash
cd /Users/heng/Development/campfire/ai-bot

# Copy from production-faithful template
cp .env.local.example .env.local

# Edit to add your actual keys
nano .env.local
```

**What to configure:**

1. **HusanAI Primary API** (matches production):
   ```bash
   ANTHROPIC_BASE_URL=https://husanai.com
   ANTHROPIC_API_KEY=sk-9DCclt4ifSpkP1WVx1EPZcHf798R6Fbh0G6HuOcrDAjrQoVj
   ```

2. **Official Anthropic Fallback** (matches production):
   ```bash
   ANTHROPIC_BASE_URL_FALLBACK=https://api.anthropic.com
   ANTHROPIC_API_KEY_FALLBACK=sk-ant-api03-YOUR_OFFICIAL_KEY_HERE
   FALLBACK_MODEL=claude-haiku-4-5-20251001
   ```

3. **Supabase** (optional - for operations/menu bots):
   ```bash
   SUPABASE_URL=https://wdpeoyugsxqnpwwtkqsl.supabase.co
   SUPABASE_KEY=your-supabase-anon-key-here
   ```

**Important Notes:**
- ✅ Use **same HusanAI endpoint** as production for true fidelity
- ✅ Use **same HusanAI API key** (already in template)
- ✅ Add your **official Anthropic key** for fallback
- ✅ Supabase is optional (only needed for operations/menu bots)
- ❌ **Never commit** `.env.local` to git

**Quick verification:**
```bash
# Check your .env.local has correct values
grep "ANTHROPIC_BASE_URL" .env.local
# Should show: ANTHROPIC_BASE_URL=https://husanai.com

grep "SUPABASE_URL" .env.local
# Should show: SUPABASE_URL=https://wdpeoyugsxqnpwwtkqsl.supabase.co
```

### Step 2: Initialize Campfire Database

First-time setup to create database and admin user:

```bash
cd /Users/heng/Development/campfire

# Create storage directories
mkdir -p storage/db storage/files log

# Build Campfire image (takes ~5 minutes)
docker-compose -f docker-compose.dev.yml build campfire

# Initialize database
docker-compose -f docker-compose.dev.yml run --rm campfire \
  bin/rails db:setup

# This creates:
# - storage/db/development.sqlite3
# - Default admin user: admin@example.com / password
```

### Step 3: Create Bot Users

Bots need to exist as users in Campfire. Create them via Rails console:

```bash
# Start Rails console
docker-compose -f docker-compose.dev.yml run --rm campfire \
  bin/rails console

# In Rails console, create 8 bots:
bots = [
  {name: "财务分析师", id: "financial_analyst"},
  {name: "技术助手", id: "technical_assistant"},
  {name: "个人助手", id: "personal_assistant"},
  {name: "日报助手", id: "briefing_assistant"},
  {name: "AI Assistant", id: "default"},
  {name: "运营数据助手", id: "operations_assistant"},
  {name: "Claude Code导师", id: "cc_tutor"},
  {name: "菜单工程师", id: "menu_engineer"}
]

bots.each do |bot_info|
  bot = User.create!(
    name: bot_info[:name],
    email: "#{bot_info[:id]}@bots.local",
    password: "devpassword123",
    role: "bot"
  )

  # Generate bot token (Campfire creates this automatically)
  puts "#{bot_info[:name]}: Bot Key = #{bot.id}-#{bot.bot_token}"
  puts "  Webhook URL: http://ai-bot:8000/webhook/#{bot_info[:id]}"
  puts ""
end

# Exit console
exit
```

**Save the bot keys!** You'll need them to update bot configurations.

### Step 4: Configure Bot Keys

Update AI Bot configurations with the bot keys from Step 3:

```bash
cd /Users/heng/Development/campfire/ai-bot/bots

# Example: Update financial_analyst.json
nano financial_analyst.json

# Change bot_key to match the key from Step 3:
{
  "bot_id": "financial_analyst",
  "bot_key": "2-AbC123dEf456",  # ← Use actual key from console
  "name": "财务分析师 (Financial Analyst)",
  ...
}

# Repeat for all 8 bot JSON files
```

### Step 5: Start Services

```bash
cd /Users/heng/Development/campfire

# Start all services
docker-compose -f docker-compose.dev.yml up

# OR: Start in detached mode (background)
docker-compose -f docker-compose.dev.yml up -d

# Watch logs
docker-compose -f docker-compose.dev.yml logs -f
```

**Wait for health checks to pass** (~30 seconds):
```
campfire-dev     | ✅ Listening on http://0.0.0.0:80
campfire-ai-bot-dev | ✅ Campfire AI Bot ready
redis-dev        | ✅ Ready to accept connections
```

### Step 6: Access Campfire

Open browser: **http://localhost:3000**

1. **Sign in** with admin account created in Step 2
   - Email: `admin@example.com`
   - Password: `password`

2. **Create a test room**
   - Click "New Room"
   - Name: "Bot Testing"

3. **Add a bot to the room**
   - Room settings → Members → Add
   - Select "财务分析师" (or any bot)

4. **Test conversation!**
   - Type: `@财务分析师 你好，介绍一下你的功能`
   - Bot should respond within 5-10 seconds

---

## Usage

### Basic Testing

```bash
# Start environment
docker-compose -f docker-compose.dev.yml up

# Access Campfire UI
open http://localhost:3000

# Access AI Bot health check
curl http://localhost:8000/health

# Access AI Bot cache stats
curl http://localhost:8000/cache/stats
```

### File Upload Testing

1. In Campfire, click the paperclip icon
2. Upload a file (Excel, PDF, DOCX, image)
3. Mention a bot: `@财务分析师 请分析这个Excel文件`
4. Bot will process the file and respond

### Multi-turn Conversation Testing

```
You: @财务分析师 你好
Bot: (greeting response)

You: 分析这个文件 (upload Excel)
Bot: (analysis response)

You: 利润率是多少？
Bot: (uses conversation context to answer)
```

### Session Management Testing

```bash
# Check active sessions
curl http://localhost:8000/cache/stats

# Clear all sessions
curl -X POST http://localhost:8000/session/clear/all

# Test hot/warm/cold paths
# - First message = cold start (~15s)
# - Second message = hot path (~9s)
# - After 24h = warm path (~12s)
```

---

## Development Workflow

### Hot Reload for AI Bot

Enable source code hot reload:

```yaml
# Edit docker-compose.dev.yml, add to ai-bot volumes:
volumes:
  - ./ai-bot/src:/app/src  # Hot reload Python code
  - ./ai-bot/bots:/app/bots  # Already enabled
```

After changes:
```bash
# Restart only AI Bot
docker-compose -f docker-compose.dev.yml restart ai-bot
```

### Database Inspection

```bash
# Access Campfire database
sqlite3 storage/db/development.sqlite3

# Useful queries:
SELECT id, name, email, role FROM users WHERE role = 'bot';
SELECT * FROM rooms;
SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;

# Exit
.quit
```

### Log Monitoring

```bash
# All services
docker-compose -f docker-compose.dev.yml logs -f

# Specific service
docker-compose -f docker-compose.dev.yml logs -f campfire
docker-compose -f docker-compose.dev.yml logs -f ai-bot
docker-compose -f docker-compose.dev.yml logs -f redis

# Filter for errors
docker-compose -f docker-compose.dev.yml logs -f | grep -i error
```

### Debugging

```bash
# Enter Campfire Rails console
docker-compose -f docker-compose.dev.yml exec campfire bin/rails console

# Enter AI Bot container
docker-compose -f docker-compose.dev.yml exec ai-bot bash

# Check service health
docker-compose -f docker-compose.dev.yml ps
```

---

## Troubleshooting

### Issue 1: Services won't start

**Symptom:** Docker containers crash or fail to start

**Solution:**
```bash
# Check logs
docker-compose -f docker-compose.dev.yml logs

# Rebuild images
docker-compose -f docker-compose.dev.yml build --no-cache

# Clear volumes (WARNING: deletes data)
docker-compose -f docker-compose.dev.yml down -v
```

### Issue 2: Bot doesn't respond

**Symptom:** Mention bot in Campfire, no response

**Check:**
1. Bot user exists in database
2. Bot key matches configuration
3. Webhook URL is correct
4. AI Bot service is healthy: `curl http://localhost:8000/health`
5. Check AI Bot logs: `docker-compose -f docker-compose.dev.yml logs ai-bot`

**Common fixes:**
```bash
# Restart AI Bot
docker-compose -f docker-compose.dev.yml restart ai-bot

# Check bot configuration
cat ai-bot/bots/financial_analyst.json
```

### Issue 3: Database locked

**Symptom:** SQLite errors about locked database

**Solution:**
```bash
# Stop all services
docker-compose -f docker-compose.dev.yml down

# Wait 5 seconds

# Start again
docker-compose -f docker-compose.dev.yml up
```

### Issue 4: Port already in use

**Symptom:** Error: "Port 3000 is already allocated"

**Solution:**
```bash
# Find what's using the port
lsof -i :3000

# Kill the process
kill -9 <PID>

# OR: Change port in docker-compose.dev.yml
ports:
  - "3001:80"  # Use 3001 instead
```

### Issue 5: API key not working

**Symptom:** Bot responds with API errors

**Check:**
1. `.env` file exists in `ai-bot/` directory
2. `ANTHROPIC_API_KEY` is set correctly
3. No quotes around the key value
4. No extra spaces

**Verify:**
```bash
# Check environment variables in container
docker-compose -f docker-compose.dev.yml exec ai-bot env | grep ANTHROPIC
```

---

## Production Fidelity Checklist

When testing locally, verify these match production behavior:

✅ **Webhook flow** - Campfire sends webhook on @mention
✅ **API posting** - Bot response appears in Campfire
✅ **File handling** - Files uploaded via Campfire UI
✅ **HTML rendering** - Tables, lists, formatting displays correctly
✅ **Session persistence** - Conversation memory works
✅ **Multi-turn** - Bot remembers context
✅ **All 8 bots** - Each bot responds with correct capabilities
✅ **MCP tools** - Financial MCP, Skills MCP, Supabase tools work

---

## Cleanup

### Soft Cleanup (keeps data)

```bash
# Stop services
docker-compose -f docker-compose.dev.yml down

# Data persists in:
# - storage/db/development.sqlite3
# - storage/files/
# - ai-bot/session_cache/
```

### Hard Cleanup (removes everything)

```bash
# Stop and remove volumes
docker-compose -f docker-compose.dev.yml down -v

# Remove database and files
rm -rf storage/db storage/files log

# Remove session cache
rm -rf ai-bot/session_cache/*
```

---

## Next Steps

After successful local testing:

1. **Test all 8 bots** - Verify each bot's unique capabilities
2. **Test file uploads** - Excel, PDF, DOCX, PPTX, images
3. **Test multi-turn** - Conversation memory and context
4. **Test edge cases** - Long messages, multiple files, rapid requests
5. **Deploy to production** - If local tests pass, production will work identically

---

## Support

**Documentation:**
- Architecture: `/campfire/DESIGN.md`
- Deployment: `/campfire/IMPLEMENTATION_PLAN.md`
- AI Bot: `/campfire/ai-bot/README.md`

**Logs:**
```bash
# Real-time logs
docker-compose -f docker-compose.dev.yml logs -f

# Service-specific
docker-compose -f docker-compose.dev.yml logs -f ai-bot
```

**Health Checks:**
```bash
# Campfire
curl http://localhost:3000/up

# AI Bot
curl http://localhost:8000/health

# Redis
redis-cli -h localhost -p 6379 ping
```

---

**Document Version:** 1.0
**Last Updated:** 2025-10-27
**Status:** ✅ Production-ready local testing environment
