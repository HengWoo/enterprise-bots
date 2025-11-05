"""Test menu_engineer migration"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from bot_manager import BotManager
from prompt_loader import PromptLoader

def main():
    print("\n" + "="*60)
    print("Testing menu_engineer migration...")
    print("="*60)
    
    # Test YAML config loading
    manager = BotManager(bots_dirs=['bots', 'prompts/configs'])
    config = manager.load_bot_config('menu_engineer')
    
    assert config is not None, "Failed to load config"
    assert config.system_prompt_file == "menu_engineer.md", f"Wrong prompt file: {config.system_prompt_file}"
    print(f"✅ YAML config loaded: {config.system_prompt_file}")
    print(f"   Bot key: {config.bot_key}")
    print(f"   MCP servers: {config.mcp_servers}")
    
    # Test prompt loading
    loader = PromptLoader(prompts_dir='prompts')
    context = {
        'current_date': '2025-11-04',
        'user_name': 'Test User',
        'room_name': 'Test Room'
    }
    
    prompt = loader.load_bot_prompt('menu_engineer', context)
    assert prompt, "Failed to load prompt"
    assert '$current_date' not in prompt, "Template variable not substituted"
    assert '2025-11-04' in prompt, "Date not substituted"
    print(f"✅ Prompt loaded: {len(prompt)} chars")
    print(f"   Template variables substituted correctly")
    
    # Test Skill tool
    builtin_tools = config.tools.get('builtin', [])
    assert 'Skill' in builtin_tools, "Skill tool not found"
    print(f"✅ Native Skill tool enabled")
    
    # Test menu engineering tools
    campfire_tools = config.tools.get('campfire', [])
    menu_tools = [
        'get_menu_profitability',
        'get_top_profitable_dishes',
        'get_low_profit_dishes',
        'get_cost_coverage_rate',
        'get_dishes_missing_cost'
    ]
    for tool in menu_tools:
        assert tool in campfire_tools, f"Missing menu tool: {tool}"
    print(f"✅ All 5 menu engineering tools configured")
    
    print(f"\n{'='*60}")
    print("✅ menu_engineer migration PASSED")
    print(f"{'='*60}\n")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
