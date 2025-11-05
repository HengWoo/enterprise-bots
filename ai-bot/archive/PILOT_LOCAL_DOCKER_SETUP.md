# v0.5.0 Pilot Validation - Local Docker Environment Setup

**Environment:** Local Docker (Campfire + AI Bot)
**Purpose:** Full-stack testing with real Campfire UI
**Complexity:** Production-faithful environment

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  YOUR MACHINE (Docker Desktop)                               │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Campfire Container (campfire-dev)                  │    │
│  │  • Rails + Redis + Workers                          │    │
│  │  • Port: 3000 → Browser UI                          │    │
│  │  • Database: ./storage/db/production.sqlite3        │    │
│  │  • Sends webhooks to: ai-bot:8000                   │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                          │
│                   │ Docker Network: campfire-dev-network    │
│                   ↓                                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │  AI Bot Container (campfire-ai-bot-dev)             │    │
│  │  • FastAPI + Claude SDK                             │    │
│  │  • Port: 8000 → Health checks                       │    │
│  │  • Verification module: ENABLED (v0.5.0)            │    │
│  │  • Posts responses to: campfire:80                  │    │
│  │  • Database: /campfire-db/production.sqlite3 (ro)   │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### 1. Docker Desktop
```bash
# Verify Docker is running
docker --version
docker compose version
```

**Expected:**
- Docker version 20.10+ or later
- Docker Compose version 2.0+ or later

### 2. Environment Variables
```bash
# Check .env.local exists
ls -la /Users/heng/Development/campfire/ai-bot/.env.local
```

**Required variables in .env.local:**
- `ANTHROPIC_API_KEY` - Your Claude API key ✅
- `FILE_TEMP_DIR` - Temp directory for file downloads
- `CAMPFIRE_DB_PATH` - Path to database (set by docker-compose)

### 3. Disk Space
- **Minimum:** 2GB free space
- **Recommended:** 5GB free space (for Docker images + data)

---

## Quick Start

### Step 1: Navigate to Project Root
```bash
cd /Users/heng/Development/campfire
```

### Step 2: Start Docker Environment
```bash
docker-compose -f docker-compose.dev.yml up --build
```

**What happens:**
- Builds Campfire container from base image
- Builds AI Bot container from local Dockerfile
- Creates shared Docker network
- Mounts local database (read-only)
- Starts both services

**Expected output:**
```
campfire-dev        | => Booting Puma
campfire-dev        | => Rails 7.x application starting
campfire-ai-bot-dev | INFO:     Started server process
campfire-ai-bot-dev | INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Verify Services Running
**Open 3 browser tabs:**

1. **Campfire UI:** http://localhost:3000
   - Should show Campfire login/signup page

2. **AI Bot Health:** http://localhost:8000/health
   - Should return: `{"status": "healthy", "version": "0.5.0"}`

3. **AI Bot Metrics:** http://localhost:8000/files/stats
   - Should return file registry statistics

**Check Docker logs:**
```bash
# In separate terminal
docker logs -f campfire-ai-bot-dev
```

Look for:
- `✅ Verification module loaded (v0.5.0)`
- `✅ personal_assistant bot configured`
- `✅ Skills MCP server connected`

---

## Step 4: Create Test Account & Room

### 4.1 Create Account
1. Open http://localhost:3000
2. Click "Sign up"
3. Fill in:
   - Name: "Pilot Tester"
   - Email: "pilot@test.local"
   - Password: (your choice)
4. Submit

### 4.2 Create Test Room
1. Click "New Room"
2. Name: "v0.5.0 Pilot Validation"
3. Type: Open or Closed (your choice)
4. Create

### 4.3 Find Bot Key
```bash
# Check logs for bot keys
docker logs campfire-ai-bot-dev | grep "bot_key"
```

**Personal Assistant Bot Key:** Should be in `bots/personal_assistant.json`

---

## Testing the Setup

### Test 1: Basic @mention
1. In your test room, type:
   ```
   @个人助手 你好，请介绍一下你的功能
   ```
2. Press Enter
3. Wait for bot response

**Expected:**
- Bot responds within 3-5 seconds
- Response includes HTML formatting
- Response mentions verification module (v0.5.0)

### Test 2: Verification Module
1. Type:
   ```
   @个人助手 计算 100 除以 0
   ```
2. Send

**Expected:**
- Verification module catches division by zero
- Response includes warning or error message
- Gate 1 metric +1 (error caught)

### Test 3: Code Generation
1. Type:
   ```
   @个人助手 生成一个简单的Python hello world脚本
   ```
2. Send

**Expected:**
- Bot uses code generation template
- Returns valid Python code
- Code is linted with ruff
- Gate 2 metric +1 (code gen used)

---

## Monitoring & Debugging

### View Logs in Real-Time
```bash
# AI Bot logs (verification, errors, tool calls)
docker logs -f campfire-ai-bot-dev

# Campfire logs (webhooks, Rails errors)
docker logs -f campfire-dev

# Both logs interleaved
docker-compose -f docker-compose.dev.yml logs -f
```

### Useful Log Filters
```bash
# Verification module activity
docker logs campfire-ai-bot-dev | grep -i "verification"

# Errors only
docker logs campfire-ai-bot-dev | grep -i "error"

# Tool calls
docker logs campfire-ai-bot-dev | grep -i "tool:"

# Gate metrics
docker logs campfire-ai-bot-dev | grep -i "gate"
```

### Check Container Status
```bash
# List running containers
docker ps

# Expected output:
# - campfire-dev (port 3000)
# - campfire-ai-bot-dev (port 8000)
# - campfire-redis-dev (port 6379 - internal)
```

### Restart Individual Service
```bash
# Restart just AI Bot
docker-compose -f docker-compose.dev.yml restart ai-bot

# Restart just Campfire
docker-compose -f docker-compose.dev.yml restart campfire
```

---

## Troubleshooting

### Issue: "Address already in use" (Port 3000 or 8000)
**Solution:**
```bash
# Find process using port
lsof -i :3000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different ports in docker-compose.dev.yml
```

### Issue: "ANTHROPIC_API_KEY not found"
**Solution:**
```bash
# Check .env.local
cat /Users/heng/Development/campfire/ai-bot/.env.local | grep ANTHROPIC

# Verify it's set
docker exec campfire-ai-bot-dev env | grep ANTHROPIC
```

### Issue: Bot not responding
**Check:**
1. Webhook URL correct?
   ```bash
   docker logs campfire-dev | grep webhook
   ```
2. Bot running?
   ```bash
   curl http://localhost:8000/health
   ```
3. Logs show errors?
   ```bash
   docker logs campfire-ai-bot-dev | tail -50
   ```

### Issue: Database errors
**Solution:**
```bash
# Check database mounted
docker exec campfire-ai-bot-dev ls -la /campfire-db/

# Expected: production.sqlite3 file exists
```

### Issue: Verification module not loading
**Check:**
```bash
# Verify module exists
docker exec campfire-ai-bot-dev ls -la /app/src/verification/

# Check bot config
docker exec campfire-ai-bot-dev cat /app/bots/personal_assistant.json | grep verification
```

---

## Stopping the Environment

### Graceful Shutdown
```bash
# Stop containers (preserves data)
docker-compose -f docker-compose.dev.yml down
```

### Full Cleanup
```bash
# Stop and remove volumes (⚠️ deletes database)
docker-compose -f docker-compose.dev.yml down -v

# Remove images
docker-compose -f docker-compose.dev.yml down --rmi all
```

---

## Data Persistence

**What persists between restarts:**
- ✅ Database (`storage/db/production.sqlite3`)
- ✅ Uploaded files (`storage/files/`)
- ✅ Bot configurations (`bots/`)
- ✅ Session cache (`session_cache/`)

**What doesn't persist:**
- ❌ Container logs (use `docker logs` before stopping)
- ❌ In-memory cache (Redis data)

---

## Performance Benchmarks

### Expected Response Times (Local)
- Simple query: **1-2 seconds**
- With verification: **1.5-2.5 seconds** (+0.5s overhead)
- With code generation: **3-5 seconds**
- With file processing: **5-10 seconds**

**Gate 5 Target:** ≤10% overhead = ≤0.2s added by verification

### Resource Usage
- **Campfire container:** ~200MB RAM
- **AI Bot container:** ~300MB RAM
- **Redis container:** ~50MB RAM
- **Total:** ~550MB RAM (well within limits)

---

## Next Steps

Once environment is running:
1. ✅ Verify health checks pass
2. ✅ Create test account and room
3. ✅ Test basic @mention
4. 📋 Proceed to workflow testing (see PILOT_TEST_SETUP.md)
5. 📊 Document results in PILOT_VALIDATION_LOG.md

---

**Setup Status:** ✅ Ready for pilot validation
**Documentation:** See PILOT_TEST_SETUP.md for workflow test instructions
**Support:** Check logs first, then review troubleshooting section above
