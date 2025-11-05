# Claude SDK Pattern Comparison - Visual Guide

## Pattern A: Stateless with Resume (YOUR CURRENT - RECOMMENDED) ✅

```
┌─────────────────────────────────────────────────────────────┐
│ Flask App (Gunicorn multi-worker)                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Webhook 1 (Thread 1)          Webhook 2 (Thread 2)        │
│  ┌──────────────────┐          ┌──────────────────┐        │
│  │ Event Loop 1     │          │ Event Loop 2     │        │
│  │ ┌──────────────┐ │          │ ┌──────────────┐ │        │
│  │ │ Client 1     │ │          │ │ Client 2     │ │        │
│  │ │ resume="abc" │ │          │ │ resume="def" │ │        │
│  │ └──────────────┘ │          │ └──────────────┘ │        │
│  │ query("...")     │          │ query("...")     │        │
│  │ response         │          │ response         │        │
│  │ loop.close()     │          │ loop.close()     │        │
│  └──────────────────┘          └──────────────────┘        │
│         ↓                              ↓                    │
│    Saves session_id             Saves session_id           │
│         ↓                              ↓                    │
└─────────┼──────────────────────────────┼───────────────────┘
          ↓                              ↓
    ┌─────────────────────────────────────────┐
    │ Session Cache (in-memory or Redis)      │
    │ {"room1:bot1": "abc", "room2:bot1": "def"} │
    └─────────────────────────────────────────┘
```

**Characteristics:**
- ✅ Each webhook = fresh client
- ✅ Each thread = own event loop
- ✅ Thread-safe (no shared state)
- ✅ Process-safe (works across Gunicorn workers with Redis)
- ✅ Horizontally scalable
- ✅ Crash-resilient (session_id survives restart)
- ⚠️ Subprocess overhead (~250-550ms per request)

---

## Pattern B: Stateful with Shared Client (ATTEMPTED v1.0.8-1.0.12) ❌

```
┌─────────────────────────────────────────────────────────────┐
│ Flask App                                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Agent Cache (PROBLEMATIC)                            │  │
│  │ {"room1:bot1": Client instance (bound to Loop 1)}   │  │
│  └──────────────────────────────────────────────────────┘  │
│         ↑                              ↑                    │
│         │                              │                    │
│  Webhook 1 (Thread 1)          Webhook 2 (Thread 2)        │
│  ┌──────────────────┐          ┌──────────────────┐        │
│  │ Event Loop 1     │          │ Event Loop 2     │        │
│  │ Gets Client from │          │ Gets Client from │        │
│  │ cache (OK)       │          │ cache (ERROR!)   │        │
│  │ query("...")     │          │ RuntimeError:    │        │
│  │ ✅ Works         │          │ Different loop   │        │
│  └──────────────────┘          └──────────────────┘        │
│                                        ❌                    │
└─────────────────────────────────────────────────────────────┘
```

**Why This Fails:**
- ❌ Client bound to Loop 1
- ❌ Thread 2 tries to use same client with Loop 2
- ❌ RuntimeError: "Task attached to a different loop"
- ❌ Race conditions on transport file descriptors
- ❌ Subprocess cleanup issues

**Error Messages:**
```
RuntimeError: Task <Task> attached to a different loop
RuntimeError: cannot schedule new futures after interpreter shutdown
RuntimeError: Transport closed
```

---

## Pattern C: Persistent Event Loop (POSSIBLE, NOT RECOMMENDED FOR YOU) ⚠️

```
┌──────────────────────────────────────────────────────────────┐
│ Flask App                                                     │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Webhook 1 (Thread 1)     Webhook 2 (Thread 2)              │
│  ┌──────────────────┐     ┌──────────────────┐             │
│  │ Submit task to   │     │ Submit task to   │             │
│  │ event loop       │────┐│ event loop       │────┐        │
│  │ Return 200       │    ││ Return 200       │    │        │
│  └──────────────────┘    │└──────────────────┘    │        │
│                          │                         │        │
│  ┌───────────────────────┼─────────────────────────┼─────┐ │
│  │ Persistent Event Loop Thread                     │     │ │
│  │ ┌─────────────────────↓─────────────────────────↓───┐ │ │
│  │ │ Task Queue                                         │ │ │
│  │ │ [task1, task2, ...]                                │ │ │
│  │ └────────────────────────────────────────────────────┘ │ │
│  │                                                         │ │
│  │ ┌─────────────────────────────────────────────────────┐│ │
│  │ │ Client Pool                                         ││ │
│  │ │ {"room1:bot1": Client1, "room2:bot1": Client2}     ││ │
│  │ │ (Clients persist across requests)                   ││ │
│  │ └─────────────────────────────────────────────────────┘│ │
│  │                                                         │ │
│  │ Process tasks sequentially from queue                  │ │
│  │ ↓                                                       │ │
│  │ client.query("...")                                    │ │
│  │ response → callback → post to Campfire                 │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

**Characteristics:**
- ✅ No subprocess overhead (client persists)
- ✅ Thread-safe (all async in single thread)
- ✅ Natural conversation flow (multiple query() on same client)
- ❌ Does NOT work with Gunicorn multi-worker
- ❌ Single thread bottleneck (all rooms share one loop)
- ❌ Complex lifecycle management
- ❌ Not crash-resilient (restart loses clients)
- ❌ Harder to scale horizontally

**Use Cases:**
- Desktop applications
- Local development tools
- Single-process servers

**NOT for:**
- Production web servers with Gunicorn ← YOUR CASE
- Horizontally scaled deployments
- Serverless environments

---

## Session ID Flow (Pattern A - Your Current)

```
┌─────────────────────────────────────────────────────────────┐
│ Turn 1: New Conversation                                     │
└─────────────────────────────────────────────────────────────┘

User: "Hello bot"
    ↓
Webhook receives request
    ↓
session_cache.get(room_id, bot_id) → None (no session yet)
    ↓
Create agent with resume=None
    ↓
client.query("Hello bot")
    ↓
Receive response:
    - SystemMessage(subtype='init', data={'session_id': 'abc123'})
    - AssistantMessage("Hello! How can I help?")
    ↓
Extract session_id = "abc123"
    ↓
session_cache.set(room_id, bot_id, "abc123")
    ↓
Post response to Campfire


┌─────────────────────────────────────────────────────────────┐
│ Turn 2+: Continue Conversation                               │
└─────────────────────────────────────────────────────────────┘

User: "Tell me more"
    ↓
Webhook receives request
    ↓
session_cache.get(room_id, bot_id) → "abc123" (found!)
    ↓
Create agent with resume="abc123"
    ↓
client.query("Tell me more")
    ↓
Server restores conversation from session "abc123"
    ↓
Receive response:
    - AssistantMessage("Here's more information...")
    ↓
Post response to Campfire

(Note: session_id doesn't change after first turn)
```

---

## Threading Model Comparison

### Pattern A: Per-Request Threads (Your Current)

```
┌────────────────────────────────────────────────┐
│ Main Thread (Flask)                            │
│ ┌────────────────────────────────────────────┐ │
│ │ Webhook Handler                            │ │
│ │ 1. Receive POST                            │ │
│ │ 2. Start background thread                 │ │
│ │ 3. Return 200 immediately                  │ │
│ └────────────────────────────────────────────┘ │
└────────────────┬───────────────────────────────┘
                 │
                 ↓ spawn
┌────────────────────────────────────────────────┐
│ Background Thread (daemon=True)                │
│ ┌────────────────────────────────────────────┐ │
│ │ loop = asyncio.new_event_loop()           │ │
│ │ asyncio.set_event_loop(loop)              │ │
│ │                                            │ │
│ │ agent = CampfireAgent(resume=session_id)  │ │
│ │ await agent.process_message()             │ │
│ │                                            │ │
│ │ loop.close()                               │ │
│ └────────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘
           Thread exits
```

**Key Points:**
- Each webhook spawns new thread
- Thread creates own event loop
- Thread exits after processing
- Clean, no state sharing

---

### Pattern C: Single Persistent Thread

```
┌────────────────────────────────────────────────┐
│ Main Thread (Flask)                            │
│ ┌────────────────────────────────────────────┐ │
│ │ Webhook Handler                            │ │
│ │ 1. Receive POST                            │ │
│ │ 2. Submit task to queue                    │ │
│ │ 3. Return 200 immediately                  │ │
│ └────────────────────────────────────────────┘ │
└────────────────┬───────────────────────────────┘
                 │
                 ↓ asyncio.run_coroutine_threadsafe
┌────────────────────────────────────────────────┐
│ Persistent Event Loop Thread (daemon=False)    │
│ ┌────────────────────────────────────────────┐ │
│ │ loop = asyncio.new_event_loop()           │ │
│ │ asyncio.set_event_loop(loop)              │ │
│ │                                            │ │
│ │ while running:                             │ │
│ │     task = await queue.get()              │ │
│ │     await process_task(task)              │ │
│ │                                            │ │
│ │ (Clients persist in memory)                │ │
│ └────────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘
    Thread runs forever (until shutdown)
```

**Key Points:**
- Single thread runs continuously
- All webhooks submit to same queue
- Clients reused across requests
- Complex lifecycle management

---

## Performance Comparison

### Pattern A (Your Current)

**Request Timeline:**
```
t=0ms    : Webhook received
t=0ms    : Spawn background thread
t=1ms    : Return 200 to Campfire
         -------- async processing --------
t=10ms   : Create event loop
t=50ms   : Create ClaudeSDKClient
t=250ms  : Subprocess startup (claude CLI)
t=300ms  : Connect to Claude API
t=500ms  : Send query
t=3000ms : Receive response (depends on Claude)
t=3050ms : Post to Campfire
t=3100ms : Clean up loop, thread exits
```

**Total:** ~3.1 seconds (mostly Claude API processing)
**Overhead:** ~250-550ms (subprocess + client creation)

---

### Pattern C (Persistent Event Loop)

**Request Timeline:**
```
t=0ms    : Webhook received
t=0ms    : Submit to queue
t=1ms    : Return 200 to Campfire
         -------- async processing --------
t=5ms    : Task dequeued
t=10ms   : Reuse existing client (no subprocess!)
t=50ms   : Send query
t=2550ms : Receive response (depends on Claude)
t=2600ms : Post to Campfire
```

**Total:** ~2.6 seconds
**Overhead:** ~50ms (queue + client lookup)

**Savings:** ~250ms per request (eliminates subprocess)

**Is this worth the complexity?**
- For typical webhook (1-2 req/min): **NO**
- For high volume (>10 req/min): **Maybe**
- For production with Gunicorn: **NO (doesn't work)**

---

## Gunicorn Multi-Worker Compatibility

### Pattern A: Works ✅

```
┌──────────────────────────────────────────────────┐
│ Gunicorn Master Process                          │
├──────────────────────────────────────────────────┤
│                                                   │
│  ┌─────────────────┐    ┌─────────────────┐     │
│  │ Worker 1        │    │ Worker 2        │     │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │     │
│  │ │ Flask App   │ │    │ │ Flask App   │ │     │
│  │ │ Fresh client│ │    │ │ Fresh client│ │     │
│  │ │ per request │ │    │ │ per request │ │     │
│  │ └─────────────┘ │    │ └─────────────┘ │     │
│  └────────┬────────┘    └────────┬────────┘     │
│           │                      │               │
└───────────┼──────────────────────┼───────────────┘
            ↓                      ↓
    ┌───────────────────────────────────────┐
    │ Shared Session Cache (Redis)          │
    │ session_id strings only               │
    └───────────────────────────────────────┘
```

**Works because:**
- No shared state between workers
- Each creates own clients
- Session IDs shared via Redis
- Process isolation maintained

---

### Pattern C: Doesn't Work ❌

```
┌──────────────────────────────────────────────────┐
│ Gunicorn Master Process                          │
├──────────────────────────────────────────────────┤
│                                                   │
│  ┌─────────────────┐    ┌─────────────────┐     │
│  │ Worker 1        │    │ Worker 2        │     │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │     │
│  │ │ Event Loop  │ │    │ │ Event Loop  │ │     │
│  │ │ Thread      │ │    │ │ Thread      │ │     │
│  │ │ Clients for │ │    │ │ Clients for │ │     │
│  │ │ Worker 1    │ │    │ │ Worker 2    │ │     │
│  │ └─────────────┘ │    │ └─────────────┘ │     │
│  └─────────────────┘    └─────────────────┘     │
│                                                   │
└──────────────────────────────────────────────────┘
```

**Doesn't work because:**
- Each worker has own event loop
- Clients not shared across workers
- Load balancer may route requests to different workers
- Conversation state fragmented

**Workaround:**
- Sticky sessions (route same room to same worker)
- But defeats purpose of multi-worker
- Single worker = single point of failure

---

## Recommendation Summary

### For Your Campfire Bot

**KEEP Pattern A (Stateless with Resume)** ✅

**Why:**
1. Production-ready (works with Gunicorn)
2. Horizontally scalable (add more servers)
3. Crash-resilient (session survives restart)
4. SDK-recommended pattern
5. Simple, maintainable code

**Don't:**
- Don't cache client instances
- Don't optimize prematurely
- Don't implement Pattern C unless proven bottleneck

**Focus on:**
1. Fix max_turns bug (v1.0.15) ← Current priority
2. Redis session cache (when scaling)
3. Error handling and monitoring
4. Performance measurement (THEN optimize)

---

**Your current architecture is correct. Ship v1.0.15 and move on!**
