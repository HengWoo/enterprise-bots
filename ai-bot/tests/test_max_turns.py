"""
Test max_turns parameter and multi-turn agent workflow.

This test reproduces the production bug where the bot returns empty "..."
responses after MCP tool calls, even though max_turns=10 is set.
"""

import pytest
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from claude_agent_sdk.types import AssistantMessage, ToolUseBlock, TextBlock, ResultMessage


class TestMaxTurnsParameter:
    """Test that max_turns parameter is correctly configured"""

    def test_max_turns_set_in_options(self):
        """Verify max_turns is present in ClaudeAgentOptions"""
        options = ClaudeAgentOptions(
            model="claude-sonnet-4-5-20250929",
            max_turns=10
        )

        assert options.max_turns == 10, "max_turns should be set to 10"

    def test_max_turns_passed_to_cli_command(self):
        """Verify max_turns is included in CLI command generation"""
        from claude_agent_sdk._internal.transport.subprocess_cli import SubprocessCLITransport

        options = ClaudeAgentOptions(
            model="claude-sonnet-4-5-20250929",
            max_turns=30,
            system_prompt="You are a test bot"
        )

        transport = SubprocessCLITransport(
            prompt="test",
            options=options
        )

        cmd = transport._build_command()

        # Check that --max-turns is in command
        assert "--max-turns" in cmd, "Command should include --max-turns flag"

        # Check that value is correct
        max_turns_index = cmd.index("--max-turns")
        assert cmd[max_turns_index + 1] == "30", "max_turns value should be 30"


class TestMultiTurnWorkflow:
    """Test multi-turn agent workflow with tool calls

    This simulates the production scenario where:
    1. User asks a question
    2. Agent calls MCP tools
    3. Agent should synthesize results into text
    4. But currently returns empty response
    """

    @pytest.mark.asyncio
    @pytest.mark.integration  # Mark as integration test (requires Claude API)
    async def test_simple_question_no_tools(self):
        """Baseline: Simple question without tools should work"""
        options = ClaudeAgentOptions(
            model="claude-sonnet-4-5-20250929",
            system_prompt="You are a helpful assistant. Answer concisely.",
            max_turns=10
        )

        client = ClaudeSDKClient(options=options)

        try:
            await client.connect()
            await client.query("What is 2 + 2?")

            # Collect messages
            messages = []
            async for message in client.receive_response():
                messages.append(message)

            # Find AssistantMessage
            assistant_messages = [m for m in messages if isinstance(m, AssistantMessage)]

            assert len(assistant_messages) > 0, "Should receive at least one AssistantMessage"

            # Check that we got text response
            text_blocks = []
            for msg in assistant_messages:
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        text_blocks.append(block)

            assert len(text_blocks) > 0, "Should receive at least one TextBlock"
            assert len(text_blocks[0].text) > 0, "TextBlock should not be empty"
            assert "4" in text_blocks[0].text, "Response should contain the answer"

            print(f"✅ Baseline test passed: {text_blocks[0].text[:100]}")

        finally:
            await client.disconnect()

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires MCP server - manual test only")
    async def test_question_with_mcp_tools(self):
        """Test question that triggers MCP tool calls

        This should FAIL if the production bug exists:
        - Agent calls tools successfully
        - But returns empty text response
        """
        # Create simple test MCP server
        from claude_agent_sdk import create_sdk_mcp_server, tool

        @tool("get_test_data", "Get test data", {"key": str})
        async def get_test_data(args):
            return {"content": [{"type": "text", "text": f"Test data for key: {args['key']}"}]}

        test_server = create_sdk_mcp_server(
            name="test",
            tools=[get_test_data]
        )

        options = ClaudeAgentOptions(
            model="claude-sonnet-4-5-20250929",
            system_prompt="You are a helpful assistant. Use available tools when needed.",
            mcp_servers={"test": test_server},
            allowed_tools=["mcp__test__get_test_data"],
            max_turns=10
        )

        client = ClaudeSDKClient(options=options)

        try:
            await client.connect()
            await client.query("Use get_test_data with key 'example' and tell me what you find.")

            # Collect messages
            messages = []
            tool_use_found = False
            assistant_text_found = False

            async for message in client.receive_response():
                messages.append(message)

                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, ToolUseBlock):
                            tool_use_found = True
                            print(f"🔧 Tool called: {block.name}")
                        elif isinstance(block, TextBlock):
                            if block.text.strip():
                                assistant_text_found = True
                                print(f"💬 Assistant text: {block.text[:100]}")

            # Assertions
            assert tool_use_found, "Agent should call MCP tool"
            assert assistant_text_found, "Agent should generate text response after tool call (THIS IS THE BUG!)"

            # Find final text response
            final_text = None
            for msg in reversed(messages):
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock) and block.text.strip():
                            final_text = block.text
                            break
                    if final_text:
                        break

            assert final_text is not None, "Should have final text response"
            assert len(final_text) > 10, "Final response should be substantial (not just '...')"
            assert "example" in final_text.lower(), "Response should reference the tool result"

            print(f"✅ Multi-turn test passed: {final_text[:200]}")

        finally:
            await client.disconnect()


class TestConversationRoundTracking:
    """Test conversation round counting for dedicated chat suggestions"""

    def test_count_conversation_rounds(self):
        """Count back-and-forth rounds between user and bot"""
        # Simulate conversation history from database
        messages = [
            {"creator_name": "User", "body": "Hello"},
            {"creator_name": "Bot", "body": "Hi! How can I help?"},
            {"creator_name": "User", "body": "What is X?"},
            {"creator_name": "Bot", "body": "X is..."},
            {"creator_name": "User", "body": "Tell me more"},
            {"creator_name": "Bot", "body": "Here's more info..."},
            # ... 8 more rounds ...
        ]

        # Add more messages to reach 10 rounds
        for i in range(7):
            messages.append({"creator_name": "User", "body": f"Question {i+4}"})
            messages.append({"creator_name": "Bot", "body": f"Answer {i+4}"})

        # Count rounds (a round = user message + bot response)
        rounds = len([m for m in messages if m["creator_name"] == "User"])

        assert rounds >= 10, f"Test should have 10+ rounds, got {rounds}"

    def test_detect_long_conversation(self):
        """Detect when conversation exceeds 10 rounds"""
        # This will be implemented in campfire_agent.py
        # For now, test the logic

        def should_suggest_dedicated_chat(message_count: int, bot_name: str) -> bool:
            """Logic to determine if we should suggest dedicated chat"""
            # Count messages from current user and bot responses
            # If > 10 back-and-forth rounds, suggest dedicated chat
            user_messages = message_count // 2  # Rough estimate
            return user_messages > 10

        assert not should_suggest_dedicated_chat(10, "Bot"), "10 messages (5 rounds) should not trigger"
        assert not should_suggest_dedicated_chat(20, "Bot"), "20 messages (10 rounds) at threshold"
        assert should_suggest_dedicated_chat(22, "Bot"), "22 messages (11 rounds) should trigger"


if __name__ == "__main__":
    print("Running max_turns tests...")
    print("\nTo run all tests:")
    print("  pytest tests/test_max_turns.py -v")
    print("\nTo run only unit tests (no API calls):")
    print("  pytest tests/test_max_turns.py -v -m 'not integration'")
    print("\nTo run integration tests (requires API key):")
    print("  pytest tests/test_max_turns.py -v -m integration")
