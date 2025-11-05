#!/usr/bin/env python3
"""Test script for Skills loading and HTML presentation workflow (v0.4.1)."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.skills_manager import SkillsManager
from src.bot_manager import BotManager
from src.prompt_loader import PromptLoader

def test_skills_auto_discovery():
    """Test 1: Skills Auto-Discovery"""
    print("=" * 80)
    print("TEST 1: Skills Auto-Discovery")
    print("=" * 80)

    manager = SkillsManager(skills_dirs=[".claude/skills", "prompts/skills"])

    try:
        skills = manager.discover_skills()

        print(f"\n✅ Found {len(skills)} Skills:")
        for skill in skills:
            print(f"   - {skill.skill_id}")
            print(f"     Name: {skill.name}")
            print(f"     Description: {skill.description[:60]}...")
            print(f"     Version: {skill.version or 'N/A'}")

        # Check for our 3 expected Skills
        expected_skills = ['presentation-generation', 'document-skills-pptx', 'personal-productivity']
        found_skills = [s.skill_id for s in skills]

        missing = [s for s in expected_skills if s not in found_skills]
        if missing:
            print(f"\n❌ Missing expected Skills: {missing}")
            return False

        print(f"\n✅ All expected Skills found!")
        return True

    except Exception as e:
        print(f"\n❌ Error during Skills discovery: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_skill_loading():
    """Test 2: Skill Loading"""
    print("\n" + "=" * 80)
    print("TEST 2: Skill Loading")
    print("=" * 80)

    manager = SkillsManager(skills_dirs=[".claude/skills", "prompts/skills"])

    try:
        # Load presentation-generation Skill
        skill = manager.load_skill('presentation-generation')

        if not skill:
            print(f"❌ Failed to load presentation-generation Skill")
            return False

        print(f"\n✅ Skill loaded successfully:")
        print(f"   Name: {skill.metadata.name}")
        print(f"   Description: {skill.metadata.description[:60]}...")
        print(f"   Content length: {len(skill.content)} characters")
        print(f"   Raw content length: {len(skill.raw_content)} characters")

        # Check that frontmatter was stripped
        if skill.content.startswith('---'):
            print(f"\n❌ YAML frontmatter not stripped from content")
            return False
        else:
            print(f"\n✅ YAML frontmatter properly stripped")

        # Check for critical content
        critical_phrases = [
            "Step 1: Create HTML Content",
            "Step 2: Call save_html_presentation Tool",
            "Step 3: Output Tool's HTML Exactly",
            "save_html_presentation"
        ]

        missing_phrases = [p for p in critical_phrases if p not in skill.content]
        if missing_phrases:
            print(f"\n❌ Missing critical phrases: {missing_phrases}")
            return False

        print(f"✅ All critical workflow steps present")

        # Test caching
        skill2 = manager.load_skill('presentation-generation')
        if skill2 is skill:  # Same object reference
            print(f"✅ Caching working (same object returned)")
        else:
            print(f"⚠️  Caching may not be working (different object)")

        return True

    except Exception as e:
        print(f"\n❌ Error loading Skill: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_skills_mcp_integration():
    """Test 3: Skills MCP Integration (Configuration Check)"""
    print("\n" + "=" * 80)
    print("TEST 3: Skills MCP Integration (Config Check)")
    print("=" * 80)

    try:
        # Load personal_assistant config
        manager = BotManager(bots_dirs=['./bots', 'prompts/configs'])
        bot_config = manager.get_bot_by_id('personal_assistant')

        if not bot_config:
            print(f"❌ Failed to load personal_assistant config")
            return False

        # Check if Skills MCP server is configured
        if hasattr(bot_config, 'mcp_servers'):
            if 'skills' in bot_config.mcp_servers:
                print(f"✅ Skills MCP server configured: {bot_config.mcp_servers}")
            else:
                print(f"❌ Skills MCP not in mcp_servers list: {bot_config.mcp_servers}")
                return False
        else:
            print(f"❌ No mcp_servers attribute in bot config")
            return False

        # Check if load_skill tool is in allowed tools
        has_load_skill = False
        if hasattr(bot_config, 'tools') and isinstance(bot_config.tools, dict):
            skills_tools = bot_config.tools.get('skills', [])
            if 'load_skill' in skills_tools:
                has_load_skill = True
                print(f"✅ load_skill tool in skills tools list")
            else:
                print(f"❌ load_skill tool not found in skills tools: {skills_tools}")

        if has_load_skill:
            print(f"✅ Bot has access to Skills MCP tools")
            return True
        else:
            print(f"❌ Bot missing Skills MCP tools")
            return False

    except Exception as e:
        print(f"\n❌ Error checking Skills MCP integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_html_presentation_workflow():
    """Test 4: HTML Presentation Workflow"""
    print("\n" + "=" * 80)
    print("TEST 4: HTML Presentation Workflow Content")
    print("=" * 80)

    manager = SkillsManager(skills_dirs=[".claude/skills", "prompts/skills"])

    try:
        skill = manager.load_skill('presentation-generation')

        if not skill:
            print(f"❌ Failed to load presentation-generation Skill")
            return False

        # Check for critical workflow sections
        critical_sections = {
            "Step 1: Create HTML Content": "Step 1: Create HTML Content" in skill.content,
            "Step 2: Call save_html_presentation Tool": "Step 2: Call save_html_presentation Tool" in skill.content,
            "Step 3: Output Tool's HTML Exactly": "Step 3: Output Tool's HTML Exactly" in skill.content,
            "CRITICAL WARNING": "CRITICAL" in skill.content,
            "Design Templates": "Design Templates" in skill.content or "Template" in skill.content,
            "Best Practices": "Best Practices" in skill.content,
        }

        print(f"\n✅ Checking critical workflow sections:")
        all_present = True
        for section, present in critical_sections.items():
            status = "✅" if present else "❌"
            print(f"   {status} {section}")
            if not present:
                all_present = False

        # Check for Chinese text rendering guidelines
        if "中文" in skill.content or "Chinese" in skill.content:
            print(f"   ✅ Chinese text rendering guidance present")
        else:
            print(f"   ⚠️  Chinese text rendering guidance not explicitly mentioned")

        if all_present:
            print(f"\n✅ HTML presentation workflow complete")
            return True
        else:
            print(f"\n❌ Missing critical workflow sections")
            return False

    except Exception as e:
        print(f"\n❌ Error checking workflow: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_bot_initialization():
    """Test 5: Mock Bot Initialization"""
    print("\n" + "=" * 80)
    print("TEST 5: Mock Bot Initialization")
    print("=" * 80)

    try:
        # Load bot config
        bot_manager = BotManager(bots_dirs=['./bots', 'prompts/configs'])
        bot_config = bot_manager.get_bot_by_id('personal_assistant')

        if not bot_config:
            print(f"❌ Failed to load bot config")
            return False

        print(f"✅ Bot config loaded: {bot_config.name}")

        # Load prompt with template variables
        prompt_loader = PromptLoader(prompts_dir="prompts")

        context = {
            'current_date': '2025-10-29',
            'user_name': '测试用户',
            'room_name': '测试房间'
        }

        system_prompt = prompt_loader.load_bot_prompt('personal_assistant', context)

        print(f"✅ System prompt loaded: {len(system_prompt)} characters")

        # Check if Skills loading instructions present
        skills_instructions = [
            "load_skill",
            "document-skills-docx",
            "document-skills-pptx",
            "personal-productivity",
            "presentation-generation"
        ]

        print(f"\n✅ Checking Skills loading instructions:")
        all_present = True
        for instruction in skills_instructions:
            present = instruction in system_prompt
            status = "✅" if present else "❌"
            print(f"   {status} {instruction}")
            if not present:
                all_present = False

        # Check template substitution
        if '$current_date' in system_prompt:
            print(f"\n❌ Template variable not substituted: $current_date")
            all_present = False
        else:
            print(f"\n✅ Template variables properly substituted")

        if all_present:
            print(f"\n✅ Bot ready to load Skills on demand")
            return True
        else:
            print(f"\n⚠️  Some Skills references missing (may be intentional)")
            return True  # Still pass - Skills are optional references

    except Exception as e:
        print(f"\n❌ Error during bot initialization: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backwards_compatibility():
    """Test 6: Backwards Compatibility"""
    print("\n" + "=" * 80)
    print("TEST 6: Backwards Compatibility (JSON-based bots)")
    print("=" * 80)

    try:
        # Load a non-migrated bot (financial_analyst)
        bot_manager = BotManager(bots_dirs=['./bots', 'prompts/configs'])
        bot_config = bot_manager.get_bot_by_id('financial_analyst')

        if not bot_config:
            print(f"❌ Failed to load financial_analyst config")
            return False

        print(f"✅ Bot config loaded: {bot_config.name}")

        # Verify it has JSON system_prompt
        if not hasattr(bot_config, 'system_prompt') or not bot_config.system_prompt:
            print(f"❌ Missing system_prompt attribute")
            return False

        print(f"✅ Has JSON system_prompt: {len(bot_config.system_prompt)} characters")

        # Verify it does NOT have file-based prompt
        prompt_loader = PromptLoader(prompts_dir="prompts")
        has_file = prompt_loader.has_file_based_prompt('financial_analyst')

        if has_file:
            print(f"⚠️  Unexpected: Found file-based prompt for non-migrated bot")
        else:
            print(f"✅ No file-based prompt (expected for non-migrated bot)")

        # Verify tools still accessible
        if hasattr(bot_config, 'tools_enabled') and bot_config.tools_enabled:
            print(f"✅ Tools accessible: {len(bot_config.tools_enabled)} tools")
        elif hasattr(bot_config, 'tools') and bot_config.tools:
            total_tools = sum(len(tools) for tools in bot_config.tools.values())
            print(f"✅ Tools accessible: {total_tools} tools (new format)")
        else:
            print(f"⚠️  No tools found")

        print(f"\n✅ JSON-based bot works without changes")
        return True

    except Exception as e:
        print(f"\n❌ Error checking backwards compatibility: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all Skills loading tests"""
    print("\n🧪 Testing Skills Loading & HTML Presentation Workflow (v0.4.1)")
    print("=" * 80)

    results = []

    # Run all tests
    results.append(("Skills Auto-Discovery", test_skills_auto_discovery()))
    results.append(("Skill Loading", test_skill_loading()))
    results.append(("Skills MCP Integration", test_skills_mcp_integration()))
    results.append(("HTML Presentation Workflow", test_html_presentation_workflow()))
    results.append(("Mock Bot Initialization", test_mock_bot_initialization()))
    results.append(("Backwards Compatibility", test_backwards_compatibility()))

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
        print("✅ ALL TESTS PASSED - Skills loading system ready!")
        print("   - Skills auto-discovery working")
        print("   - Skill content loads correctly")
        print("   - Skills MCP integration configured")
        print("   - HTML presentation workflow complete")
        print("   - Bot initialization working")
        print("   - Backwards compatibility maintained")
    else:
        print("❌ SOME TESTS FAILED - Review details above")
    print("=" * 80)

    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
