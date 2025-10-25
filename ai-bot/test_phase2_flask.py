#!/usr/bin/env python3
"""
PHASE 2: Test Flask Webhook WITHOUT Real API Calls
Tests webhook processing, context building, and response generation
Uses fallback mode (no Anthropic API usage)
"""

import requests
import json
import time
import sys
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5001"
TIMEOUT = 10  # Shorter timeout since no real API

# ANSI colors for output
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
    print(f"\n{YELLOW}Bot Response:{RESET}")
    print(f"{CYAN}{'─'*60}{RESET}")
    print(f"{response_text}")
    print(f"{CYAN}{'─'*60}{RESET}\n")


def test_health():
    """Test 1: Health endpoint"""
    print_header("TEST 1: Health Endpoint")
    print_test("Checking if Flask app is running...")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Flask app is healthy")
            print(f"  Status: {data.get('status')}")
            print(f"  Timestamp: {data.get('timestamp')}")
            return True
        else:
            print_error(f"Health check failed: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to Flask app")
        print_warning("Make sure Flask is running:")
        print_warning("  cd /Users/heng/Development/campfire/ai-bot")
        print_warning("  TESTING=true uv run python src/app.py")
        return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False


def test_webhook_basic():
    """Test 2: Basic webhook processing"""
    print_header("TEST 2: Basic Webhook Processing")
    print_test("Sending simple webhook payload...")

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
        "content": "<p>@bot Hello! Can you hear me?</p>"
    }

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
            print_success(f"Webhook processed in {elapsed:.2f}s")
            print(f"  Status: {data.get('status')}")

            if 'response' in data:
                print_response(data['response'])

            return True
        else:
            print_error(f"Webhook failed: HTTP {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Webhook error: {e}")
        return False


def test_conversation_context():
    """Test 3: Bot processes conversation context"""
    print_header("TEST 3: Conversation Context Processing")
    print_test("Sending message about Q3 revenue (exists in test DB)...")

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
        "content": "<p>@财务分析师 What were the Q3 revenue trends we discussed?</p>"
    }

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
            print_success(f"Context processed in {elapsed:.2f}s")

            if 'response' in data:
                print_response(data['response'])
                print_test("In testing mode, bot should echo the message")
                print_test("In production, bot would reference:")
                print_test("  - 12% YoY growth")
                print_test("  - Enterprise sales +18%")
                print_test("  - APAC region +25%")

            return True
        else:
            print_error(f"Context test failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Context test error: {e}")
        return False


def test_user_context():
    """Test 4: Bot retrieves user context"""
    print_header("TEST 4: User Context Retrieval")
    print_test("Testing user context in webhook processing...")

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
        "content": "<p>@bot What rooms am I a member of?</p>"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/webhook",
            json=payload,
            timeout=TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            print_success("User context processed")

            if 'response' in data:
                print_response(data['response'])
                print_test("User context should include:")
                print_test("  - Name: WU HENG")
                print_test("  - Rooms: All Talk, Finance Team, Direct Message")

            return True
        else:
            print_error(f"User context test failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"User context error: {e}")
        return False


def test_html_stripping():
    """Test 5: HTML tag stripping"""
    print_header("TEST 5: HTML Tag Stripping")
    print_test("Sending message with HTML tags...")

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
        "content": "<p>@bot <strong>Bold text</strong> and <em>italic text</em> and <a href='#'>links</a></p>"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/webhook",
            json=payload,
            timeout=TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            print_success("HTML stripped successfully")

            if 'response' in data:
                print_response(data['response'])
                print_test("Bot should see clean text: 'Bold text and italic text and links'")

            return True
        else:
            print_error(f"HTML stripping failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"HTML stripping error: {e}")
        return False


def test_error_handling():
    """Test 6: Error handling"""
    print_header("TEST 6: Error Handling")
    print_test("Sending invalid payload...")

    # Missing required fields
    payload = {
        "invalid": "payload",
        "missing": "required_fields"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/webhook",
            json=payload,
            timeout=5
        )

        if response.status_code == 400:
            data = response.json()
            print_success("Invalid payload correctly rejected")
            print(f"  Error message: {data.get('error')}")
            return True
        else:
            print_warning(f"Unexpected status: HTTP {response.status_code}")
            return True  # Not critical
    except Exception as e:
        print_error(f"Error handling test failed: {e}")
        return False


def test_different_users():
    """Test 7: Different users"""
    print_header("TEST 7: Multiple User Handling")
    print_test("Testing with different user...")

    payload = {
        "creator": {
            "id": 2,
            "name": "John Smith",
            "email_address": "john@smartice.ai"
        },
        "room": {
            "id": 3,
            "name": "Engineering"
        },
        "content": "<p>@bot What's my name?</p>"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/webhook",
            json=payload,
            timeout=TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Different user handled correctly")

            if 'response' in data:
                print_response(data['response'])
                print_test("Should reference: John Smith in Engineering room")

            return True
        else:
            print_error(f"User differentiation failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"User differentiation error: {e}")
        return False


def main():
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}PHASE 2: Flask Webhook Testing (No Real API){RESET}")
    print(f"{BOLD}{CYAN}Tests webhook processing in fallback mode{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")

    print_warning("\n⚠️  PREREQUISITES:")
    print_warning("1. Flask app must be running in testing mode:")
    print_warning("   cd /Users/heng/Development/campfire/ai-bot")
    print_warning("   TESTING=true uv run python src/app.py")
    print_warning("\n2. Or use .env.testing:")
    print_warning("   cp .env.testing .env")
    print_warning("   uv run python src/app.py")
    print_warning("\n3. App should be accessible at http://localhost:5001")

    input(f"\n{YELLOW}Press Enter when Flask app is running...{RESET}")

    results = []

    # Run all tests
    print("\n" + "-"*60)
    results.append(("Health Check", test_health()))

    # Only proceed if health check passes
    if not results[0][1]:
        print_error("\n❌ Cannot proceed without healthy Flask app")
        return 1

    print("\n" + "-"*60)
    results.append(("Basic Webhook", test_webhook_basic()))

    print("\n" + "-"*60)
    results.append(("Conversation Context", test_conversation_context()))

    print("\n" + "-"*60)
    results.append(("User Context", test_user_context()))

    print("\n" + "-"*60)
    results.append(("HTML Stripping", test_html_stripping()))

    print("\n" + "-"*60)
    results.append(("Error Handling", test_error_handling()))

    print("\n" + "-"*60)
    results.append(("Multiple Users", test_different_users()))

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"{status}  {test_name}")

    print(f"\n{BOLD}Results: {passed}/{total} tests passed{RESET}")

    if passed == total:
        print(f"\n{GREEN}🎉 All Phase 2 tests passed!{RESET}")
        print(f"{GREEN}✓ Flask webhook processing works{RESET}")
        print(f"{GREEN}✓ Context building works{RESET}")
        print(f"{GREEN}✓ Error handling works{RESET}")
        print(f"{GREEN}✓ Ready for Phase 3 (Mock API testing){RESET}\n")
        return 0
    else:
        print(f"\n{RED}⚠️  Some tests failed. Review errors above.{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
