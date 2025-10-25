"""
Test 3: Actual Skills usage with Agent SDK

Based on findings from Test 2, attempt to use Skills in a real query.
This will test if Skills actually work with Agent SDK.
"""
import asyncio
import os
from pathlib import Path
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

# Load .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Ensure we have API key
if not os.getenv("ANTHROPIC_API_KEY"):
    print("❌ ANTHROPIC_API_KEY not set in .env")
    exit(1)

async def test_real_skills_usage():
    """Try to use Skills in an actual Agent SDK query."""

    print("=" * 60)
    print("Test 3: Real Skills usage with Agent SDK")
    print("=" * 60)

    # Test case 1: Try the pptx skill (PowerPoint)
    print("\n📋 Test Case 1: Using pptx (PowerPoint) skill")
    print("-" * 60)

    try:
        # Based on Skills documentation, we might need to:
        # 1. Enable code execution (required for Skills)
        # 2. Specify Skills somehow in options
        # 3. Use specific beta flags

        options = ClaudeAgentOptions(
            # Enable code execution (required for Skills per documentation)
            allowed_tools=["code_execution_20250825"],

            # Try passing Skills via extra_args (educated guess)
            extra_args={
                "--anthropic-beta": "skills-2025-10-02,code-execution-2025-08-25",
                # Possible Skills specification methods:
                # Method A: CLI flag approach
                "--skills": "pptx",
                # Method B: Container JSON approach (might not work with CLI)
                # "--container": '{"skills":[{"type":"anthropic","skill_id":"pptx","version":"latest"}]}'
            },

            permission_mode="default",
            max_turns=5
        )

        print("Options created, attempting query...")

        async with ClaudeSDKClient(options=options) as client:
            await client.query("Create a simple 2-slide presentation about renewable energy")

            # Collect response
            response_text = []
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            response_text.append(block.text)
                            print(f"💭 Claude: {block.text[:200]}...")

            full_response = " ".join(response_text)

            # Check if Skills were actually used
            if "pptx" in full_response.lower() or "powerpoint" in full_response.lower() or "presentation" in full_response.lower():
                print("\n✅ Response mentions presentation/PowerPoint")
            else:
                print("\n⚠️  Response doesn't clearly indicate Skills usage")

            print(f"\n📊 Full response length: {len(full_response)} characters")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"   Traceback:\n{traceback.format_exc()}")

    # Test case 2: Without Skills (baseline)
    print("\n" + "=" * 60)
    print("📋 Test Case 2: Same query WITHOUT Skills (baseline)")
    print("-" * 60)

    try:
        options_baseline = ClaudeAgentOptions(
            allowed_tools=["Read", "Write"],
            permission_mode="default",
            max_turns=5
        )

        async with ClaudeSDKClient(options=options_baseline) as client:
            await client.query("Create a simple 2-slide presentation about renewable energy")

            response_text = []
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            response_text.append(block.text)
                            print(f"💭 Claude: {block.text[:200]}...")

            print(f"\n📊 Baseline response length: {len(' '.join(response_text))} characters")

    except Exception as e:
        print(f"\n❌ Baseline test failed: {e}")

    print("\n" + "=" * 60)
    print("Test 3 Complete")
    print("=" * 60)
    print("\n💡 Compare the two responses to see if Skills made a difference")

if __name__ == "__main__":
    asyncio.run(test_real_skills_usage())
