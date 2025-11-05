# v0.2.4.2 Deployment Guide - Daily Briefing Permission + Date Query Fix

**Date:** 2025-10-16
**Status:** ✅ Built and pushed to Docker Hub
**Purpose:** Fix permission errors in daily briefing script AND fix date query bug that returned 0 messages

---

## 🔧 What Changed in v0.2.4.2

### Two Critical Fixes

#### Fix 1: Permission Denied Error
**Issue:** Daily briefing script failed with `[Errno 13] Permission denied: 'user_contexts'`

**Root Cause:**
- `CampfireTools.__init__` defaults to `./user_contexts` (relative path)
- Relative path resolves to `/app/user_contexts` (current working directory)
- Container runs as `appuser` (UID 1000)
- `/app` directory is owned by root, appuser can't create subdirectories

**Solution Implemented:**
**Design Philosophy:** "Soft-sustainable" Docker images with external configuration via environment variables

**Changes Made:**

1. **`scripts/generate_daily_briefing.py` (Lines 78-93)**
   - Added `CONTEXT_DIR` environment variable support
   - Default: `/app/ai-knowledge/user_contexts` (matches Docker volume mount)
   - Updated `CAMPFIRE_DB_PATH` default to container path: `/campfire-db/production.sqlite3`
   ```python
   # Get database path from environment or use container default
   # Container path: /campfire-db/production.sqlite3 (read-only bind mount)
   db_path = os.environ.get("CAMPFIRE_DB_PATH", "/campfire-db/production.sqlite3")

   # Use CONTEXT_DIR env var with container path default
   # Container path: /app/ai-knowledge/user_contexts (Docker named volume)
   context_dir = os.environ.get("CONTEXT_DIR", "/app/ai-knowledge/user_contexts")
   tools = CampfireTools(db_path=db_path, context_dir=context_dir)
   print(f"[Cron] ✅ CampfireTools initialized (context_dir: {context_dir})")
   ```

#### Fix 2: Date Query Bug (No Messages Found)
**Issue:** Script ran without errors but returned 0 messages despite messages existing in database

**Root Cause:**
- Database stores timestamps in ISO format: `2025-10-04T06:13:00.711524`
- Query used string comparison: `BETWEEN '2025-10-04 00:00:00' AND '2025-10-04 23:59:59'`
- String comparison fails: `"2025-10-04 00:00:00" < "2025-10-04T06:13:00.711524"` = FALSE

**Solution Implemented:**

2. **`src/tools/campfire_tools.py` (Lines 705-732 and 771-793)**
   - Changed from `WHERE m.created_at BETWEEN ? AND ?` with two parameters
   - To: `WHERE DATE(m.created_at) = ?` with single date parameter
   - Applied to both message query and file attachments query

   **Before:**
   ```python
   start_time = f"{date_str} 00:00:00"
   end_time = f"{date_str} 23:59:59"
   WHERE m.created_at BETWEEN ? AND ?
   params = [start_time, end_time]
   ```

   **After:**
   ```python
   date_str = target_date.strftime("%Y-%m-%d")
   WHERE DATE(m.created_at) = ?
   params = [date_str]
   ```

3. **`Dockerfile` (Line 30)**
   - Version label updated: `0.2.4.2`

---

## 📊 Testing Results

**Local Test Command:**
```bash
CAMPFIRE_DB_PATH=./tests/fixtures/test.db \
CONTEXT_DIR=./test_output/user_contexts \
uv run python scripts/generate_daily_briefing.py --date 2025-10-04
```

**Results:**
```
✅ 9 messages found (was 0 before Fix 2)
✅ 3 files found (was 0 before Fix 2)
✅ 2 rooms covered
✅ Full briefing content generated
✅ No permission errors (Fix 1 working)
```

**Generated File:**
`./ai-knowledge/company_kb/briefings/2025/10/daily-briefing-2025-10-04.md`

---

## 📦 Docker Images

**Tags Pushed:**
- `hengwoo/campfire-ai-bot:0.2.4.2`
- `hengwoo/campfire-ai-bot:latest`

**Image Digest:** `sha256:d2ea3b1b30db791b50587996d9f99d8fcd7094d5d811ff1e5dc5979d5f5f375d`

**Platform:** `linux/amd64` (DigitalOcean compatible)

---

## 🚀 Production Deployment Steps

### Step 1: SSH to Production Server
```bash
# Use DigitalOcean console (SSH blocked by Cloudflare VPN)
# Server: 128.199.175.50
# User: root
```

### Step 2: Pull New Image
```bash
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:0.2.4.2
docker pull hengwoo/campfire-ai-bot:latest
```

### Step 3: Update Environment Configuration (OPTIONAL)
The script now uses smart defaults that match the docker-compose.yml volume mounts. You **don't need** to modify `.env` unless you want to override defaults.

**Default Behavior (No changes needed):**
```bash
# These paths are automatically used if not specified in .env:
CAMPFIRE_DB_PATH=/campfire-db/production.sqlite3
CONTEXT_DIR=/app/ai-knowledge/user_contexts
```

**If you want to override (optional):**
```bash
# Edit .env file
nano .env

# Add these lines only if you need custom paths:
CAMPFIRE_DB_PATH=/campfire-db/production.sqlite3
CONTEXT_DIR=/app/ai-knowledge/user_contexts
```

### Step 4: Restart Container
```bash
docker-compose up -d
docker logs -f campfire-ai-bot
```

**Expected Log Output:**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 5: Test Daily Briefing Script
```bash
# Test with yesterday's date (default)
docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py

# Test with specific date
docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py --date 2025-10-15

# Test with detailed format
docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py --format detailed
```

**Expected Output (Success):**
```
[Cron] Generating briefing for yesterday: 2025-10-15
[Cron] Target: All rooms
[Cron] Using database: /campfire-db/production.sqlite3
[Cron] ✅ CampfireTools initialized (context_dir: /app/ai-knowledge/user_contexts)
[Cron] 📋 Generating briefing...
[Cron] Debug: Result = {...}
[Cron] ✅ Success!
[Cron]    File: /app/ai-knowledge/briefings/briefing_2025-10-15.md
[Cron]    Messages: 42
[Cron]    Files: 3
[Cron]    Rooms: 5
[Cron]    Participants: 8
[Cron] 🎉 Daily briefing generation complete!
```

### Step 6: Verify Briefing File Created
```bash
# List generated briefings (on host)
ls -lh /var/lib/docker/volumes/ai-service_ai-knowledge/_data/briefings/

# View briefing content
docker exec campfire-ai-bot cat /app/ai-knowledge/briefings/briefing_$(date -d "yesterday" +%Y-%m-%d).md
```

### Step 7: Set Up Cron Job (if not already set up)
```bash
# Edit crontab
sudo crontab -e

# Add this line for 9:00 AM daily briefings:
0 9 * * * docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py >> /var/lib/docker/volumes/ai-service_ai-knowledge/_data/logs/briefing-cron.log 2>&1

# Verify cron job
sudo crontab -l
```

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Container starts successfully (`docker ps | grep campfire-ai-bot`)
- [ ] Health endpoint responds: `curl http://localhost:8000/health`
- [ ] Daily briefing script runs without errors
- [ ] Script finds messages (NOT 0 messages) ← **Fix 2 verification**
- [ ] Briefing file created at `/app/ai-knowledge/briefings/briefing_YYYY-MM-DD.md`
- [ ] Briefing file contains actual message content ← **Fix 2 verification**
- [ ] All 4 bots still working (Financial, Technical, Personal, Briefing)
- [ ] No permission denied errors ← **Fix 1 verification**

---

## 🔍 Troubleshooting

### Issue: Permission Denied (Still)
**Symptom:**
```
[Cron] Error: Failed to initialize CampfireTools: [Errno 13] Permission denied
```

**Solution 1: Check Volume Ownership**
```bash
# On host, check Docker volume
sudo ls -la /var/lib/docker/volumes/ai-service_ai-knowledge/_data/

# Should be owned by UID 1000 (appuser)
# If not, fix ownership:
sudo chown -R 1000:1000 /var/lib/docker/volumes/ai-service_ai-knowledge/_data/
```

**Solution 2: Check Environment Variables**
```bash
# Inside container, verify env vars
docker exec campfire-ai-bot env | grep -E "(CONTEXT_DIR|CAMPFIRE_DB_PATH)"

# Should show:
# CONTEXT_DIR=/app/ai-knowledge/user_contexts  (or empty, defaults work)
# CAMPFIRE_DB_PATH=/campfire-db/production.sqlite3  (or empty, defaults work)
```

**Solution 3: Check Volume Mounts**
```bash
# Verify volumes are mounted correctly
docker inspect campfire-ai-bot | grep -A 10 "Mounts"

# Should show:
# /var/once/campfire/db:/campfire-db:ro
# ai-knowledge:/app/ai-knowledge
```

### Issue: Database Not Found
**Symptom:**
```
[Cron] Error: Database not found at /campfire-db/production.sqlite3
```

**Solution:**
Verify database path in docker-compose.yml:
```yaml
volumes:
  - /var/once/campfire/db:/campfire-db:ro
```

Check database exists on host:
```bash
ls -lh /var/once/campfire/db/production.sqlite3
```

### Issue: No Messages Found (Still)
**Symptom:**
```
[Cron] Debug: Result = {'success': False, 'error': 'No messages found for 2025-10-15'}
```

**This should NOT happen in v0.2.4.2 (Fix 2 addresses this)**

**If it does happen, check:**
```bash
# Verify messages exist in database for that date
docker exec campfire-ai-bot sqlite3 /campfire-db/production.sqlite3 \
  "SELECT COUNT(*), DATE(created_at) FROM messages WHERE DATE(created_at) = '2025-10-15' GROUP BY DATE(created_at);"

# Should return: <count>|2025-10-15
# If 0 results, there really are no messages for that date
```

### Issue: Cron Not Running
**Solution:**
```bash
# Check cron daemon
sudo systemctl status cron

# Check cron logs
sudo grep CRON /var/log/syslog | grep briefing | tail -20

# Verify cron job exists
sudo crontab -l | grep briefing
```

---

## 📊 Design Architecture

### Docker Volume Configuration (docker-compose.yml)
```yaml
volumes:
  # Campfire database (read-only)
  - /var/once/campfire/db:/campfire-db:ro

  # Campfire files (read-only)
  - /var/once/campfire/files:/campfire-files:ro

  # AI knowledge base (read-write, persistent)
  - ai-knowledge:/app/ai-knowledge  # ← Named volume
```

### Container Paths (Used by Scripts)
```
/app/ai-knowledge/user_contexts/     ← CONTEXT_DIR default
/app/ai-knowledge/briefings/         ← Output directory
/app/ai-knowledge/logs/              ← Log directory
/campfire-db/production.sqlite3      ← CAMPFIRE_DB_PATH default
/campfire-files/                     ← Uploaded files
```

### Host Paths (Docker Volume Storage)
```
/var/lib/docker/volumes/ai-service_ai-knowledge/_data/user_contexts/
/var/lib/docker/volumes/ai-service_ai-knowledge/_data/briefings/
/var/lib/docker/volumes/ai-service_ai-knowledge/_data/logs/
/var/once/campfire/db/production.sqlite3
/var/once/campfire/files/
```

---

## 🎯 Design Philosophy: "Soft-Sustainable" Docker Images

### Key Principles Applied in v0.2.4.2:

**1. Configuration via Environment Variables**
- `CONTEXT_DIR` - Configure knowledge base location
- `CAMPFIRE_DB_PATH` - Configure database path
- External .env file, not hardcoded paths

**2. Smart Defaults**
- Defaults match docker-compose.yml volume mounts
- No .env changes required for standard setup
- Container paths, not host paths

**3. Multi-Organization Support**
- Easy to deploy to different servers
- Customize via .env without rebuilding image
- Named volumes for portability

**4. Minimal Rebuilds**
- Change configuration → restart container (seconds)
- Not: change code → rebuild image → push → deploy (minutes)

### Example: Deploying to Different Organization

**Organization A (Standard Setup):**
```yaml
# docker-compose.yml
volumes:
  - ai-knowledge:/app/ai-knowledge  # Default paths work
```

**Organization B (Custom Paths):**
```bash
# .env
CONTEXT_DIR=/custom/path/contexts
CAMPFIRE_DB_PATH=/custom/db/path.sqlite3
```

Same Docker image, different configuration! 🎉

---

## 🔄 Version History

| Version | Date | Changes | Status |
|---------|------|---------|--------|
| v0.2.3 | 2025-10-16 | 3 new bots + API fallback | Deployed (had bot_key bug) |
| v0.2.4 | 2025-10-16 | Bot key hotfix | ✅ Deployed & working |
| **v0.2.4.2** | **2025-10-16** | **Permission fix + Date query fix** | **🎯 READY FOR DEPLOY** |

---

## 📝 Success Criteria

v0.2.4.2 deployment is successful when:

- ✅ Daily briefing script runs without permission errors (Fix 1)
- ✅ Script finds messages (NOT 0 messages) (Fix 2)
- ✅ Briefing files created with actual content
- ✅ Briefings contain messages, files, rooms, participants
- ✅ All 4 bots continue working normally
- ✅ Environment variables correctly configure paths
- ✅ No code changes needed for standard docker-compose.yml setup

---

## 🔄 Rollback Plan

If v0.2.4.2 fails in production:

```bash
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:0.2.4
docker-compose up -d
```

**Note:** Rollback to v0.2.4 brings back permission error AND date query bug, but all bots still work.

---

**Document Version:** 1.0
**Created:** 2025-10-16
**Status:** ✅ Built and Ready for Production Deployment
**Design Philosophy:** "Soft-sustainable" Docker images with external configuration
**Key Achievements:**
- Daily briefing automation with flexible, multi-organization deployment support
- Fixed critical date query bug that caused 0 messages to be returned
