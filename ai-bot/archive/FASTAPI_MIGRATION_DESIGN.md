# FastAPI Migration Design - v2.0.0 Stateful Architecture

**Status:** Design Phase
**Target Version:** v2.0.0
**Created:** 2025-10-14
**Objective:** Migrate from Flask + stateless resume pattern to FastAPI + stateful session management

---

## Executive Summary

**Current Problem (v1.0.16):**
- Flask webhook creates NEW thread + NEW event loop for each request
- Cannot reuse ClaudeSDKClient instances across webhooks (event loop context limitation)
- Workaround: Use `resume=session_id` parameter to load conversation history
- This works but is NOT the intended SDK design pattern

**Target Solution (v2.0.0):**
- FastAPI native async with single event loop
- Persistent ClaudeSDKClient instances per (room_id, bot_id) pair
- Multiple `query()` calls on SAME client naturally maintains conversation context
- Uses SDK's intended stateful session management design

**Key Insight from Research:**
The Claude Agent SDK was designed for stateful patterns where ClaudeSDKClient lives across multiple query() calls. The `resume` parameter is for session recovery (crashes, restarts), not as the primary conversation continuity mechanism.

---

## Architecture Comparison

### Current Flask Architecture (v1.0.16)

```
Webhook Request
    ↓
Flask Handler (sync, creates daemon thread)
    ↓
Background Thread
    ↓
NEW asyncio.new_event_loop() [Problem: different loop each time]
    ↓
CampfireAgent.__init__(resume_session=cached_session_id)
    ↓
ClaudeSDKClient created with resume parameter
    ↓
client.connect() → query() → receive_response()
    ↓
Extract session_id, cache for next webhook
    ↓
loop.close() [Client destroyed]
```

**Issues:**
1. Each webhook = NEW event loop context
2. ClaudeSDKClient cannot be reused across different event loops
3. All conversation context must be reloaded via `resume` parameter
4. Pattern doesn't leverage SDK's natural stateful design

---

### Target FastAPI Architecture (v2.0.0)

```
Application Startup (lifespan event)
    ↓
Initialize SessionManager (app.state.session_manager)
    ↓
[Sessions persist until timeout/shutdown]

---

Webhook Request (async def)
    ↓
FastAPI Handler (native async)
    ↓
BackgroundTasks.add_task(process_message_async)
    ↓
Return 200 OK immediately
    ↓
[Background task runs in SAME event loop]
    ↓
SessionManager.get_or_create_client(room_id, bot_id)
    ↓
Reuse EXISTING ClaudeSDKClient (already connected)
    ↓
client.query(new_message)  [No resume needed - client remembers!]
    ↓
client.receive_response()
    ↓
Post to Campfire
    ↓
[Client remains alive for next webhook]
```

**Benefits:**
1. Single event loop - clients can be reused
2. Conversation context maintained naturally by SDK
3. No need to cache/reload session_id for every request
4. Faster responses (client already connected + warmed up)
5. Aligns with SDK's intended design

---

## Key Components

### 1. SessionManager (NEW)

**Purpose:** Manage lifecycle of persistent ClaudeSDKClient instances with crash recovery

**File:** `src/session_manager.py`

**Key Features:**
- Thread-safe in-memory cache: `{(room_id, bot_id): SessionState}`
- Disk persistence for session IDs (crash recovery)
- Auto-cleanup for inactive sessions (24h TTL)
- Graceful shutdown handling
- Three-tier session strategy (hot/warm/cold)

**SessionState Structure:**
```python
@dataclass
class SessionState:
    client: ClaudeSDKClient
    agent: CampfireAgent         # ✅ Keep agent for context building
    session_id: Optional[str]    # ✅ Track for disk persistence
    last_used: datetime
    room_id: int
    bot_id: str
    connected: bool
    query_count: int
    created_at: datetime
```

**Core Methods:**
```python
async def get_or_create_client(
    room_id: int,
    bot_id: str,
    bot_config: BotConfig,
    campfire_tools: CampfireTools
) -> ClaudeSDKClient:
    """
    Get existing client or create new one.

    Strategy:
    1. Check in-memory cache (Tier 1: Hot path)
    2. Check disk for session_id (Tier 2: Warm path)
    3. Create fresh client (Tier 3: Cold path)
    """

def update_session_id(room_id: int, bot_id: str, session_id: str):
    """
    Update session_id and persist to disk.
    Called after capturing session_id from SystemMessage.
    """

def _save_session_id_to_disk(room_id: int, bot_id: str, session_id: str):
    """Save session_id to ./session_cache/session_{room}_{bot}.json"""

def _load_session_id_from_disk(room_id: int, bot_id: str) -> Optional[str]:
    """
    Load session_id from disk (for crash recovery).
    Returns None if file doesn't exist or session expired.
    """

async def cleanup_inactive_sessions(max_age_hours: int = 24):
    """
    Remove sessions older than TTL.
    Cleans both in-memory cache and disk files.
    """

async def shutdown_all():
    """
    Graceful shutdown for all sessions.
    Closes clients, keeps disk files for recovery.
    """
```

---

### 2. FastAPI Application (REPLACE app.py)

**File:** `src/app_fastapi.py` (or replace `src/app.py`)

**Lifespan Event:**
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[Startup] Initializing SessionManager...")
    app.state.session_manager = SessionManager(
        ttl_hours=24,
        cleanup_interval=3600  # 1 hour
    )

    # Start cleanup task
    cleanup_task = asyncio.create_task(
        app.state.session_manager.periodic_cleanup()
    )

    yield

    # Shutdown
    print("[Shutdown] Gracefully closing all sessions...")
    await app.state.session_manager.shutdown_all()
    cleanup_task.cancel()

app = FastAPI(lifespan=lifespan)
```

**Webhook Endpoint:**
```python
@app.post("/webhook")
@app.post("/webhook/{bot_id}")
async def webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    bot_id: Optional[str] = None
):
    """
    Campfire webhook endpoint (returns immediately)
    """
    payload = await request.json()

    # Extract webhook data
    creator = payload.get('creator') or payload.get('user')
    room = payload.get('room')
    content = payload.get('content') or ...

    # Validation...

    # Add background task
    background_tasks.add_task(
        process_message_async,
        room_id=room['id'],
        user_id=creator['id'],
        user_name=creator['name'],
        room_name=room['name'],
        content=content,
        bot_id=bot_id,
        session_manager=request.app.state.session_manager
    )

    # Return immediately (Campfire requirement)
    return Response(status_code=200)
```

**Background Task:**
```python
async def process_message_async(
    room_id: int,
    user_id: int,
    user_name: str,
    room_name: str,
    content: str,
    bot_id: str,
    session_manager: SessionManager
):
    """Process message in background (FastAPI native async)"""

    # Get bot config
    bot_config = bot_manager.get_bot_by_id(bot_id) or bot_manager.get_default_bot()

    # Get or create persistent client
    client = await session_manager.get_or_create_client(
        room_id=room_id,
        bot_id=bot_config.bot_id,
        bot_config=bot_config,
        campfire_tools=tools
    )

    # Process message using EXISTING client
    # No resume parameter needed - client remembers conversation!
    response = await process_with_client(
        client=client,
        content=content,
        context={...}
    )

    # Post to Campfire
    await post_to_campfire_async(room_id, response)
```

---

### 3. Modified CampfireAgent

**CORRECTION:** CampfireAgent KEEPS session ID tracking for crash recovery!

**Changes to `src/campfire_agent.py`:**

**Keep (NO CHANGES):**
- `resume_session` parameter from `__init__` ✅
- Session ID extraction logic ✅
- Return type: `tuple[str, Optional[str]]` ✅
- All current functionality ✅

**Why:** Session IDs enable crash recovery and session persistence to disk.

**Updated Pattern:**
```python
class CampfireAgent:
    """
    Wrapper for persistent ClaudeSDKClient instances.

    For v2.0.0 stateful pattern with crash recovery:
    - Persistent clients for hot path performance
    - Session ID tracking for crash recovery
    - Resume parameter for warm path recovery
    - Three-tier strategy: hot/warm/cold
    """

    def __init__(
        self,
        bot_config: BotConfig,
        campfire_tools: CampfireTools,
        resume_session: Optional[str] = None  # ✅ KEEP THIS!
    ):
        self.bot_config = bot_config
        self.campfire_tools = campfire_tools
        self.client: Optional[ClaudeSDKClient] = None
        self.resume_session = resume_session  # ✅ KEEP THIS!

        # Initialize tools
        initialize_tools(campfire_tools)

        # Create client
        self._create_client()

        self._connected = False

    def _create_client(self):
        """Create Claude Agent SDK client with bot configuration"""
        # ... (same MCP setup)

        options_dict = {
            "model": self.bot_config.model,
            "system_prompt": self.bot_config.system_prompt,
            "mcp_servers": mcp_servers,
            "allowed_tools": allowed_tools,
            "permission_mode": 'default',
            "cwd": cwd_path,
            "max_turns": 30
        }

        # ✅ KEEP RESUME PARAMETER FOR CRASH RECOVERY!
        if self.resume_session:
            options_dict["resume"] = self.resume_session
            print(f"[Agent Init] 🔄 Resuming session: {self.resume_session}")
        else:
            print(f"[Agent Init] 🆕 Starting new session")

        options = ClaudeAgentOptions(**options_dict)
        self.client = ClaudeSDKClient(options=options)

    async def process_message(
        self,
        content: str,
        context: Dict,
        on_text_block: Optional[Callable[[str], None]] = None
    ) -> tuple[str, Optional[str]]:  # ✅ STILL RETURN SESSION_ID!
        """
        Process message with persistent client.

        Returns:
            Tuple of (response_text, session_id)
            - response_text: AI response
            - session_id: Session ID for persistence (may be None on subsequent calls)
        """
        if not self.client:
            raise RuntimeError("Agent client not initialized")

        # Connect ONCE (first time only)
        if not self._connected:
            await self.client.connect()
            self._connected = True

        # Build prompt
        prompt = self._build_prompt(content, context)

        # Query on EXISTING client (remembers previous queries)
        await self.client.query(prompt)

        # Receive response and extract session_id
        response_text = ""
        session_id = None

        async for message in self.client.receive_response():
            print(f"[Agent SDK] Received: {message.__class__.__name__}")

            # ✅ KEEP SESSION ID EXTRACTION FOR DISK PERSISTENCE!
            if hasattr(message, '__class__') and message.__class__.__name__ == 'SystemMessage':
                if hasattr(message, 'subtype') and message.subtype == 'init':
                    if hasattr(message, 'data') and 'session_id' in message.data:
                        session_id = message.data['session_id']
                        print(f"[Agent Session] 💾 Captured session_id: {session_id}")

            # Extract text blocks
            if hasattr(message, '__class__') and message.__class__.__name__ == 'AssistantMessage':
                if hasattr(message, 'content'):
                    for block in message.content:
                        if block.__class__.__name__ == 'TextBlock':
                            if hasattr(block, 'text'):
                                text = block.text
                                response_text += text
                                if on_text_block and text.strip():
                                    try:
                                        on_text_block(text)
                                    except Exception as e:
                                        print(f"[Warning] Error in callback: {e}")

        return response_text, session_id  # ✅ RETURN BOTH!
```

---

## Three-Tier Session Strategy

**CRITICAL DESIGN PRINCIPLE:** Session IDs enable crash recovery and must be persisted to disk.

### Tier 1: Hot Path (In-Memory Persistent Clients)
```python
# Best case: Client still in memory from previous webhook
client = await session_manager.get_or_create_client(room_id, bot_id, ...)
# Returns: Existing connected client instantly
# Performance: ~9 seconds (no connection overhead)
# Use case: Follow-up questions within 24 hours
```

### Tier 2: Warm Path (Disk-Persisted Session Recovery)
```python
# Client died (restart/cleanup), but session_id persisted to disk
session_id = load_from_disk(room_id, bot_id)  # "abc-123"
client = ClaudeSDKClient(resume="abc-123")
await client.connect()
# SDK contacts Claude API to restore conversation history
# Performance: ~12 seconds (resume overhead)
# Use case: After container restart or memory cleanup
```

### Tier 3: Cold Path (Fresh Start)
```python
# No client in memory, no session_id on disk
client = ClaudeSDKClient()  # No resume
await client.connect()
# Claude API assigns new session_id
# Save to disk: ./session_cache/session_{room}_{bot}.json
# Performance: ~15 seconds (full initialization)
# Use case: First conversation or expired session (>24h)
```

### Performance Comparison

**v1.0.16 (Flask - Every webhook uses Tier 2):**
```
User Q1: 15s (cold)
User Q2: 15s (warm - always resumes)
User Q3: 15s (warm - always resumes)
[Container restart]
User Q4: 15s (warm - resumes)
```

**v2.0.0 (FastAPI - Smart tiering):**
```
User Q1: 15s (cold - fresh start)
User Q2: 9s (hot - reuse client) ← 40% faster!
User Q3: 9s (hot - reuse client)
[Container restart]
User Q4: 12s (warm - resume from disk)
User Q5: 9s (hot - reuse client)
```

### Session Persistence to Disk

**File structure:**
```
./session_cache/
├── session_1_financial_analyst.json
├── session_1_technical_assistant.json
└── session_2_financial_analyst.json
```

**File format:**
```json
{
  "session_id": "abc-123",
  "room_id": 1,
  "bot_id": "financial_analyst",
  "last_used": "2025-10-14T08:24:49.123456",
  "created_at": "2025-10-14T08:21:55.789012"
}
```

**Persistence operations:**
```python
# Save on every session_id capture
def update_session_id(room_id, bot_id, session_id):
    file_path = f"./session_cache/session_{room_id}_{bot_id}.json"
    save_to_disk(file_path, {
        'session_id': session_id,
        'last_used': now(),
        ...
    })

# Load on client creation
def get_or_create_client(room_id, bot_id, ...):
    # Check memory first
    if key in self._sessions:
        return self._sessions[key].client

    # Check disk second
    session_id = load_from_disk(room_id, bot_id)
    if session_id:
        # Create with resume (Tier 2: Warm path)
        agent = CampfireAgent(resume_session=session_id, ...)
    else:
        # Create fresh (Tier 3: Cold path)
        agent = CampfireAgent(...)
```

---

## Session Lifecycle

### Session Creation
```
Webhook arrives → SessionManager.get_or_create_client()
    ↓
Check cache: (room_id=1, bot_id='financial_analyst')
    ↓
NOT FOUND
    ↓
Create CampfireAgent(bot_config, tools)
    ↓
agent.client.connect()
    ↓
Store in cache: {(1, 'financial_analyst'): SessionState(...)}
    ↓
Return client
```

### Session Reuse
```
Second webhook (same room/bot) → SessionManager.get_or_create_client()
    ↓
Check cache: (room_id=1, bot_id='financial_analyst')
    ↓
FOUND! (last_used: 2 minutes ago)
    ↓
Update last_used timestamp
    ↓
Return EXISTING client (already connected, remembers conversation)
```

### Session Expiration
```
Background cleanup task (runs every hour)
    ↓
For each session in cache:
    if (now - last_used) > 24 hours:
        await session.client.close()
        remove from cache
        print(f"[Cleanup] Expired session for room {room_id}")
```

### Graceful Shutdown
```
FastAPI shutdown event
    ↓
SessionManager.shutdown_all()
    ↓
For each session:
    await session.client.close()
    print(f"[Shutdown] Closed session for room {room_id}, bot {bot_id}")
```

---

## Concurrency Control

### Request Queue Integration

**Keep existing request_queue.py for same-room concurrency:**

```python
async def process_message_async(...):
    request_queue = get_request_queue()

    # Check if busy (non-blocking)
    if request_queue.is_busy(room_id, bot_id):
        await post_to_campfire_async(
            room_id,
            "⏳ I'm currently helping someone else..."
        )

    # Acquire lock (blocks until available)
    acquired = request_queue.acquire(room_id, bot_id, blocking=True, timeout=300)

    if not acquired:
        await post_to_campfire_async(room_id, "⚠️ Sorry, overloaded...")
        return

    try:
        # Get persistent client (may be shared, but protected by lock)
        client = await session_manager.get_or_create_client(...)

        # Process message
        response = await agent.process_message(...)

        # Post response
        await post_to_campfire_async(room_id, response)
    finally:
        request_queue.release(room_id, bot_id)
```

**Why this works:**
- Request queue ensures ONE request per (room, bot) at a time
- Persistent client can be safely reused because access is serialized
- No race conditions even with shared client instances

---

## Error Handling

### Client Connection Errors
```python
try:
    client = await session_manager.get_or_create_client(...)
except Exception as e:
    print(f"[Error] Failed to create client: {e}")
    # Remove stale session
    session_manager.remove_session(room_id, bot_id)
    # Post error to Campfire
    await post_to_campfire_async(
        room_id,
        "Sorry, I encountered a connection error. Please try again."
    )
    return
```

### Query Failures
```python
try:
    await client.query(prompt)
    response = await client.receive_response()
except Exception as e:
    print(f"[Error] Query failed: {e}")
    # Session may be corrupted, remove it
    session_manager.remove_session(room_id, bot_id)
    # Next webhook will create fresh session
    await post_to_campfire_async(
        room_id,
        f"Sorry, I encountered an error: {str(e)}"
    )
```

---

## Migration Steps

### Phase 1: Preparation
1. ✅ Research FastAPI patterns (DONE)
2. ✅ Design SessionManager (DONE)
3. Create `src/session_manager.py`
4. Write unit tests for SessionManager

### Phase 2: FastAPI Implementation
1. Create `src/app_fastapi.py` (or rename current `app.py` → `app_flask.py`)
2. Implement lifespan event with SessionManager
3. Implement webhook endpoint with BackgroundTasks
4. Implement `post_to_campfire_async()` using httpx
5. Keep all other endpoints (health, queue/stats, session/stats)

### Phase 3: CampfireAgent Refactor
1. Remove `resume_session` parameter from `__init__`
2. Remove session_id extraction in `process_message`
3. Change return type from `tuple[str, Optional[str]]` to `str`
4. Remove all session caching logic references

### Phase 4: Dependencies Update
1. Update `pyproject.toml`:
   - Add `fastapi`
   - Add `uvicorn[standard]`
   - Add `httpx` (async HTTP client)
   - Remove `flask`
   - Remove `requests` (sync HTTP)
2. Update `Dockerfile`:
   - Change CMD to use uvicorn
   - Update version to 2.0.0

### Phase 5: Testing
1. Local testing with test.db
2. Verify session persistence across multiple webhooks
3. Test concurrent requests (request queue)
4. Test session cleanup/expiration
5. Load testing (multiple rooms, multiple bots)

### Phase 6: Deployment
1. Build Docker image: `campfire-ai-bot:2.0.0`
2. Deploy to staging (if available)
3. Monitor logs for session lifecycle
4. Deploy to production

---

## Dependency Changes

### pyproject.toml

**Remove:**
```toml
flask = "^3.0.0"
requests = "^2.31.0"
gunicorn = "^21.2.0"
```

**Add:**
```toml
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
httpx = "^0.28.0"  # Async HTTP client
```

**Keep:**
```toml
python = "^3.11"
anthropic = "^0.40.0"
claude-agent-sdk = "^1.0.0"
python-dotenv = "^1.0.0"
openpyxl = "^3.1.2"
# ... etc
```

---

## Dockerfile Changes

**Current CMD (v1.0.16):**
```dockerfile
CMD ["python", "src/app.py"]
```

**New CMD (v2.0.0):**
```dockerfile
CMD ["uvicorn", "src.app_fastapi:app", "--host", "0.0.0.0", "--port", "5000"]
```

**Alternative with workers (for production):**
```dockerfile
CMD ["uvicorn", "src.app_fastapi:app", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--workers", "1", \  # Single worker to share SessionManager state
     "--timeout-keep-alive", "75"]
```

**Note:** Use single worker to ensure SessionManager state is shared. For multi-worker, would need Redis or similar for distributed session cache (future enhancement).

---

## Testing Strategy

### Unit Tests

**test_session_manager.py:**
```python
@pytest.mark.asyncio
async def test_session_creation():
    """Test creating new session"""

@pytest.mark.asyncio
async def test_session_reuse():
    """Test reusing existing session"""

@pytest.mark.asyncio
async def test_session_cleanup():
    """Test automatic cleanup of expired sessions"""

@pytest.mark.asyncio
async def test_concurrent_access():
    """Test thread-safe access to sessions"""
```

### Integration Tests

**test_app_fastapi.py:**
```python
@pytest.mark.asyncio
async def test_webhook_creates_session():
    """First webhook creates new session"""

@pytest.mark.asyncio
async def test_webhook_reuses_session():
    """Second webhook reuses existing session"""

@pytest.mark.asyncio
async def test_conversation_continuity():
    """Test that client remembers conversation"""
```

### Local Testing Commands

```bash
# Start FastAPI dev server
cd /Users/heng/Development/campfire/ai-bot
uv run uvicorn src.app_fastapi:app --reload --port 5002

# Test webhook (first message)
curl -X POST http://localhost:5002/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":1,"name":"Test User"},"room":{"id":1,"name":"Test Room"},"content":"你好，介绍一下你的功能"}'

# Test webhook (follow-up message)
curl -X POST http://localhost:5002/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":1,"name":"Test User"},"room":{"id":1,"name":"Test Room"},"content":"我在第一次对话中问了什么?"}'

# Check session stats
curl http://localhost:5002/session/stats

# Expected: 1 active session for (room=1, bot='financial_analyst')
```

---

## Expected Behavior Changes

### v1.0.16 (Current - Stateless Resume Pattern)

**First Message:**
```
[Agent Init] 🆕 Starting new session
[Agent Session] 💾 Captured session_id: abc-123
[Session Cache] 💾 Stored session for room 1, bot 'financial_analyst': abc-123
```

**Second Message:**
```
[Session Cache] ♻️  Found session for room 1, bot 'financial_analyst': abc-123
[Agent Init] 🔄 Resuming session: abc-123
[Agent Session] 💾 Captured session_id: abc-123  (same ID)
```

### v2.0.0 (Target - Stateful Client Pattern)

**First Message:**
```
[SessionManager] Creating new client for room 1, bot 'financial_analyst'
[Agent] Connecting client...
[Agent] Client connected
[SessionManager] Stored client in cache (room=1, bot='financial_analyst')
```

**Second Message:**
```
[SessionManager] Reusing existing client for room 1, bot 'financial_analyst'
[SessionManager] Client last used: 2 minutes ago
[Agent] Querying existing client... (no connect needed)
```

**Key Difference:** No session_id logging, no resume parameter, client just exists and remembers.

---

## Rollback Plan

If v2.0.0 fails in production:

```bash
# On server
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:1.0.16  # Last stable version
docker-compose up -d
```

Keep v1.0.16 code tagged and Docker image available for emergency rollback.

---

## Success Criteria

v2.0.0 is successful when:

1. ✅ FastAPI server starts and responds to webhooks
2. ✅ SessionManager creates persistent clients
3. ✅ Follow-up messages reuse existing clients (no new connection)
4. ✅ Bot remembers conversation context without `resume` parameter
5. ✅ Session cleanup works (expired sessions removed)
6. ✅ Graceful shutdown closes all sessions cleanly
7. ✅ Request queue still prevents concurrent requests per room
8. ✅ Performance: Response time < 30 seconds (same as v1.0.16)
9. ✅ Stability: No memory leaks, sessions properly cleaned up

---

## Future Enhancements (Post-v2.0.0)

### Multi-Worker Support
- Use Redis for distributed session cache
- Share SessionManager state across workers
- Horizontal scaling capability

### Session Persistence
- Save session state to disk on shutdown
- Reload sessions on startup
- Survive container restarts

### Advanced Session Management
- Per-room session TTL configuration
- Manual session reset endpoint
- Session analytics (query count, uptime, etc.)

### WebSocket Support
- Real-time streaming responses
- Bi-directional communication
- Live typing indicators

---

## References

**Research:**
- FastAPI lifespan events: https://fastapi.tiangolo.com/advanced/events/
- FastAPI background tasks: https://fastapi.tiangolo.com/tutorial/background-tasks/
- Singleton pattern with FastAPI: https://medium.com/@hieutrantrung.it/using-fastapi-like-a-pro-with-singleton-and-dependency-injection-patterns-28de0a833a52

**Claude Agent SDK:**
- Session management: https://docs.claude.com/en/api/agent-sdk/sessions
- GitHub examples: https://github.com/anthropics/claude-code/examples

**User Research:**
- Claude.ai conversation on stateful webhook bot patterns
- Recommendation: Use ClaudeSDKClient as persistent resource, not ephemeral per-request

---

**Document Version:** 1.0
**Last Updated:** 2025-10-14
**Status:** Design Complete, Ready for Implementation
**Next Steps:** Create `src/session_manager.py` and `src/app_fastapi.py`
