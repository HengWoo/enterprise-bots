# Phase 1 MVP Implementation Plan (TDD + Containerized)
## Campfire AI Bot with Claude Agent SDK

**Version:** 2.0 (Revised with TDD + Local Development)
**Date:** October 6, 2025
**Approach:** Test-Driven Development + Docker Containerization
**Timeline:** Week 1 (6-8 hours including tests)

---

## Table of Contents

1. [Philosophy: Why TDD + Containers](#philosophy)
2. [Development Environment Setup](#development-environment-setup)
3. [TDD Workflow](#tdd-workflow)
4. [Implementation Steps](#implementation-steps)
5. [Testing Strategy](#testing-strategy)
6. [Containerization](#containerization)
7. [Deployment](#deployment)
8. [Success Criteria](#success-criteria)

---

## Philosophy

### Why Test-Driven Development?

**Benefits:**
- ✅ **Better Design** - Writing tests first forces you to think about interfaces
- ✅ **Confidence** - Know your code works before deployment
- ✅ **Refactoring Safety** - Tests catch regressions immediately
- ✅ **Documentation** - Tests show how code should be used
- ✅ **Faster Debugging** - Failures are caught in tests, not production

**TDD Cycle:**
```
🔴 RED: Write a failing test
    ↓
🟢 GREEN: Write minimal code to pass
    ↓
🔵 REFACTOR: Clean up code
    ↓
REPEAT
```

### Why Local Development + Containers?

**Problems with Console Development:**
- ❌ No IDE features (autocomplete, linting, debugging)
- ❌ No version control
- ❌ Difficult to test
- ❌ Can't work offline
- ❌ Painful editing experience

**Benefits of Local + Docker:**
- ✅ **Proper IDE** - VS Code, PyCharm, etc.
- ✅ **Git Version Control** - Track all changes
- ✅ **Local Testing** - Fast iteration without deploying
- ✅ **Reproducible** - Same environment locally and in production
- ✅ **Isolated** - Container = clean environment
- ✅ **Easy Deployment** - Build once, deploy anywhere

---

## Development Environment Setup

### Prerequisites

**On Your Mac:**
- ✅ Python 3.10+ (check: `python3 --version`)
- ✅ Docker Desktop (install from docker.com if needed)
- ✅ Git (already have)
- ✅ VS Code or preferred IDE
- ✅ Campfire source code at `/Users/heng/Development/campfire/`

### Initial Setup (15 minutes)

**Step 1: Create Project Structure**
```bash
cd /Users/heng/Development/campfire

# Create ai-bot directory
mkdir -p ai-bot/{src/tools,tests/fixtures}

cd ai-bot
```

**Step 2: Initialize Git (if not already in repo)**
```bash
# Check if already in git repo
git status

# If not, initialize
git init

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
*.local

# Docker
*.tar

# Logs
*.log
EOF
```

**Step 3: Create Python Virtual Environment**
```bash
cd /Users/heng/Development/campfire/ai-bot

# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate

# Verify
which python  # Should show ./venv/bin/python
```

**Step 4: Create Requirements Files**

`requirements.txt` (production dependencies):
```bash
cat > requirements.txt << 'EOF'
# Web framework
flask==3.0.0
gunicorn==21.2.0

# Claude Agent SDK
claude-agent-sdk==1.0.0

# HTTP client
requests==2.31.0

# Utilities
python-dotenv==1.0.0
EOF
```

`requirements-dev.txt` (development/testing dependencies):
```bash
cat > requirements-dev.txt << 'EOF'
# Include production requirements
-r requirements.txt

# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-asyncio==0.21.1

# Code quality
black==23.11.0
flake8==6.1.0
mypy==1.7.1

# Development utilities
ipython==8.18.0
ipdb==0.13.13
EOF
```

**Step 5: Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements-dev.txt
```

**Step 6: Create .env.example (template)**
```bash
cat > .env.example << 'EOF'
# Anthropic API Configuration
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# Campfire Configuration
CAMPFIRE_URL=https://chat.smartice.ai
BOT_KEY=2-CsheovnLtzjM
CAMPFIRE_DB_PATH=/var/once/campfire/db/production.sqlite3

# For local development, use local test database:
# CAMPFIRE_DB_PATH=./tests/fixtures/campfire_test.db

# Bot Personality
SYSTEM_PROMPT=You are a professional financial analyst AI assistant.

# Server Configuration
FLASK_PORT=5000
FLASK_HOST=0.0.0.0
LOG_LEVEL=DEBUG
EOF
```

**Step 7: Create Actual .env (copy and edit)**
```bash
cp .env.example .env
nano .env  # Add your actual ANTHROPIC_API_KEY
```

**Step 8: Configure Pytest**
```bash
cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --cov=src
    --cov-report=html
    --cov-report=term-missing
EOF
```

---

## TDD Workflow

### Red-Green-Refactor Cycle

**Example: Implementing `search_conversations` tool**

**🔴 RED - Write Failing Test First:**
```python
# tests/test_tools.py
def test_search_conversations_returns_formatted_text():
    """Test that search returns formatted conversation history"""
    tools = CampfireTools(db_path='./tests/fixtures/test.db')

    result = tools.search_conversations(
        query="revenue",
        room_id=1,
        limit=5
    )

    assert "Recent conversation:" in result
    assert "User:" in result  # Should have user names
```

Run test: `pytest tests/test_tools.py::test_search_conversations_returns_formatted_text`
**Result:** ❌ FAIL (function doesn't exist yet)

**🟢 GREEN - Write Minimal Code to Pass:**
```python
# src/tools/campfire_tools.py
def search_conversations(self, query, room_id, limit=5):
    # Minimal implementation to pass test
    return "Recent conversation:\nUser: test message"
```

Run test: `pytest tests/test_tools.py::test_search_conversations_returns_formatted_text`
**Result:** ✅ PASS

**🔵 REFACTOR - Improve Code:**
```python
# src/tools/campfire_tools.py
def search_conversations(self, query, room_id, limit=5):
    # Full implementation with database query
    conn = sqlite3.connect(self.db_path)
    # ... proper implementation
    return formatted_result
```

Run test: `pytest tests/test_tools.py::test_search_conversations_returns_formatted_text`
**Result:** ✅ PASS (still passes after refactor)

**REPEAT** for each feature!

---

## Implementation Steps

### Phase 1A: Setup Test Database (30 minutes)

**Goal:** Create minimal test database with sample data

**🔴 Test First:**
```python
# tests/test_database.py
def test_database_has_users_table():
    conn = sqlite3.connect('./tests/fixtures/test.db')
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    assert cursor.fetchone() is not None
```

**🟢 Implementation:**
```python
# tests/fixtures/setup_test_db.py
import sqlite3

def create_test_database():
    """Create minimal test database based on Campfire schema"""

    conn = sqlite3.connect('./tests/fixtures/test.db')

    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email_address TEXT,
            role INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1
        )
    ''')

    # Rooms table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT NOT NULL,
            creator_id INTEGER NOT NULL
        )
    ''')

    # Messages table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            room_id INTEGER NOT NULL,
            creator_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            client_message_id TEXT NOT NULL
        )
    ''')

    # Action Text Rich Texts table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS action_text_rich_texts (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            body TEXT,
            record_type TEXT NOT NULL,
            record_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    # Insert test data
    conn.execute("INSERT INTO users (id, name, email_address) VALUES (1, 'Test User', 'test@example.com')")
    conn.execute("INSERT INTO users (id, name, email_address) VALUES (2, 'Bot User', 'bot@example.com')")

    conn.execute("INSERT INTO rooms (id, name, type, creator_id) VALUES (1, 'Test Room', 'Rooms::Open', 1)")

    conn.execute("""
        INSERT INTO messages (id, room_id, creator_id, created_at, updated_at, client_message_id)
        VALUES (1, 1, 1, '2025-10-01 10:00:00', '2025-10-01 10:00:00', 'msg-001')
    """)

    conn.execute("""
        INSERT INTO action_text_rich_texts (id, name, body, record_type, record_id, created_at, updated_at)
        VALUES (1, 'body', '<p>Hello, this is a test message about revenue</p>', 'Message', 1, '2025-10-01 10:00:00', '2025-10-01 10:00:00')
    """)

    conn.commit()
    conn.close()
    print("✅ Test database created at ./tests/fixtures/test.db")

if __name__ == '__main__':
    create_test_database()
```

**Run:**
```bash
python tests/fixtures/setup_test_db.py
pytest tests/test_database.py
```

---

### Phase 1B: Implement Tools with TDD (2 hours)

**File: `tests/test_tools.py`**

Write ALL tests first, then implement:

```python
"""
Tests for Campfire tools
Following TDD: Write tests BEFORE implementation
"""

import pytest
import sqlite3
import json
import os
from src.tools.campfire_tools import CampfireTools


@pytest.fixture
def tools():
    """Fixture providing CampfireTools instance with test database"""
    return CampfireTools(
        db_path='./tests/fixtures/test.db',
        knowledge_base_path='./tests/fixtures/knowledge_base'
    )


@pytest.fixture
def setup_knowledge_base(tmp_path):
    """Create temporary knowledge base directory"""
    kb_path = tmp_path / "knowledge_base"
    kb_path.mkdir()
    (kb_path / "user_contexts").mkdir()
    return str(kb_path)


class TestSearchConversations:
    """Tests for search_conversations tool"""

    def test_search_returns_string(self, tools):
        """Test that search returns a string"""
        result = tools.search_conversations("", room_id=1)
        assert isinstance(result, str)

    def test_search_includes_user_names(self, tools):
        """Test that search results include user names"""
        result = tools.search_conversations("", room_id=1, limit=5)
        assert "Test User" in result or "Recent conversation" in result

    def test_search_respects_limit(self, tools):
        """Test that limit parameter is respected"""
        result = tools.search_conversations("", room_id=1, limit=1)
        # Should only have 1 message
        lines = [line for line in result.split('\n') if line.strip()]
        assert len(lines) <= 3  # Header + 1 message

    def test_search_filters_by_room(self, tools):
        """Test that search only returns messages from specified room"""
        result = tools.search_conversations("", room_id=999)
        assert "No conversation history" in result or result == ""

    def test_search_handles_empty_database(self, tools):
        """Test graceful handling of empty results"""
        result = tools.search_conversations("nonexistent", room_id=1)
        assert isinstance(result, str)  # Should not crash

    def test_search_concise_format(self, tools):
        """Test concise format returns brief output"""
        result = tools.search_conversations("", room_id=1, format="concise")
        assert "Recent conversation" in result
        # Concise should not include timestamps
        assert "[2025-" not in result

    def test_search_detailed_format(self, tools):
        """Test detailed format includes timestamps"""
        result = tools.search_conversations("", room_id=1, format="detailed")
        assert "Conversation History" in result or "Recent" in result


class TestGetUserContext:
    """Tests for get_user_context tool"""

    def test_returns_string(self, tools):
        """Test that user context returns a string"""
        result = tools.get_user_context(user_id=1)
        assert isinstance(result, str)

    def test_includes_user_name(self, tools):
        """Test that result includes user name"""
        result = tools.get_user_context(user_id=1)
        assert "User:" in result

    def test_loads_saved_context(self, setup_knowledge_base, tools):
        """Test loading previously saved user context"""
        # Create a saved context file
        context_file = os.path.join(
            setup_knowledge_base,
            'user_contexts',
            'user_1.json'
        )
        context_data = {
            'user_id': 1,
            'name': 'Test User',
            'preferences': {'language': 'English'},
            'expertise_areas': ['finance']
        }

        with open(context_file, 'w') as f:
            json.dump(context_data, f)

        tools_with_kb = CampfireTools(
            db_path='./tests/fixtures/test.db',
            knowledge_base_path=setup_knowledge_base
        )

        result = tools_with_kb.get_user_context(user_id=1)

        assert 'Test User' in result
        assert 'Preferences' in result or 'language' in result
        assert 'finance' in result.lower()

    def test_handles_missing_context_gracefully(self, tools):
        """Test behavior when no saved context exists"""
        result = tools.get_user_context(user_id=999)
        assert isinstance(result, str)
        # Should fallback to basic user info from database

    def test_handles_database_error(self, tools):
        """Test graceful error handling"""
        # Use invalid database path
        bad_tools = CampfireTools(
            db_path='/nonexistent/path.db',
            knowledge_base_path='./tests/fixtures/knowledge_base'
        )
        result = bad_tools.get_user_context(user_id=1)
        assert "Error" in result or "not found" in result.lower()


class TestSaveUserContext:
    """Tests for save_user_context tool"""

    def test_saves_preference(self, setup_knowledge_base):
        """Test saving a user preference"""
        tools = CampfireTools(
            db_path='./tests/fixtures/test.db',
            knowledge_base_path=setup_knowledge_base
        )

        result = tools.save_user_context(
            user_id=1,
            key='preference',
            value='language: Chinese'
        )

        assert 'Saved' in result

        # Verify file was created
        context_file = os.path.join(
            setup_knowledge_base,
            'user_contexts',
            'user_1.json'
        )
        assert os.path.exists(context_file)

        # Verify content
        with open(context_file) as f:
            data = json.load(f)

        assert data['preferences']['language'] == 'Chinese'

    def test_saves_expertise(self, setup_knowledge_base):
        """Test saving user expertise"""
        tools = CampfireTools(
            db_path='./tests/fixtures/test.db',
            knowledge_base_path=setup_knowledge_base
        )

        tools.save_user_context(user_id=1, key='expertise', value='data analysis')

        # Load and verify
        context_file = os.path.join(
            setup_knowledge_base,
            'user_contexts',
            'user_1.json'
        )

        with open(context_file) as f:
            data = json.load(f)

        assert 'data analysis' in data['expertise_areas']

    def test_saves_memory(self, setup_knowledge_base):
        """Test saving conversation memory"""
        tools = CampfireTools(
            db_path='./tests/fixtures/test.db',
            knowledge_base_path=setup_knowledge_base
        )

        tools.save_user_context(
            user_id=1,
            key='memory',
            value='Discussed Q3 revenue trends'
        )

        # Load and verify
        context_file = os.path.join(
            setup_knowledge_base,
            'user_contexts',
            'user_1.json'
        )

        with open(context_file) as f:
            data = json.load(f)

        assert len(data['conversation_memory']) > 0
        assert 'Q3 revenue' in data['conversation_memory'][0]['summary']

    def test_updates_existing_context(self, setup_knowledge_base):
        """Test updating existing user context"""
        tools = CampfireTools(
            db_path='./tests/fixtures/test.db',
            knowledge_base_path=setup_knowledge_base
        )

        # Save first preference
        tools.save_user_context(user_id=1, key='preference', value='tone: professional')

        # Save second preference
        tools.save_user_context(user_id=1, key='preference', value='format: concise')

        # Load and verify both are saved
        context_file = os.path.join(
            setup_knowledge_base,
            'user_contexts',
            'user_1.json'
        )

        with open(context_file) as f:
            data = json.load(f)

        assert data['preferences']['tone'] == 'professional'
        assert data['preferences']['format'] == 'concise'


class TestHelperMethods:
    """Tests for helper methods"""

    def test_html_to_text_strips_tags(self, tools):
        """Test HTML tag stripping"""
        html = "<p>Hello <strong>world</strong></p>"
        text = tools._html_to_text(html)
        assert text == "Hello world"
        assert '<' not in text

    def test_html_to_text_handles_empty(self, tools):
        """Test handling of empty HTML"""
        assert tools._html_to_text("") == ""
        assert tools._html_to_text(None) == ""

    def test_html_to_text_cleans_whitespace(self, tools):
        """Test whitespace normalization"""
        html = "<p>Hello    \n   world</p>"
        text = tools._html_to_text(html)
        assert text == "Hello world"
```

**Run Tests (They should FAIL):**
```bash
pytest tests/test_tools.py -v
```

**🟢 Now Implement `src/tools/campfire_tools.py` to Make Tests Pass**

(Implementation code is the same as in IMPLEMENTATION_PLAN.md but guided by tests)

**After Implementation:**
```bash
pytest tests/test_tools.py -v --cov=src/tools
```

Should see: ✅ All tests passing with coverage report

---

### Phase 1C: Implement Flask App with TDD (1.5 hours)

**File: `tests/test_app.py`**

```python
"""
Tests for Flask webhook application
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from src.app import app, post_to_campfire


@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for /health endpoint"""

    def test_health_returns_200(self, client):
        """Test health endpoint returns 200"""
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        """Test health endpoint returns JSON"""
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'status' in data

    def test_health_shows_agent_status(self, client):
        """Test health shows agent configuration status"""
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'agent_configured' in data
        assert 'tools_count' in data


class TestRootEndpoint:
    """Tests for / endpoint"""

    def test_root_returns_200(self, client):
        """Test root endpoint returns 200"""
        response = client.get('/')
        assert response.status_code == 200

    def test_root_shows_service_info(self, client):
        """Test root shows service information"""
        response = client.get('/')
        data = json.loads(response.data)
        assert 'service' in data
        assert 'endpoints' in data


class TestWebhookEndpoint:
    """Tests for /webhook endpoint"""

    def test_webhook_rejects_get(self, client):
        """Test webhook only accepts POST"""
        response = client.get('/webhook')
        assert response.status_code == 405  # Method Not Allowed

    @patch('src.app.agent')
    @patch('src.app.post_to_campfire')
    def test_webhook_processes_valid_payload(self, mock_post, mock_agent, client):
        """Test webhook processes valid Campfire payload"""
        # Setup mock agent
        mock_result = Mock()
        mock_result.response = "Test response from AI"
        mock_agent.run = AsyncMock(return_value=mock_result)

        # Valid webhook payload
        payload = {
            'user': {'id': 1, 'name': 'Test User'},
            'room': {'id': 1, 'name': 'Test Room', 'path': '/rooms/1/bot-key/messages'},
            'message': {
                'id': 1,
                'body': {'plain': '@bot help', 'html': '<p>@bot help</p>'},
                'path': '/rooms/1/@1'
            }
        }

        response = client.post(
            '/webhook',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

    def test_webhook_handles_missing_fields(self, client):
        """Test webhook handles incomplete payload gracefully"""
        payload = {'user': {'id': 1}}  # Incomplete

        response = client.post(
            '/webhook',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'

    @patch('src.app.agent')
    @patch('src.app.post_to_campfire')
    def test_webhook_calls_agent_with_context(self, mock_post, mock_agent, client):
        """Test webhook passes context to agent"""
        mock_result = Mock()
        mock_result.response = "Response"
        mock_agent.run = AsyncMock(return_value=mock_result)

        payload = {
            'user': {'id': 1, 'name': 'Test User'},
            'room': {'id': 5, 'name': 'Finance', 'path': '/rooms/5/bot/messages'},
            'message': {'id': 1, 'body': {'plain': 'test', 'html': 'test'}, 'path': '/rooms/5/@1'}
        }

        client.post('/webhook', data=json.dumps(payload), content_type='application/json')

        # Verify agent.run was called with correct context
        mock_agent.run.assert_called_once()
        call_args = mock_agent.run.call_args

        assert call_args.kwargs['message'] == 'test'
        assert call_args.kwargs['context']['user_id'] == 1
        assert call_args.kwargs['context']['room_id'] == 5


class TestCampfirePosting:
    """Tests for posting back to Campfire"""

    @patch('src.app.requests.post')
    def test_post_to_campfire_makes_request(self, mock_post):
        """Test post_to_campfire makes HTTP request"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        post_to_campfire('/rooms/1/bot/messages', 'Test message')

        mock_post.assert_called_once()
        call_args = mock_post.call_args

        assert 'chat.smartice.ai' in call_args.args[0]
        assert call_args.kwargs['data'] == b'Test message'

    @patch('src.app.requests.post')
    def test_post_to_campfire_handles_errors(self, mock_post):
        """Test error handling when posting fails"""
        mock_post.side_effect = Exception("Network error")

        # Should not raise exception
        post_to_campfire('/rooms/1/bot/messages', 'Test')
```

**Run Tests (FAIL):**
```bash
pytest tests/test_app.py -v
```

**🟢 Implement `src/app.py` to Pass Tests**

(Same code as before, but now guided by tests)

**After Implementation:**
```bash
pytest tests/test_app.py -v --cov=src
```

---

### Phase 1D: Integration Tests (45 minutes)

**File: `tests/test_integration.py`**

```python
"""
Integration tests - test full workflow
"""

import pytest
import json
import sqlite3
from unittest.mock import patch, Mock, AsyncMock
from src.app import app
from src.tools.campfire_tools import CampfireTools


@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def populated_db(tmp_path):
    """Create a populated test database"""
    db_path = tmp_path / "test_integration.db"

    conn = sqlite3.connect(str(db_path))

    # Create tables and insert test data
    # (Reuse setup_test_db.py logic)

    conn.close()
    return str(db_path)


class TestFullWorkflow:
    """Test complete workflow from webhook to response"""

    @patch('src.app.agent')
    @patch('src.app.post_to_campfire')
    def test_complete_mention_workflow(self, mock_post, mock_agent, client):
        """Test: User mentions bot → Agent processes → Response posted"""

        # Setup mock agent
        mock_result = Mock()
        mock_result.response = "Based on the conversation, revenue is up 12%."
        mock_agent.run = AsyncMock(return_value=mock_result)

        # Simulate Campfire webhook
        payload = {
            'user': {'id': 1, 'name': 'WU HENG'},
            'room': {'id': 1, 'name': 'Finance Team', 'path': '/rooms/1/2-CsheovnLtzjM/messages'},
            'message': {
                'id': 42,
                'body': {
                    'plain': '@财务分析师 What were we discussing about revenue?',
                    'html': '<p>@财务分析师 What were we discussing about revenue?</p>'
                },
                'path': '/rooms/1/@42'
            }
        }

        # Send webhook
        response = client.post(
            '/webhook',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Verify success
        assert response.status_code == 200

        # Verify agent was called
        assert mock_agent.run.called

        # Verify response was posted to Campfire
        assert mock_post.called
        assert 'revenue is up 12%' in mock_post.call_args.args[1]
```

---

## Testing Strategy

### Test Coverage Goals

- **Unit Tests:** 80%+ coverage of `src/tools/`
- **Integration Tests:** All critical paths
- **End-to-End:** Manual testing in production

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/test_tools.py

# Specific test
pytest tests/test_tools.py::TestSearchConversations::test_search_returns_string

# Watch mode (re-run on file changes)
pytest-watch
```

### Test Organization

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── fixtures/
│   ├── test.db              # Test database
│   ├── setup_test_db.py     # Database creation script
│   └── knowledge_base/      # Test KB directory
├── test_tools.py            # Tool unit tests
├── test_app.py              # Flask app tests
└── test_integration.py      # Integration tests
```

---

## Containerization

### Dockerfile

Create `Dockerfile`:

```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create directories for runtime data
RUN mkdir -p /data/user_contexts /data/logs

# Environment variables (override at runtime)
ENV CAMPFIRE_DB_PATH=/campfire/db/production.sqlite3
ENV FLASK_PORT=5000
ENV FLASK_HOST=0.0.0.0

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Run with gunicorn
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "--timeout", "120", "src.app:app"]
```

### docker-compose.yml (Local Testing)

```yaml
version: '3.8'

services:
  ai-bot:
    build: .
    ports:
      - "5000:5000"
    volumes:
      # Mount local Campfire database (read-only)
      - ../db:/campfire/db:ro
      # Mount knowledge base (read-write)
      - ./data:/data
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - CAMPFIRE_URL=${CAMPFIRE_URL}
      - BOT_KEY=${BOT_KEY}
      - CAMPFIRE_DB_PATH=/campfire/db/production.sqlite3
      - LOG_LEVEL=DEBUG
    env_file:
      - .env
```

### .dockerignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Testing
tests/
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp

# Git
.git/
.gitignore

# Documentation
*.md
!README.md

# Development files
docker-compose.yml
requirements-dev.txt
```

### Building and Testing Locally

```bash
# Build Docker image
docker build -t campfire-ai-bot:latest .

# Run locally (without compose)
docker run --rm \
  -p 5000:5000 \
  -v /var/once/campfire/db:/campfire/db:ro \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  campfire-ai-bot:latest

# Or use docker-compose
docker-compose up

# Test health endpoint
curl http://localhost:5000/health
```

---

## Deployment

### Option 1: Deploy Built Image

**On Your Mac:**
```bash
# Build image
docker build -t campfire-ai-bot:latest .

# Save image to tar
docker save campfire-ai-bot:latest > campfire-ai-bot.tar

# Transfer to server
scp campfire-ai-bot.tar root@128.199.175.50:/root/
```

**On Server (DigitalOcean Console):**
```bash
# Load image
docker load < /root/campfire-ai-bot.tar

# Stop existing service (if any)
systemctl stop campfire-ai-bot

# Run container
docker run -d \
  --name campfire-ai-bot \
  --restart always \
  -p 5000:5000 \
  -v /var/once/campfire/db:/campfire/db:ro \
  -v /root/ai-knowledge:/data \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -e CAMPFIRE_URL=https://chat.smartice.ai \
  -e BOT_KEY=2-CsheovnLtzjM \
  campfire-ai-bot:latest

# Check logs
docker logs -f campfire-ai-bot
```

### Option 2: Build on Server

**Transfer source code:**
```bash
# From your Mac
cd /Users/heng/Development/campfire/ai-bot
tar czf ai-bot.tar.gz src/ Dockerfile requirements.txt
scp ai-bot.tar.gz root@128.199.175.50:/root/
```

**On server:**
```bash
cd /root
tar xzf ai-bot.tar.gz
cd ai-bot

# Create .env file
cat > .env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
CAMPFIRE_URL=https://chat.smartice.ai
BOT_KEY=2-CsheovnLtzjM
CAMPFIRE_DB_PATH=/campfire/db/production.sqlite3
EOF

# Build and run
docker build -t campfire-ai-bot:latest .
docker run -d --name campfire-ai-bot --restart always \
  -p 5000:5000 \
  -v /var/once/campfire/db:/campfire/db:ro \
  -v /root/ai-knowledge:/data \
  --env-file .env \
  campfire-ai-bot:latest
```

### Option 3: Systemd + Docker (Recommended)

**Create `/etc/systemd/system/campfire-ai-bot.service`:**

```ini
[Unit]
Description=Campfire AI Bot Container
After=docker.service
Requires=docker.service

[Service]
Type=simple
Restart=always
RestartSec=10

# Stop old container
ExecStartPre=-/usr/bin/docker stop campfire-ai-bot
ExecStartPre=-/usr/bin/docker rm campfire-ai-bot

# Start new container
ExecStart=/usr/bin/docker run --rm \
  --name campfire-ai-bot \
  -p 5000:5000 \
  -v /var/once/campfire/db:/campfire/db:ro \
  -v /root/ai-knowledge:/data \
  --env-file /root/ai-bot/.env \
  campfire-ai-bot:latest

# Stop container
ExecStop=/usr/bin/docker stop campfire-ai-bot

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
systemctl daemon-reload
systemctl enable campfire-ai-bot
systemctl start campfire-ai-bot
systemctl status campfire-ai-bot
```

---

## Success Criteria

### Development Phase
- ✅ All unit tests pass (80%+ coverage)
- ✅ All integration tests pass
- ✅ Docker image builds successfully
- ✅ Container runs locally
- ✅ Health endpoint responds

### Deployment Phase
- ✅ Container deploys to DigitalOcean
- ✅ Bot responds to @mentions
- ✅ Context tools work correctly
- ✅ User preferences are saved
- ✅ Service auto-restarts

### Production Phase
- ✅ Response time < 10 seconds
- ✅ No crashes for 24 hours
- ✅ Logs are clean
- ✅ API costs within budget

---

## Summary: TDD + Container Workflow

```
🏠 LOCAL DEVELOPMENT (Mac)
├─ Write failing test (RED)
├─ Write code to pass (GREEN)
├─ Refactor (BLUE)
├─ Run all tests
├─ Git commit
└─ Repeat

🐳 CONTAINERIZATION
├─ Write Dockerfile
├─ Build image locally
├─ Test with docker-compose
└─ Verify all features work

🚀 DEPLOYMENT (DigitalOcean)
├─ Transfer image or source
├─ Build on server (or load image)
├─ Run container
├─ Configure webhook in Campfire
└─ Monitor logs

✅ VALIDATION
├─ End-to-end testing
├─ Performance monitoring
└─ Production readiness check
```

---

**This approach gives you:**
- ✅ Confidence from tests
- ✅ Proper development workflow
- ✅ Version control
- ✅ Reproducible deployments
- ✅ Easy updates
- ✅ Professional code quality

**Ready to start TDD implementation?**
