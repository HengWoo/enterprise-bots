"""
Comprehensive local test for all 7 migrated bots
Tests bot configuration loading, prompt loading, and tool availability
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from bot_manager import BotManager
from prompt_loader import PromptLoader

# All 7 bots that should be using file-based prompts
ALL_BOTS = [
    'personal_assistant',
    'cc_tutor', 
    'technical_assistant',
    'briefing_assistant',
    'operations_assistant',
    'financial_analyst',
    'menu_engineer'
]

def test_bot_loading(bot_id: str):
    """Test that a bot loads correctly with file-based prompts"""
    print(f"\n{'='*60}")
    print(f"Testing {bot_id}...")
    print(f"{'='*60}")
    
    # Initialize managers
    manager = BotManager(bots_dirs=['bots', 'prompts/configs'])
    loader = PromptLoader(prompts_dir='prompts')
    
    # Load bot config
    config = manager.load_bot_config(bot_id)
    assert config is not None, f"Failed to load config for {bot_id}"
    assert config.system_prompt_file, f"No system_prompt_file for {bot_id}"
    
    print(f"✅ Config loaded: {config.system_prompt_file}")
    print(f"   Bot key: {config.bot_key}")
    print(f"   Model: {config.model}")
    print(f"   MCP servers: {config.mcp_servers}")
    
    # Load prompt with template variables
    context = {
        'current_date': '2025-11-04',
        'user_name': 'Test User',
        'room_name': 'Test Room'
    }
    
    prompt = loader.load_bot_prompt(bot_id, context)
    assert prompt, f"Failed to load prompt for {bot_id}"
    assert '$current_date' not in prompt, f"Template vars not substituted in {bot_id}"
    assert '2025-11-04' in prompt, f"Date not substituted in {bot_id}"
    
    print(f"✅ Prompt loaded: {len(prompt)} chars")
    
    # Check for Skill tool
    builtin_tools = config.tools.get('builtin', [])
    assert 'Skill' in builtin_tools, f"Skill tool missing for {bot_id}"
    
    print(f"✅ Native Skill tool enabled")
    
    # Check tool counts
    campfire_tools = config.tools.get('campfire', [])
    print(f"✅ Campfire tools: {len(campfire_tools)}")
    
    # Bot-specific checks
    if bot_id == 'financial_analyst':
        assert 'fin-report-agent' in config.mcp_servers, "Financial MCP missing"
        print(f"✅ Financial MCP configured (17 tools)")
    
    if bot_id == 'menu_engineer':
        assert 'get_menu_profitability' in campfire_tools, "Menu tools missing"
        print(f"✅ Menu engineering tools configured")
    
    if bot_id == 'operations_assistant':
        assert 'get_daily_revenue' in campfire_tools, "Operations tools missing"
        print(f"✅ Operations analytics tools configured")
    
    print(f"✅ {bot_id} validation PASSED")
    return True

def main():
    """Test all 7 bots"""
    print("\n" + "="*70)
    print("COMPREHENSIVE LOCAL TEST - ALL 7 MIGRATED BOTS")
    print("="*70)
    print(f"\nTesting {len(ALL_BOTS)} bots with file-based prompts...")
    
    results = {}
    
    for bot_id in ALL_BOTS:
        try:
            test_bot_loading(bot_id)
            results[bot_id] = "✅ PASS"
        except Exception as e:
            results[bot_id] = f"❌ FAIL: {e}"
            print(f"\n❌ {bot_id} failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for bot_id, result in results.items():
        status = result.split(":")[0]
        print(f"{bot_id:25} {status}")
    
    passed = sum(1 for r in results.values() if r.startswith("✅"))
    total = len(results)
    
    print(f"\n{'='*70}")
    print(f"RESULT: {passed}/{total} bots passed ({passed/total*100:.0f}%)")
    print(f"{'='*70}")
    
    if passed == total:
        print("\n🎉 ALL BOTS VALIDATED - READY FOR DEPLOYMENT!")
    else:
        print(f"\n⚠️  {total - passed} bot(s) failed validation")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
