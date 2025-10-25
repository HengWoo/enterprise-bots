#!/usr/bin/env python3
"""
Test Bot Intelligence - Show actual Claude responses
"""

import requests
import json

BASE_URL = "http://localhost:5001"

print("🧠 Testing Bot Intelligence with Real Claude Responses\n")
print("="*60)

# Test 1: Q3 Revenue Context
print("\n📊 TEST 1: Conversation Context Awareness")
print("-"*60)

print("\nSending: '@财务分析师 What were the Q3 revenue trends we discussed?'")
print("Expected: Bot should reference the Finance Team conversation history\n")

response = requests.post(
    f"{BASE_URL}/webhook",
    json={
        "creator": {"id": 1, "name": "WU HENG", "email_address": "heng.woo@gmail.com"},
        "room": {"id": 2, "name": "Finance Team"},
        "content": "<p>@财务分析师 What were the Q3 revenue trends we discussed?</p>"
    },
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Note: In test mode, the actual Claude response is printed to console
# but not sent to Campfire. We'd see it in the Flask logs.

print("\n" + "="*60)
print("\n✅ Check Flask logs above to see the actual Claude AI responses")
print("   The bot should demonstrate:")
print("   - Knowledge of conversation history")
print("   - Understanding of user context")
print("   - Contextually relevant financial analysis\n")
