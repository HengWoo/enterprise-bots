# v0.2.4 Hotfix - Bot Key Posting Issue

**Date:** 2025-10-16
**Priority:** CRITICAL
**Status:** Ready for deployment

---

## 🔥 Critical Issue Fixed

### Problem

All 3 new bots (Personal Assistant, Briefing Assistant, Technical Assistant) were **using the wrong bot_key** when posting responses to Campfire:

- **Expected:** Each bot uses its own `bot_key` from configuration
- **Actual:** All bots used hardcoded `2-CsheovnLtzjM` (Financial Analyst's key)
- **Result:** Campfire returned **500 errors** because wrong bot tried to post

### Root Cause

`post_to_campfire()` function always used `config['BOT_KEY']` from environment variable, which defaults to the Financial Analyst's key. The function ignored which bot was actually processing the webhook.

**Code Location:** `src/app_fastapi.py:73-76`

```python
# OLD (WRONG):
url = f"{config['CAMPFIRE_URL']}/rooms/{room_id}/{config['BOT_KEY']}/messages"

# NEW (FIXED):
actual_bot_key = bot_key or config['BOT_KEY']
url = f"{config['CAMPFIRE_URL']}/rooms/{room_id}/{actual_bot_key}/messages"
```

### Impact

- ✅ Financial Analyst bot: **Working** (used correct key by accident)
- ❌ Technical Assistant: **BROKEN** (500 error on all responses)
- ❌ Personal Assistant: **BROKEN** (500 error on all responses)
- ❌ Briefing Assistant: **BROKEN** (500 error on all responses)

---

## ✅ Fix Applied

### Changes Made

**1. Updated `post_to_campfire()` signature** (`app_fastapi.py:51`)
```python
async def post_to_campfire(room_id: int, message: str, bot_key: str = None, testing: bool = False):
```

**2. Added bot_key parameter to URL construction** (`app_fastapi.py:75-76`)
```python
actual_bot_key = bot_key or config['BOT_KEY']
url = f"{config['CAMPFIRE_URL']}/rooms/{room_id}/{actual_bot_key}/messages"
```

**3. Updated all 6 calls to pass `bot_config.bot_key`:**
- Line 385: Busy wait message
- Line 400: Timeout error message
- Line 409: Acknowledgment message
- Line 449: Milestone updates
- Line 484: Final response
- Line 495: Error handler

**4. Version bumps:**
- `app_fastapi.py` header: v0.2.4
- Startup message: "v0.2.4 - FastAPI + API Fallback + Multi-Bot Fix"
- FastAPI version: `0.2.4`
- `/health` endpoint: `version: '0.2.4'`
- Dockerfile LABEL: `version="0.2.4"`

### Files Modified

```
src/app_fastapi.py (7 changes)
Dockerfile (1 change)
HOTFIX_v0.2.4.md (NEW - this file)
```

---

## 🧪 Testing Required

### Test Scenarios

**Test 1: Technical Assistant**
```bash
# In Campfire, send message to Technical Assistant
@技术助手 Hello

# Expected: Bot responds successfully (not 500 error)
# Verify logs show: BOT_KEY: 12-LTm3bcplyjci
```

**Test 2: Personal Assistant**
```bash
# In Campfire, send message to Personal Assistant
@个人助手 创建任务：测试Bot Key修复

# Expected: Bot responds successfully
# Verify logs show: BOT_KEY: 10-vWgb0YVbUSYs
```

**Test 3: Briefing Assistant**
```bash
# In Campfire, send message to Briefing Assistant
@日报助手 介绍一下你的功能

# Expected: Bot responds successfully
# Verify logs show: BOT_KEY: 11-cLwvq6mLx4WV
```

**Test 4: Financial Analyst (Regression Test)**
```bash
# In Campfire, send message to Financial Analyst
@财务分析师 介绍一下你的功能

# Expected: Bot still works (no regression)
# Verify logs show: BOT_KEY: 2-CsheovnLtzjM
```

---

## 🚀 Deployment Steps

### Step 1: Build Docker Image

```bash
cd /Users/heng/Development/campfire/ai-bot

# Build for linux/amd64 (DigitalOcean)
docker buildx build --platform linux/amd64 \
  -t hengwoo/campfire-ai-bot:0.2.4 \
  -t hengwoo/campfire-ai-bot:latest \
  --no-cache \
  .
```

**Expected:** Build succeeds in ~5-7 minutes

### Step 2: Push to Docker Hub

```bash
docker push hengwoo/campfire-ai-bot:0.2.4
docker push hengwoo/campfire-ai-bot:latest
```

**Expected:** Two tags pushed with same digest

### Step 3: Deploy to Production

```bash
# SSH to production server (use DigitalOcean console if SSH blocked)
cd /root/ai-service

# Pull new image
docker pull hengwoo/campfire-ai-bot:latest

# Restart container
docker-compose down
docker-compose up -d

# Verify startup
docker logs campfire-ai-bot -f
```

**Expected startup log:**
```
============================================================
🚀 Campfire AI Bot v0.2.4 - FastAPI + API Fallback + Multi-Bot Fix
============================================================

[Startup] Initializing application components...
[Startup] ✅ CampfireTools initialized
[Startup] ✅ BotManager loaded 5 bot(s) from /app/bots:
           - 财务分析师 (Financial Analyst)
           - 技术助手 (Technical Assistant)
           - AI Assistant (default)
           - 个人助手 (Personal Assistant)
           - 日报助手 (Briefing Assistant)
[Startup] ✅ SessionManager initialized (TTL: 24h)
[Startup] ✅ RequestQueue initialized

[Startup] 🎯 FastAPI server ready
============================================================
```

### Step 4: Verify Fix in Production

1. **Health Check:**
   ```bash
   curl http://localhost:5000/health
   # Expected: {"status":"healthy","version":"0.2.4", ...}
   ```

2. **Test Technical Assistant in Campfire:**
   - Message: `@技术助手 Hello`
   - Expected: Successful response (NOT 500 error)

3. **Check Logs:**
   ```bash
   docker logs campfire-ai-bot | grep "BOT_KEY"
   # Expected: BOT_KEY: 12-LTm3bcplyjci (for Technical Assistant)
   # Expected: BOT_KEY: 2-CsheovnLtzjM (for Financial Analyst)
   ```

---

## ✅ Success Criteria

Deployment successful when:

1. ✅ All 5 bots listed in startup log
2. ✅ `/health` returns version `0.2.4`
3. ✅ Technical Assistant responds successfully
4. ✅ Personal Assistant responds successfully
5. ✅ Briefing Assistant responds successfully
6. ✅ Financial Analyst still works (no regression)
7. ✅ Logs show correct `BOT_KEY` for each bot
8. ✅ No 500 errors in Campfire or logs

---

## 🔄 Rollback Plan

If issues occur, rollback to v0.2.3:

```bash
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:0.2.3
docker-compose up -d
```

**Note:** Rollback returns to broken state for new bots, but keeps Financial Analyst working.

---

## 📊 Expected Log Patterns

**Before Fix (v0.2.3):**
```
Processing webhook with bot: 技术助手 (Technical Assistant)
[POST] BOT_KEY: 2-CsheovnLtzjM  # ← WRONG!
[POST] Response status: 500
[POST] ❌ Error posting to Campfire
```

**After Fix (v0.2.4):**
```
Processing webhook with bot: 技术助手 (Technical Assistant)
[POST] BOT_KEY: 12-LTm3bcplyjci  # ← CORRECT!
[POST] Response status: 200
[POST] ✅ Successfully posted to room 23
```

---

## 🎯 Next Actions After Deployment

1. **Monitor logs** for 30 minutes after deployment
2. **Test all 5 bots** in Campfire
3. **Verify no 500 errors** in logs
4. **Update DEPLOYMENT_SUMMARY_v0.2.3.md** to reflect hotfix applied
5. **Clean up old Docker tags** if desired

---

**Document Version:** 1.0
**Created:** 2025-10-16
**Status:** Ready for deployment
**Confidence Level:** HIGH (simple fix, well-tested pattern)

**Critical Learning:**
Always pass bot-specific parameters through the entire call chain. Don't rely on environment variables for multi-bot systems.
