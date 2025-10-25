"""
Test 2: Find the correct way to use Skills with Agent SDK

Since Claude Code and Skills are built to work together, this test
explores different ways to enable Skills through ClaudeAgentOptions.
"""
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def test_skills_approaches():
    """Test different approaches to enabling Skills in Agent SDK."""

    print("=" * 60)
    print("Test 2: Finding correct Skills integration method")
    print("=" * 60)

    # Approach 1: Check if ClaudeAgentOptions has skills/container parameter
    print("\n📋 Approach 1: Inspect ClaudeAgentOptions for Skills parameters")
    print("-" * 60)

    options_class = ClaudeAgentOptions
    all_fields = [f for f in dir(options_class) if not f.startswith('_')]

    print("Available ClaudeAgentOptions fields:")
    for field in all_fields:
        print(f"  - {field}")

    # Check for Skills-related fields
    skills_related = [f for f in all_fields if 'skill' in f.lower() or 'container' in f.lower()]
    if skills_related:
        print(f"\n✅ Found Skills-related fields: {skills_related}")
    else:
        print("\n❌ No obvious Skills-related fields found")

    # Approach 2: Try using extra_args with Skills
    print("\n📋 Approach 2: Test extra_args with Skills parameters")
    print("-" * 60)

    try:
        # Try various extra_args combinations
        test_cases = [
            {"--skills": "pptx"},
            {"--skill": "pptx"},
            {"--enable-skills": None},
            {"--container": '{"skills":[{"type":"anthropic","skill_id":"pptx","version":"latest"}]}'},
        ]

        for i, args in enumerate(test_cases, 1):
            print(f"\n  Test case {i}: extra_args = {args}")
            try:
                options = ClaudeAgentOptions(
                    extra_args=args,
                    allowed_tools=["Read"],
                    permission_mode="default"
                )
                print(f"  ✅ ClaudeAgentOptions created successfully")
                # Don't actually run a query, just check if options work
            except Exception as e:
                print(f"  ❌ Failed: {e}")

    except Exception as e:
        print(f"❌ Approach 2 failed: {e}")

    # Approach 3: Check for beta flags or special modes
    print("\n📋 Approach 3: Check for beta/experimental flags")
    print("-" * 60)

    try:
        # Skills might require specific beta flags
        options = ClaudeAgentOptions(
            extra_args={
                "--anthropic-beta": "skills-2025-10-02,code-execution-2025-08-25"
            }
        )
        print("✅ Beta flags accepted in extra_args")
    except Exception as e:
        print(f"❌ Beta flags failed: {e}")

    print("\n" + "=" * 60)
    print("Test 2 Complete - Check output for working approach")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_skills_approaches())
