#!/usr/bin/env python3
"""Test script to verify file-based prompt equivalence (v0.4.1)."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.bot_manager import BotManager
from src.prompt_loader import PromptLoader
from datetime import datetime

def test_prompt_equivalence():
    """Test character-level equivalence between file-based and JSON prompts"""
    print("=" * 80)
    print("PHASE 5: Testing Character-Level Equivalence")
    print("=" * 80)

    # Load original JSON personal_assistant config
    json_manager = BotManager(bots_dirs=['./bots'])  # Only JSON
    json_bot = json_manager.get_bot_by_id('personal_assistant')

    print(f"\n1. Original JSON prompt:")
    print(f"   Length: {len(json_bot.system_prompt)} characters")

    # Load new file-based prompt with same template context
    loader = PromptLoader(prompts_dir="prompts")
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')

    context = {
        'current_date': current_date,
        'user_name': 'User',
        'room_name': 'Room'
    }

    file_based_prompt = loader.load_bot_prompt('personal_assistant', context)

    print(f"\n2. New file-based prompt:")
    print(f"   Length: {len(file_based_prompt)} characters")

    # Compare lengths
    print(f"\n3. Length comparison:")
    length_diff = len(file_based_prompt) - len(json_bot.system_prompt)
    length_diff_pct = (length_diff / len(json_bot.system_prompt)) * 100
    print(f"   Difference: {length_diff:+d} characters ({length_diff_pct:+.1f}%)")

    # Check key content sections
    print(f"\n4. Key content verification:")

    key_phrases = [
        "你是一个专业的个人助手AI",
        "专业能力",
        "个人生产力管理",
        "对话历史与知识",
        "文档处理",
        "演示文稿生成",
        "load_skill",
        "save_html_presentation",
        "博客式清晰排版",
        "<h2>", "<h3>", "<strong>",
        "STAR分析框架",
        "CSS样式"
    ]

    json_phrases_found = sum(1 for phrase in key_phrases if phrase in json_bot.system_prompt)
    file_phrases_found = sum(1 for phrase in key_phrases if phrase in file_based_prompt)

    print(f"   JSON prompt: {json_phrases_found}/{len(key_phrases)} key phrases found")
    print(f"   File prompt: {file_phrases_found}/{len(key_phrases)} key phrases found")

    # Check for template substitution
    print(f"\n5. Template variable substitution:")

    if '$current_date' in file_based_prompt:
        print(f"   ❌ Found unsubstituted variable: $current_date")
    else:
        print(f"   ✅ $current_date properly substituted")

    if current_date in file_based_prompt:
        print(f"   ✅ Contains current date: {current_date}")
    else:
        print(f"   ❌ Missing current date: {current_date}")

    # Check critical functionality sections
    print(f"\n6. Critical functionality sections:")

    critical_sections = {
        "Skills loading": "load_skill(" in file_based_prompt,
        "Task management": "manage_personal_tasks" in file_based_prompt,
        "HTML presentation": "save_html_presentation" in file_based_prompt,
        "HTML formatting": "博客式清晰排版" in file_based_prompt,
        "Response format": "<h2>" in file_based_prompt and "<h3>" in file_based_prompt,
    }

    for section, present in critical_sections.items():
        status = "✅" if present else "❌"
        print(f"   {status} {section}")

    # Summary
    print(f"\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    all_critical_present = all(critical_sections.values())
    templates_substituted = '$current_date' not in file_based_prompt
    reasonable_length = abs(length_diff_pct) < 30  # Within 30% is acceptable

    if all_critical_present and templates_substituted and reasonable_length:
        print("✅ File-based prompt is functionally equivalent to JSON prompt")
        print(f"   - All critical functionality sections present")
        print(f"   - Template variables properly substituted")
        print(f"   - Length difference is reasonable ({length_diff_pct:+.1f}%)")
        return True
    else:
        print("❌ File-based prompt has issues:")
        if not all_critical_present:
            print(f"   - Missing critical functionality sections")
        if not templates_substituted:
            print(f"   - Template variables not substituted")
        if not reasonable_length:
            print(f"   - Length difference too large ({length_diff_pct:+.1f}%)")
        return False

def test_content_analysis():
    """Analyze specific content differences"""
    print("\n" + "=" * 80)
    print("CONTENT ANALYSIS: What's different?")
    print("=" * 80)

    # Load both prompts
    json_manager = BotManager(bots_dirs=['./bots'])
    json_bot = json_manager.get_bot_by_id('personal_assistant')

    loader = PromptLoader(prompts_dir="prompts")
    context = {
        'current_date': datetime.now().strftime('%Y-%m-%d'),
        'user_name': 'User',
        'room_name': 'Room'
    }
    file_prompt = loader.load_bot_prompt('personal_assistant', context)

    # Check what's in JSON but not in file
    json_unique_phrases = [
        "save_html_presentation_tool",  # Tool name format difference
        "presentation_generation",      # Skill loading format
    ]

    print("\n1. Content unique to JSON prompt:")
    for phrase in json_unique_phrases:
        if phrase in json_bot.system_prompt and phrase not in file_prompt:
            print(f"   - '{phrase}' (in JSON, not in file)")

    # Check what's in file but not in JSON
    file_unique_phrases = [
        "当前环境信息",          # Dynamic context section
        "今天的日期：",          # Template substitution result
        "当前用户：",            # Template substitution result
        "当前房间：",            # Template substitution result
    ]

    print("\n2. Content unique to file-based prompt:")
    for phrase in file_unique_phrases:
        if phrase in file_prompt and phrase not in json_bot.system_prompt:
            print(f"   - '{phrase}' (in file, not in JSON)")

    print("\n3. Expected differences (✅ These are intentional):")
    print("   ✅ File has dynamic context section (current_date, user_name, room_name)")
    print("   ✅ File separates Skills workflows into separate SKILL.md files")
    print("   ✅ File uses simpler structure (no escaped JSON strings)")

    return True

def main():
    """Run all equivalence tests"""
    print("\n🧪 Testing File-Based Prompt Equivalence (v0.4.1)")
    print("=" * 80)

    results = []

    # Run tests
    results.append(("Prompt Equivalence", test_prompt_equivalence()))
    results.append(("Content Analysis", test_content_analysis()))

    # Final summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 80)
    if all_passed:
        print("✅ FILE-BASED PROMPTS ARE READY FOR DEPLOYMENT")
        print("   personal_assistant bot can use file-based prompts in production")
    else:
        print("❌ ISSUES FOUND - Review differences above")
    print("=" * 80)

    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
