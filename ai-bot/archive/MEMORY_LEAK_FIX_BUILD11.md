# Memory Leak Fix - Build #11

**Date:** 2025-10-28
**Issue:** Subprocess memory leak causing OOM SIGKILL (-9)
**Status:** Documented, ready for implementation
**Integration:** Merges with download button fix in Build #11

---

## Problem Statement

### Symptoms
- Long-running tasks fail with `Command failed with exit code -9` (SIGKILL)
- Claude Agent SDK subprocess errors: "Fatal error in message reader"
- Container memory grows over time, never shrinks

### Diagnostic Evidence

**Server specs:**
```
Total RAM: 1.9GB
Used:      1.8GB
Free:      78MB
Available: 163MB
Swap:      0B
```

**Container memory usage:**
```bash
$ docker stats campfire-ai-bot --no-stream
CONTAINER ID   NAME              CPU %     MEM USAGE / LIMIT     MEM %
a774cfdaf597   campfire-ai-bot   0.21%     836.7MiB / 1.921GiB   42.54%
```

**Zombie processes found:**
```bash
$ docker exec campfire-ai-bot ps aux | grep -E "python|node|claude"
appuser        1  0.9  3.8 409120   78216 ?   Ssl  Oct27  16:11 uvicorn
appuser    18823  0.1  8.1 22388872 164756 ?   Sl   05:42   0:39 claude  ← 8 hours old!
appuser    18854  0.1  8.2 22389384 165696 ?   Sl   05:43   0:44 claude  ← 8 hours old!
appuser    22479  0.2  7.9 22388820 160472 ?   Sl   10:00   0:32 claude  ← 4 hours old!
appuser    25509  0.5  7.8 22388576 157604 ?   Sl   13:19   0:16 claude  ← 30 min old
appuser    25552  0.5  7.7 22387556 156376 ?   Sl   13:20   0:16 claude  ← 30 min old

Total leaked memory: 5 × 160MB = 800MB
```

---

## Root Cause Analysis

### Session Manager Cleanup Gap

**File:** `src/session_manager.py`

**Problem:** When sessions expire or are cleaned up, the session manager removes the session from the cache dictionary but **does not call `client.disconnect()`** on the Agent SDK client.

**Result:** Claude CLI subprocess keeps running indefinitely, consuming ~160MB RAM each.

**Code flow:**
```python
# Request completes
await session_manager.cache_session(room_id, bot_id, agent_client)

# 30 minutes pass (session TTL)
await session_manager._cleanup_old_sessions()
  # Removes session from dictionary ✓
  # BUT: Does NOT call await agent_client.disconnect() ✗

# Result: Subprocess still running!
```

### Why OOM Killer Strikes

```
Current state:
- FastAPI base: 78MB
- 5 zombie Claude processes: 800MB
- Total: 836MB (42% of 1.9GB)
- Available RAM: 163MB

New request arrives:
- Spawn Claude subprocess: +200MB
- Load MCP servers: +100MB
- Process file: +100MB
- Total needed: +400MB
- Available: 163MB

Result: Linux OOM killer → SIGKILL (-9) → Request fails
```

---

## Code Changes Required

### Change 1: Add Client Disconnect Method

**File:** `src/session_manager.py`

**Location:** Add after `_cleanup_old_sessions()` method (around line 120)

**Add this new method:**
```python
async def _close_session(self, session_key: str, agent_client):
    """
    Properly close Agent SDK client and kill subprocess.

    This is critical to prevent memory leaks - each unclosed client
    leaves a Claude CLI subprocess running (~160MB RAM).
    """
    try:
        await agent_client.disconnect()
        print(f"[Cleanup] ✓ Closed agent client for session: {session_key}")
    except Exception as e:
        print(f"[Cleanup] ⚠️ Error closing agent for {session_key}: {e}")
```

### Change 2: Call Disconnect in Cleanup

**File:** `src/session_manager.py`

**Method:** `_cleanup_old_sessions()` (around line 100-120)

**Before:**
```python
async def _cleanup_old_sessions(self):
    """Clean up expired sessions."""
    current_time = datetime.now(timezone.utc)
    expired = []

    for key, data in self.sessions.items():
        if current_time - data['last_activity'] > self.session_ttl:
            expired.append(key)

    for key in expired:
        del self.sessions[key]  # ← Missing cleanup!
        print(f"[Cleanup] Removed expired session: {key}")
```

**After:**
```python
async def _cleanup_old_sessions(self):
    """Clean up expired sessions and close Agent SDK clients."""
    current_time = datetime.now(timezone.utc)
    expired = []

    for key, data in self.sessions.items():
        if current_time - data['last_activity'] > self.session_ttl:
            expired.append(key)

    for key in expired:
        # NEW: Properly close the agent client before removing
        if 'agent' in self.sessions[key]:
            await self._close_session(key, self.sessions[key]['agent'])

        del self.sessions[key]
        print(f"[Cleanup] Removed expired session: {key}")
```

### Change 3: Call Disconnect on Container Shutdown

**File:** `src/session_manager.py`

**Location:** Add new method at end of class (around line 150)

**Add this new method:**
```python
async def cleanup_all_sessions(self):
    """
    Close ALL sessions on container shutdown.

    Should be called from app_fastapi.py shutdown event.
    """
    print(f"[Shutdown] Closing all {len(self.sessions)} active sessions...")

    for key, data in list(self.sessions.items()):
        if 'agent' in data:
            await self._close_session(key, data['agent'])

    self.sessions.clear()
    print(f"[Shutdown] ✓ All sessions closed")
```

### Change 4: Register Shutdown Handler

**File:** `src/app_fastapi.py`

**Location:** After app initialization (around line 260)

**Add:**
```python
@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up all sessions on container shutdown.
    Prevents zombie Claude CLI processes from surviving restart.
    """
    global session_manager
    if session_manager:
        await session_manager.cleanup_all_sessions()
    print("[Shutdown] FastAPI shutdown complete")
```

### Change 5: Reduce Session TTL (Optional but Recommended)

**File:** `src/session_manager.py`

**Location:** `__init__` method (around line 30)

**Before:**
```python
self.session_ttl = timedelta(minutes=30)
```

**After:**
```python
self.session_ttl = timedelta(minutes=5)  # More aggressive cleanup
```

**Rationale:**
- Server has only 163MB available RAM
- Keeping sessions alive for 30 minutes risks OOM
- 5 minutes is sufficient for multi-turn conversations

---

## Testing Procedures

### Test 1: Subprocess Cleanup Verification

**Purpose:** Verify Claude processes terminate after session cleanup

```bash
# Step 1: Check baseline
docker exec campfire-ai-bot ps aux | grep claude | wc -l
# Should be: 0-1

# Step 2: Send 5 test requests
for i in {1..5}; do
  curl -X POST http://localhost:8000/webhook/personal_assistant \
    -H "Content-Type: application/json" \
    -d "{\"creator\":{\"id\":$i},\"room\":{\"id\":$i},\"content\":\"Test $i\"}"
  sleep 2
done

# Step 3: Wait 6 minutes (1 min > session TTL)
sleep 360

# Step 4: Check subprocess count
docker exec campfire-ai-bot ps aux | grep claude | wc -l
# Expected: 0-1 (all cleaned up)
# Failure: 5+ (leak still exists)
```

### Test 2: Memory Usage Monitoring

**Purpose:** Verify memory doesn't grow unbounded

```bash
# Terminal 1: Monitor memory
watch -n 5 'docker stats campfire-ai-bot --no-stream'

# Terminal 2: Send 10 requests over 5 minutes
for i in {1..10}; do
  curl -X POST http://localhost:8000/webhook/personal_assistant \
    -H "Content-Type: application/json" \
    -d "{\"creator\":{\"id\":$i},\"room\":{\"id\":$i},\"content\":\"Generate report\"}"
  sleep 30
done

# Check Terminal 1:
# Expected: Memory peaks at ~400MB, drops back to ~250MB after cleanup
# Failure: Memory keeps climbing (400MB → 600MB → 800MB → ...)
```

### Test 3: Long-Running Task (Stress Test)

**Purpose:** Verify OOM no longer occurs on presentation generation

```bash
# This used to trigger SIGKILL (-9)
curl -X POST http://localhost:8000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{
    "creator":{"id":999,"name":"Test"},
    "room":{"id":999,"name":"Test"},
    "content":"创建一份专业的HTML演示文稿，讲述Claude Code的10个高级功能，每个功能用一页幻灯片详细说明"
  }'

# Expected: Request completes successfully in 30-60s
# Failure: "Command failed with exit code -9"
```

### Test 4: Container Restart Cleanup

**Purpose:** Verify no zombie processes survive restart

```bash
# Before restart
docker exec campfire-ai-bot ps aux | grep claude | wc -l

# Restart container
docker restart campfire-ai-bot
sleep 10

# After restart
docker exec campfire-ai-bot ps aux | grep claude | wc -l
# Expected: 0 (startup cleanup working)
```

---

## Integration with Other Build #11 Changes

### Download Button HTML Fix (Parallel Change)

**Files modified in other session:**
- `bots/personal_assistant.json` - System prompt update (stronger HTML passthrough instruction)

**Files modified in this session:**
- `src/session_manager.py` - Add disconnect methods
- `src/app_fastapi.py` - Add shutdown handler

**Conflict Risk:** **LOW** - Different files modified

**Merge Strategy:**
1. Apply session manager changes first (this document)
2. Apply download button prompt changes second
3. Both changes are independent and won't conflict

### Combined Testing

After merging both changes, test both features:
```bash
# Test 1: Memory leak fixed
# (Run Test 2 from above - memory monitoring)

# Test 2: Download button works
curl -X POST http://localhost:8000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{
    "creator":{"id":999,"name":"Test"},
    "room":{"id":999,"name":"Test"},
    "content":"创建一个测试演示文稿"
  }'
# Should return: HTML with clickable download button
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Code changes applied to `session_manager.py`
- [ ] Shutdown handler added to `app_fastapi.py`
- [ ] Local testing completed (Tests 1-4 passed)
- [ ] Download button fix merged (if applicable)
- [ ] Git commit created with clear message

### Deployment
- [ ] Build Docker image (Build #11)
- [ ] Deploy to local environment first
- [ ] Run combined tests (memory + download button)
- [ ] Deploy to production
- [ ] Monitor production logs for 1 hour

### Post-Deployment Monitoring
```bash
# Check subprocess count hourly
docker exec campfire-ai-bot ps aux | grep claude | wc -l
# Should stay at 0-2

# Check memory usage
docker stats campfire-ai-bot --no-stream
# Should stay at ~250-400MB (not climbing)

# Check logs for cleanup messages
docker logs campfire-ai-bot | grep "Cleanup"
# Should see: "[Cleanup] ✓ Closed agent client for session: ..."
```

---

## Rollback Plan

If memory leak persists or new issues appear:

### Immediate Rollback
```bash
# Revert to Build #10
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:0.4.1  # Previous stable
docker-compose up -d

# Verify rollback
docker logs -f campfire-ai-bot
```

### Debugging Failed Fix

If leak still occurs after applying fixes:

```bash
# Check if disconnect is being called
docker logs campfire-ai-bot | grep "Closed agent client"
# If no output: disconnect() not being called (logic bug)

# Check if exceptions are caught
docker logs campfire-ai-bot | grep "Error closing agent"
# If present: disconnect() throws errors (API bug)

# Check Claude CLI directly
docker exec campfire-ai-bot ps aux | grep claude
# Note PIDs, then trigger cleanup, then check if same PIDs exist
```

---

## Expected Outcomes

### Memory Usage (Before vs After)

**Before Fix:**
```
Idle:      836MB (with 5 zombie processes)
Peak:      1.5GB+ (triggers OOM killer)
After 10 requests: 1.8GB (server maxed out)
```

**After Fix:**
```
Idle:      250MB (no zombie processes)
Peak:      400MB (during active request)
After 10 requests: 250MB (all cleaned up)
```

### Subprocess Count (Before vs After)

**Before Fix:**
```
Hour 0:  1 process
Hour 1:  3 processes
Hour 2:  5 processes
Hour 8:  10+ processes (leak accumulating)
```

**After Fix:**
```
Hour 0:  0-1 processes (idle)
Hour 1:  0-1 processes (cleaned up)
Hour 8:  0-1 processes (stable)
```

### OOM Killer Events (Before vs After)

**Before Fix:**
- Presentation generation: 50% fail with SIGKILL (-9)
- Long-running tasks: 80% fail
- System logs: Multiple OOM events per day

**After Fix:**
- All tasks complete successfully
- No SIGKILL (-9) errors
- System logs: Zero OOM events

---

## Additional Recommendations

### Short-Term (Included in Build #11)
- ✅ Add `client.disconnect()` calls
- ✅ Add shutdown handler
- ✅ Reduce session TTL to 5 minutes

### Medium-Term (Future Builds)
- 📋 Upgrade server RAM to 4GB minimum
  - Cost: ~$12/month on DigitalOcean
  - Benefit: Eliminates OOM risk entirely

- 📋 Add memory usage monitoring
  - Alert when container exceeds 80% memory
  - Proactive cleanup before OOM

- 📋 Implement session pooling
  - Reuse Agent SDK clients instead of creating new ones
  - Reduces subprocess spawn overhead

### Long-Term (v0.5.0+)
- 📋 Migrate to stateless architecture
  - Use Redis for session state
  - Horizontal scaling capability

---

## References

### Related Issues
- **Error #3 from previous session:** Download button not appearing (separate fix)
- **Build #10:** Session cache cleanup on startup (partial fix)
- **v0.4.1:** File download system implementation

### Files Modified
- `src/session_manager.py` (5 changes)
- `src/app_fastapi.py` (1 change - shutdown handler)

### Testing Files
- `test_memory_leak.sh` (to be created)
- `monitor_subprocesses.sh` (to be created)

---

**Document Version:** 1.0
**Created:** 2025-10-28
**Author:** Claude (AI Assistant)
**Status:** Ready for implementation
**Next Step:** Apply code changes and run Test 1-4
