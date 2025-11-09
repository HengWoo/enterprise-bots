"""
Campfire AI Bot - FastAPI webhook server (v0.5.0)
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

v0.4.0 Changes:
- Document Processing Architecture: PDF (native Read), Images (Claude API vision), DOCX (Skills MCP + pandoc), PPTX (Skills MCP + markitdown)
- PPTX Support: Text extraction, visual analysis, editing via Skills MCP
- Dependencies: markitdown[pptx], libreoffice, poppler-utils
- Re-enabled Bash tool for personal_assistant (Docker sandboxed, safe for document processing)
- Updated personal_assistant system prompt with DOCX/PPTX workflows
- Set pptx_support: true in capabilities
- Comprehensive error handling: file validation, format detection, API calls

v0.4.0 Changes (Multi-Bot Collaboration):
- Distributed peer-to-peer subagent architecture - all 8 bots can spawn other bots as subagents
- Each bot intelligently delegates to specialists when needed (no centralized orchestrator)
- English technical guidance for subagent coordination (appended to Chinese prompts)
- 3 new helper methods: _map_bot_tools_to_subagent_format(), _get_subagents_for_bot(), _get_subagent_guidance()
- Updated CampfireAgent.__init__ to accept bot_manager parameter
- Modified _create_client() to add "agents" parameter to ClaudeAgentOptions

v0.4.0.1 Changes (HTML Formatting Fix):
- Restored comprehensive HTML formatting instructions to personal_assistant.json
- Added blog-style layout guidelines (div containers, heading hierarchy, Chinese text spacing)
- Fixes plain text response issue - bot now generates styled HTML with proper visual hierarchy
- No code changes - configuration-only update
- Parallel subagent execution for faster multi-domain analyses
- Context isolation: Each subagent runs independently without cluttering main conversation
- Safety: Recursion prevention, clear delegation rules, cost-aware guidance

v0.4.1 Changes (File Download System):
- Temporary file serving system with UUID token-based download links
- File registry with automatic expiry (default 1 hour)
- Background cleanup task (runs every 5 minutes)
- Three new endpoints: POST /files/register, GET /files/download/{token}, GET /files/stats
- Foundation for v0.4.2 presentation generation features
"""

import os
import re
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import httpx
from fastapi import FastAPI, Request, BackgroundTasks, Response, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from dotenv import load_dotenv

from src.tools.campfire_tools import CampfireTools
from src.bot_manager import BotManager
from src.session_manager import SessionManager
from src.request_queue import get_request_queue
from src.file_registry import file_registry
from src.exceptions import SessionRecoveryError
from src.reminder_scheduler import create_scheduler
from apscheduler.schedulers.background import BackgroundScheduler


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


def detect_html(message: str) -> bool:
    """
    Check if message contains HTML tags.

    Used to determine Content-Type for Campfire API posts:
    - HTML content → text/html (renders links, formatting)
    - Plain text → text/plain (progress messages)

    Args:
        message: Message content to check

    Returns:
        True if HTML detected, False otherwise
    """
    import re
    # Check for common HTML tags
    # Pattern matches opening tags: <div>, <p>, <h1-6>, <ul>, <ol>, <li>, <a>, <strong>, <em>, <br>, <table>, <tr>, <td>
    html_pattern = r'<(?:div|p|h[1-6]|ul|ol|li|a|strong|em|br|table|tr|td)[\s>]'
    return bool(re.search(html_pattern, message, re.IGNORECASE))


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

    # Detect if message is HTML and set appropriate Content-Type
    is_html = detect_html(message)
    content_type = 'text/html; charset=utf-8' if is_html else 'text/plain; charset=utf-8'
    print(f"[POST] Content-Type: {content_type} (HTML detected: {is_html})")

    try:
        # Use async httpx client
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                content=message.encode('utf-8'),
                headers={'Content-Type': content_type}
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


async def cleanup_expired_files_task():
    """
    Background task to clean up expired files from registry.

    Runs every 5 minutes and removes:
    - Expired file entries from registry
    - Corresponding files from disk
    """
    while True:
        try:
            # Wait 5 minutes
            await asyncio.sleep(60 * 5)

            # Clean up expired files
            count = file_registry.cleanup_expired()
            if count > 0:
                print(f"[FileRegistry] Cleaned up {count} expired files")

        except asyncio.CancelledError:
            print("[FileRegistry] Cleanup task cancelled")
            break
        except Exception as e:
            print(f"[FileRegistry] Error in cleanup task: {e}")
            # Continue running even if one iteration fails


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
    print("🚀 Campfire AI Bot v0.5.3 - Code Execution with MCP (85-95% Token Savings)")
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
    # v0.4.1: Support multiple bot directories (JSON + YAML)
    bots_dirs = os.getenv('BOTS_DIRS', './bots,prompts/configs').split(',')
    app.state.bot_manager = BotManager(bots_dirs=bots_dirs)
    print(f"[Startup] ✅ BotManager loaded {len(app.state.bot_manager.bots)} bot(s) from {', '.join(bots_dirs)}:")
    for bot_id, bot_info in app.state.bot_manager.list_bots().items():
        print(f"           - {bot_info['display_name']} (model: {bot_info['model']})")

    # Initialize session manager (persistent client lifecycle)
    app.state.session_manager = SessionManager(
        ttl_hours=config['SESSION_TTL_HOURS']
    )
    print(f"[Startup] ✅ SessionManager initialized (TTL: {config['SESSION_TTL_HOURS']}h)")

    # Clear all session cache files on startup to prevent stale sessions after container restart
    # This prevents "No conversation found with session ID" errors from cached IDs that no longer exist
    import glob
    session_files = glob.glob("./session_cache/session_*.json")
    if session_files:
        for file in session_files:
            try:
                os.remove(file)
            except Exception as e:
                print(f"[Startup] ⚠️  Could not remove session file {file}: {e}")
        print(f"[Startup] 🗑️  Cleared {len(session_files)} stale session file(s) from disk")
    else:
        print(f"[Startup] ✓ No stale session files to clean")

    # Initialize request queue (concurrency control)
    app.state.request_queue = get_request_queue()
    print(f"[Startup] ✅ RequestQueue initialized")

    # Start background cleanup task for file registry (v0.4.1)
    cleanup_task = asyncio.create_task(cleanup_expired_files_task())
    print(f"[Startup] ✅ File registry cleanup task started (runs every 5 minutes)")

    # Initialize reminder scheduler (v0.5.1)
    # Get bot_key for personal_assistant (the bot that sends reminders)
    personal_assistant_bot = app.state.bot_manager.get_bot_by_id('personal_assistant')
    reminder_bot_key = personal_assistant_bot.bot_key if personal_assistant_bot else config['BOT_KEY']

    reminder_scheduler = create_scheduler(
        context_dir=config['CONTEXT_DIR'],
        campfire_url=config['CAMPFIRE_URL'],
        bot_key=reminder_bot_key,
        testing=os.getenv('TESTING', '').lower() == 'true'
    )

    # Start APScheduler (runs check_and_send_reminders every 1 minute)
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        reminder_scheduler.check_and_send_reminders,
        'interval',
        minutes=1,
        id='reminder_check',
        name='Check and send due reminders'
    )
    scheduler.start()
    app.state.scheduler = scheduler
    app.state.reminder_scheduler = reminder_scheduler
    print(f"[Startup] ✅ Reminder scheduler started (checks every 1 minute)")

    # Start background session cleanup task (v0.5.2 - Critical memory leak fix)
    async def cleanup_sessions_task():
        """
        Background task to clean up inactive sessions.

        Runs every hour and removes:
        - Expired sessions from memory
        - Corresponding session cache files from disk

        This prevents memory leaks and disk space issues from orphaned sessions.
        """
        while True:
            try:
                # Wait 1 hour
                await asyncio.sleep(60 * 60)

                # Clean up inactive sessions (TTL default: 24 hours)
                await app.state.session_manager.cleanup_inactive_sessions()
                print(f"[SessionManager] Cleaned up inactive sessions")

            except asyncio.CancelledError:
                print("[SessionManager] Cleanup task cancelled")
                break
            except Exception as e:
                print(f"[SessionManager] Error in cleanup task: {e}")
                # Continue running even if one iteration fails

    session_cleanup_task = asyncio.create_task(cleanup_sessions_task())
    print(f"[Startup] ✅ Session cleanup task started (runs every 1 hour)")

    print(f"\n[Startup] 🎯 FastAPI server ready")
    print(f"[Startup]    Database: {config['CAMPFIRE_DB_PATH']}")
    print(f"[Startup]    Campfire URL: {config['CAMPFIRE_URL']}")
    print(f"[Startup]    Session persistence: ./session_cache/")
    print(f"[Startup]    File registry: In-memory with automatic expiry")
    print("=" * 60)

    yield  # Application runs here

    # Cancel cleanup tasks on shutdown
    cleanup_task.cancel()
    session_cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    try:
        await session_cleanup_task
    except asyncio.CancelledError:
        pass

    # Shutdown: Cleanup
    print("\n" + "=" * 60)
    print("🛑 Shutting down Campfire AI Bot...")
    print("=" * 60)

    # Stop reminder scheduler
    if hasattr(app.state, 'scheduler'):
        app.state.scheduler.shutdown(wait=False)
        print("[Shutdown] ✅ Reminder scheduler stopped")

    await app.state.session_manager.shutdown_all()

    print("[Shutdown] ✅ Shutdown complete")
    print("=" * 60)


# Create FastAPI application with lifespan management
app = FastAPI(
    title="Campfire AI Bot",
    description="AI-powered bot for Campfire chat using Claude Agent SDK with automated reminder delivery",
    version="0.5.1",
    lifespan=lifespan
)


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'version': '0.5.0',
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


# File Download System Endpoints (v0.4.1)

@app.post("/files/register")
async def register_file(request: Request):
    """
    Register a file for download with UUID token.

    Request body:
        {
            "file_path": "/tmp/presentation.html",
            "filename": "Q3_Report.html",
            "expiry_hours": 1,
            "mime_type": "text/html"
        }

    Returns:
        {
            "success": true,
            "token": "abc123-uuid-456def",
            "download_url": "/files/download/abc123-uuid-456def",
            "expires_in_hours": 1
        }
    """
    try:
        body = await request.json()
        file_path = body.get("file_path")
        filename = body.get("filename")
        expiry_hours = body.get("expiry_hours", 1)
        mime_type = body.get("mime_type", "text/html")

        if not file_path or not filename:
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: file_path and filename"
            )

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on disk")

        # Register file and get token
        token = file_registry.register_file(
            file_path=file_path,
            filename=filename,
            expiry_hours=expiry_hours,
            mime_type=mime_type
        )

        return {
            "success": True,
            "token": token,
            "download_url": f"/files/download/{token}",
            "expires_in_hours": expiry_hours
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering file: {str(e)}")


@app.get("/files/download/{token}")
async def download_file(token: str):
    """
    Download file by UUID token.

    Returns file if token is valid and not expired.
    Returns 404 if token not found or expired.
    """
    file_info = file_registry.get_file_info(token)

    if not file_info:
        raise HTTPException(
            status_code=404,
            detail="File not found or link expired"
        )

    if not os.path.exists(file_info["file_path"]):
        raise HTTPException(
            status_code=404,
            detail="File no longer exists on disk"
        )

    return FileResponse(
        path=file_info["file_path"],
        filename=file_info["filename"],
        media_type=file_info["mime_type"]
    )


@app.get("/files/stats")
async def get_file_stats():
    """
    Admin endpoint to view registered files.

    Returns:
        {
            "total_files": 5,
            "files": [
                {
                    "token": "abc123...",
                    "filename": "report.html",
                    "created_at": "2025-10-27T14:30:00",
                    "expires_at": "2025-10-27T15:30:00"
                },
                ...
            ]
        }
    """
    return file_registry.get_stats()


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
        campfire_tools=request.app.state.tools,
        bot_manager=request.app.state.bot_manager  # v0.4.0: For subagent access
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
    campfire_tools: CampfireTools,
    bot_manager  # v0.4.0: For subagent coordination
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
                campfire_tools=campfire_tools,
                bot_manager=bot_manager  # v0.4.0: For subagent coordination
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
            try:
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
            except SessionRecoveryError as e:
                # Stale session detected - clean up and retry with fresh session
                print(f"[Session Recovery] 🔄 Handling stale session error: {str(e)[:100]}")

                # Extract session ID from agent's resume_session
                if hasattr(agent, 'resume_session') and agent.resume_session:
                    await session_manager.handle_invalid_session(
                        room_id, bot_config.bot_id, agent.resume_session
                    )

                # Get fresh client (will be Tier 3 Cold Path now)
                print(f"[Session Recovery] 🔄 Creating fresh session and retrying...")
                client, agent = await session_manager.get_or_create_client(
                    room_id, bot_config.bot_id, bot_config,
                    request.app.state.tools, request.app.state.bot_manager
                )

                # Retry with fresh session
                response_text, new_session_id = await agent.process_message(
                    content=content,
                    context={
                        'user_id': user_id,
                        'user_name': user_name,
                        'room_id': room_id,
                        'room_name': room_name,
                        'message_id': message_id
                    },
                    on_milestone=post_milestone
                )
                print(f"[Session Recovery] ✅ Retry succeeded with fresh session")

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

    print(f"Starting Campfire AI Bot v0.4.1 on {host}:{port}")
    print(f"Database: {config['CAMPFIRE_DB_PATH']}")
    print(f"Campfire URL: {config['CAMPFIRE_URL']}")

    uvicorn.run(app, host=host, port=port)
