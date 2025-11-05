# Docker Shutdown Optimization - v0.4.1

**Date:** 2025-10-27
**Status:** ✅ Implemented
**Estimated Improvement:** 10+ seconds → ~2-3 seconds

---

## Problem Statement

Docker container shutdown was taking 10+ seconds (used to be instant). This caused:
- Slow deployments
- Delayed restarts
- Poor developer experience
- Potential resource leaks

## Root Causes Identified

1. **Claude SDK clients not properly closed** (session_manager.py:356 TODO)
   - SessionManager._close_session() was not calling disconnect()
   - Relied on garbage collection instead of explicit cleanup
   - SDK clients maintain connections that need explicit closure

2. **No stop_grace_period in docker-compose.yml**
   - Docker defaults to 10 seconds before sending SIGKILL
   - Not enough time for graceful cleanup if SDK clients are slow to respond

3. **MCP subprocess cleanup delays**
   - External MCP servers (Skills MCP, Financial MCP) run as subprocesses
   - Need to be terminated properly via SDK disconnect

## Solution Implemented

### 1. Proper SDK Client Cleanup (session_manager.py)

**File:** `src/session_manager.py`
**Lines:** 346-367 (updated)

**Before:**
```python
async def _close_session(self, cache_key: Tuple[int, str]):
    if cache_key in self._sessions:
        session_state = self._sessions[cache_key]

        # TODO: Close client connection if SDK provides close method
        # For now, just remove from cache and let garbage collection handle it

        del self._sessions[cache_key]
```

**After:**
```python
async def _close_session(self, cache_key: Tuple[int, str]):
    if cache_key in self._sessions:
        session_state = self._sessions[cache_key]

        # Properly disconnect Claude SDK client
        try:
            if session_state.client:
                await session_state.client.disconnect()
                print(f"[SessionManager] 🔌 Disconnected Claude SDK client")
        except Exception as e:
            print(f"[SessionManager] ⚠️  Error disconnecting client: {e}")

        del self._sessions[cache_key]
```

**What this does:**
- Calls `ClaudeSDKClient.disconnect()` to properly close connections
- Handles Claude API connection closure
- Terminates stdio-based MCP server subprocesses (Skills MCP, Financial MCP)
- Cleans up asyncio resources
- Gracefully handles errors during disconnect

### 2. Extended Graceful Shutdown Period (docker-compose.yml)

**File:** `docker-compose.yml`
**Lines:** 18-19 (added)

**Change:**
```yaml
# Graceful shutdown timeout (allow time for SDK clients to disconnect)
stop_grace_period: 30s
```

**What this does:**
- Gives Docker 30 seconds to gracefully shutdown before sending SIGKILL
- Allows time for:
  - FastAPI lifespan shutdown handler to run
  - SessionManager.shutdown_all() to complete
  - All SDK clients to disconnect
  - MCP subprocesses to terminate
- Default was 10 seconds (too short for multiple active sessions)

## Technical Details

### ClaudeSDKClient.disconnect() Method

From Claude Agent SDK documentation:

```python
async def disconnect(self) -> None
```

This method:
- Closes the connection to Claude API
- Terminates any stdio-based MCP server subprocesses
- Cleans up asyncio event loop resources
- Should be called when client is no longer needed

**Context Manager Alternative:**
The SDK also supports async context manager pattern:
```python
async with ClaudeSDKClient(options=options) as client:
    # Use client
# Automatic cleanup via __aexit__
```

However, we don't use this pattern because:
1. We want persistent sessions across webhook requests (hot/warm/cold path optimization)
2. Context manager would create/destroy client for each request (slow)
3. SessionManager provides better control over lifecycle

### Shutdown Flow

```
Docker sends SIGTERM
    ↓
FastAPI receives shutdown signal
    ↓
Lifespan shutdown handler called (app_fastapi.py:217)
    ↓
SessionManager.shutdown_all() called
    ↓
For each active session:
    ├─ SessionManager._close_session() called
    ├─ ClaudeSDKClient.disconnect() called
    │   ├─ Close Claude API connection
    │   ├─ Terminate Skills MCP subprocess (if active)
    │   └─ Terminate Financial MCP subprocess (if active)
    └─ Remove session from cache
    ↓
All sessions cleaned up
    ↓
Container exits gracefully (exit code 0)
```

**If shutdown takes > 30 seconds:**
- Docker sends SIGKILL (forceful termination)
- Container exits immediately (exit code 137)
- Not ideal, but prevents infinite hangs

## Expected Performance

**Before optimization:**
- Shutdown time: 10-15 seconds
- Exit code: 143 (SIGTERM) or 137 (SIGKILL)
- Warning: "Service didn't stop gracefully"

**After optimization:**
- Shutdown time: 2-3 seconds (typical with 1-3 active sessions)
- Exit code: 0 (clean shutdown)
- No warnings

**Worst case (many active sessions):**
- Shutdown time: 5-10 seconds (20+ active sessions)
- Still completes within 30s grace period
- Still much faster than before

## Testing Instructions

### Local Testing

1. **Start the service:**
   ```bash
   cd /Users/heng/Development/campfire/ai-bot
   docker-compose up -d
   ```

2. **Create some active sessions:**
   ```bash
   # Send 3 requests to different bots to create sessions
   curl -X POST http://localhost:8000/webhook/financial_analyst \
     -H "Content-Type: application/json" \
     -d '{"creator":{"id":1,"name":"Test"},"room":{"id":1,"name":"Test"},"content":"你好"}'

   curl -X POST http://localhost:8000/webhook/personal_assistant \
     -H "Content-Type: application/json" \
     -d '{"creator":{"id":1,"name":"Test"},"room":{"id":2,"name":"Test"},"content":"你好"}'

   curl -X POST http://localhost:8000/webhook/operations_assistant \
     -H "Content-Type: application/json" \
     -d '{"creator":{"id":1,"name":"Test"},"room":{"id":3,"name":"Test"},"content":"你好"}'
   ```

3. **Test shutdown performance:**
   ```bash
   # Time the shutdown
   time docker-compose down

   # Check logs for disconnect messages
   docker logs campfire-ai-bot 2>&1 | grep -A5 "Shutting down"
   ```

4. **Verify clean shutdown:**
   ```bash
   # Check exit code (should be 0)
   docker inspect campfire-ai-bot --format='{{.State.ExitCode}}'

   # Should see these log messages:
   # [SessionManager] 🔌 Disconnected Claude SDK client
   # [SessionManager] 🗑️  Closed session for room X, bot 'Y'
   # [Shutdown] ✅ Shutdown complete
   ```

### Production Deployment Testing

After deploying to production:

```bash
# SSH to server
ssh root@128.199.175.50

# Check current active sessions
curl http://localhost:5000/cache/stats

# Test shutdown
cd /root/ai-service
time docker-compose restart

# Should complete in < 5 seconds
# Check logs
docker logs campfire-ai-bot --tail 50
```

## Monitoring

### Success Indicators

✅ **Docker shutdown completes in < 5 seconds**
✅ **Container exit code is 0**
✅ **Logs show "Disconnected Claude SDK client" messages**
✅ **Logs show "Shutdown complete" message**
✅ **No "Service didn't stop gracefully" warnings**

### Failure Indicators

❌ **Shutdown takes > 10 seconds**
❌ **Exit code is 137 (SIGKILL)**
❌ **Logs show disconnect errors**
❌ **MCP subprocesses remain after shutdown (zombie processes)**

### Rollback Plan

If issues occur, revert both files:

```bash
git checkout HEAD~1 -- src/session_manager.py docker-compose.yml
docker-compose build
docker-compose up -d
```

## Files Modified

1. **src/session_manager.py** (line 356-367)
   - Added `await session_state.client.disconnect()` call
   - Added error handling for disconnect failures
   - Added log message for successful disconnects

2. **docker-compose.yml** (line 18-19)
   - Added `stop_grace_period: 30s`
   - Added comment explaining purpose

## Dependencies

- `claude-agent-sdk>=0.1.4` - Provides `ClaudeSDKClient.disconnect()` method
- No new dependencies added

## Benefits

1. **Faster Deployments** - 10+ seconds saved per restart
2. **Cleaner Resource Management** - No reliance on garbage collection
3. **Better Developer Experience** - Immediate feedback during development
4. **Proper MCP Cleanup** - Subprocesses terminated correctly
5. **Production Readiness** - Graceful shutdowns prevent data loss

## Future Enhancements

**Not included in this PR, but could be added later:**

1. **Connection Pooling** - Reuse HTTP connections across sessions
2. **Lazy MCP Loading** - Only start MCP servers when first needed
3. **Session Timeout** - Automatically disconnect idle sessions earlier
4. **Health Check Integration** - Expose session metrics to health endpoint
5. **Metrics Collection** - Track shutdown time, active sessions, disconnect failures

## Conclusion

This optimization addresses all three root causes:
1. ✅ SDK clients properly closed via `disconnect()`
2. ✅ Adequate grace period for cleanup (30s)
3. ✅ MCP subprocesses terminated via SDK disconnect

Expected improvement: **10+ seconds → 2-3 seconds** (80-85% reduction)

---

**Document Version:** 1.0
**Created:** 2025-10-27
**Status:** ✅ Ready for testing
**Target Version:** v0.4.1
