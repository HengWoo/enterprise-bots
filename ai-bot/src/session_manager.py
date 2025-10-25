"""
SessionManager - Persistent ClaudeSDKClient lifecycle management for v0.2.0 (Beta)

Implements three-tier session strategy:
- Tier 1 (Hot Path): In-memory persistent clients (~9s response)
- Tier 2 (Warm Path): Disk-persisted session recovery (~12s response)
- Tier 3 (Cold Path): Fresh start (~15s response)

Key Features:
- Maintains in-memory cache of ClaudeSDKClient instances
- Persists session IDs to disk for crash recovery
- Auto-cleanup of expired sessions (memory + disk)
- Graceful shutdown handling
"""

import asyncio
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple, Optional

from claude_agent_sdk import ClaudeSDKClient
from src.bot_manager import BotConfig
from src.tools.campfire_tools import CampfireTools
from src.campfire_agent import CampfireAgent


@dataclass
class SessionState:
    """
    Tracks state for a persistent Claude Agent SDK client.

    Why track both client AND agent:
    - client: The persistent ClaudeSDKClient instance (hot path)
    - agent: The CampfireAgent wrapper (builds context, manages tools)
    - session_id: Extracted from SDK's SystemMessage (for disk persistence)

    Cache key: (room_id, bot_id) - per-room sessions (group chat pattern)
    """
    client: ClaudeSDKClient
    agent: CampfireAgent
    session_id: Optional[str]
    last_used: datetime
    room_id: int
    bot_id: str
    connected: bool
    query_count: int
    created_at: datetime


class SessionManager:
    """
    Manages persistent ClaudeSDKClient instances with three-tier strategy.

    Tier 1 (Hot Path): Reuse existing connected client from memory
    Tier 2 (Warm Path): Load session_id from disk, resume with SDK
    Tier 3 (Cold Path): Create fresh client, capture session_id, save to disk

    Why this works with FastAPI:
    - Single event loop for entire application lifetime
    - Clients bound to event loop CAN be reused across webhook requests
    - Unlike Flask where each webhook = new thread = new event loop

    Thread Safety:
    - Uses asyncio.Lock() for concurrent access control
    - Works with FastAPI background tasks (same event loop)
    - Existing request_queue provides per-(room, bot) serialization
    """

    def __init__(
        self,
        ttl_hours: int = 24,
        persistence_dir: str = "./session_cache"
    ):
        """
        Initialize SessionManager.

        Args:
            ttl_hours: Time-to-live for inactive sessions (default 24 hours)
            persistence_dir: Directory for session ID persistence (default ./session_cache)
        """
        self._sessions: Dict[Tuple[int, str], SessionState] = {}
        self._lock = asyncio.Lock()
        self.ttl_hours = ttl_hours
        self.persistence_dir = Path(persistence_dir)
        self.persistence_dir.mkdir(exist_ok=True)

        print(f"[SessionManager] Initialized with TTL={ttl_hours}h, persistence={persistence_dir}")

    async def get_or_create_client(
        self,
        room_id: int,
        bot_id: str,
        bot_config: BotConfig,
        campfire_tools: CampfireTools
    ) -> Tuple[ClaudeSDKClient, CampfireAgent]:
        """
        Get existing client or create new one using three-tier strategy.

        Three-Tier Strategy:
        1. Hot Path: Check in-memory cache for existing connected client
        2. Warm Path: Check disk for session_id, create client with resume=session_id
        3. Cold Path: Create fresh client, capture session_id later

        Args:
            room_id: Room ID
            bot_id: Bot ID
            bot_config: Bot configuration
            campfire_tools: CampfireTools instance

        Returns:
            Tuple of (ClaudeSDKClient, CampfireAgent)
        """
        async with self._lock:
            cache_key = (room_id, bot_id)

            # TIER 1: Hot Path - Check in-memory cache
            if cache_key in self._sessions:
                session_state = self._sessions[cache_key]

                # Verify session not expired
                age = datetime.now() - session_state.last_used
                if age.total_seconds() / 3600 < self.ttl_hours:
                    # Update last_used timestamp
                    session_state.last_used = datetime.now()
                    session_state.query_count += 1

                    print(f"[SessionManager] ✅ Tier 1 (Hot): Reusing client for room {room_id}, bot '{bot_id}'")
                    print(f"[SessionManager]    Session age: {age.seconds}s, queries: {session_state.query_count}")

                    return session_state.client, session_state.agent
                else:
                    # Expired - remove from cache
                    print(f"[SessionManager] ⏰ Session expired for room {room_id}, bot '{bot_id}' (age: {age.total_seconds() / 3600:.1f}h)")
                    await self._close_session(cache_key)

            # TIER 2: Warm Path - Check disk for session_id
            session_id = self._load_session_id_from_disk(room_id, bot_id)

            if session_id:
                print(f"[SessionManager] ♻️  Tier 2 (Warm): Found session_id on disk: {session_id}")
                print(f"[SessionManager]    Creating client with resume='{session_id}'")

                # Create agent with resume
                agent = CampfireAgent(
                    bot_config=bot_config,
                    campfire_tools=campfire_tools,
                    resume_session=session_id  # SDK will resume this session
                )
            else:
                # TIER 3: Cold Path - Create fresh client
                print(f"[SessionManager] 🆕 Tier 3 (Cold): Creating fresh client for room {room_id}, bot '{bot_id}'")

                agent = CampfireAgent(
                    bot_config=bot_config,
                    campfire_tools=campfire_tools,
                    resume_session=None  # Fresh session
                )

            # Get client from agent
            client = agent.client

            # Store in cache
            session_state = SessionState(
                client=client,
                agent=agent,
                session_id=session_id,  # May be None for Tier 3 (will be captured later)
                last_used=datetime.now(),
                room_id=room_id,
                bot_id=bot_id,
                connected=False,  # Will be connected when first used
                query_count=0,
                created_at=datetime.now()
            )

            self._sessions[cache_key] = session_state

            print(f"[SessionManager] 💾 Cached session for room {room_id}, bot '{bot_id}'")

            return client, agent

    def update_session_id(self, room_id: int, bot_id: str, session_id: str):
        """
        Update session_id in memory AND persist to disk.

        Called after agent.process_message() returns new session_id.
        Critical for crash recovery - ensures session_id survives restarts.

        Args:
            room_id: Room ID
            bot_id: Bot ID
            session_id: Session ID from Claude Agent SDK
        """
        cache_key = (room_id, bot_id)

        # Update in-memory cache
        if cache_key in self._sessions:
            self._sessions[cache_key].session_id = session_id
            print(f"[SessionManager] 💾 Updated session_id in memory: {session_id}")

        # Persist to disk immediately
        self._save_session_id_to_disk(room_id, bot_id, session_id)

    def _save_session_id_to_disk(self, room_id: int, bot_id: str, session_id: str):
        """
        Persist session_id to disk as JSON file.

        File format: ./session_cache/session_{room_id}_{bot_id}.json

        Content:
        {
          "session_id": "abc-123",
          "room_id": 1,
          "bot_id": "financial_analyst",
          "last_used": "2025-10-14T08:24:49.123456",
          "created_at": "2025-10-14T08:21:55.789012"
        }

        Args:
            room_id: Room ID
            bot_id: Bot ID
            session_id: Session ID to persist
        """
        file_path = self.persistence_dir / f"session_{room_id}_{bot_id}.json"

        data = {
            "session_id": session_id,
            "room_id": room_id,
            "bot_id": bot_id,
            "last_used": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()  # Will be overwritten if file exists
        }

        # Preserve created_at if file already exists
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    existing_data = json.load(f)
                    data["created_at"] = existing_data.get("created_at", data["created_at"])
            except Exception:
                pass  # Use current timestamp if can't read

        # Write to disk
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"[SessionManager] 💾 Persisted session_id to disk: {file_path.name}")

    def _load_session_id_from_disk(self, room_id: int, bot_id: str) -> Optional[str]:
        """
        Load session_id from disk (for crash recovery).

        Returns None if:
        - File doesn't exist
        - File is too old (exceeds TTL)
        - File is corrupted

        Args:
            room_id: Room ID
            bot_id: Bot ID

        Returns:
            session_id if found and valid, None otherwise
        """
        file_path = self.persistence_dir / f"session_{room_id}_{bot_id}.json"

        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Check TTL
            last_used_str = data.get("last_used")
            if last_used_str:
                last_used = datetime.fromisoformat(last_used_str)
                age = datetime.now() - last_used

                if age.total_seconds() / 3600 >= self.ttl_hours:
                    print(f"[SessionManager] ⏰ Disk session expired (age: {age.total_seconds() / 3600:.1f}h)")
                    # Delete expired file
                    file_path.unlink()
                    return None

            session_id = data.get("session_id")
            if session_id:
                print(f"[SessionManager] 📂 Loaded session_id from disk: {session_id}")
                return session_id

        except Exception as e:
            print(f"[SessionManager] ⚠️  Error loading session from disk: {e}")
            # Delete corrupted file
            try:
                file_path.unlink()
            except Exception:
                pass

        return None

    async def cleanup_inactive_sessions(self):
        """
        Remove expired sessions from memory AND disk.

        Should be called periodically (e.g., every hour) to prevent memory leaks.
        """
        async with self._lock:
            now = datetime.now()
            expired_keys = []

            # Find expired sessions in memory
            for cache_key, session_state in self._sessions.items():
                age = now - session_state.last_used
                if age.total_seconds() / 3600 >= self.ttl_hours:
                    expired_keys.append(cache_key)

            # Remove expired sessions
            for cache_key in expired_keys:
                await self._close_session(cache_key)

            # Clean up expired files from disk
            for file_path in self.persistence_dir.glob("session_*.json"):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)

                    last_used_str = data.get("last_used")
                    if last_used_str:
                        last_used = datetime.fromisoformat(last_used_str)
                        age = now - last_used

                        if age.total_seconds() / 3600 >= self.ttl_hours:
                            file_path.unlink()
                            print(f"[SessionManager] 🗑️  Deleted expired session file: {file_path.name}")
                except Exception as e:
                    print(f"[SessionManager] ⚠️  Error cleaning up {file_path.name}: {e}")

            if expired_keys:
                print(f"[SessionManager] 🧹 Cleaned up {len(expired_keys)} expired session(s)")

    async def _close_session(self, cache_key: Tuple[int, str]):
        """
        Close and remove a session from cache.

        Args:
            cache_key: (room_id, bot_id)
        """
        if cache_key in self._sessions:
            session_state = self._sessions[cache_key]

            # TODO: Close client connection if SDK provides close method
            # For now, just remove from cache and let garbage collection handle it

            del self._sessions[cache_key]

            room_id, bot_id = cache_key
            print(f"[SessionManager] 🗑️  Closed session for room {room_id}, bot '{bot_id}'")

    async def shutdown_all(self):
        """
        Gracefully shutdown all active sessions.

        Called during FastAPI lifespan shutdown.
        Ensures all clients are properly closed before application exits.
        """
        async with self._lock:
            print(f"[SessionManager] 🛑 Shutting down {len(self._sessions)} active session(s)...")

            for cache_key in list(self._sessions.keys()):
                await self._close_session(cache_key)

            print("[SessionManager] ✅ Shutdown complete")

    def stats(self) -> dict:
        """
        Get current session statistics.

        Returns:
            Dict with session metrics for monitoring
        """
        return {
            "active_sessions": len(self._sessions),
            "ttl_hours": self.ttl_hours,
            "persistence_dir": str(self.persistence_dir),
            "sessions": [
                {
                    "room_id": state.room_id,
                    "bot_id": state.bot_id,
                    "session_id": state.session_id,
                    "connected": state.connected,
                    "query_count": state.query_count,
                    "age_seconds": (datetime.now() - state.last_used).seconds,
                    "created_at": state.created_at.isoformat()
                }
                for state in self._sessions.values()
            ]
        }
