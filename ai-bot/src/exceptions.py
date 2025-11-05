"""
Custom exceptions for Campfire AI Bot

This module defines custom exceptions used throughout the application for
specific error handling scenarios.
"""


class SessionRecoveryError(Exception):
    """
    Raised when a stale session is detected and needs recovery.

    This occurs when:
    1. Session ID exists in disk cache (Tier 2 Warm Path)
    2. But Claude CLI subprocess has no record of that session
    3. Typically after container restart or process crash

    Handlers should:
    1. Delete stale session from memory cache
    2. Delete stale session file from disk
    3. Retry with fresh session (Tier 3 Cold Path)

    Example:
        try:
            response = await agent.process_message(...)
        except SessionRecoveryError as e:
            print(f"Stale session detected: {e}")
            await session_manager.handle_invalid_session(room_id, bot_id)
            # Retry with fresh session
            response = await agent.process_message(...)
    """
    pass
