# Production Port Mapping Fix (v0.5.2)

**Date:** 2025-11-05
**Status:** ✅ COMPLETE - Ready for deployment
**Issue:** Incorrect port mapping in production docker-compose.yml

---

## Problem Summary

### Issue: Port Mapping Mismatch

**File:** `docker-compose.yml` (production configuration)

**Problem:**
```yaml
# BEFORE (BROKEN):
ports:
  - "${FLASK_PORT:-5000}:5000"  # ❌ Maps to port 5000 in container

healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]  # ❌ Checks port 5000
```

**Root Cause:**
- Configuration file still references Flask (legacy framework from v1.0.x)
- But the application migrated to FastAPI in v0.2.0 (October 14, 2025)
- FastAPI runs on port 8000, not 5000 (see Dockerfile line 40-41)

**Impact:**
- External port 5000 mapped to non-existent internal port 5000
- Health checks failing (checking wrong port)
- Production webhooks likely not working
- Container appears unhealthy in Docker

**Evidence from Dockerfile:**
```dockerfile
# Line 40-41 (from Dockerfile)
EXPOSE 8000
CMD ["uvicorn", "src.app_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
```

Application clearly runs on port 8000, not 5000.

---

## Solution Implemented

### 1. Fixed Port Mapping (Line 24)

**Before:**
```yaml
ports:
  - "${FLASK_PORT:-5000}:5000"  # Wrong
```

**After:**
```yaml
# Port mapping (production: 5000 -> 8000, local dev: 5001 -> 8000)
# External port : Internal port (FastAPI runs on 8000)
ports:
  - "${FLASK_PORT:-5000}:8000"  # Correct
```

**Explanation:**
- External: Port 5000 (no change for production compatibility)
- Internal: Port 8000 (matches FastAPI actual port)
- Environment variable `FLASK_PORT` still works (defaults to 5000)

### 2. Fixed Health Check (Line 80)

**Before:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]  # Wrong port
```

**After:**
```yaml
# Health check (FastAPI runs on port 8000 internally)
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]  # Correct port
```

**Explanation:**
- Health check now queries the correct internal port (8000)
- Docker will properly detect container health status
- Health checks will pass once container starts

### 3. Updated Documentation (Lines 4-6)

**Before:**
```yaml
# Campfire AI Bot - Production Docker Compose
# Multi-MCP Support: Campfire + Financial MCP
# Author: Wu Heng | Date: 2025-10-06
```

**After:**
```yaml
# Campfire AI Bot - Production Docker Compose
# Framework: FastAPI + Claude Agent SDK
# Multi-MCP Support: Campfire + Financial MCP + Operations + Menu Engineering
# Author: Wu Heng | Last Updated: 2025-11-05
```

**Explanation:**
- Clarified we use FastAPI (not Flask)
- Added missing MCP servers (Operations, Menu Engineering)
- Updated last modified date

---

## Verification

### Port Architecture

**Production Server (128.199.175.50):**
```
External Request → Port 5000 (host)
                    ↓
               Port 8000 (container)
                    ↓
              FastAPI Application
```

**How This Works:**
1. Campfire sends webhook to: `http://128.199.175.50:5000/webhook/{bot_id}`
2. Docker maps port 5000 → 8000
3. FastAPI receives request on port 8000
4. Response sent back through same path

**Health Check Flow:**
1. Docker runs: `curl -f http://localhost:8000/health` (inside container)
2. FastAPI `/health` endpoint responds with 200 OK
3. Docker marks container as healthy

### Comparison with Other Files

**✅ docker-compose.dev.yml (Local Dev):**
```yaml
ports:
  - "8000:8000"  # Direct mapping, correct
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]  # Correct
```

**✅ docker-compose.test.yml (Testing):**
```yaml
ports:
  - "5001:8000"  # External 5001 → Internal 8000, correct
# No health check defined (not needed for testing)
```

**✅ docker-compose.yml (Production) - NOW FIXED:**
```yaml
ports:
  - "${FLASK_PORT:-5000}:8000"  # External 5000 → Internal 8000, correct
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]  # Correct
```

---

## Deployment Impact

### What Will Change

**When this fix is deployed to production:**

1. **Container will start correctly** ✅
   - Port 5000 properly mapped to FastAPI's port 8000

2. **Health checks will pass** ✅
   - Docker will detect container as healthy
   - No more false "unhealthy" status

3. **Webhooks will work** ✅
   - Campfire webhook calls to port 5000 will reach FastAPI
   - Bots will respond to @mentions

4. **No external changes needed** ✅
   - Campfire still sends webhooks to port 5000
   - No configuration changes required on Campfire side

### What Will NOT Change

- **External port:** Still 5000 (same as before)
- **Webhook URLs:** Still `http://128.199.175.50:5000/webhook/{bot_id}`
- **API endpoints:** All existing endpoints still work
- **Environment variables:** `FLASK_PORT` still supported

---

## Testing Recommendation

### Before Deployment

**Verify current production status:**
```bash
# SSH to production server
ssh root@128.199.175.50

# Check current container status
docker ps | grep campfire-ai-bot

# Check health status (likely failing)
docker inspect campfire-ai-bot | grep -A 5 Health

# Test current webhook (likely failing)
curl -X POST http://localhost:5000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":1,"name":"Test"},"room":{"id":1,"name":"Test"},"content":"hello"}'
```

### After Deployment

**1. Deploy the fix:**
```bash
# On local machine - build and push new image
cd /Users/heng/Development/campfire/ai-bot
docker build -t hengwoo/campfire-ai-bot:v0.5.2 .
docker push hengwoo/campfire-ai-bot:v0.5.2

# On production server
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:v0.5.2
docker-compose up -d
```

**2. Verify fix:**
```bash
# Check container started
docker ps | grep campfire-ai-bot

# Check health status (should be healthy)
docker inspect campfire-ai-bot | grep -A 5 Health

# Check logs
docker logs --tail 50 campfire-ai-bot

# Test health endpoint from inside container
docker exec campfire-ai-bot curl -f http://localhost:8000/health

# Test health endpoint from host
curl http://localhost:5000/health

# Test webhook
curl -X POST http://localhost:5000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":1,"name":"Test"},"room":{"id":1,"name":"Test"},"content":"介绍一下你自己"}'
```

**3. Monitor for 5 minutes:**
```bash
# Watch logs for errors
docker logs -f campfire-ai-bot
```

---

## Files Modified

### `docker-compose.yml`
**Changes:**
- Line 4-6: Updated header comments (framework, MCP servers, date)
- Line 21-24: Fixed port mapping from `5000:5000` to `5000:8000`
- Line 78-80: Fixed health check from port 5000 to 8000

**Total:** 3 sections, ~10 lines changed

---

## Related Fixes

This production port fix is part of **v0.5.2** which also includes:

1. **Knowledge Base Save Fix** (completed earlier today)
   - Fixed `store_knowledge_document` silent failures
   - Added category normalization
   - Enhanced logging

2. **File-Based Prompts Migration** (7/7 bots complete)
   - All bots using markdown prompts
   - 20% token savings for simple queries

3. **Native Skills Migration** (completed Nov 2)
   - Deprecated Skills MCP server
   - Using Anthropic's native Agent SDK skills

---

## Risk Assessment

**Risk Level:** ⚠️ MEDIUM

**Why Medium Risk:**
- Changes production port mapping (critical path)
- If wrong, webhooks will fail completely
- Affects all 8 bots simultaneously

**Mitigation:**
1. ✅ Verified against Dockerfile (port 8000 confirmed)
2. ✅ Verified against dev/test compose files (same pattern)
3. ✅ Health check updated to match
4. ✅ No external changes needed
5. ✅ Rollback plan ready (revert to v0.4.0.2)

**Rollback Plan:**
```bash
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:0.4.0.2  # Last known good
docker-compose up -d
```

---

## Success Criteria

✅ **Fix is successful if:**
1. Container starts and stays running
2. Health check shows "healthy" status
3. `/health` endpoint responds on port 5000 (external)
4. Webhooks respond correctly
5. Bots answer @mentions in Campfire
6. No errors in logs

❌ **Fix has failed if:**
- Container keeps restarting
- Health check remains "unhealthy"
- Port 5000 not accessible from host
- Webhooks return errors
- Logs show port binding errors

---

**Version:** v0.5.2
**Author:** Claude (AI Assistant)
**Reviewer:** Awaiting production deployment
**Next Step:** Build Docker image and deploy to production
