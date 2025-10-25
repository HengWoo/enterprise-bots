"""
Session Cache - Store Claude Agent SDK session IDs for multi-turn conversations

Unlike agent_cache.py which cached ClaudeSDKClient instances (causing event loop issues),
this module caches only session IDs and creates fresh clients for each request with resume.

Pattern:
- Request 1: Create new agent → extract session_id from SystemMessage → cache it
- Request 2+: Create new agent with resume=session_id → maintains conversation state

Key: Session IDs are safe to cache because they're just strings, not client instances.
"""

import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple


class SessionCache:
    """
    Thread-safe cache for Claude Agent SDK session IDs.

    Stores mapping of (room_id, bot_id) -> (session_id, last_used_timestamp)

    Session IDs persist for 24 hours (configurable) to maintain conversation
    continuity while preventing indefinite memory growth.
    """

    def __init__(self, ttl_hours: int = 24):
        """
        Initialize session cache.

        Args:
            ttl_hours: Time-to-live for session IDs in hours (default: 24)
        """
        self._cache: Dict[Tuple[int, str], Tuple[str, datetime]] = {}
        self._lock = threading.Lock()
        self.ttl_hours = ttl_hours

    def get(self, room_id: int, bot_id: str) -> Optional[str]:
        """
        Get session ID for (room_id, bot_id) pair.

        Returns None if:
        - No session exists
        - Session expired (older than TTL)

        Args:
            room_id: Room ID
            bot_id: Bot identifier

        Returns:
            Session ID string or None
        """
        with self._lock:
            key = (room_id, bot_id)

            if key not in self._cache:
                return None

            session_id, last_used = self._cache[key]

            # Check if session expired
            if datetime.now() - last_used > timedelta(hours=self.ttl_hours):
                print(f"[Session Cache] ⏰ Session expired for room {room_id}, bot '{bot_id}' (age: {datetime.now() - last_used})")
                del self._cache[key]
                return None

            # Update last_used timestamp
            self._cache[key] = (session_id, datetime.now())
            print(f"[Session Cache] ♻️  Found session for room {room_id}, bot '{bot_id}': {session_id}")
            return session_id

    def set(self, room_id: int, bot_id: str, session_id: str):
        """
        Store session ID for (room_id, bot_id) pair.

        Args:
            room_id: Room ID
            bot_id: Bot identifier
            session_id: Session ID from Claude Agent SDK SystemMessage
        """
        with self._lock:
            key = (room_id, bot_id)
            self._cache[key] = (session_id, datetime.now())
            print(f"[Session Cache] 💾 Stored session for room {room_id}, bot '{bot_id}': {session_id}")

    def clear_room(self, room_id: int):
        """
        Clear all sessions for a specific room.

        Useful for testing or resetting conversation state.

        Args:
            room_id: Room ID to clear sessions for
        """
        with self._lock:
            keys_to_delete = [key for key in self._cache if key[0] == room_id]
            for key in keys_to_delete:
                del self._cache[key]
            print(f"[Session Cache] 🗑️  Cleared {len(keys_to_delete)} session(s) for room {room_id}")

    def clear_all(self):
        """
        Clear all cached sessions.

        WARNING: This will reset all conversation memory.
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            print(f"[Session Cache] 🗑️  Cleared all {count} session(s)")

    def cleanup_expired(self):
        """
        Remove expired sessions from cache.

        Called periodically to prevent memory growth.
        Returns number of sessions removed.
        """
        with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, (session_id, last_used) in self._cache.items()
                if now - last_used > timedelta(hours=self.ttl_hours)
            ]

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                print(f"[Session Cache] 🧹 Cleaned up {len(expired_keys)} expired session(s)")

            return len(expired_keys)

    def stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dict with metrics:
            - active_sessions: Number of cached sessions
            - rooms: Number of unique rooms with sessions
            - bots: Number of unique bot types cached
            - ttl_hours: Time-to-live configuration
            - session_keys: List of cached (room_id, bot_id) pairs
        """
        with self._lock:
            rooms = set(key[0] for key in self._cache)
            bots = set(key[1] for key in self._cache)

            return {
                "active_sessions": len(self._cache),
                "rooms": len(rooms),
                "bots": len(bots),
                "ttl_hours": self.ttl_hours,
                "session_keys": [
                    {"room_id": key[0], "bot_id": key[1], "last_used": last_used.isoformat()}
                    for key, (session_id, last_used) in self._cache.items()
                ]
            }


# Global singleton instance
_session_cache: Optional[SessionCache] = None


def get_session_cache() -> SessionCache:
    """
    Get global session cache instance (singleton pattern).

    Returns:
        SessionCache instance
    """
    global _session_cache
    if _session_cache is None:
        _session_cache = SessionCache()
    return _session_cache
