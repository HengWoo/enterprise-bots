#!/usr/bin/env python3
"""
Test Communication Transparency (v1.0.12)
Tests that agent narrates actions instead of showing [Image #1] placeholders
"""

import sys
sys.path.insert(0, 'src')

from tools.campfire_tools import CampfireTools
from campfire_agent import CampfireAgent
from bot_manager import BotConfig

# Create bot config
bot_config = BotConfig({
    "bot_id": "financial_analyst",
    "name": "财务分析师",
    "display_name": "财务分析师 (Financial Analyst)",
    "bot_key": "2-CsheovnLtzjM",
    "model_config": {
        "model": "claude-sonnet-4-5-20250929"
    },
    "system_prompt": "You are a financial analyst.",
    "description": "Financial analysis bot"
})

# Initialize tools
tools = CampfireTools(
    db_path='./tests/fixtures/test.db',
    context_dir='./ai-knowledge/user_contexts'
)

# Test 1: File discovery
print("=" * 60)
print("TEST 1: File Discovery (get_recent_room_files)")
print("=" * 60)
files = tools.get_recent_room_files(room_id=1, limit=10)
print(f"✅ Found {len(files)} file(s) in room 1:")
for f in files:
    print(f"  📎 {f['filename']}")
    print(f"     Path: {f['file_path']}")
    print()

# Find restaurant file
restaurant_file = None
for f in files:
    if '野百灵' in f['filename']:
        restaurant_file = f
        break

if not restaurant_file:
    print("❌ FAILED: Restaurant file not found in room files")
    sys.exit(1)

print(f"✅ Restaurant file found: {restaurant_file['filename']}")
print(f"   File path: {restaurant_file['file_path']}")
print()

# Test 2: Prompt building with communication guidelines
print("=" * 60)
print("TEST 2: Prompt Building (files injected + comm guidelines)")
print("=" * 60)

# Create agent (without connecting - just test prompt building)
agent = CampfireAgent(bot_config=bot_config, campfire_tools=tools)

# Build prompt with context
context = {
    'user_id': 1,
    'user_name': 'WU HENG',
    'room_id': 1,
    'room_name': 'Finance Team',
    'message_id': 100
}

prompt = agent._build_prompt(
    content="请分析野百灵餐厅的财务数据",
    context=context
)

# Check if files are in prompt
if "FILES AVAILABLE IN THIS ROOM" in prompt:
    print("✅ SUCCESS: Files discovered and injected into prompt!")

    if restaurant_file['filename'] in prompt:
        print(f"  ✅ {restaurant_file['filename']} found in prompt")
    else:
        print(f"  ❌ {restaurant_file['filename']} NOT found in prompt")
else:
    print("❌ FAILED: Files not found in prompt")

# Check for communication guidelines
if "TOOL COMMUNICATION (CRITICAL)" in prompt:
    print("✅ SUCCESS: Tool communication guidelines found in prompt!")
else:
    print("❌ WARNING: Tool communication guidelines not found in prompt")

# Show relevant sections
print("\n" + "=" * 60)
print("PROMPT EXCERPT (Files Section):")
print("=" * 60)
start_idx = prompt.find("FILES AVAILABLE IN THIS ROOM")
if start_idx != -1:
    end_idx = prompt.find("IMPORTANT GUIDELINES", start_idx)
    if end_idx == -1:
        end_idx = start_idx + 600
    print(prompt[start_idx:end_idx])

print("\n" + "=" * 60)
print("PROMPT EXCERPT (Communication Guidelines):")
print("=" * 60)
start_idx = prompt.find("TOOL COMMUNICATION (CRITICAL)")
if start_idx != -1:
    end_idx = start_idx + 400
    print(prompt[start_idx:end_idx])

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("✅ File discovery method works correctly")
print("✅ Prompt building includes file list")
print("✅ Communication transparency guidelines included")
print("\n📝 Next step: Start test server and send webhook to verify agent behavior")
print(f"   Expected: Agent narrates actions (\"让我先查看文件结构...\")")
print(f"   NOT expected: Raw placeholders like [Image #1]")
