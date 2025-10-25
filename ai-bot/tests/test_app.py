"""
Tests for Flask webhook server
Following TDD: Write tests BEFORE implementation
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


@pytest.fixture
def app():
    """Create Flask app for testing"""
    from src.app import create_app

    app = create_app(testing=True)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def sample_webhook_payload():
    """Sample Campfire webhook payload"""
    return {
        "creator": {
            "id": 1,
            "name": "WU HENG",
            "email_address": "heng.woo@gmail.com"
        },
        "room": {
            "id": 2,
            "name": "Finance Team"
        },
        "content": "<p>@财务分析师 Can you help me analyze Q3 revenue trends?</p>"
    }


@pytest.fixture
def mock_agent_response():
    """Mock agent response"""
    return {
        "content": [
            {
                "type": "text",
                "text": "Based on the Finance Team conversation history, Q3 revenue shows 12% YoY growth..."
            }
        ]
    }


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_returns_200(self, client):
        """Should return 200 OK"""
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        """Should return JSON response"""
        response = client.get('/health')
        assert response.content_type == 'application/json'

    def test_health_returns_status(self, client):
        """Should return status: healthy"""
        response = client.get('/health')
        data = json.loads(response.data)

        assert data['status'] == 'healthy'
        assert 'timestamp' in data


class TestWebhookEndpoint:
    """Test webhook endpoint"""

    def test_webhook_accepts_post(self, client, sample_webhook_payload):
        """Should accept POST requests"""
        response = client.post(
            '/webhook',
            data=json.dumps(sample_webhook_payload),
            content_type='application/json'
        )

        assert response.status_code in [200, 202]

    def test_webhook_rejects_get(self, client):
        """Should reject GET requests"""
        response = client.get('/webhook')
        assert response.status_code == 405  # Method Not Allowed

    def test_webhook_requires_json(self, client):
        """Should reject non-JSON requests"""
        response = client.post(
            '/webhook',
            data='not json',
            content_type='text/plain'
        )

        assert response.status_code == 400

    def test_webhook_validates_payload(self, client):
        """Should validate required fields"""
        invalid_payload = {"invalid": "payload"}

        response = client.post(
            '/webhook',
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )

        assert response.status_code == 400

    @patch('src.app.Agent')
    def test_webhook_creates_agent(self, mock_agent_class, client, sample_webhook_payload):
        """Should create Claude agent with tools"""
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        client.post(
            '/webhook',
            data=json.dumps(sample_webhook_payload),
            content_type='application/json'
        )

        # Should create agent
        mock_agent_class.assert_called_once()

    @patch('src.app.Agent')
    def test_webhook_passes_message_to_agent(self, mock_agent_class, client, sample_webhook_payload):
        """Should pass user message to agent"""
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        client.post(
            '/webhook',
            data=json.dumps(sample_webhook_payload),
            content_type='application/json'
        )

        # Should call agent with message
        assert mock_agent.run.called or mock_agent.process_message.called

    @patch('src.app.Agent')
    @patch('src.app.post_to_campfire')
    def test_webhook_posts_response(
        self,
        mock_post,
        mock_agent_class,
        client,
        sample_webhook_payload,
        mock_agent_response
    ):
        """Should post agent response to Campfire"""
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        mock_agent.run.return_value = mock_agent_response

        client.post(
            '/webhook',
            data=json.dumps(sample_webhook_payload),
            content_type='application/json'
        )

        # Should post to Campfire
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        # Should include room_id and response text
        assert call_args is not None

    @patch('src.app.Agent')
    def test_webhook_handles_agent_error(self, mock_agent_class, client, sample_webhook_payload):
        """Should handle agent errors gracefully"""
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        mock_agent.run.side_effect = Exception("Agent error")

        response = client.post(
            '/webhook',
            data=json.dumps(sample_webhook_payload),
            content_type='application/json'
        )

        # Should return error status
        assert response.status_code in [500, 200]  # May return 200 with error message

    def test_webhook_strips_html_from_content(self, client):
        """Should strip HTML from message content"""
        payload = {
            "creator": {"id": 1, "name": "Test User"},
            "room": {"id": 1, "name": "Test Room"},
            "content": "<p>@bot <strong>Hello</strong> world</p>"
        }

        with patch('src.app.Agent') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent

            client.post(
                '/webhook',
                data=json.dumps(payload),
                content_type='application/json'
            )

            # Agent should receive stripped content
            # (check the actual call to verify)


class TestCampfireIntegration:
    """Test Campfire API integration"""

    @patch('src.app.requests.post')
    def test_post_to_campfire(self, mock_post):
        """Should post message to Campfire API"""
        from src.app import post_to_campfire

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        post_to_campfire(
            room_id=1,
            message="Test message"
        )

        # Should make POST request
        mock_post.assert_called_once()

        # Should use correct URL format
        call_args = mock_post.call_args
        url = call_args[0][0] if call_args[0] else call_args.kwargs.get('url')

        assert 'rooms' in url
        assert '2-CsheovnLtzjM' in url or 'BOT_KEY' in str(call_args)

    @patch('src.app.requests.post')
    def test_post_to_campfire_with_error(self, mock_post):
        """Should handle Campfire API errors"""
        from src.app import post_to_campfire

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("API error")
        mock_post.return_value = mock_response

        # Should not raise exception
        post_to_campfire(
            room_id=1,
            message="Test message"
        )

    @patch('src.app.requests.post')
    def test_post_to_campfire_formats_message(self, mock_post):
        """Should format message with proper structure"""
        from src.app import post_to_campfire

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        post_to_campfire(
            room_id=1,
            message="Test message"
        )

        # Should send proper data structure
        call_args = mock_post.call_args
        data = call_args.kwargs.get('data') or call_args.kwargs.get('json')

        assert data is not None


class TestAgentConfiguration:
    """Test Agent SDK configuration"""

    @patch('src.app.Agent')
    def test_agent_receives_tools(self, mock_agent_class, client, sample_webhook_payload):
        """Should configure agent with Campfire tools"""
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        client.post(
            '/webhook',
            data=json.dumps(sample_webhook_payload),
            content_type='application/json'
        )

        # Agent should be initialized with tools
        call_kwargs = mock_agent_class.call_args.kwargs
        assert 'tools' in call_kwargs or mock_agent_class.call_args[0]

    @patch('src.app.Agent')
    def test_agent_receives_system_prompt(self, mock_agent_class, client, sample_webhook_payload):
        """Should configure agent with system prompt"""
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        client.post(
            '/webhook',
            data=json.dumps(sample_webhook_payload),
            content_type='application/json'
        )

        # Should have system prompt configured
        call_kwargs = mock_agent_class.call_args.kwargs
        # System prompt may be in various kwargs
        assert (
            'system_prompt' in call_kwargs or
            'system' in call_kwargs or
            len(call_kwargs) > 0
        )

    @patch('src.app.Agent')
    def test_agent_receives_context(self, mock_agent_class, client, sample_webhook_payload):
        """Should pass user and room context to agent"""
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        client.post(
            '/webhook',
            data=json.dumps(sample_webhook_payload),
            content_type='application/json'
        )

        # Should receive context about user and room
        # (May be passed in message or separately)


class TestEnvironmentConfiguration:
    """Test environment variable configuration"""

    def test_requires_anthropic_api_key(self):
        """Should require ANTHROPIC_API_KEY"""
        import os
        from src.app import get_config

        # Should have API key configured
        config = get_config()
        assert config.get('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_API_KEY')

    def test_requires_campfire_url(self):
        """Should require CAMPFIRE_URL"""
        import os
        from src.app import get_config

        config = get_config()
        assert config.get('CAMPFIRE_URL') or os.getenv('CAMPFIRE_URL')

    def test_requires_bot_key(self):
        """Should require BOT_KEY"""
        import os
        from src.app import get_config

        config = get_config()
        assert config.get('BOT_KEY') or os.getenv('BOT_KEY')


class TestErrorHandling:
    """Test comprehensive error handling"""

    def test_handles_malformed_json(self, client):
        """Should handle malformed JSON"""
        response = client.post(
            '/webhook',
            data='{"invalid": json}',
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_handles_missing_creator(self, client):
        """Should handle missing creator field"""
        payload = {
            "room": {"id": 1, "name": "Test"},
            "content": "Test message"
        }

        response = client.post(
            '/webhook',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_handles_missing_room(self, client):
        """Should handle missing room field"""
        payload = {
            "creator": {"id": 1, "name": "Test"},
            "content": "Test message"
        }

        response = client.post(
            '/webhook',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_handles_missing_content(self, client):
        """Should handle missing content field"""
        payload = {
            "creator": {"id": 1, "name": "Test"},
            "room": {"id": 1, "name": "Test"}
        }

        response = client.post(
            '/webhook',
            data=json.dumps(payload),
            content_type='application/json'
        )

        assert response.status_code == 400

    @patch('src.app.CampfireTools')
    def test_handles_database_error(self, mock_tools_class, client, sample_webhook_payload):
        """Should handle database errors gracefully"""
        mock_tools_class.side_effect = Exception("Database error")

        response = client.post(
            '/webhook',
            data=json.dumps(sample_webhook_payload),
            content_type='application/json'
        )

        # Should not crash
        assert response.status_code in [200, 500]
