# FastAPI Backend Redesign - Project Memory

**Date:** 2025-10-14
**Status:** Design Phase Complete
**Target:** v2.0.0 Architecture Redesign
**Current Production:** v1.0.16 (Flask + Stateless Resume Pattern)

---

## Executive Summary

We are redesigning the Campfire AI Bot backend to migrate from Flask to FastAPI, enabling **stateful session management** with persistent ClaudeSDKClient instances. This is not just a framework swap—it's a fundamental architectural improvement that leverages the Claude Agent SDK's intended design pattern.

**Key Insight:** The Claude Agent SDK was designed for stateful patterns where clients persist across multiple queries. The `resume` parameter is for crash recovery, not the primary conversation mechanism.

---

## The Problem We're Solving

### Current Architecture (v1.0.16 - Flask)

**The Limitation:**
```python
# Each webhook creates NEW thread with NEW event loop
def webhook():
    thread = threading.Thread(target=background_worker)
    thread.start()

def background_worker():
    loop = asyncio.new_event_loop()  # NEW loop
    client = ClaudeSDKClient(resume=cached_session_id)
    # Process...
    loop.close()  # Client dies
```

**Problems:**
1. ClaudeSDKClient bound to event loop context—cannot be reused across different loops
2. Every webhook = new connection overhead (~4s)
3. Always uses Tier 2 (warm path) with resume overhead
4. Working around SDK's design, not with it

### Target Architecture (v2.0.0 - FastAPI)

**The Solution:**
```python
# FastAPI: Single event loop for entire application
# Clients can persist across multiple webhooks

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize SessionManager
    app.state.session_manager = SessionManager()
    yield
    # Shutdown: Close all sessions gracefully

@app.post("/webhook")
async def webhook(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_message)
    return Response(200)

async def process_message():
    # Reuse existing client from SessionManager
    client = await session_manager.get_or_create_client(...)
    await client.query(new_message)  # Client remembers conversation!
```

**Benefits:**
1. Same event loop—clients CAN be reused
2. No connection overhead for follow-ups (Tier 1: hot path)
3. 40% faster response times (9s vs 15s)
4. Uses SDK's intended stateful design

---

## Three-Tier Session Strategy

This is the **critical design principle** that makes v2.0.0 robust:

### Tier 1: Hot Path (In-Memory Persistent Clients)
```
Best case: Client still in memory
Performance: ~9 seconds
Use case: Follow-up questions within 24 hours
Strategy: Reuse existing connected client instantly
```

### Tier 2: Warm Path (Disk-Persisted Session Recovery)
```
Client died, but session_id saved to disk
Performance: ~12 seconds
Use case: After container restart or memory cleanup
Strategy: Resume session from disk using ClaudeSDKClient(resume=...)
```

### Tier 3: Cold Path (Fresh Start)
```
No client, no session_id
Performance: ~15 seconds
Use case: First conversation or expired session (>24h)
Strategy: Create fresh client, capture new session_id, save to disk
```

**Why This Matters:**
- Most requests use Tier 1 (hot path) → 40% faster
- Crash recovery via Tier 2 (warm path) → seamless UX
- Session IDs persisted to disk → survives container restarts

---

## Session ID Persistence - CRITICAL CORRECTION

**Initial Design Mistake:** Thought we could eliminate session ID tracking.
**User Correction:** Session IDs are ESSENTIAL for crash recovery.
**Corrected Design:** Track session IDs AND persist to disk.

### Why Session IDs Are Mandatory

1. **Container Restarts** - All in-memory clients lost, need to resume from session_id
2. **Application Crashes** - Clients destroyed, session_id allows recovery
3. **Deployment Updates** - New version deployed, sessions must resume
4. **Memory Cleanup** - Old clients removed, can recreate with resume later

### Disk Persistence Implementation

**File Structure:**
```
./session_cache/
├── session_1_financial_analyst.json
├── session_1_technical_assistant.json
└── session_2_financial_analyst.json
```

**File Format:**
```json
{
  "session_id": "abc-123",
  "room_id": 1,
  "bot_id": "financial_analyst",
  "last_used": "2025-10-14T08:24:49.123456",
  "created_at": "2025-10-14T08:21:55.789012"
}
```

**Operations:**
```python
# Save immediately after capturing session_id
session_manager.update_session_id(room_id, bot_id, session_id)
# → Writes to ./session_cache/session_{room}_{bot}.json

# Load on client creation (after restart)
session_id = session_manager._load_session_id_from_disk(room_id, bot_id)
if session_id:
    agent = CampfireAgent(resume_session=session_id, ...)  # Tier 2
else:
    agent = CampfireAgent(...)  # Tier 3
```

---

## Key Components

### 1. SessionManager (`src/session_manager.py` - NEW)

**Responsibilities:**
- Maintain in-memory cache of persistent clients
- Persist session IDs to disk for crash recovery
- Auto-cleanup expired sessions (both memory and disk)
- Graceful shutdown handling

**SessionState:**
```python
@dataclass
class SessionState:
    client: ClaudeSDKClient
    agent: CampfireAgent         # Keep for context building
    session_id: Optional[str]    # Persist to disk
    last_used: datetime
    room_id: int
    bot_id: str
    connected: bool
    query_count: int
    created_at: datetime
```

**Key Methods:**
```python
async def get_or_create_client(...) -> ClaudeSDKClient:
    # 1. Check in-memory cache (Tier 1)
    # 2. Check disk for session_id (Tier 2)
    # 3. Create fresh client (Tier 3)

def update_session_id(room_id, bot_id, session_id):
    # Update in-memory AND persist to disk immediately

async def cleanup_inactive_sessions(max_age_hours=24):
    # Clean both in-memory cache and disk files
```

### 2. FastAPI Application (`src/app_fastapi.py` - NEW)

**Lifespan Management:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.session_manager = SessionManager(ttl_hours=24)
    app.state.bot_manager = BotManager(...)
    app.state.tools = CampfireTools(...)

    yield  # App runs

    # Shutdown
    await app.state.session_manager.shutdown_all()
```

**Webhook Endpoint:**
```python
@app.post("/webhook/{bot_id}")
async def webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    bot_id: str
):
    payload = await request.json()

    # Add background task (runs in SAME event loop)
    background_tasks.add_task(
        process_message_async,
        room_id=payload['room']['id'],
        content=payload['content'],
        bot_id=bot_id,
        session_manager=request.app.state.session_manager
    )

    return Response(status_code=200)  # Immediate return
```

### 3. CampfireAgent (`src/campfire_agent.py` - MINIMAL CHANGES)

**What STAYS the same:**
- ✅ `resume_session` parameter in `__init__`
- ✅ Session ID extraction in `process_message`
- ✅ Return type: `tuple[str, Optional[str]]`
- ✅ All existing functionality

**Why:** Enables three-tier strategy with disk persistence.

**No changes needed** - current implementation already supports persistent clients!

---

## Performance Comparison

### v1.0.16 (Flask - Every webhook = Tier 2)
```
User Q1: 15s (cold start)
User Q2: 15s (warm - resume)
User Q3: 15s (warm - resume)
[Container restart]
User Q4: 15s (warm - resume)
User Q5: 15s (warm - resume)
```

### v2.0.0 (FastAPI - Smart tiering)
```
User Q1: 15s (cold start)
User Q2:  9s (hot - reuse) ← 40% faster!
User Q3:  9s (hot - reuse)
[Container restart]
User Q4: 12s (warm - resume from disk)
User Q5:  9s (hot - reuse)
```

**Key Insight:** Most requests use hot path = dramatically better UX.

---

## Migration Plan

### Phase 1: Design (COMPLETE ✅)
- Research FastAPI patterns
- Design SessionManager with disk persistence
- Document three-tier strategy
- Create comprehensive design doc

### Phase 2: Implementation (NEXT)
1. Create `src/session_manager.py`
2. Create `src/app_fastapi.py`
3. Update dependencies (add FastAPI, uvicorn, httpx)
4. NO changes to `campfire_agent.py` needed!

### Phase 3: Testing
1. Unit tests for SessionManager
2. Integration tests for FastAPI app
3. Local testing with test.db
4. Verify session persistence across restarts

### Phase 4: Deployment
1. Docker build with tag `2.0.0-alpha`
2. Test in staging (if available)
3. Monitor memory usage and session cleanup
4. Deploy to production
5. Keep v1.0.16 image for rollback

---

## Dependency Changes

**Remove:**
- `flask` - Synchronous web framework
- `gunicorn` - WSGI server
- `requests` - Synchronous HTTP client

**Add:**
- `fastapi` - Async web framework
- `uvicorn[standard]` - ASGI server
- `httpx` - Async HTTP client

**Keep:**
- All existing dependencies (anthropic, claude-agent-sdk, etc.)

---

## Critical Design Decisions Made

### Decision 1: Keep Session ID Tracking
**Initial thought:** Eliminate session IDs with persistent clients
**User feedback:** Session IDs needed for crash recovery
**Final decision:** Track session IDs AND persist to disk
**Rationale:** Enables three-tier strategy with robust crash recovery

### Decision 2: Per-Room Sessions (Not Per-User)
**Cache key:** `(room_id, bot_id)`
**Rationale:** Campfire is group chat, bot participates in group conversation
**Benefit:** All users see full context including each other's messages

### Decision 3: 24-Hour TTL for Sessions
**Default:** 24 hours inactive → cleanup
**Rationale:** Balance between memory usage and conversation continuity
**Configurable:** Can adjust per bot if needed

### Decision 4: Single Worker Deployment Initially
**Strategy:** One uvicorn worker, sessions in process memory
**Future:** Add Redis for multi-worker if needed
**Rationale:** Simpler for MVP, scales vertically first

---

## Risk Mitigation

### Risk 1: Memory Leaks
**Mitigation:**
- Aggressive TTL (24h → consider 6h)
- Memory-based cleanup (if >80% memory, remove 50% oldest)
- Monitoring endpoint: `/metrics` with memory usage

### Risk 2: Client Hangs
**Mitigation:**
- Query timeout (3 minutes max)
- Health check per session (kill if stuck >5 min)
- Session removal on timeout

### Risk 3: Race Conditions
**Mitigation:**
- `asyncio.Lock()` in SessionManager
- Existing request_queue prevents concurrent access per room
- Thoroughly test with concurrent webhooks

---

## Testing Strategy

### Unit Tests
```python
tests/test_session_manager.py:
- test_create_new_session
- test_reuse_existing_session
- test_cleanup_expired_sessions
- test_concurrent_access_thread_safety
- test_disk_persistence_save_load
```

### Integration Tests
```python
tests/test_app_fastapi.py:
- test_webhook_creates_session
- test_webhook_reuses_session
- test_conversation_continuity
- test_crash_recovery_from_disk
```

### Load Tests
```python
locustfile.py:
- Simulate 100 users across 10 rooms
- Measure response time, memory usage, error rate
- Verify session cleanup works under load
```

---

## Open Questions & Answers

### Q1: Should we make session scope configurable?
**Current:** Per-room sessions (all users share conversation)
**Alternative:** Per-user sessions (private conversations)
**Decision:** Start with per-room, add per-user option later if needed
**In bot config:**
```json
{
  "session_scope": "room"  // or "user"
}
```

### Q2: Should sessions persist across deployments?
**Current:** Sessions in process memory, disk files survive restarts
**Enhancement:** Could add Redis for distributed cache
**Decision:** Start simple (disk files), add Redis if scaling needed

### Q3: Should we add session monitoring dashboard?
**Current:** `/session/stats` endpoint returns JSON
**Enhancement:** Web UI to view active sessions, memory usage, etc.
**Decision:** API first, UI later if useful

---

## Success Criteria

v2.0.0 is successful when:

1. ✅ FastAPI server starts and handles webhooks
2. ✅ SessionManager creates and reuses clients correctly
3. ✅ Follow-up messages 40% faster (9s vs 15s)
4. ✅ Bot remembers conversation without explicit resume
5. ✅ Session IDs persist to disk
6. ✅ Crash recovery works (restart container, conversation continues)
7. ✅ Session cleanup works (memory + disk)
8. ✅ Graceful shutdown closes all clients
9. ✅ No memory leaks under extended operation
10. ✅ Request queue still prevents concurrent processing

---

## Key Files & Documentation

**Design Documents:**
- `/Users/heng/Development/campfire/ai-bot/FASTAPI_MIGRATION_DESIGN.md` - Complete technical design
- `/Users/heng/Development/campfire/FASTAPI_REDESIGN_MEMORY.md` - This file (project memory)

**Current Implementation (v1.0.16):**
- `src/app.py` - Flask webhook server
- `src/campfire_agent.py` - Agent wrapper (already compatible with v2.0.0!)
- `src/session_cache.py` - Simple session ID cache (replaced by SessionManager)
- `src/request_queue.py` - Concurrency control (keep as-is)

**New Implementation (v2.0.0):**
- `src/session_manager.py` - NEW: Persistent client manager with disk persistence
- `src/app_fastapi.py` - NEW: FastAPI webhook server
- `src/session_cache/` - NEW: Directory for disk-persisted session files
- `src/campfire_agent.py` - NO CHANGES NEEDED!

---

## Rollback Plan

If v2.0.0 fails in production:

```bash
# Emergency rollback
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:1.0.16
docker-compose up -d
```

**Keep these images available:**
- `hengwoo/campfire-ai-bot:1.0.16` - Last stable Flask version
- `hengwoo/campfire-ai-bot:2.0.0-alpha` - Testing version
- `hengwoo/campfire-ai-bot:2.0.0` - Production FastAPI version

---

## Timeline Estimate

**Total:** 2-3 weeks

**Week 1: Implementation**
- Day 1-2: Create SessionManager with disk persistence
- Day 3-4: Create FastAPI app
- Day 5: Update dependencies, write unit tests

**Week 2: Testing**
- Day 1-2: Integration tests
- Day 3: Local testing with test.db
- Day 4: Test crash recovery and session persistence
- Day 5: Load testing, performance benchmarking

**Week 3: Deployment**
- Day 1: Docker build, alpha testing
- Day 2-3: Staging deployment (if available)
- Day 4: Production deployment with monitoring
- Day 5: Buffer for issues

---

## References

**Research Sources:**
- FastAPI lifespan events: https://fastapi.tiangolo.com/advanced/events/
- FastAPI background tasks: https://fastapi.tiangolo.com/tutorial/background-tasks/
- Claude Agent SDK sessions: https://docs.claude.com/en/api/agent-sdk/sessions
- Singleton pattern with FastAPI: https://medium.com/@hieutrantrung.it/using-fastapi-like-a-pro-with-singleton-and-dependency-injection-patterns-28de0a833a52

**User Research:**
- Claude.ai conversation on stateful webhook bot patterns
- Key recommendation: Use ClaudeSDKClient as persistent resource, leverage `resume` for crash recovery

---

## Future Enhancements (Post-v2.0.0)

### Multi-Worker Support with Redis
```python
# Distributed session cache
session_manager = SessionManager(redis_url="redis://localhost:6379")
# All workers share same session cache via Redis
```

### Advanced Monitoring
```python
# Prometheus metrics
from prometheus_client import Gauge
active_sessions = Gauge('active_sessions', 'Number of active sessions')
memory_usage = Gauge('memory_usage_mb', 'Memory usage in MB')
```

### WebSocket Streaming
```python
@app.websocket("/ws/{room_id}/{bot_id}")
async def websocket_endpoint(websocket: WebSocket):
    # Real-time streaming responses
    async for chunk in client.receive_response():
        await websocket.send_text(chunk)
```

### Session Analytics Dashboard
- Web UI to view active sessions
- Memory usage per session
- Query count, average response time
- Session lifecycle visualizations

---

**Document Version:** 1.0
**Last Updated:** 2025-10-14
**Status:** Design Complete, Ready for Implementation
**Next Action:** Create `src/session_manager.py`

---

## For Future Claude Sessions

**When resuming this work:**

1. Read this file first for complete context
2. Review `FASTAPI_MIGRATION_DESIGN.md` for technical details
3. Check current production version in CLAUDE.md
4. Verify no v1.0.x work is in progress before starting v2.0.0
5. Remember: Session IDs MUST be tracked and persisted to disk!

**Key Principle to Remember:**
The three-tier strategy (hot/warm/cold) is what makes this architecture robust. We're not just making things faster—we're building a system that gracefully handles crashes, restarts, and long conversations while still being fast for the common case.
