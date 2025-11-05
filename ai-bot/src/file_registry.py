"""
File Registry for Temporary File Downloads

Manages temporary file downloads with UUID tokens and automatic expiry.
Part of v0.4.1 File Download System implementation.
"""

import uuid
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional


class FileRegistry:
    """Manages temporary file downloads with UUID tokens."""

    def __init__(self):
        self._registry: Dict[str, dict] = {}

    def register_file(
        self,
        file_path: str,
        filename: str,
        expiry_hours: int = 1,
        mime_type: str = "text/html"
    ) -> str:
        """
        Register a file for download.

        Args:
            file_path: Absolute path to the file on disk
            filename: User-facing filename for download
            expiry_hours: Hours until download link expires (default: 1)
            mime_type: MIME type for Content-Type header (default: text/html)

        Returns:
            UUID token for download URL

        Example:
            token = file_registry.register_file(
                file_path="/tmp/presentation_xyz.html",
                filename="Q3_Financial_Performance.html",
                expiry_hours=1
            )
            # Returns: "abc123-uuid-456def"
        """
        token = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=expiry_hours)

        self._registry[token] = {
            "file_path": file_path,
            "filename": filename,
            "mime_type": mime_type,
            "expires_at": expires_at,
            "created_at": now
        }

        return token

    def get_file_info(self, token: str) -> Optional[dict]:
        """
        Get file info by token (returns None if expired/not found).

        Args:
            token: UUID token from register_file()

        Returns:
            File info dict if valid and not expired, None otherwise

        Example:
            info = file_registry.get_file_info("abc123-uuid-456def")
            if info:
                print(f"File: {info['filename']}")
                print(f"Path: {info['file_path']}")
                print(f"Expires: {info['expires_at']}")
        """
        if token not in self._registry:
            return None

        file_info = self._registry[token]

        # Check expiry
        now = datetime.now(timezone.utc)
        if now > file_info["expires_at"]:
            del self._registry[token]
            return None

        return file_info

    def cleanup_expired(self) -> int:
        """
        Remove expired files from registry and delete from disk.

        Returns:
            Number of files cleaned up

        Example:
            count = file_registry.cleanup_expired()
            print(f"Cleaned up {count} expired files")
        """
        now = datetime.now(timezone.utc)
        expired_tokens = [
            token for token, info in self._registry.items()
            if now > info["expires_at"]
        ]

        for token in expired_tokens:
            file_path = self._registry[token]["file_path"]

            # Delete file from disk
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                # Log error but continue cleanup
                print(f"[FileRegistry] Error deleting file {file_path}: {e}")

            # Remove from registry
            del self._registry[token]

        return len(expired_tokens)

    def get_stats(self) -> dict:
        """
        Get registry statistics.

        Returns:
            Dictionary with total files and detailed file list

        Example:
            stats = file_registry.get_stats()
            print(f"Total files: {stats['total_files']}")
            for file in stats['files']:
                print(f"- {file['filename']} (expires: {file['expires_at']})")
        """
        return {
            "total_files": len(self._registry),
            "files": [
                {
                    "token": token,
                    "filename": info["filename"],
                    "created_at": info["created_at"].isoformat(),
                    "expires_at": info["expires_at"].isoformat()
                }
                for token, info in self._registry.items()
            ]
        }


# Global instance
file_registry = FileRegistry()
