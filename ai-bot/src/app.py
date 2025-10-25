"""
Campfire AI Bot - Flask webhook server
Receives Campfire webhooks and responds using Claude Agent SDK
"""

import os
import re
import threading
from datetime import datetime
from pathlib import Path

import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from tools.campfire_tools import CampfireTools
from bot_manager import BotManager
from campfire_agent import CampfireAgent
from request_queue import get_request_queue
from session_cache import get_session_cache


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
        'SYSTEM_PROMPT': os.getenv(
            'SYSTEM_PROMPT',
            'You are a professional financial analyst AI assistant in Campfire. '
            'You provide clear, actionable insights based on conversation context and user preferences.'
        )
    }


def strip_html(html: str) -> str:
    """Strip HTML tags from text"""
    if not html:
        return ""
    text = re.sub(r'<[^>]+>', '', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def post_to_campfire(room_id: int, message: str, testing=False):
    """
    Post message to Campfire room

    Args:
        room_id: Room ID to post to
        message: Message content (plain text)
        testing: If True, skip actual HTTP request
    """
    config = get_config()

    # Skip actual posting in testing mode - check multiple ways
    testing_mode = (
        testing or
        os.getenv('TESTING', '').lower() == 'true' or
        config.get('TESTING', '').lower() == 'true'
    )

    if testing_mode:
        print(f"[TEST MODE] Would post to room {room_id}: {message[:50]}...")
        return None

    url = f"{config['CAMPFIRE_URL']}/rooms/{room_id}/{config['BOT_KEY']}/messages"

    # DEBUG: Print exact URL being used
    print(f"[POST] Attempting to post to URL: {url}")
    print(f"[POST] Room ID: {room_id}, BOT_KEY: {config['BOT_KEY']}")
    print(f"[POST] Message preview: {message[:100]}...")

    try:
        # Campfire expects raw text data, not form-encoded
        response = requests.post(
            url,
            data=message.encode('utf-8'),
            headers={'Content-Type': 'text/plain; charset=utf-8'},
            timeout=10
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


def create_app(testing=False):
    """Create and configure Flask app"""
    app = Flask(__name__)

    if testing:
        app.config['TESTING'] = True

    config = get_config()

    # Initialize tools (will be reused across requests)
    tools = CampfireTools(
        db_path=config['CAMPFIRE_DB_PATH'],
        context_dir=config['CONTEXT_DIR']
    )

    # Initialize bot manager (will load all bot configurations)
    # Support external bot directory via environment variable for hot-reload capability
    bots_dir = os.getenv('BOTS_DIR', './bots')
    bot_manager = BotManager(bots_dir=bots_dir)
    print(f"\nLoaded {len(bot_manager.bots)} bot configuration(s) from {bots_dir}:")
    for bot_id, bot_info in bot_manager.list_bots().items():
        print(f"  - {bot_info['display_name']} (model: {bot_info['model']})")

    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        })

    @app.route('/queue/stats', methods=['GET'])
    def queue_stats():
        """
        Get request queue statistics.

        Returns:
            JSON with queue metrics:
            - total_requests: Total requests processed
            - queued_requests: Requests that had to wait
            - active_agents: Number of agents currently processing
            - active_keys: List of (room_id, bot_id) currently active
        """
        request_queue = get_request_queue()
        stats = request_queue.get_stats()
        return jsonify(stats)

    @app.route('/session/stats', methods=['GET'])
    def session_stats():
        """
        Get session cache statistics.

        Returns:
            JSON with session metrics:
            - active_sessions: Number of cached sessions
            - rooms: Number of unique rooms with sessions
            - bots: Number of unique bot types cached
            - ttl_hours: Time-to-live for inactive sessions
            - session_keys: List of cached (room_id, bot_id) pairs with last_used
        """
        session_cache = get_session_cache()
        return jsonify(session_cache.stats())

    @app.route('/session/clear/room/<int:room_id>', methods=['POST'])
    def clear_room_session(room_id: int):
        """
        Clear session cache for a specific room.

        Useful for testing or resetting conversation state.

        Args:
            room_id: Room ID to clear sessions for

        Returns:
            JSON with success status
        """
        session_cache = get_session_cache()
        session_cache.clear_room(room_id)
        return jsonify({"status": "success", "room_id": room_id})

    @app.route('/session/clear/all', methods=['POST'])
    def clear_all_sessions():
        """
        Clear all session cache.

        WARNING: This will reset all conversation memory.

        Returns:
            JSON with success status
        """
        session_cache = get_session_cache()
        session_cache.clear_all()
        return jsonify({"status": "success", "message": "All sessions cleared"})

    @app.route('/webhook', methods=['POST'])
    @app.route('/webhook/<bot_id>', methods=['POST'])
    async def webhook(bot_id=None):
        """
        Campfire webhook endpoint (supports multiple bots)

        URL options:
          - POST /webhook (uses default bot)
          - POST /webhook?bot_id=financial_analyst
          - POST /webhook/financial_analyst
        """
        # Log raw payload for debugging
        print(f"\n[WEBHOOK] Received payload:")
        print(f"Content-Type: {request.content_type}")
        print(f"Raw data: {request.data}")

        # Validate JSON
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        try:
            payload = request.get_json()
            print(f"Parsed JSON: {payload}")
        except Exception as e:
            return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400

        # Try to handle different payload formats
        # Format 1: Our expected format (creator, room, content)
        # Format 2: Campfire format (user, room, message)

        creator = payload.get('creator') or payload.get('user')
        room = payload.get('room')
        content = payload.get('content') or (payload.get('message', {}).get('body', {}).get('plain') if payload.get('message') else None)

        if not creator:
            print(f"ERROR: No creator/user field in payload: {payload.keys()}")
            return jsonify({'error': 'Missing required field: creator or user'}), 400

        if not room:
            print(f"ERROR: No room field in payload: {payload.keys()}")
            return jsonify({'error': 'Missing required field: room'}), 400

        if not content:
            print(f"ERROR: No content/message field in payload: {payload.keys()}")
            return jsonify({'error': 'Missing required field: content or message'}), 400

        # Determine which bot to use
        # Priority: URL path > query param > bot_key from ENV > default
        bot_config = None

        if not bot_id:
            bot_id = request.args.get('bot_id')

        if bot_id:
            bot_config = bot_manager.get_bot_by_id(bot_id)
            if not bot_config:
                return jsonify({'error': f'Bot not found: {bot_id}'}), 404
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

        # Extract data (using variables already extracted above)
        user_id = creator['id']
        user_name = creator['name']
        room_id = room['id']
        room_name = room['name']
        # content is already plain text from extraction above, no need for strip_html

        # DEBUG: Log extracted data
        print(f"[WEBHOOK DATA] User: {user_name} (ID: {user_id})")
        print(f"[WEBHOOK DATA] Room: {room_name} (ID: {room_id})")
        print(f"[WEBHOOK DATA] Content: {content[:100]}...")
        print(f"[WEBHOOK DATA] Bot: {bot_config.display_name}")

        # Extract message ID (if present)
        message_id = payload.get('id') or payload.get('message', {}).get('id')

        # NOTE: File discovery now happens in agent's prompt building
        # via get_recent_room_files() which queries files from entire room history

        # Return 200 immediately to Campfire (avoid timeout)
        # Process in background with acknowledgment
        def process_in_background():
            """Process message and send response in background thread"""
            import asyncio
            import sys

            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            print(f"[Webhook] Background thread started for room {room_id}", flush=True)
            sys.stdout.flush()

            # Get request queue for concurrency control
            request_queue = get_request_queue()

            # Check if agent is currently busy (non-blocking check)
            if request_queue.is_busy(room_id, bot_config.bot_id):
                # Agent is busy - post waiting message
                wait_msg = f"⏳ I'm currently helping someone else in this room. Your request will be processed shortly..."
                post_to_campfire(room_id, wait_msg, testing=app.config.get('TESTING', False))
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
                post_to_campfire(room_id, error_msg, testing=app.config.get('TESTING', False))
                print(f"[Queue] Failed to acquire lock for room {room_id} after 5 minutes")
                return

            print(f"[Queue] Acquired lock for room {room_id}, bot {bot_config.bot_id}")

            try:
                # Send immediate acknowledgment (if not already posted)
                acknowledgment = "🤔 Processing your request..."
                post_to_campfire(room_id, acknowledgment, testing=app.config.get('TESTING', False))
                print(f"[Background] Posted acknowledgment to room {room_id}")

                # Create agent with tools
                api_key = config.get('ANTHROPIC_API_KEY')

                # Skip actual API call if in testing mode with fake key
                if api_key and not api_key.startswith('sk-ant-test'):
                    # Get session cache (stores session IDs, not agent instances)
                    # This enables multi-turn conversations via SDK's resume pattern
                    session_cache = get_session_cache()

                    # Check if we have an existing session for this (room, bot) pair
                    resume_session = session_cache.get(room_id, bot_config.bot_id)

                    # Create FRESH agent for this request (no caching of client instances)
                    # Pass resume_session to continue existing conversation or start new one
                    agent = CampfireAgent(
                        bot_config=bot_config,
                        campfire_tools=tools,
                        resume_session=resume_session  # None for new session, session_id for resume
                    )

                    # Process message with Agent SDK
                    print(f"[Background] Calling Claude Agent SDK with model: {bot_config.model}")

                    # Track if we posted any text blocks during streaming
                    posted_blocks = []

                    # Define callback to post each text block as it arrives
                    def post_text_block(text: str):
                        """Post intermediate text block to Campfire"""
                        post_to_campfire(room_id, text, testing=app.config.get('TESTING', False))
                        posted_blocks.append(text)
                        print(f"[Streaming] Posted text block to Campfire ({len(text)} chars)")

                    # Run async function in thread's event loop with streaming callback
                    # Returns tuple: (response_text, session_id)
                    response_text, new_session_id = loop.run_until_complete(
                        agent.process_message(
                            content=content,
                            context={
                                'user_id': user_id,
                                'user_name': user_name,
                                'room_id': room_id,
                                'room_name': room_name,
                                'message_id': message_id
                            },
                            on_text_block=post_text_block
                        )
                    )

                    # Save session ID for future requests (if returned)
                    if new_session_id:
                        session_cache.set(room_id, bot_config.bot_id, new_session_id)
                else:
                    # Fallback for testing without real API key
                    response_text = f"Received your message in {room_name}: {content[:50]}..."

                # Log response in debug mode
                if config.get('LOG_LEVEL') == 'DEBUG':
                    print(f"\n{'='*60}")
                    print(f"🤖 BOT RESPONSE for room {room_id}:")
                    print(f"{'='*60}")
                    print(response_text)
                    print(f"{'='*60}\n")

                # Post final response to Campfire ONLY if we didn't already post blocks during streaming
                if posted_blocks:
                    print(f"[Background] Already posted {len(posted_blocks)} text blocks during streaming - skipping final post")
                else:
                    # No streaming occurred, post the complete response
                    post_to_campfire(room_id, response_text, testing=app.config.get('TESTING', False))
                    print(f"[Background] Successfully posted response to room {room_id}")

            except Exception as e:
                print(f"[Background] Error processing webhook: {e}", flush=True)
                import traceback
                traceback.print_exc()
                # Post error to Campfire (will be skipped in testing mode)
                post_to_campfire(
                    room_id,
                    f"Sorry, I encountered an error: {str(e)}",
                    testing=app.config.get('TESTING', False)
                )
            finally:
                # Release the lock - CRITICAL to allow next request
                print(f"[Queue] Releasing lock for room {room_id}, bot {bot_config.bot_id}")
                request_queue.release(room_id, bot_config.bot_id)

                # Clean up pending tasks before closing loop
                try:
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()
                    # Give tasks a chance to cancel
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                except Exception:
                    pass
                loop.close()
                print(f"[Background] Thread completed for room {room_id}", flush=True)

        # Start background thread (fire and forget)
        thread = threading.Thread(target=process_in_background, daemon=True)
        thread.start()
        print(f"[Webhook] Started background thread for room {room_id}")

        # Return immediately to avoid webhook timeout (empty response, not JSON)
        return '', 200

    return app


# For gunicorn
app = create_app()


if __name__ == '__main__':
    config = get_config()
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '0.0.0.0')

    print(f"Starting Campfire AI Bot on {host}:{port}")
    print(f"Database: {config['CAMPFIRE_DB_PATH']}")
    print(f"Campfire URL: {config['CAMPFIRE_URL']}")

    app.run(host=host, port=port, debug=False)
