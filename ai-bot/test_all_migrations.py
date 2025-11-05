"""Test all 4 migrated bots: technical_assistant, briefing_assistant, operations_assistant, financial_analyst"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bot_manager import BotManager
from prompt_loader import PromptLoader

def test_bot_migration(bot_id: str):
    """Test that a bot can load YAML config and markdown prompt"""
    print(f"\n{'='*60}")
    print(f"Testing {bot_id} migration...")
    print(f"{'='*60}")
    
    # Test YAML config loading
    manager = BotManager(bots_dirs=['bots', 'prompts/configs'])
    config = manager.load_bot_config(bot_id)
    
    assert config is not None, f"Failed to load config for {bot_id}"
    assert config.system_prompt_file, f"No system_prompt_file in {bot_id} config"
    print(f"✅ YAML config loaded: {config.system_prompt_file}")
    print(f"   Bot key: {config.bot_key}")
    print(f"   MCP servers: {config.mcp_servers}")
    
    # Test prompt loading with template variables
    loader = PromptLoader(prompts_dir='prompts')
    context = {
        'current_date': '2025-11-04',
        'user_name': 'Test User',
        'room_name': 'Test Room'
    }
    
    prompt = loader.load_bot_prompt(bot_id, context)
    assert prompt, f"Failed to load prompt for {bot_id}"
    assert '$current_date' not in prompt, "Template variable not substituted"
    assert '2025-11-04' in prompt, "Date not substituted correctly"
    print(f"✅ Prompt loaded: {len(prompt)} chars")
    print(f"   Template variables substituted correctly")
    
    # Test Skill tool in builtin tools
    builtin_tools = config.tools.get('builtin', [])
    assert 'Skill' in builtin_tools, f"Skill tool not in builtin tools for {bot_id}"
    print(f"✅ Native Skill tool enabled")
    
    # Test file existence using correct relative paths
    base_dir = Path('/Users/heng/Development/campfire/ai-bot')
    prompt_file = base_dir / 'prompts' / 'bots' / f"{bot_id}.md"
    yaml_file = base_dir / 'prompts' / 'configs' / f"{bot_id}.yaml"
    assert prompt_file.exists(), f"Prompt file not found: {prompt_file}"
    assert yaml_file.exists(), f"YAML file not found: {yaml_file}"
    print(f"✅ Files exist:")
    print(f"   - {prompt_file}")
    print(f"   - {yaml_file}")
    
    return True

def main():
    """Test all 4 migrated bots"""
    bots = [
        'technical_assistant',
        'briefing_assistant', 
        'operations_assistant',
        'financial_analyst'
    ]
    
    print("\n" + "="*60)
    print("BATCH MIGRATION VALIDATION TEST")
    print("Testing 4 bots migrated to file-based prompts")
    print("="*60)
    
    results = {}
    for bot_id in bots:
        try:
            test_bot_migration(bot_id)
            results[bot_id] = "✅ PASS"
        except Exception as e:
            results[bot_id] = f"❌ FAIL: {e}"
            print(f"\n❌ {bot_id} failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    for bot_id, result in results.items():
        print(f"{bot_id:25} {result}")
    
    passed = sum(1 for r in results.values() if r == "✅ PASS")
    total = len(results)
    print(f"\n{'='*60}")
    print(f"RESULT: {passed}/{total} bots passed validation")
    print(f"{'='*60}\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
