"""
Campfire tools for Claude Agent SDK
Provides consolidated tools for conversation search, user context, and knowledge base
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
import re

logger = logging.getLogger(__name__)


class CampfireTools:
    """Consolidated tools for Campfire AI bot"""

    def __init__(self, db_path: str, context_dir: str = "./user_contexts", knowledge_base_dir: str = "./ai-knowledge/company_kb"):
        """
        Initialize CampfireTools

        Args:
            db_path: Path to Campfire SQLite database
            context_dir: Directory to store user context JSON files
            knowledge_base_dir: Directory containing company knowledge base
        """
        self.db_path = db_path
        self.context_dir = Path(context_dir)
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_base_dir = Path(knowledge_base_dir)
        self._db_conn = None

    def _get_db_connection(self) -> sqlite3.Connection:
        """Get read-only database connection"""
        if self._db_conn is None:
            # Open in read-only mode with URI
            self._db_conn = sqlite3.connect(
                f'file:{self.db_path}?mode=ro',
                uri=True,
                check_same_thread=False
            )
            self._db_conn.row_factory = sqlite3.Row
            # Enforce read-only
            self._db_conn.execute('PRAGMA query_only = ON')
        return self._db_conn

    def _strip_html(self, html: Optional[str]) -> str:
        """Strip HTML tags from text"""
        if not html:
            return ""

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def search_conversations(
        self,
        query: str,
        room_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search conversation history

        Args:
            query: Search query (case-insensitive)
            room_id: Optional room filter
            limit: Maximum results to return

        Returns:
            List of message dictionaries with keys:
            - message_id, room_id, room_name, creator_name, body, created_at
        """
        conn = self._get_db_connection()
        cursor = conn.cursor()

        # Build query
        sql = """
            SELECT
                m.id as message_id,
                m.room_id,
                r.name as room_name,
                u.name as creator_name,
                art.body,
                m.created_at
            FROM messages m
            JOIN rooms r ON m.room_id = r.id
            JOIN users u ON m.creator_id = u.id
            LEFT JOIN action_text_rich_texts art
                ON art.record_type = 'Message' AND art.record_id = m.id
            WHERE 1=1
        """

        params = []

        # Add query filter
        if query:
            sql += " AND LOWER(art.body) LIKE LOWER(?)"
            params.append(f"%{query}%")

        # Add room filter
        if room_id is not None:
            sql += " AND m.room_id = ?"
            params.append(room_id)

        # Order by most recent
        sql += " ORDER BY m.created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                "message_id": row["message_id"],
                "room_id": row["room_id"],
                "room_name": row["room_name"],
                "creator_name": row["creator_name"],
                "body": self._strip_html(row["body"]),
                "created_at": row["created_at"]
            })

        return results

    def get_user_context(self, user_id: int) -> Dict[str, Any]:
        """
        Get user context (from DB + saved JSON file)

        Args:
            user_id: User ID

        Returns:
            Dictionary with user info, rooms, preferences, expertise, etc.
        """
        conn = self._get_db_connection()
        cursor = conn.cursor()

        # Get basic user info from DB
        cursor.execute("""
            SELECT id, name, email_address
            FROM users
            WHERE id = ?
        """, (user_id,))

        user_row = cursor.fetchone()

        if user_row:
            context = {
                "user_id": user_row["id"],
                "user_name": user_row["name"],
                "email": user_row["email_address"]
            }
        else:
            context = {
                "user_id": user_id,
                "user_name": None,
                "email": None
            }

        # Get user's rooms
        cursor.execute("""
            SELECT r.id as room_id, r.name as room_name, r.type as room_type
            FROM memberships m
            JOIN rooms r ON m.room_id = r.id
            WHERE m.user_id = ?
        """, (user_id,))

        rooms = []
        for row in cursor.fetchall():
            rooms.append({
                "room_id": row["room_id"],
                "room_name": row["room_name"],
                "room_type": row["room_type"]
            })

        context["rooms"] = rooms

        # Load saved context from JSON file
        context_file = self.context_dir / f"user_{user_id}.json"
        if context_file.exists():
            with open(context_file, 'r') as f:
                saved_context = json.load(f)

            # Merge saved context
            for key in ["preferences", "expertise", "conversation_memory", "last_updated"]:
                if key in saved_context:
                    context[key] = saved_context[key]

        return context

    def save_user_context(
        self,
        user_id: int,
        preferences: Optional[Dict[str, Any]] = None,
        expertise: Optional[List[str]] = None,
        conversation_memory: Optional[List[str]] = None
    ) -> None:
        """
        Save user context to JSON file

        Args:
            user_id: User ID
            preferences: User preferences dict
            expertise: List of expertise areas
            conversation_memory: List of conversation memories
        """
        context_file = self.context_dir / f"user_{user_id}.json"

        # Load existing context
        if context_file.exists():
            with open(context_file, 'r') as f:
                context = json.load(f)
        else:
            context = {
                "user_id": user_id,
                "preferences": {},
                "expertise": [],
                "conversation_memory": []
            }

        # Update fields
        if preferences is not None:
            context["preferences"].update(preferences)

        if expertise is not None:
            context["expertise"] = expertise

        if conversation_memory is not None:
            # Append new memories
            if "conversation_memory" not in context:
                context["conversation_memory"] = []
            context["conversation_memory"].extend(conversation_memory)

        # Update timestamp
        context["last_updated"] = datetime.now().isoformat()

        # Save to file
        with open(context_file, 'w') as f:
            json.dump(context, f, indent=2)

    def get_message_attachments(self, message_id: int, files_base_path: str = "/campfire-files") -> List[Dict[str, Any]]:
        """
        Get file attachments for a message

        Args:
            message_id: Message ID
            files_base_path: Base path where Campfire stores files

        Returns:
            List of attachment dictionaries with keys:
            - filename, content_type, file_path, byte_size, metadata
        """
        conn = self._get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                b.filename,
                b.content_type,
                b.key as blob_key,
                b.byte_size,
                b.metadata
            FROM active_storage_attachments a
            JOIN active_storage_blobs b ON a.blob_id = b.id
            WHERE a.record_type = 'Message'
              AND a.record_id = ?
        """, (message_id,))

        attachments = []
        for row in cursor.fetchall():
            # Construct file path from blob key
            # Campfire uses hash-based partitioning: first 2 chars / next 2 chars / remaining
            blob_key = row["blob_key"]
            if len(blob_key) >= 4:
                partition = f"{blob_key[0:2]}/{blob_key[2:4]}"
                file_path = f"{files_base_path}/{partition}/{blob_key}"
            else:
                file_path = f"{files_base_path}/{blob_key}"

            # Parse metadata JSON if present
            metadata = {}
            if row["metadata"]:
                try:
                    metadata = json.loads(row["metadata"])
                except:
                    pass

            attachments.append({
                "filename": row["filename"],
                "content_type": row["content_type"],
                "file_path": file_path,
                "byte_size": row["byte_size"],
                "metadata": metadata,
                "blob_key": blob_key
            })

        return attachments

    def get_recent_room_files(self, room_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get files uploaded in recent messages in a room

        Args:
            room_id: Room ID to search
            limit: Maximum number of recent messages to check

        Returns:
            List of file dictionaries with keys:
            - filename, content_type, file_path, message_id, uploaded_at, blob_key
        """
        conn = self._get_db_connection()
        cursor = conn.cursor()

        files_base_path = "/campfire-files"

        # Query: Get attachments from recent messages in this room
        cursor.execute("""
            SELECT DISTINCT
                b.filename,
                b.content_type,
                b.key as blob_key,
                b.byte_size,
                m.id as message_id,
                m.created_at as uploaded_at
            FROM messages m
            JOIN active_storage_attachments a
                ON a.record_type = 'Message' AND a.record_id = m.id
            JOIN active_storage_blobs b
                ON a.blob_id = b.id
            WHERE m.room_id = ?
            ORDER BY m.created_at DESC
            LIMIT ?
        """, (room_id, limit))

        files = []
        for row in cursor.fetchall():
            blob_key = row["blob_key"]
            if len(blob_key) >= 4:
                partition = f"{blob_key[0:2]}/{blob_key[2:4]}"
                file_path = f"{files_base_path}/{partition}/{blob_key}"
            else:
                file_path = f"{files_base_path}/{blob_key}"

            files.append({
                "filename": row["filename"],
                "content_type": row["content_type"],
                "file_path": file_path,
                "message_id": row["message_id"],
                "uploaded_at": row["uploaded_at"],
                "blob_key": blob_key
            })

        return files

    # ====================
    # Knowledge Base Methods
    # ====================

    def search_knowledge_base(
        self,
        query: str,
        category: Optional[str] = None,
        max_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search company knowledge base using keyword search (agentic approach).

        Following Anthropic's recommendation: simple file system search is
        often more effective than semantic/vector search for small-medium
        knowledge bases.

        Args:
            query: Search keywords or natural language question
            category: Optional filter ('policies', 'procedures', 'technical', 'financial', 'all')
            max_results: Maximum number of results to return

        Returns:
            List of result dicts with keys: path, title, excerpt, relevance_score
        """
        if not self.knowledge_base_dir.exists():
            return []

        # Determine search path based on category
        if category and category != "all":
            search_path = self.knowledge_base_dir / category
            if not search_path.exists():
                return []
        else:
            search_path = self.knowledge_base_dir

        # Search for markdown files
        results = []
        query_lower = query.lower()

        for md_file in search_path.rglob("*.md"):
            # Skip README files
            if md_file.name == "README.md":
                continue

            try:
                content = md_file.read_text(encoding="utf-8")

                # Check if query appears in content
                if query_lower in content.lower():
                    # Extract title (first H1 heading)
                    title = "Untitled"
                    for line in content.split("\n"):
                        if line.startswith("# "):
                            title = line[2:].strip()
                            break

                    # Find relevant excerpt (3 lines around first match)
                    lines = content.split("\n")
                    excerpt_lines = []
                    relevance_score = 0

                    for i, line in enumerate(lines):
                        if query_lower in line.lower():
                            # Count occurrences for relevance scoring
                            relevance_score += line.lower().count(query_lower)

                            # Extract context (1 line before, match line, 1 line after)
                            start = max(0, i - 1)
                            end = min(len(lines), i + 2)
                            context = "\n".join(lines[start:end])

                            if context not in excerpt_lines:
                                excerpt_lines.append(context)

                            # Only get first few matches
                            if len(excerpt_lines) >= 2:
                                break

                    excerpt = "\n...\n".join(excerpt_lines)
                    if not excerpt:
                        # If no excerpt found, use first 200 chars
                        excerpt = content[:200] + "..."

                    # Get relative path from knowledge base root
                    relative_path = md_file.relative_to(self.knowledge_base_dir)

                    results.append({
                        "path": str(relative_path),
                        "title": title,
                        "excerpt": excerpt,
                        "relevance_score": relevance_score
                    })

            except Exception as e:
                # Skip files that can't be read
                continue

        # Sort by relevance score (descending)
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Return top N results
        return results[:max_results]

    def read_knowledge_document(self, path: str) -> Dict[str, Any]:
        """
        Read full content of a knowledge base document.

        Args:
            path: Relative path to document (e.g., 'policies/financial-reporting-standards.md')

        Returns:
            Dict with keys: path, title, content, last_updated, category, success
        """
        doc_path = self.knowledge_base_dir / path

        if not doc_path.exists():
            return {
                "success": False,
                "error": f"Document not found: {path}",
                "path": path
            }

        try:
            content = doc_path.read_text(encoding="utf-8")

            # Extract title (first H1 heading)
            title = "Untitled"
            for line in content.split("\n"):
                if line.startswith("# "):
                    title = line[2:].strip()
                    break

            # Extract last updated date if present
            last_updated = None
            for line in content.split("\n")[:20]:  # Check first 20 lines
                if "Last Updated:" in line or "last updated:" in line.lower():
                    # Extract date (format: YYYY-MM-DD)
                    parts = line.split(":")
                    if len(parts) >= 2:
                        date_str = parts[1].strip().split()[0]  # Get first word after colon
                        last_updated = date_str
                    break

            # Determine category from path
            category = str(Path(path).parent) if "/" in path else "root"

            return {
                "success": True,
                "path": path,
                "title": title,
                "content": content,
                "last_updated": last_updated,
                "category": category
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading document: {str(e)}",
                "path": path
            }

    def list_knowledge_documents(
        self,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List available knowledge base documents.

        Args:
            category: Optional category filter ('policies', 'procedures', 'technical', 'financial')

        Returns:
            List of document metadata dicts with keys: path, title, category, last_updated
        """
        if not self.knowledge_base_dir.exists():
            return []

        # Determine search path
        if category and category != "all":
            search_path = self.knowledge_base_dir / category
            if not search_path.exists():
                return []
        else:
            search_path = self.knowledge_base_dir

        documents = []

        for md_file in search_path.rglob("*.md"):
            # Skip README files
            if md_file.name == "README.md":
                continue

            try:
                content = md_file.read_text(encoding="utf-8")

                # Extract title
                title = "Untitled"
                for line in content.split("\n"):
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break

                # Extract last updated
                last_updated = None
                for line in content.split("\n")[:20]:
                    if "Last Updated:" in line or "last updated:" in line.lower():
                        parts = line.split(":")
                        if len(parts) >= 2:
                            date_str = parts[1].strip().split()[0]
                            last_updated = date_str
                        break

                # Get relative path and category
                relative_path = md_file.relative_to(self.knowledge_base_dir)
                doc_category = str(relative_path.parent) if "/" in str(relative_path) else "root"

                documents.append({
                    "path": str(relative_path),
                    "title": title,
                    "category": doc_category,
                    "last_updated": last_updated
                })

            except Exception:
                continue

        # Sort by category, then title
        documents.sort(key=lambda x: (x["category"], x["title"]))

        return documents

    def store_knowledge_document(
        self,
        category: str,
        title: str,
        content: str,
        author: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Store new document to knowledge base.

        Args:
            category: Document category (any string, will be normalized to kebab-case)
            title: Document title
            content: Markdown content
            author: Optional author name

        Returns:
            Dict with keys: success, path, message
        """
        # Normalize category to kebab-case for filesystem compatibility
        # Accepts any input: "Strategic Planning" → "strategic-planning"
        normalized_category = category.lower()
        normalized_category = re.sub(r'[^\w\s-]', '', normalized_category)  # Remove special chars
        normalized_category = re.sub(r'[-\s]+', '-', normalized_category)   # Replace spaces/hyphens with single hyphen
        normalized_category = normalized_category.strip('-')

        if not normalized_category:
            logger.error(f"[KB] Invalid category after normalization: '{category}'")
            return {
                "success": False,
                "message": f"Invalid category: '{category}' - cannot be empty after normalization"
            }

        # Create category directory if it doesn't exist
        category_dir = self.knowledge_base_dir / normalized_category
        try:
            category_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"[KB] Failed to create category directory '{normalized_category}': {str(e)}")
            return {
                "success": False,
                "message": f"Failed to create category directory: {str(e)}"
            }

        # Generate filename from title (kebab-case)
        filename = title.lower()
        filename = re.sub(r'[^\w\s-]', '', filename)  # Remove special chars
        filename = re.sub(r'[-\s]+', '-', filename)   # Replace spaces/hyphens with single hyphen
        filename = filename.strip('-') + '.md'

        file_path = category_dir / filename

        # Check if file already exists
        if file_path.exists():
            logger.warning(f"[KB] Document already exists: {normalized_category}/{filename}")
            return {
                "success": False,
                "message": f"Document already exists: {normalized_category}/{filename}",
                "path": f"{normalized_category}/{filename}"
            }

        # Prepare content with metadata header
        current_date = datetime.now().strftime("%Y-%m-%d")
        full_content = f"""# {title}

**Last Updated:** {current_date}
**Category:** {normalized_category}
**Original Category:** {category}
"""

        if author:
            full_content += f"**Author:** {author}\n"

        full_content += f"\n---\n\n{content}\n\n---\n\n"
        full_content += f"**Document Owner:** {author if author else 'TBD'}\n"
        full_content += f"**Review Cycle:** TBD\n"
        full_content += f"**Next Review:** TBD\n"

        try:
            file_path.write_text(full_content, encoding="utf-8")
            logger.info(f"[KB] ✅ Document created: {normalized_category}/{filename} (original category: '{category}')")

            return {
                "success": True,
                "path": f"{normalized_category}/{filename}",
                "message": f"Document created successfully at: {normalized_category}/{filename} (original category: '{category}')"
            }

        except Exception as e:
            logger.error(f"[KB] ❌ Failed to create document '{normalized_category}/{filename}': {str(e)}")
            return {
                "success": False,
                "message": f"Error creating document: {str(e)}"
            }

    # ====================
    # Daily Briefing Methods
    # ====================

    def generate_daily_briefing(
        self,
        date: Optional[str] = None,
        room_ids: Optional[List[int]] = None,
        include_files: bool = True,
        summary_length: str = "concise"
    ) -> Dict[str, Any]:
        """
        Generate daily briefing from Campfire conversations and files.

        Args:
            date: Date to generate briefing for (YYYY-MM-DD), defaults to today
            room_ids: Optional list of room IDs to include, defaults to all active rooms
            include_files: Include file attachments in briefing (default: True)
            summary_length: "concise" (1-2 pages) or "detailed" (5-10 pages)

        Returns:
            Dict with keys: success, briefing_path, briefing_content, message_count, file_count
        """
        from datetime import datetime, timedelta

        # Parse date or use today
        if date:
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid date format: {date}. Use YYYY-MM-DD"
                }
        else:
            target_date = datetime.now()

        # Format dates for database query
        date_str = target_date.strftime("%Y-%m-%d")

        # Get database connection
        conn = self._get_db_connection()
        cursor = conn.cursor()

        # Query 1: Get all messages for the day
        # Use DATE() function to handle both ISO timestamps (2025-10-04T06:13:00.711524)
        # and space-separated timestamps (2025-10-04 06:13:00)
        sql = """
            SELECT
                m.id as message_id,
                m.room_id,
                r.name as room_name,
                u.name as creator_name,
                u.role as creator_role,
                art.body,
                m.created_at
            FROM messages m
            JOIN rooms r ON m.room_id = r.id
            JOIN users u ON m.creator_id = u.id
            LEFT JOIN action_text_rich_texts art
                ON art.record_type = 'Message' AND art.record_id = m.id
            WHERE DATE(m.created_at) = ?
        """

        params = [date_str]

        # Add room filter if specified
        if room_ids:
            placeholders = ",".join("?" * len(room_ids))
            sql += f" AND m.room_id IN ({placeholders})"
            params.extend(room_ids)

        sql += " ORDER BY m.room_id, m.created_at"

        cursor.execute(sql, params)
        messages = cursor.fetchall()

        if not messages:
            return {
                "success": False,
                "error": f"No messages found for {date_str}"
            }

        # Organize messages by room
        rooms_data = {}
        for row in messages:
            room_id = row["room_id"]
            if room_id not in rooms_data:
                rooms_data[room_id] = {
                    "room_name": row["room_name"],
                    "messages": [],
                    "participants": set()
                }

            rooms_data[room_id]["messages"].append({
                "message_id": row["message_id"],
                "creator_name": row["creator_name"],
                "creator_role": row["creator_role"],
                "body": self._strip_html(row["body"]),
                "created_at": row["created_at"]
            })
            rooms_data[room_id]["participants"].add(row["creator_name"])

        # Query 2: Get files uploaded that day
        files_list = []
        if include_files:
            cursor.execute("""
                SELECT DISTINCT
                    b.filename,
                    b.content_type,
                    b.byte_size,
                    m.id as message_id,
                    m.room_id,
                    r.name as room_name,
                    u.name as uploader_name,
                    m.created_at
                FROM messages m
                JOIN active_storage_attachments a
                    ON a.record_type = 'Message' AND a.record_id = m.id
                JOIN active_storage_blobs b
                    ON a.blob_id = b.id
                JOIN rooms r ON m.room_id = r.id
                JOIN users u ON m.creator_id = u.id
                WHERE DATE(m.created_at) = ?
                ORDER BY m.created_at
            """, (date_str,))

            for row in cursor.fetchall():
                files_list.append({
                    "filename": row["filename"],
                    "content_type": row["content_type"],
                    "byte_size": row["byte_size"],
                    "message_id": row["message_id"],
                    "room_name": row["room_name"],
                    "uploader_name": row["uploader_name"],
                    "created_at": row["created_at"]
                })

        # Generate briefing document
        briefing_content = self._format_briefing(
            date_str=date_str,
            rooms_data=rooms_data,
            files_list=files_list,
            summary_length=summary_length
        )

        # Save briefing to knowledge base
        year = target_date.strftime("%Y")
        month = target_date.strftime("%m")
        briefing_dir = self.knowledge_base_dir / "briefings" / year / month
        briefing_dir.mkdir(parents=True, exist_ok=True)

        briefing_filename = f"daily-briefing-{date_str}.md"
        briefing_path = briefing_dir / briefing_filename
        briefing_path.write_text(briefing_content, encoding="utf-8")

        relative_path = f"briefings/{year}/{month}/{briefing_filename}"

        return {
            "success": True,
            "briefing_path": relative_path,
            "briefing_content": briefing_content,
            "message_count": len(messages),
            "file_count": len(files_list),
            "rooms_covered": len(rooms_data)
        }

    def _format_briefing(
        self,
        date_str: str,
        rooms_data: Dict[int, Dict],
        files_list: List[Dict],
        summary_length: str
    ) -> str:
        """Format briefing document as markdown"""
        from datetime import datetime

        # Count totals
        total_messages = sum(len(r["messages"]) for r in rooms_data.values())
        all_participants = set()
        for room_data in rooms_data.values():
            all_participants.update(room_data["participants"])

        # Generate document
        content = f"""# Daily Briefing - {date_str}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Coverage:** Full day (00:00 - 23:59)
**Rooms Covered:** {len(rooms_data)} room(s)
**Total Messages:** {total_messages} messages
**Files Uploaded:** {len(files_list)} file(s)
**Active Participants:** {len(all_participants)} user(s)

---

## Executive Summary

"""

        # Generate executive summary (AI-friendly placeholder for now)
        if total_messages == 0:
            content += "No significant activity recorded for this day.\n"
        elif total_messages < 10:
            content += f"Light activity day with {total_messages} messages across {len(rooms_data)} room(s). "
        elif total_messages < 50:
            content += f"Moderate activity with {total_messages} messages across {len(rooms_data)} room(s). "
        else:
            content += f"Active day with {total_messages} messages across {len(rooms_data)} room(s). "

        if files_list:
            content += f"{len(files_list)} file(s) were uploaded and discussed.\n"

        content += "\n---\n\n## By Room Activity\n\n"

        # Room-by-room breakdown
        for room_id, room_data in sorted(rooms_data.items(), key=lambda x: len(x[1]["messages"]), reverse=True):
            room_name = room_data["room_name"]
            msg_count = len(room_data["messages"])
            participants = ", ".join(sorted(room_data["participants"]))

            content += f"### 💬 {room_name} (Room #{room_id})\n\n"
            content += f"**Messages:** {msg_count} | **Participants:** {participants}\n\n"

            if summary_length == "concise":
                # Concise: Show first 3 and last 3 messages
                messages_to_show = room_data["messages"][:3]
                if len(room_data["messages"]) > 6:
                    content += "**First messages:**\n\n"
                    for msg in messages_to_show:
                        timestamp = msg["created_at"].split(" ")[1][:5] if " " in msg["created_at"] else "00:00"
                        content += f"- [{timestamp}] **{msg['creator_name']}:** {msg['body'][:100]}{'...' if len(msg['body']) > 100 else ''}\n"

                    content += f"\n_(... {len(room_data['messages']) - 6} messages omitted ...)_\n\n"
                    content += "**Last messages:**\n\n"
                    for msg in room_data["messages"][-3:]:
                        timestamp = msg["created_at"].split(" ")[1][:5] if " " in msg["created_at"] else "00:00"
                        content += f"- [{timestamp}] **{msg['creator_name']}:** {msg['body'][:100]}{'...' if len(msg['body']) > 100 else ''}\n"
                else:
                    content += "**Messages:**\n\n"
                    for msg in room_data["messages"]:
                        timestamp = msg["created_at"].split(" ")[1][:5] if " " in msg["created_at"] else "00:00"
                        content += f"- [{timestamp}] **{msg['creator_name']}:** {msg['body'][:100]}{'...' if len(msg['body']) > 100 else ''}\n"
            else:
                # Detailed: Show all messages
                content += "**Messages:**\n\n"
                for msg in room_data["messages"]:
                    timestamp = msg["created_at"].split(" ")[1][:5] if " " in msg["created_at"] else "00:00"
                    content += f"- [{timestamp}] **{msg['creator_name']}:** {msg['body']}\n"

            content += "\n"

        # Files section
        if files_list:
            content += "---\n\n## Files & Attachments\n\n"
            for i, file_info in enumerate(files_list, 1):
                timestamp = file_info["created_at"].split(" ")[1][:5] if " " in file_info["created_at"] else "00:00"
                size_kb = file_info["byte_size"] / 1024
                content += f"{i}. **{file_info['filename']}**\n"
                content += f"   - Uploaded by: {file_info['uploader_name']} at {timestamp}\n"
                content += f"   - Room: {file_info['room_name']}\n"
                content += f"   - Type: {file_info['content_type']}\n"
                content += f"   - Size: {size_kb:.1f} KB\n\n"

        # Participant summary
        content += "---\n\n## Participant Summary\n\n"

        # Count messages per participant
        participant_counts = {}
        for room_data in rooms_data.values():
            for msg in room_data["messages"]:
                name = msg["creator_name"]
                participant_counts[name] = participant_counts.get(name, 0) + 1

        # Sort by message count
        sorted_participants = sorted(participant_counts.items(), key=lambda x: x[1], reverse=True)

        if sorted_participants:
            most_active = sorted_participants[0]
            content += f"- **Most Active:** {most_active[0]} ({most_active[1]} messages)\n"

        content += f"- **Total Participants:** {len(all_participants)} user(s)\n"
        content += "\n**Activity Breakdown:**\n\n"
        for name, count in sorted_participants:
            content += f"- {name}: {count} message(s)\n"

        # Footer
        content += f"\n---\n\n"
        content += f"**Tags:** #daily-briefing #{date_str}\n"
        content += f"**Category:** briefings\n"
        content += f"**Generated by:** Campfire AI Bot\n"

        return content

    def search_briefings(
        self,
        query: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search historical briefings by date range or keywords.

        Args:
            query: Optional search keywords
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            max_results: Maximum results to return (default: 5)

        Returns:
            List of briefing dicts with keys: path, date, excerpt, message_count
        """
        briefings_dir = self.knowledge_base_dir / "briefings"

        if not briefings_dir.exists():
            return []

        results = []

        # Search all briefing markdown files
        for md_file in briefings_dir.rglob("daily-briefing-*.md"):
            try:
                # Extract date from filename
                filename = md_file.name
                if filename.startswith("daily-briefing-") and filename.endswith(".md"):
                    date_str = filename.replace("daily-briefing-", "").replace(".md", "")

                    # Filter by date range
                    if start_date and date_str < start_date:
                        continue
                    if end_date and date_str > end_date:
                        continue

                    content = md_file.read_text(encoding="utf-8")

                    # Filter by query keyword
                    if query and query.lower() not in content.lower():
                        continue

                    # Extract metadata
                    message_count = 0
                    file_count = 0
                    rooms_count = 0

                    for line in content.split("\n")[:20]:
                        if "Total Messages:" in line:
                            try:
                                message_count = int(line.split(":")[1].strip().split()[0])
                            except:
                                pass
                        if "Files Uploaded:" in line:
                            try:
                                file_count = int(line.split(":")[1].strip().split()[0])
                            except:
                                pass
                        if "Rooms Covered:" in line:
                            try:
                                rooms_count = int(line.split(":")[1].strip().split()[0])
                            except:
                                pass

                    # Extract excerpt from executive summary
                    excerpt = ""
                    in_summary = False
                    for line in content.split("\n"):
                        if "## Executive Summary" in line:
                            in_summary = True
                            continue
                        if in_summary:
                            if line.startswith("##") or line.startswith("---"):
                                break
                            if line.strip():
                                excerpt = line.strip()
                                break

                    # Get relative path
                    relative_path = md_file.relative_to(self.knowledge_base_dir)

                    results.append({
                        "path": str(relative_path),
                        "date": date_str,
                        "excerpt": excerpt,
                        "message_count": message_count,
                        "file_count": file_count,
                        "rooms_count": rooms_count
                    })

            except Exception:
                continue

        # Sort by date (most recent first)
        results.sort(key=lambda x: x["date"], reverse=True)

        return results[:max_results]

    # ====================
    # Personal Productivity Methods
    # ====================

    def manage_personal_tasks(
        self,
        user_id: int,
        action: str,
        task_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Manage personal tasks (create, list, complete, delete).

        Args:
            user_id: User ID
            action: Action to perform ('create', 'list', 'complete', 'delete')
            task_data: Task data dict with keys:
                - For create: {title, description, priority, due_date}
                - For complete/delete: {task_id}
                - For list: {status} ('pending', 'completed', 'all')

        Returns:
            Dict with keys: success, message, tasks (for list), task (for create)
        """
        # Ensure user directory exists
        user_dir = self.context_dir / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)

        tasks_file = user_dir / "tasks.json"

        # Load existing tasks
        if tasks_file.exists():
            with open(tasks_file, 'r') as f:
                all_tasks = json.load(f)
        else:
            all_tasks = {
                "tasks": [],
                "next_id": 1
            }

        if action == "create":
            # Create new task
            if not task_data or "title" not in task_data:
                return {
                    "success": False,
                    "message": "Task title is required"
                }

            task = {
                "id": all_tasks["next_id"],
                "title": task_data["title"],
                "description": task_data.get("description", ""),
                "priority": task_data.get("priority", "medium"),
                "due_date": task_data.get("due_date", None),
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "completed_at": None
            }

            all_tasks["tasks"].append(task)
            all_tasks["next_id"] += 1

            # Save
            with open(tasks_file, 'w') as f:
                json.dump(all_tasks, f, indent=2)

            return {
                "success": True,
                "message": f"Task #{task['id']} created successfully",
                "task": task
            }

        elif action == "list":
            # List tasks
            status_filter = task_data.get("status", "pending") if task_data else "pending"

            if status_filter == "all":
                filtered_tasks = all_tasks["tasks"]
            else:
                filtered_tasks = [t for t in all_tasks["tasks"] if t["status"] == status_filter]

            return {
                "success": True,
                "message": f"Found {len(filtered_tasks)} task(s)",
                "tasks": filtered_tasks
            }

        elif action == "complete":
            # Complete task
            if not task_data or "task_id" not in task_data:
                return {
                    "success": False,
                    "message": "Task ID is required"
                }

            task_id = task_data["task_id"]
            task_found = False

            for task in all_tasks["tasks"]:
                if task["id"] == task_id:
                    task["status"] = "completed"
                    task["completed_at"] = datetime.now().isoformat()
                    task_found = True
                    break

            if not task_found:
                return {
                    "success": False,
                    "message": f"Task #{task_id} not found"
                }

            # Save
            with open(tasks_file, 'w') as f:
                json.dump(all_tasks, f, indent=2)

            return {
                "success": True,
                "message": f"Task #{task_id} marked as completed"
            }

        elif action == "delete":
            # Delete task
            if not task_data or "task_id" not in task_data:
                return {
                    "success": False,
                    "message": "Task ID is required"
                }

            task_id = task_data["task_id"]
            initial_count = len(all_tasks["tasks"])
            all_tasks["tasks"] = [t for t in all_tasks["tasks"] if t["id"] != task_id]

            if len(all_tasks["tasks"]) == initial_count:
                return {
                    "success": False,
                    "message": f"Task #{task_id} not found"
                }

            # Save
            with open(tasks_file, 'w') as f:
                json.dump(all_tasks, f, indent=2)

            return {
                "success": True,
                "message": f"Task #{task_id} deleted successfully"
            }

        else:
            return {
                "success": False,
                "message": f"Unknown action: {action}. Use 'create', 'list', 'complete', or 'delete'"
            }

    def set_reminder(
        self,
        user_id: int,
        reminder_text: str,
        remind_at: str
    ) -> Dict[str, Any]:
        """
        Set a personal reminder.

        Args:
            user_id: User ID
            reminder_text: Reminder content
            remind_at: When to remind (YYYY-MM-DD HH:MM or natural language)

        Returns:
            Dict with keys: success, message, reminder
        """
        # Ensure user directory exists
        user_dir = self.context_dir / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)

        reminders_file = user_dir / "reminders.json"

        # Load existing reminders
        if reminders_file.exists():
            with open(reminders_file, 'r') as f:
                all_reminders = json.load(f)
        else:
            all_reminders = {
                "reminders": [],
                "next_id": 1
            }

        # Parse remind_at (basic parsing, can be enhanced)
        # For now, store as-is and note it's a placeholder for actual scheduling
        reminder = {
            "id": all_reminders["next_id"],
            "text": reminder_text,
            "remind_at": remind_at,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "triggered_at": None
        }

        all_reminders["reminders"].append(reminder)
        all_reminders["next_id"] += 1

        # Save
        with open(reminders_file, 'w') as f:
            json.dump(all_reminders, f, indent=2)

        return {
            "success": True,
            "message": f"Reminder #{reminder['id']} set for {remind_at}",
            "reminder": reminder,
            "note": "✅ Reminder will be automatically delivered at the scheduled time (v0.5.1)"
        }

    def save_personal_note(
        self,
        user_id: int,
        title: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Save a personal note.

        Args:
            user_id: User ID
            title: Note title
            content: Note content (supports Markdown)

        Returns:
            Dict with keys: success, message, note_path
        """
        # Ensure user notes directory exists
        user_dir = self.context_dir / f"user_{user_id}"
        notes_dir = user_dir / "notes"
        notes_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        # Clean title for filename
        clean_title = re.sub(r'[^\w\s-]', '', title)
        clean_title = re.sub(r'[-\s]+', '-', clean_title).strip('-')
        filename = f"{timestamp}_{clean_title[:30]}.md"

        note_path = notes_dir / filename

        # Create note content
        note_content = f"""# {title}

**Created:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**User:** user_{user_id}

---

{content}

---

**Tags:** #personal-note #{datetime.now().strftime("%Y-%m")}
"""

        # Save note
        note_path.write_text(note_content, encoding="utf-8")

        relative_path = f"user_{user_id}/notes/{filename}"

        return {
            "success": True,
            "message": f"Note saved successfully",
            "note_path": relative_path,
            "title": title,
            "created_at": datetime.now().isoformat()
        }

    def search_personal_notes(
        self,
        user_id: int,
        query: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search user's personal notes.

        Args:
            user_id: User ID
            query: Optional search keywords (if None, list all notes)
            max_results: Maximum results to return

        Returns:
            List of note dicts with keys: path, title, excerpt, created_at
        """
        user_dir = self.context_dir / f"user_{user_id}"
        notes_dir = user_dir / "notes"

        if not notes_dir.exists():
            return []

        results = []

        for note_file in notes_dir.glob("*.md"):
            try:
                content = note_file.read_text(encoding="utf-8")

                # If query provided, filter by keyword
                if query and query.lower() not in content.lower():
                    continue

                # Extract title (first H1 heading)
                title = "Untitled"
                for line in content.split("\n"):
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break

                # Extract created date
                created_at = None
                for line in content.split("\n")[:10]:
                    if "**Created:**" in line:
                        created_at = line.split("**Created:**")[1].strip()
                        break

                # Extract excerpt (first paragraph after metadata)
                lines = content.split("\n")
                excerpt = ""
                in_content = False
                for line in lines:
                    if line.startswith("---") and in_content:
                        break
                    if in_content and line.strip() and not line.startswith("#") and not line.startswith("**"):
                        excerpt = line.strip()[:200]
                        break
                    if line.startswith("---"):
                        in_content = True

                results.append({
                    "path": f"user_{user_id}/notes/{note_file.name}",
                    "title": title,
                    "excerpt": excerpt,
                    "created_at": created_at,
                    "filename": note_file.name
                })

            except Exception:
                continue

        # Sort by creation time (most recent first)
        results.sort(key=lambda x: x["filename"], reverse=True)

        return results[:max_results]

    def __del__(self):
        """Close database connection on cleanup"""
        if self._db_conn:
            self._db_conn.close()
