#!/usr/bin/env python3
"""Test script for PromptLoader integration (v0.4.1)."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.bot_manager import BotManager
from src.prompt_loader import PromptLoader

def test_bot_manager_yaml():
    """Test 1: Verify BotManager loads personal_assistant.yaml"""
    print("=" * 80)
    print("TEST 1: BotManager YAML Loading")
    print("=" * 80)

    manager = BotManager(bots_dirs=['./bots', 'prompts/configs'])

    # Load personal_assistant
    bot_config = manager.get_bot_by_id('personal_assistant')

    if bot_config:
        print(f"✅ Bot loaded: {bot_config.name}")
        print(f"   bot_id: {bot_config.bot_id}")
        print(f"   model: {bot_config.model}")

        # Check for system_prompt_file attribute
        if hasattr(bot_config, 'system_prompt_file'):
            print(f"✅ Has system_prompt_file: {bot_config.system_prompt_file}")
        else:
            print(f"❌ Missing system_prompt_file attribute")

        # Check for mcp_servers
        if hasattr(bot_config, 'mcp_servers'):
            print(f"✅ MCP servers: {bot_config.mcp_servers}")
        else:
            print(f"⚠️  No mcp_servers attribute")

        # Check tools configuration
        if hasattr(bot_config, 'tools') and isinstance(bot_config.tools, dict):
            print(f"✅ Tools config (dict format):")
            for category, tools in bot_config.tools.items():
                print(f"   - {category}: {len(tools)} tools")
        elif hasattr(bot_config, 'tools_enabled'):
            print(f"⚠️  Using old tools_enabled format: {len(bot_config.tools_enabled)} tools")

        return True
    else:
        print("❌ Failed to load personal_assistant bot")
        return False

def test_prompt_loader():
    """Test 2: Verify PromptLoader loads file and substitutes variables"""
    print("\n" + "=" * 80)
    print("TEST 2: PromptLoader File Loading & Template Substitution")
    print("=" * 80)

    loader = PromptLoader(prompts_dir="prompts")

    # Check if file exists
    has_file = loader.has_file_based_prompt('personal_assistant')
    print(f"{'✅' if has_file else '❌'} File exists: prompts/bots/personal_assistant.md")

    if not has_file:
        return False

    # Test template substitution
    context = {
        'current_date': '2025-10-28',
        'user_name': '测试用户',
        'room_name': '测试房间'
    }

    try:
        prompt = loader.load_bot_prompt('personal_assistant', context)

        print(f"✅ Prompt loaded successfully")
        print(f"   Length: {len(prompt)} characters")

        # Check if template variables were substituted
        if '$current_date' in prompt:
            print(f"❌ Template variable not substituted: $current_date")
            return False
        else:
            print(f"✅ Template variable substituted: $current_date")

        if '$user_name' in prompt:
            print(f"❌ Template variable not substituted: $user_name")
            return False
        else:
            print(f"✅ Template variable substituted: $user_name")

        if '$room_name' in prompt:
            print(f"❌ Template variable not substituted: $room_name")
            return False
        else:
            print(f"✅ Template variable substituted: $room_name")

        # Show first 500 characters of prompt
        print(f"\n📄 First 500 characters of loaded prompt:")
        print("-" * 80)
        print(prompt[:500])
        print("-" * 80)

        return True

    except Exception as e:
        print(f"❌ Error loading prompt: {e}")
        return False

def test_fallback_to_json():
    """Test 3: Verify fallback to JSON for non-migrated bots"""
    print("\n" + "=" * 80)
    print("TEST 3: Fallback to JSON for Non-Migrated Bots")
    print("=" * 80)

    loader = PromptLoader(prompts_dir="prompts")
    manager = BotManager(bots_dirs=['./bots', 'prompts/configs'])

    # Test with financial_analyst (should not have file-based prompt yet)
    financial_bot = manager.get_bot_by_id('financial_analyst')

    if financial_bot:
        print(f"✅ Bot loaded: {financial_bot.name}")

        has_file = loader.has_file_based_prompt('financial_analyst')
        if not has_file:
            print(f"✅ No file-based prompt (expected for non-migrated bot)")

            # Should have JSON system_prompt
            if hasattr(financial_bot, 'system_prompt'):
                prompt_length = len(financial_bot.system_prompt)
                print(f"✅ Has JSON system_prompt: {prompt_length} characters")
                return True
            else:
                print(f"❌ Missing system_prompt in JSON config")
                return False
        else:
            print(f"⚠️  Found file-based prompt (unexpected for non-migrated bot)")
            return True
    else:
        print(f"❌ Failed to load financial_analyst bot")
        return False

def main():
    """Run all tests"""
    print("\n🧪 Testing PromptLoader Integration (v0.4.1)")
    print("=" * 80)

    results = []

    # Run tests
    results.append(("BotManager YAML Loading", test_bot_manager_yaml()))
    results.append(("PromptLoader File Loading", test_prompt_loader()))
    results.append(("Fallback to JSON", test_fallback_to_json()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED - PromptLoader integration working correctly!")
    else:
        print("❌ SOME TESTS FAILED - See details above")
    print("=" * 80)

    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
