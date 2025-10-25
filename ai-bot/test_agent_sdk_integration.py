#!/usr/bin/env python3
"""
Test Agent SDK Integration
Verify that all components are properly integrated
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")

    try:
        from tools.campfire_tools import CampfireTools
        print("✓ CampfireTools imported")
    except ImportError as e:
        print(f"✗ Failed to import CampfireTools: {e}")
        return False

    try:
        from bot_manager import BotManager, BotConfig
        print("✓ BotManager imported")
    except ImportError as e:
        print(f"✗ Failed to import BotManager: {e}")
        return False

    try:
        from agent_tools import AGENT_TOOLS, initialize_tools
        print("✓ Agent tools imported")
    except ImportError as e:
        print(f"✗ Failed to import agent_tools: {e}")
        return False

    try:
        from campfire_agent import CampfireAgent
        print("✓ CampfireAgent imported")
    except ImportError as e:
        print(f"✗ Failed to import CampfireAgent: {e}")
        return False

    try:
        from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
        print("✓ Claude Agent SDK imported")
    except ImportError as e:
        print(f"✗ Failed to import Claude Agent SDK: {e}")
        print("  Make sure claude-agent-sdk is installed: uv add claude-agent-sdk")
        return False

    print("\n✓ All imports successful!\n")
    return True


def test_tools_initialization():
    """Test that tools can be initialized"""
    print("Testing tools initialization...")

    from tools.campfire_tools import CampfireTools
    from agent_tools import initialize_tools, AGENT_TOOLS

    # Create CampfireTools instance
    tools = CampfireTools(
        db_path="./tests/fixtures/test.db",
        context_dir="./test_contexts"
    )
    print("✓ CampfireTools instance created")

    # Initialize agent tools
    initialize_tools(tools)
    print("✓ Agent tools initialized")

    # Check tool count
    print(f"✓ Found {len(AGENT_TOOLS)} agent tools:")
    for tool in AGENT_TOOLS:
        # Agent SDK tools don't have __name__, use their name attribute
        tool_name = getattr(tool, 'name', str(tool))
        print(f"  - {tool_name}")

    print()
    return True


def test_bot_config():
    """Test that bot configuration loads"""
    print("Testing bot configuration...")

    from bot_manager import BotManager

    bot_manager = BotManager(bots_dir='./bots')
    print(f"✓ BotManager loaded {len(bot_manager.bots)} bots")

    # Get financial analyst bot
    financial_bot = bot_manager.get_bot_by_id('financial_analyst')
    if financial_bot:
        print(f"✓ Financial Analyst bot loaded:")
        print(f"  - Name: {financial_bot.display_name}")
        print(f"  - Model: {financial_bot.model}")
        print(f"  - Temperature: {financial_bot.temperature}")
    else:
        print("✗ Financial Analyst bot not found")
        return False

    print()
    return True


async def test_agent_creation():
    """Test that CampfireAgent can be created"""
    print("Testing CampfireAgent creation...")

    from tools.campfire_tools import CampfireTools
    from bot_manager import BotManager
    from campfire_agent import CampfireAgent
    from agent_tools import initialize_tools

    # Create tools
    tools = CampfireTools(
        db_path="./tests/fixtures/test.db",
        context_dir="./test_contexts"
    )
    initialize_tools(tools)

    # Load bot config
    bot_manager = BotManager(bots_dir='./bots')
    bot_config = bot_manager.get_bot_by_id('financial_analyst')

    if not bot_config:
        print("✗ Bot config not found")
        return False

    # Note: This will fail if ANTHROPIC_API_KEY is not set
    # But we can still verify the object creation
    try:
        agent = CampfireAgent(
            bot_config=bot_config,
            campfire_tools=tools
        )
        print("✓ CampfireAgent instance created")
        print(f"  - Bot: {agent.bot_config.display_name}")
        print(f"  - Model: {agent.bot_config.model}")
        print(f"  - Client initialized: {agent.client is not None}")
        print()
        return True
    except Exception as e:
        print(f"✗ Failed to create CampfireAgent: {e}")
        print("  (This is expected if ANTHROPIC_API_KEY is not set)")
        print()
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Agent SDK Integration Tests")
    print("=" * 60)
    print()

    # Test imports
    if not test_imports():
        print("\n✗ Import tests failed. Fix imports before continuing.")
        return

    # Test tools initialization
    if not test_tools_initialization():
        print("\n✗ Tools initialization failed.")
        return

    # Test bot config
    if not test_bot_config():
        print("\n✗ Bot configuration failed.")
        return

    # Test agent creation
    await test_agent_creation()

    print("=" * 60)
    print("Integration Tests Complete")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Set ANTHROPIC_API_KEY in .env file")
    print("2. Run Flask server: uv run python src/app.py")
    print("3. Test with webhook: curl -X POST http://localhost:5001/webhook ...")
    print()


if __name__ == '__main__':
    asyncio.run(main())
