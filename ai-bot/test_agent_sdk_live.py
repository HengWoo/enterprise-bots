#!/usr/bin/env python3
"""
Live Agent SDK Test
Test the complete Agent SDK integration with real API calls

⚠️  WARNING: This uses real API calls (~$0.01-0.02 per test)
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Load environment
from dotenv import load_dotenv
load_dotenv()


def check_api_key():
    """Check if API key is configured"""
    api_key = os.getenv('ANTHROPIC_API_KEY', '')

    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set in .env file")
        print("\nPlease set your API key:")
        print("  echo 'ANTHROPIC_API_KEY=sk-ant-api03-...' >> .env")
        return False

    if api_key.startswith('sk-ant-test'):
        print("❌ Test API key detected. Please use real API key.")
        return False

    print(f"✓ API key configured: {api_key[:20]}...")
    return True


async def test_agent_simple_message():
    """Test agent with a simple message (no tool use)"""
    print("\n" + "="*60)
    print("Test 1: Simple Message (no tools)")
    print("="*60)
    print("\nThis should respond without using any tools.")
    print("Expected cost: ~$0.005")

    from tools.campfire_tools import CampfireTools
    from bot_manager import BotManager
    from campfire_agent import CampfireAgent
    from agent_tools import initialize_tools

    # Setup
    tools = CampfireTools(
        db_path="./tests/fixtures/test.db",
        context_dir="./test_contexts"
    )
    initialize_tools(tools)

    bot_manager = BotManager(bots_dir='./bots')
    bot_config = bot_manager.get_bot_by_id('financial_analyst')

    agent = CampfireAgent(
        bot_config=bot_config,
        campfire_tools=tools
    )

    # Test message
    print("\nSending message: 'Hello! Can you hear me?'")
    print("Processing...")

    response = await agent.process_message(
        content="Hello! Can you hear me?",
        context={
            'user_id': 1,
            'user_name': 'Test User',
            'room_id': 1,
            'room_name': 'Test Room'
        }
    )

    print("\n" + "-"*60)
    print("RESPONSE:")
    print("-"*60)
    print(response)
    print("-"*60)

    return True


async def test_agent_with_search():
    """Test agent with a question that should trigger search tool"""
    print("\n" + "="*60)
    print("Test 2: Question Requiring Search")
    print("="*60)
    print("\nThis should use the search_conversations tool.")
    print("Expected cost: ~$0.01")

    from tools.campfire_tools import CampfireTools
    from bot_manager import BotManager
    from campfire_agent import CampfireAgent
    from agent_tools import initialize_tools

    # Setup
    tools = CampfireTools(
        db_path="./tests/fixtures/test.db",
        context_dir="./test_contexts"
    )
    initialize_tools(tools)

    bot_manager = BotManager(bots_dir='./bots')
    bot_config = bot_manager.get_bot_by_id('financial_analyst')

    agent = CampfireAgent(
        bot_config=bot_config,
        campfire_tools=tools
    )

    # Test message that should trigger search
    print("\nSending message: 'What was discussed in previous conversations about revenue?'")
    print("Processing... (agent should use search_conversations tool)")

    response = await agent.process_message(
        content="What was discussed in previous conversations about revenue?",
        context={
            'user_id': 1,
            'user_name': 'WU HENG',
            'room_id': 1,
            'room_name': 'Finance Team'
        }
    )

    print("\n" + "-"*60)
    print("RESPONSE:")
    print("-"*60)
    print(response)
    print("-"*60)

    return True


async def test_flask_endpoint():
    """Test the Flask webhook endpoint with Agent SDK"""
    print("\n" + "="*60)
    print("Test 3: Flask Webhook Endpoint")
    print("="*60)
    print("\nThis tests the complete webhook flow.")
    print("Expected cost: ~$0.005")

    import requests

    # Check if Flask is running
    try:
        response = requests.get('http://localhost:5001/health', timeout=2)
        if response.status_code != 200:
            print("❌ Flask server health check failed")
            print("\nStart Flask server first:")
            print("  uv run python src/app.py")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Flask server not running on port 5001")
        print("\nStart Flask server in another terminal:")
        print("  uv run python src/app.py")
        return False

    print("✓ Flask server is running")

    # Send webhook request
    payload = {
        "creator": {
            "id": 1,
            "name": "Test User",
            "email_address": "test@example.com"
        },
        "room": {
            "id": 1,
            "name": "Test Room"
        },
        "content": "<p>@bot Hello! This is a test message.</p>"
    }

    print("\nSending webhook request...")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    response = requests.post(
        'http://localhost:5001/webhook/financial_analyst',
        json=payload,
        timeout=30
    )

    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\n" + "-"*60)
        print("RESPONSE:")
        print("-"*60)
        print(result.get('response', 'No response'))
        print("-"*60)
        return True
    else:
        print(f"❌ Request failed: {response.text}")
        return False


async def main():
    """Run all tests"""
    import sys

    print("=" * 60)
    print("Agent SDK Live Testing")
    print("=" * 60)

    # Check API key
    if not check_api_key():
        return

    # Check for command line argument
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("\n⚠️  WARNING: These tests will make real API calls")
        print("Estimated total cost: ~$0.02-0.03")
        print("\nAvailable tests:")
        print("  1. Simple message (no tools) - $0.005")
        print("  2. Search conversation (with tools) - $0.01")
        print("  3. Flask webhook endpoint - $0.005")
        print("  4. All tests - $0.02")
        print("  0. Cancel")
        print("\nUsage: python test_agent_sdk_live.py [test_number]")
        print("Example: python test_agent_sdk_live.py 1")
        return

    if choice == '0':
        print("Cancelled.")
        return
    elif choice == '1':
        await test_agent_simple_message()
    elif choice == '2':
        await test_agent_with_search()
    elif choice == '3':
        await test_flask_endpoint()
    elif choice == '4':
        print("\nRunning all tests...")
        await test_agent_simple_message()
        await test_agent_with_search()
        await test_flask_endpoint()
    else:
        print("Invalid choice.")
        return

    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)
    print("\nIf all tests passed, the Agent SDK integration is working correctly.")


if __name__ == '__main__':
    asyncio.run(main())
