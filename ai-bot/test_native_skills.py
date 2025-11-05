"""Test script to check available native Agent SDK skills"""
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def check_available_skills():
    # Enable Skill tool and filesystem-based skills discovery
    options = ClaudeAgentOptions(
        setting_sources=["user", "project"],  # Load Skills from filesystem
        allowed_tools=["Skill"]  # Only enable Skill tool for this test
    )

    client = ClaudeSDKClient(options=options)

    print("Connecting to Claude Agent SDK...")
    await client.connect()

    print("Querying available skills...")
    print("=" * 60)

    # Send query
    await client.query("What Skills are available? List all skills you can discover.")

    # Receive response
    async for message in client.receive_response():
        # Extract text from AssistantMessage content blocks
        if hasattr(message, '__class__') and message.__class__.__name__ == 'AssistantMessage':
            if hasattr(message, 'content'):
                for block in message.content:
                    block_type = block.__class__.__name__
                    if block_type == 'TextBlock':
                        print(getattr(block, 'text', ''))

    print("\n" + "=" * 60)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(check_available_skills())
