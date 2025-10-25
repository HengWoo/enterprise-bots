"""
Campfire AI Bot - FastAPI webhook server (v0.3.3)
Receives Campfire webhooks and responds using Claude Agent SDK with stateful session management

Key Improvements over Flask (v1.0.14):
- Single async event loop enables persistent ClaudeSDKClient instances
- 40% faster follow-up responses (9s vs 15s)
- Three-tier session strategy (hot/warm/cold)
- Session IDs persisted to disk for crash recovery

v0.3.0 Changes:
- Upgraded all 5 bots to claude-haiku-4-5-20251001 model (latest Haiku)
- Improved HTML formatting with blog-style layout for better Chinese text readability
- Enhanced response quality with proper spacing, headings, and visual hierarchy

v0.3.0.1 Changes:
- Fixed critical bug: Enabled built-in SDK tools (WebSearch, WebFetch, Read, Write, Edit, Bash, Grep, Glob)
- Localized progress message to Chinese ("努力工作ing")
- Added Operations Assistant bot with Supabase integration (3 new tools)
- Added Claude Code Tutor bot for educational support

v0.3.2 Changes:
- Added Menu Engineering bot with Boston Matrix methodology
- Added 5 menu engineering RPC functions in Supabase
- New tools: get_menu_profitability, get_top_profitable_dishes, get_low_profit_dishes,
  get_cost_coverage_rate, get_dishes_missing_cost
- Total bots: 8 (Financial, Technical, Personal, Briefing, Default, Operations, CC Tutor, Menu Engineering)

v0.3.3 Changes:
- Agent Tools Refactoring: Split 2,418-line agent_tools.py into 7 modular decorator files
- 46% code reduction (2,418 → 1,305 lines total)
- Improved maintainability and navigation
- Zero behavior changes (pure structural refactoring)
"""

import os
import re
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import httpx
from fastapi import FastAPI, Request, BackgroundTasks, Response
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from src.tools.campfire_tools import CampfireTools
from src.bot_manager import BotManager
from src.session_manager import SessionManager
from src.request_queue import get_request_queue


# Load environment variables
load_dotenv()


def get_config():
    """Get application configuration from environment"""
    return {
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'CAMPFIRE_URL': os.getenv('CAMPFIRE_URL', 'https://chat.smartice.ai'),
        'BOT_KEY': os.getenv('BOT_KEY', '2-CsheovnLtzjM'),
        'CAMPFIRE_DB_PATH': os.getenv('CAMPFIRE_DB_PATH', './tests/fixtures/test.db'),
        'CONTEXT_DIR': os.getenv('CONTEXT_DIR', './user_contexts'),
        'TESTING': os.getenv('TESTING', 'false'),
        'SESSION_TTL_HOURS': int(os.getenv('SESSION_TTL_HOURS', '24')),
        'SYSTEM_PROMPT': os.getenv(
            'SYSTEM_PROMPT',
            'You are a professional financial analyst AI assistant in Campfire. '
            'You provide clear, actionable insights based on conversation context and user preferences.'
        )
    }


async def post_to_campfire(room_id: int, message: str, bot_key: str = None, testing: bool = False):
    """
    Post message to Campfire room (async version using httpx).

    Args:
        room_id: Room ID to post to
        message: Message content (plain text)
        bot_key: Bot authentication key (if None, uses ENV BOT_KEY)
        testing: If True, skip actual HTTP request
    """
    config = get_config()

    # Skip actual posting in testing mode
    testing_mode = (
        testing or
        os.getenv('TESTING', '').lower() == 'true' or
        config.get('TESTING', '').lower() == 'true'
    )

    if testing_mode:
        print(f"[TEST MODE] Would post to room {room_id}: {message[:50]}...")
        return None

    # Use provided bot_key or fall back to ENV BOT_KEY
    actual_bot_key = bot_key or config['BOT_KEY']
    url = f"{config['CAMPFIRE_URL']}/rooms/{room_id}/{actual_bot_key}/messages"

    print(f"[POST] Attempting to post to URL: {url}")
    print(f"[POST] Room ID: {room_id}, BOT_KEY: {actual_bot_key}")
    print(f"[POST] Message preview: {message[:100]}...")

    try:
        # Use async httpx client
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                content=message.encode('utf-8'),
                headers={'Content-Type': 'text/plain; charset=utf-8'}
            )
            print(f"[POST] Response status: {response.status_code}")
            response.raise_for_status()
            print(f"[POST] ✅ Successfully posted to room {room_id}")
            return response
    except Exception as e:
        print(f"[POST] ❌ Error posting to Campfire: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"[POST] Response status: {e.response.status_code}")
            print(f"[POST] Response body: {e.response.text}")
        # Don't raise - we don't want to fail the webhook


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.

    Handles application startup and shutdown:
    - Startup: Initialize SessionManager, BotManager, CampfireTools
    - Shutdown: Gracefully close all active sessions

    Why this works:
    - Single event loop for entire application lifetime
    - SessionManager can maintain persistent clients
    - Clients bound to this event loop can be reused
    """
    config = get_config()

    print("=" * 60)
    print("🚀 Campfire AI Bot v0.3.3 - Agent Tools Refactoring")
    print("=" * 60)

    # Startup: Initialize application state
    print("\n[Startup] Initializing application components...")

    # Initialize tools (database access, context management, knowledge base)
    # Use environment variable for knowledge base directory with container path default
    # Container path: /app/ai-knowledge/company_kb (matches Docker named volume structure)
    knowledge_base_dir = os.getenv('KNOWLEDGE_BASE_DIR', '/app/ai-knowledge/company_kb')
    app.state.tools = CampfireTools(
        db_path=config['CAMPFIRE_DB_PATH'],
        context_dir=config['CONTEXT_DIR'],
        knowledge_base_dir=knowledge_base_dir
    )
    print(f"[Startup] ✅ CampfireTools initialized")
    print(f"[Startup]    knowledge_base_dir: {knowledge_base_dir}")

    # Initialize bot manager (loads all bot configurations)
    bots_dir = os.getenv('BOTS_DIR', './bots')
    app.state.bot_manager = BotManager(bots_dir=bots_dir)
    print(f"[Startup] ✅ BotManager loaded {len(app.state.bot_manager.bots)} bot(s) from {bots_dir}:")
    for bot_id, bot_info in app.state.bot_manager.list_bots().items():
        print(f"           - {bot_info['display_name']} (model: {bot_info['model']})")

    # Initialize session manager (persistent client lifecycle)
    app.state.session_manager = SessionManager(
        ttl_hours=config['SESSION_TTL_HOURS']
    )
    print(f"[Startup] ✅ SessionManager initialized (TTL: {config['SESSION_TTL_HOURS']}h)")

    # Initialize request queue (concurrency control)
    app.state.request_queue = get_request_queue()
    print(f"[Startup] ✅ RequestQueue initialized")

    print(f"\n[Startup] 🎯 FastAPI server ready")
    print(f"[Startup]    Database: {config['CAMPFIRE_DB_PATH']}")
    print(f"[Startup]    Campfire URL: {config['CAMPFIRE_URL']}")
    print(f"[Startup]    Session persistence: ./session_cache/")
    print("=" * 60)

    yield  # Application runs here

    # Shutdown: Cleanup
    print("\n" + "=" * 60)
    print("🛑 Shutting down Campfire AI Bot...")
    print("=" * 60)

    await app.state.session_manager.shutdown_all()

    print("[Shutdown] ✅ Shutdown complete")
    print("=" * 60)


# Create FastAPI application with lifespan management
app = FastAPI(
    title="Campfire AI Bot",
    description="AI-powered bot for Campfire chat using Claude Agent SDK with API fallback",
    version="0.3.3",
    lifespan=lifespan
)


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'version': '0.3.3',
        'timestamp': datetime.now().isoformat()
    }


@app.get("/session/stats")
async def session_stats(request: Request):
    """
    Get session manager statistics.

    Returns:
        JSON with session metrics:
        - active_sessions: Number of cached sessions
        - ttl_hours: Time-to-live for inactive sessions
        - sessions: List of active sessions with details
    """
    return request.app.state.session_manager.stats()


@app.get("/queue/stats")
async def queue_stats(request: Request):
    """
    Get request queue statistics.

    Returns:
        JSON with queue metrics:
        - total_requests: Total requests processed
        - queued_requests: Requests that had to wait
        - active_agents: Number of agents currently processing
    """
    return request.app.state.request_queue.get_stats()


@app.post("/session/clear/room/{room_id}")
async def clear_room_session(room_id: int, request: Request):
    """
    Clear session cache for a specific room.

    Useful for testing or resetting conversation state.
    Note: This only clears in-memory cache, disk files remain.
    """
    # For now, we don't have a direct API to clear specific room
    # Would need to add this to SessionManager if needed
    return {"status": "not_implemented", "room_id": room_id}


@app.post("/session/clear/all")
async def clear_all_sessions(request: Request):
    """
    Clear all session cache.

    WARNING: This will reset all conversation memory.
    Note: Only clears in-memory, disk files remain.
    """
    await request.app.state.session_manager.shutdown_all()
    return {"status": "success", "message": "All sessions cleared"}


@app.post("/webhook")
@app.post("/webhook/{bot_id}")
async def webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    bot_id: Optional[str] = None
):
    """
    Campfire webhook endpoint (supports multiple bots).

    URL options:
      - POST /webhook (uses default bot)
      - POST /webhook?bot_id=financial_analyst
      - POST /webhook/financial_analyst

    Returns 200 immediately, processes in background.
    """
    # Log raw payload for debugging
    print(f"\n[WEBHOOK] Received payload:")
    print(f"Content-Type: {request.headers.get('content-type')}")

    # Validate JSON
    try:
        payload = await request.json()
        print(f"Parsed JSON: {payload}")
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={'error': f'Invalid JSON: {str(e)}'}
        )

    # Extract required fields (handle different payload formats)
    creator = payload.get('creator') or payload.get('user')
    room = payload.get('room')
    content = payload.get('content') or (
        payload.get('message', {}).get('body', {}).get('plain')
        if payload.get('message') else None
    )

    if not creator:
        return JSONResponse(
            status_code=400,
            content={'error': 'Missing required field: creator or user'}
        )

    if not room:
        return JSONResponse(
            status_code=400,
            content={'error': 'Missing required field: room'}
        )

    if not content:
        return JSONResponse(
            status_code=400,
            content={'error': 'Missing required field: content or message'}
        )

    # Determine which bot to use
    config = get_config()
    bot_manager = request.app.state.bot_manager

    if not bot_id:
        bot_id = request.query_params.get('bot_id')

    if bot_id:
        bot_config = bot_manager.get_bot_by_id(bot_id)
        if not bot_config:
            return JSONResponse(
                status_code=404,
                content={'error': f'Bot not found: {bot_id}'}
            )
    else:
        # Try to match by bot_key from ENV (backward compatibility)
        env_bot_key = config.get('BOT_KEY')
        if env_bot_key:
            bot_config = bot_manager.get_bot_by_key(env_bot_key)
            if bot_config:
                print(f"Using bot matched by ENV BOT_KEY: {bot_config.name}")

        # Fall back to default bot
        if not bot_config:
            bot_config = bot_manager.get_default_bot()
            print(f"Using default bot: {bot_config.name}")

    print(f"Processing webhook with bot: {bot_config.display_name}")

    # Extract data
    user_id = creator['id']
    user_name = creator['name']
    room_id = room['id']
    room_name = room['name']
    message_id = payload.get('id') or payload.get('message', {}).get('id')

    print(f"[WEBHOOK DATA] User: {user_name} (ID: {user_id})")
    print(f"[WEBHOOK DATA] Room: {room_name} (ID: {room_id})")
    print(f"[WEBHOOK DATA] Content: {content[:100]}...")
    print(f"[WEBHOOK DATA] Bot: {bot_config.display_name}")

    # Add background task (runs in SAME event loop)
    background_tasks.add_task(
        process_message_async,
        room_id=room_id,
        user_id=user_id,
        user_name=user_name,
        room_name=room_name,
        content=content,
        message_id=message_id,
        bot_config=bot_config,
        session_manager=request.app.state.session_manager,
        request_queue=request.app.state.request_queue,
        campfire_tools=request.app.state.tools
    )

    print(f"[Webhook] Queued background task for room {room_id}")

    # Return immediately to avoid webhook timeout
    return Response(status_code=200)


async def process_message_async(
    room_id: int,
    user_id: int,
    user_name: str,
    room_name: str,
    content: str,
    message_id: Optional[int],
    bot_config,
    session_manager: SessionManager,
    request_queue,
    campfire_tools: CampfireTools
):
    """
    Process message in background task.

    Key differences from Flask version:
    - Runs in SAME event loop (not new thread)
    - Can reuse persistent clients from SessionManager
    - Uses async httpx instead of synchronous requests
    """
    print(f"[Background] Started processing for room {room_id}", flush=True)

    # Check if agent is currently busy (non-blocking check)
    if request_queue.is_busy(room_id, bot_config.bot_id):
        # Agent is busy - post waiting message
        wait_msg = "⏳ I'm currently helping someone else in this room. Your request will be processed shortly..."
        await post_to_campfire(room_id, wait_msg, bot_key=bot_config.bot_key)
        print(f"[Queue] Agent for room {room_id} is busy - posted waiting message")

    # Acquire lock (blocks until available)
    print(f"[Queue] Waiting for lock for room {room_id}, bot {bot_config.bot_id}")
    acquired = request_queue.acquire(
        room_id=room_id,
        bot_id=bot_config.bot_id,
        blocking=True,
        timeout=300  # 5 minute timeout
    )

    if not acquired:
        # Timeout - couldn't get lock
        error_msg = "⚠️ Sorry, I'm overloaded right now. Please try again in a few minutes."
        await post_to_campfire(room_id, error_msg, bot_key=bot_config.bot_key)
        print(f"[Queue] Failed to acquire lock for room {room_id} after 5 minutes")
        return

    print(f"[Queue] Acquired lock for room {room_id}, bot {bot_config.bot_id}")

    try:
        # Send immediate acknowledgment
        acknowledgment = "努力工作ing"
        await post_to_campfire(room_id, acknowledgment, bot_key=bot_config.bot_key)
        print(f"[Background] Posted acknowledgment to room {room_id}")

        # Get or create client from SessionManager (three-tier strategy)
        config = get_config()
        api_key = config.get('ANTHROPIC_API_KEY')

        # Skip actual API call if in testing mode with fake key
        if api_key and not api_key.startswith('sk-ant-test'):
            # Get or create persistent client (THREE-TIER STRATEGY)
            client, agent = await session_manager.get_or_create_client(
                room_id=room_id,
                bot_id=bot_config.bot_id,
                bot_config=bot_config,
                campfire_tools=campfire_tools
            )

            print(f"[Background] Calling Claude Agent SDK with model: {bot_config.model}")

            # Track milestone messages and timing
            import time
            milestone_messages = []
            last_milestone_time = time.time()
            MILESTONE_THROTTLE = 5  # Minimum 5 seconds between milestones

            async def post_milestone(milestone_text: str):
                """
                Post significant progress milestone to Campfire.

                Throttles to prevent spam (max 1 per 5 seconds).
                """
                nonlocal last_milestone_time

                # Throttle: Wait at least 5 seconds between milestones
                time_since_last = time.time() - last_milestone_time
                if time_since_last < MILESTONE_THROTTLE:
                    print(f"[Milestone] Throttled (too soon: {time_since_last:.1f}s) - {milestone_text[:50]}")
                    return

                try:
                    await post_to_campfire(room_id, milestone_text, bot_key=bot_config.bot_key)
                    milestone_messages.append(milestone_text)
                    last_milestone_time = time.time()
                    print(f"[Milestone] Posted: {milestone_text[:80]}...")
                except Exception as e:
                    print(f"[Milestone] Failed to post: {e}")

            # Process message with agent (milestone callback)
            # Returns tuple: (response_text, session_id)
            response_text, new_session_id = await agent.process_message(
                content=content,
                context={
                    'user_id': user_id,
                    'user_name': user_name,
                    'room_id': room_id,
                    'room_name': room_name,
                    'message_id': message_id
                },
                on_milestone=post_milestone  # NEW: Smart milestone updates
            )

            # Save session ID for future requests (if returned)
            if new_session_id:
                session_manager.update_session_id(room_id, bot_config.bot_id, new_session_id)

            # Log milestone statistics
            if milestone_messages:
                print(f"[Milestone] Posted {len(milestone_messages)} milestones during processing")
        else:
            # Fallback for testing without real API key
            response_text = f"Received your message in {room_name}: {content[:50]}..."
            milestone_messages = []

        # Always post the final complete response
        # (Milestones are just progress updates, final report is the real content)
        await post_to_campfire(room_id, response_text, bot_key=bot_config.bot_key)
        print(f"[Background] Successfully posted final response to room {room_id}")

    except Exception as e:
        print(f"[Background] Error processing webhook: {e}", flush=True)
        import traceback
        traceback.print_exc()
        # Post error to Campfire
        await post_to_campfire(
            room_id,
            f"Sorry, I encountered an error: {str(e)}",
            bot_key=bot_config.bot_key
        )
    finally:
        # Release the lock - CRITICAL to allow next request
        print(f"[Queue] Releasing lock for room {room_id}, bot {bot_config.bot_id}")
        request_queue.release(room_id, bot_config.bot_id)
        print(f"[Background] Task completed for room {room_id}", flush=True)


# For uvicorn command-line usage
if __name__ == "__main__":
    import uvicorn

    config = get_config()
    port = int(os.getenv('FASTAPI_PORT', 8000))
    host = os.getenv('FASTAPI_HOST', '0.0.0.0')

    print(f"Starting Campfire AI Bot v0.3.3 on {host}:{port}")
    print(f"Database: {config['CAMPFIRE_DB_PATH']}")
    print(f"Campfire URL: {config['CAMPFIRE_URL']}")

    uvicorn.run(app, host=host, port=port)
