"""
Request Queue Manager - Prevents concurrent agent access race conditions

Ensures that only one request is processed per (room_id, bot_id) at a time.
Multiple requests to the same agent are queued and processed sequentially.

This prevents conversation state corruption when multiple users in a group chat
send messages to the bot simultaneously.
"""

import asyncio
import threading
from typing import Dict, Tuple, Optional
from datetime import datetime


class RequestQueue:
    """
    Manages request queues per (room_id, bot_id) to prevent race conditions.

    Each (room_id, bot_id) pair gets its own lock to ensure sequential processing.
    """

    def __init__(self):
        # Locks per (room_id, bot_id) key
        self._locks: Dict[Tuple[int, str], threading.Lock] = {}
        self._locks_lock = threading.Lock()  # Lock for the locks dict itself

        # Queue statistics
        self._stats = {
            'total_requests': 0,
            'queued_requests': 0,
            'active_agents': set()
        }
        self._stats_lock = threading.Lock()

    def get_lock(self, room_id: int, bot_id: str) -> threading.Lock:
        """
        Get or create a lock for a specific (room_id, bot_id) pair.

        Args:
            room_id: Room ID
            bot_id: Bot ID

        Returns:
            Threading lock for this agent
        """
        key = (room_id, bot_id)

        with self._locks_lock:
            if key not in self._locks:
                self._locks[key] = threading.Lock()
            return self._locks[key]

    def is_busy(self, room_id: int, bot_id: str) -> bool:
        """
        Check if agent is currently processing a request.

        Args:
            room_id: Room ID
            bot_id: Bot ID

        Returns:
            True if agent is busy (lock is held)
        """
        key = (room_id, bot_id)

        with self._locks_lock:
            if key not in self._locks:
                return False

            lock = self._locks[key]
            # Try to acquire lock without blocking
            acquired = lock.acquire(blocking=False)
            if acquired:
                lock.release()  # Release immediately if we got it
                return False
            else:
                return True

    def acquire(self, room_id: int, bot_id: str, blocking: bool = True, timeout: float = -1) -> bool:
        """
        Acquire lock for processing a request.

        Args:
            room_id: Room ID
            bot_id: Bot ID
            blocking: Whether to block waiting for lock
            timeout: Timeout in seconds (-1 for infinite)

        Returns:
            True if lock acquired, False if timeout/non-blocking and couldn't acquire
        """
        lock = self.get_lock(room_id, bot_id)
        key = (room_id, bot_id)

        # Update stats
        with self._stats_lock:
            self._stats['total_requests'] += 1
            if self.is_busy(room_id, bot_id):
                self._stats['queued_requests'] += 1

        acquired = lock.acquire(blocking=blocking, timeout=timeout if timeout > 0 else None)

        if acquired:
            with self._stats_lock:
                self._stats['active_agents'].add(key)

        return acquired

    def release(self, room_id: int, bot_id: str):
        """
        Release lock after processing request.

        Args:
            room_id: Room ID
            bot_id: Bot ID
        """
        lock = self.get_lock(room_id, bot_id)
        key = (room_id, bot_id)

        try:
            lock.release()
        except RuntimeError:
            # Lock wasn't held - ignore
            pass

        with self._stats_lock:
            self._stats['active_agents'].discard(key)

    def get_stats(self) -> Dict:
        """
        Get queue statistics.

        Returns:
            Dict with stats:
            - total_requests: Total requests processed
            - queued_requests: Requests that had to wait
            - active_agents: Number of agents currently processing
            - active_keys: List of (room_id, bot_id) currently active
        """
        with self._stats_lock:
            return {
                'total_requests': self._stats['total_requests'],
                'queued_requests': self._stats['queued_requests'],
                'active_agents': len(self._stats['active_agents']),
                'active_keys': list(self._stats['active_agents']),
                'timestamp': datetime.now().isoformat()
            }


# Global queue instance
_request_queue: Optional[RequestQueue] = None


def get_request_queue() -> RequestQueue:
    """
    Get the global request queue instance (singleton pattern).

    Returns:
        RequestQueue instance
    """
    global _request_queue
    if _request_queue is None:
        _request_queue = RequestQueue()
    return _request_queue
