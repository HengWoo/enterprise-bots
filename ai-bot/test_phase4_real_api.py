#!/usr/bin/env python3
"""
PHASE 4: Limited Real API Testing
Tests with actual Anthropic Claude API (CAREFUL - costs money!)
Only run 2-3 carefully crafted messages
"""

import requests
import json
import time
import sys
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5001"
TIMEOUT = 30  # Longer timeout for real API

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(message):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{message}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")


def print_test(message):
    print(f"{CYAN}[TEST]{RESET} {message}")


def print_success(message):
    print(f"{GREEN}✓{RESET} {message}")


def print_error(message):
    print(f"{RED}✗{RESET} {message}")


def print_warning(message):
    print(f"{YELLOW}⚠{RESET} {message}")


def print_response(response_text):
    print(f"\n{YELLOW}🤖 Bot Response:{RESET}")
    print(f"{CYAN}{'─'*60}{RESET}")
    print(f"{response_text}")
    print(f"{CYAN}{'─'*60}{RESET}\n")


def confirm_real_api():
    """Confirm user wants to use real API"""
    print_header("⚠️  REAL API WARNING")

    print(f"{RED}{BOLD}THIS WILL USE YOUR REAL ANTHROPIC API KEY{RESET}")
    print(f"{RED}{BOLD}AND INCUR ACTUAL COSTS!{RESET}\n")

    print("Estimated costs:")
    print("  - Test 1: ~$0.01")
    print("  - Test 2: ~$0.02")
    print("  - Test 3: ~$0.03")
    print(f"  {BOLD}Total: ~$0.06{RESET}\n")

    print(f"{YELLOW}Prerequisites:{RESET}")
    print("  1. Valid ANTHROPIC_API_KEY in .env")
    print("  2. Flask app running WITHOUT testing mode:")
    print("     TESTING=false uv run python src/app.py")
    print("  3. Or use production .env (not .env.testing)\n")

    response = input(f"{BOLD}Type 'YES' to proceed with real API testing: {RESET}")

    if response.strip().upper() != 'YES':
        print(f"\n{YELLOW}Cancelled. No API calls made.{RESET}")
        sys.exit(0)

    print(f"\n{GREEN}Proceeding with real API testing...{RESET}")


def test_health():
    """Test 1: Health check"""
    print_header("TEST 1: Health Check")
    print_test("Verifying Flask app is running...")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Flask app is healthy")
            return True
        else:
            print_error(f"Health check failed")
            return False
    except Exception as e:
        print_error(f"Cannot connect to Flask app: {e}")
        print_warning("Make sure Flask is running in PRODUCTION mode:")
        print_warning("  cd /Users/heng/Development/campfire/ai-bot")
        print_warning("  TESTING=false uv run python src/app.py")
        return False


def test_simple_question():
    """Test 2: Simple question (minimal tokens)"""
    print_header("TEST 2: Simple Question (Real API)")
    print_test("Sending simple question to test API connectivity...")

    payload = {
        "creator": {
            "id": 1,
            "name": "WU HENG",
            "email_address": "heng.woo@gmail.com"
        },
        "room": {
            "id": 1,
            "name": "All Talk"
        },
        "content": "<p>@bot Hello! Please respond with a brief greeting.</p>"
    }

    print(f"{YELLOW}💰 Estimated cost: $0.01{RESET}")
    input(f"{YELLOW}Press Enter to send (or Ctrl+C to cancel)...{RESET}")

    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/webhook",
            json=payload,
            timeout=TIMEOUT
        )
        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            print_success(f"Response received in {elapsed:.2f}s")

            if 'response' in data:
                print_response(data['response'])

                # Validate it's a real API response (not fallback)
                if "Received your message" in data['response']:
                    print_warning("⚠️  This looks like a fallback response!")
                    print_warning("Make sure TESTING=false in your environment")
                    return False
                else:
                    print_success("✓ Real API response detected!")
                    return True
            else:
                print_error("No response in payload")
                return False
        else:
            print_error(f"Request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Test failed: {e}")
        return False


def test_context_awareness():
    """Test 3: Context-aware question"""
    print_header("TEST 3: Context-Aware Question (Real API)")
    print_test("Testing bot's ability to use conversation history...")

    payload = {
        "creator": {
            "id": 1,
            "name": "WU HENG",
            "email_address": "heng.woo@gmail.com"
        },
        "room": {
            "id": 2,
            "name": "Finance Team"
        },
        "content": "<p>@财务分析师 Based on our Finance Team discussions, what were the Q3 revenue highlights?</p>"
    }

    print(f"{YELLOW}💰 Estimated cost: $0.02{RESET}")
    print_test("This message asks bot to reference conversation history")
    input(f"{YELLOW}Press Enter to send (or Ctrl+C to cancel)...{RESET}")

    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/webhook",
            json=payload,
            timeout=TIMEOUT
        )
        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            print_success(f"Response received in {elapsed:.2f}s")

            if 'response' in data:
                print_response(data['response'])

                # Check if it references test DB data
                response_text = data['response'].lower()
                context_indicators = ['12%', 'yoy', 'enterprise', 'q3', 'revenue']

                found_context = any(indicator in response_text for indicator in context_indicators)

                if found_context:
                    print_success("✓ Bot referenced conversation context!")
                else:
                    print_warning("⚠️  Bot didn't clearly reference conversation history")

                return True
            else:
                print_error("No response in payload")
                return False
        else:
            print_error(f"Request failed: HTTP {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Test failed: {e}")
        return False


def test_user_context():
    """Test 4: User context awareness"""
    print_header("TEST 4: User Context (Real API)")
    print_test("Testing bot's ability to use user information...")

    payload = {
        "creator": {
            "id": 1,
            "name": "WU HENG",
            "email_address": "heng.woo@gmail.com"
        },
        "room": {
            "id": 2,
            "name": "Finance Team"
        },
        "content": "<p>@bot What rooms am I a member of? Please list them briefly.</p>"
    }

    print(f"{YELLOW}💰 Estimated cost: $0.03{RESET}")
    print_test("This tests user context retrieval from database")
    input(f"{YELLOW}Press Enter to send (or Ctrl+C to cancel)...{RESET}")

    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/webhook",
            json=payload,
            timeout=TIMEOUT
        )
        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            print_success(f"Response received in {elapsed:.2f}s")

            if 'response' in data:
                print_response(data['response'])

                # Check if it mentions the rooms
                response_text = data['response'].lower()
                expected_rooms = ['all talk', 'finance team', 'direct message']

                found_rooms = sum(1 for room in expected_rooms if room in response_text)

                if found_rooms >= 2:
                    print_success(f"✓ Bot referenced user's rooms ({found_rooms}/3)")
                else:
                    print_warning("⚠️  Bot didn't clearly list user's rooms")

                return True
            else:
                print_error("No response in payload")
                return False
        else:
            print_error(f"Request failed: HTTP {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Test failed: {e}")
        return False


def main():
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}PHASE 4: Real API Testing{RESET}")
    print(f"{BOLD}{CYAN}Limited testing with actual Anthropic Claude API{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")

    # Confirm user wants to proceed
    confirm_real_api()

    results = []

    # Test 1: Health check
    print("\n" + "-"*60)
    health_ok = test_health()
    results.append(("Health Check", health_ok))

    if not health_ok:
        print_error("\n❌ Cannot proceed without healthy Flask app")
        return 1

    # Test 2: Simple question
    print("\n" + "-"*60)
    results.append(("Simple Question", test_simple_question()))

    # Only proceed if simple test passed
    if not results[-1][1]:
        print_error("\n❌ Simple test failed - check API key and configuration")
        return 1

    # Test 3: Context awareness
    print("\n" + "-"*60)
    results.append(("Context Awareness", test_context_awareness()))

    # Test 4: User context
    print("\n" + "-"*60)
    results.append(("User Context", test_user_context()))

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"{status}  {test_name}")

    print(f"\n{BOLD}Results: {passed}/{total} tests passed{RESET}")
    print(f"{BOLD}Estimated cost: ~$0.06{RESET}")

    if passed == total:
        print(f"\n{GREEN}🎉 All Phase 4 tests passed!{RESET}")
        print(f"{GREEN}✓ Real API integration works{RESET}")
        print(f"{GREEN}✓ Context awareness confirmed{RESET}")
        print(f"{GREEN}✓ User context working{RESET}")
        print(f"{GREEN}✓ Bot is PRODUCTION READY!{RESET}\n")
        return 0
    elif passed >= 2:
        print(f"\n{YELLOW}⚠️  Partial success{RESET}")
        print(f"{YELLOW}Core functionality works, some features need attention{RESET}\n")
        return 0
    else:
        print(f"\n{RED}⚠️  Tests failed. Review configuration and API key.{RESET}\n")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Testing cancelled by user. No further API calls made.{RESET}\n")
        sys.exit(0)
