"""
Tests for Campfire tools
Following TDD: Write tests BEFORE implementation
"""

import pytest
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from src.tools.campfire_tools import CampfireTools


@pytest.fixture
def db_path():
    """Return path to test database"""
    return "./tests/fixtures/test.db"


@pytest.fixture
def tools(db_path, tmp_path):
    """Create CampfireTools instance with test database and temp context dir"""
    return CampfireTools(
        db_path=db_path,
        context_dir=str(tmp_path / "user_contexts")
    )


@pytest.fixture
def sample_user_context():
    """Sample user context data for testing"""
    return {
        "user_id": 1,
        "user_name": "WU HENG",
        "preferences": {
            "language": "en",
            "timezone": "Asia/Singapore"
        },
        "expertise": ["finance", "data analysis"],
        "conversation_memory": [
            "User prefers detailed financial reports",
            "Interested in Q3 revenue trends"
        ],
        "last_updated": datetime.now().isoformat()
    }


class TestSearchConversations:
    """Test search_conversations functionality"""

    def test_search_basic(self, tools):
        """Should find messages containing search term"""
        results = tools.search_conversations(
            query="revenue",
            limit=10
        )

        assert isinstance(results, list)
        assert len(results) > 0

        # Should contain messages about revenue from Finance Team room
        revenue_messages = [r for r in results if "revenue" in r["body"].lower()]
        assert len(revenue_messages) > 0

    def test_search_with_room_filter(self, tools):
        """Should filter by room_id"""
        # Search in Finance Team room (room_id=2)
        results = tools.search_conversations(
            query="revenue",
            room_id=2,
            limit=10
        )

        assert all(r["room_id"] == 2 for r in results)

    def test_search_limit(self, tools):
        """Should respect limit parameter"""
        results = tools.search_conversations(
            query="",  # Empty query returns all
            limit=3
        )

        assert len(results) <= 3

    def test_search_returns_full_message_info(self, tools):
        """Should return complete message information"""
        results = tools.search_conversations(
            query="revenue",
            limit=1
        )

        assert len(results) > 0
        msg = results[0]

        # Check required fields
        assert "message_id" in msg
        assert "room_id" in msg
        assert "room_name" in msg
        assert "creator_name" in msg
        assert "body" in msg
        assert "created_at" in msg

    def test_search_strips_html(self, tools):
        """Should strip HTML tags from message bodies"""
        results = tools.search_conversations(
            query="revenue",
            limit=1
        )

        assert len(results) > 0
        body = results[0]["body"]

        # Should not contain HTML tags
        assert "<p>" not in body
        assert "</p>" not in body
        assert "<" not in body or ">" not in body

    def test_search_empty_query(self, tools):
        """Empty query should return recent messages"""
        results = tools.search_conversations(
            query="",
            limit=5
        )

        assert len(results) > 0
        assert len(results) <= 5

    def test_search_no_results(self, tools):
        """Should return empty list when no matches"""
        results = tools.search_conversations(
            query="xyznonexistentterm123",
            limit=10
        )

        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_case_insensitive(self, tools):
        """Search should be case-insensitive"""
        results_lower = tools.search_conversations(query="revenue", limit=5)
        results_upper = tools.search_conversations(query="REVENUE", limit=5)
        results_mixed = tools.search_conversations(query="Revenue", limit=5)

        assert len(results_lower) == len(results_upper) == len(results_mixed)


class TestGetUserContext:
    """Test get_user_context functionality"""

    def test_get_user_from_database(self, tools):
        """Should retrieve basic user info from database"""
        context = tools.get_user_context(user_id=1)

        assert context["user_id"] == 1
        assert context["user_name"] == "WU HENG"
        assert context["email"] == "heng.woo@gmail.com"
        assert "rooms" in context
        assert isinstance(context["rooms"], list)

    def test_get_user_rooms(self, tools):
        """Should include user's room memberships"""
        context = tools.get_user_context(user_id=1)

        # WU HENG is in rooms 1, 2, 4
        room_ids = [r["room_id"] for r in context["rooms"]]
        assert 1 in room_ids  # All Talk
        assert 2 in room_ids  # Finance Team
        assert 4 in room_ids  # Direct Message

    def test_get_saved_context(self, tools, sample_user_context, tmp_path):
        """Should load saved context from JSON file"""
        # Save context file
        context_dir = tmp_path / "user_contexts"
        context_dir.mkdir(exist_ok=True)

        context_file = context_dir / "user_1.json"
        with open(context_file, "w") as f:
            json.dump(sample_user_context, f)

        # Get context
        context = tools.get_user_context(user_id=1)

        # Should include saved preferences
        assert "preferences" in context
        assert context["preferences"]["language"] == "en"
        assert context["preferences"]["timezone"] == "Asia/Singapore"

        # Should include expertise
        assert "expertise" in context
        assert "finance" in context["expertise"]

    def test_get_user_nonexistent(self, tools):
        """Should handle non-existent user gracefully"""
        context = tools.get_user_context(user_id=99999)

        assert context["user_id"] == 99999
        assert context["user_name"] is None
        assert context["email"] is None
        assert context["rooms"] == []

    def test_get_user_merges_db_and_saved(self, tools, sample_user_context, tmp_path):
        """Should merge database info with saved context"""
        # Save context file
        context_dir = tmp_path / "user_contexts"
        context_dir.mkdir(exist_ok=True)

        context_file = context_dir / "user_1.json"
        with open(context_file, "w") as f:
            json.dump(sample_user_context, f)

        # Get context
        context = tools.get_user_context(user_id=1)

        # Should have DB info
        assert context["user_name"] == "WU HENG"
        assert context["email"] == "heng.woo@gmail.com"

        # Should have saved context
        assert "preferences" in context
        assert "expertise" in context


class TestSaveUserContext:
    """Test save_user_context functionality"""

    def test_save_preferences(self, tools):
        """Should save user preferences"""
        tools.save_user_context(
            user_id=1,
            preferences={"language": "zh", "timezone": "Asia/Shanghai"}
        )

        # Verify saved
        context = tools.get_user_context(user_id=1)
        assert context["preferences"]["language"] == "zh"
        assert context["preferences"]["timezone"] == "Asia/Shanghai"

    def test_save_expertise(self, tools):
        """Should save user expertise"""
        tools.save_user_context(
            user_id=1,
            expertise=["AI", "Python", "Finance"]
        )

        context = tools.get_user_context(user_id=1)
        assert "AI" in context["expertise"]
        assert "Python" in context["expertise"]
        assert "Finance" in context["expertise"]

    def test_save_conversation_memory(self, tools):
        """Should save conversation memory"""
        memory_item = "User wants quarterly reports every Monday"

        tools.save_user_context(
            user_id=1,
            conversation_memory=[memory_item]
        )

        context = tools.get_user_context(user_id=1)
        assert memory_item in context["conversation_memory"]

    def test_save_updates_existing(self, tools):
        """Should update existing context without losing data"""
        # First save
        tools.save_user_context(
            user_id=1,
            preferences={"language": "en"}
        )

        # Second save with different field
        tools.save_user_context(
            user_id=1,
            expertise=["finance"]
        )

        # Both should be present
        context = tools.get_user_context(user_id=1)
        assert context["preferences"]["language"] == "en"
        assert "finance" in context["expertise"]

    def test_save_creates_directory(self, tools, tmp_path):
        """Should create context directory if not exists"""
        new_context_dir = tmp_path / "new_contexts"

        tools_new = CampfireTools(
            db_path="./tests/fixtures/test.db",
            context_dir=str(new_context_dir)
        )

        tools_new.save_user_context(
            user_id=1,
            preferences={"test": "value"}
        )

        assert new_context_dir.exists()
        assert (new_context_dir / "user_1.json").exists()

    def test_save_timestamp(self, tools):
        """Should update last_updated timestamp"""
        before = datetime.now()

        tools.save_user_context(
            user_id=1,
            preferences={"test": "value"}
        )

        context = tools.get_user_context(user_id=1)
        updated_at = datetime.fromisoformat(context["last_updated"])

        assert updated_at >= before


class TestHelperMethods:
    """Test helper methods"""

    def test_strip_html_tags(self, tools):
        """Should strip HTML tags from text"""
        html = "<p>This is <strong>bold</strong> text</p>"
        result = tools._strip_html(html)

        assert "<p>" not in result
        assert "<strong>" not in result
        assert "This is bold text" in result

    def test_strip_html_with_newlines(self, tools):
        """Should handle HTML with newlines"""
        html = "<p>Line 1</p>\n<p>Line 2</p>"
        result = tools._strip_html(html)

        assert "Line 1" in result
        assert "Line 2" in result
        assert "<p>" not in result

    def test_strip_html_empty(self, tools):
        """Should handle empty string"""
        result = tools._strip_html("")
        assert result == ""

    def test_strip_html_none(self, tools):
        """Should handle None gracefully"""
        result = tools._strip_html(None)
        assert result == ""


class TestDatabaseConnection:
    """Test database connection handling"""

    def test_readonly_connection(self, tools):
        """Database should be opened in read-only mode"""
        # Try to write - should fail or be ignored
        with pytest.raises(sqlite3.OperationalError):
            conn = tools._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name) VALUES ('test')")
            conn.commit()

    def test_connection_reuse(self, tools):
        """Should reuse database connection"""
        conn1 = tools._get_db_connection()
        conn2 = tools._get_db_connection()

        # Should be same connection object
        assert conn1 is conn2

    def test_database_path_validation(self, tmp_path):
        """Should handle invalid database path"""
        invalid_path = str(tmp_path / "nonexistent.db")

        with pytest.raises(Exception):
            tools = CampfireTools(db_path=invalid_path)
            tools.search_conversations(query="test")
