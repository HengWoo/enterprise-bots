#!/usr/bin/env python3
"""
PHASE 1: Test CampfireTools Directly
Tests database access and tools WITHOUT Flask or API calls
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tools.campfire_tools import CampfireTools

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


def print_data(label, data):
    print(f"{YELLOW}{label}:{RESET}")
    if isinstance(data, list):
        for item in data:
            print(f"  - {item}")
    elif isinstance(data, dict):
        for key, value in data.items():
            print(f"  {key}: {value}")
    else:
        print(f"  {data}")


def test_database_connection():
    """Test 1: Database connection"""
    print_header("TEST 1: Database Connection")
    print_test("Attempting to connect to test database...")

    try:
        tools = CampfireTools(
            db_path="./tests/fixtures/test.db",
            context_dir="./test_contexts"
        )
        print_success("Database connection successful")
        return tools
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return None


def test_search_conversations(tools):
    """Test 2: Search conversations"""
    print_header("TEST 2: Search Conversations")

    # Test 2a: Search for "revenue"
    print_test("Searching for 'revenue' in all rooms...")
    try:
        results = tools.search_conversations("revenue", limit=5)
        print_success(f"Found {len(results)} messages containing 'revenue'")

        for i, msg in enumerate(results, 1):
            print(f"\n  {BOLD}Message {i}:{RESET}")
            print(f"    Room: {msg['room_name']}")
            print(f"    User: {msg['creator_name']}")
            print(f"    Body: {msg['body'][:80]}...")
            print(f"    Date: {msg['created_at']}")

    except Exception as e:
        print_error(f"Search failed: {e}")
        return False

    # Test 2b: Search in specific room
    print_test("\nSearching for 'Q3' in Finance Team room (room_id=2)...")
    try:
        results = tools.search_conversations("Q3", room_id=2, limit=3)
        print_success(f"Found {len(results)} messages in Finance Team")

        for i, msg in enumerate(results, 1):
            print(f"\n  {BOLD}Message {i}:{RESET}")
            print(f"    User: {msg['creator_name']}")
            print(f"    Body: {msg['body'][:80]}...")

    except Exception as e:
        print_error(f"Room-specific search failed: {e}")
        return False

    return True


def test_user_context(tools):
    """Test 3: User context retrieval"""
    print_header("TEST 3: Get User Context")

    # Test 3a: Get context for user 1 (WU HENG)
    print_test("Getting context for user 1 (WU HENG)...")
    try:
        context = tools.get_user_context(user_id=1)
        print_success("User context retrieved successfully")

        print_data("\n  User Info", {
            "ID": context.get('user_id'),
            "Name": context.get('user_name'),
            "Email": context.get('email')
        })

        print_data("\n  Rooms", [
            f"{room['room_name']} (ID: {room['room_id']}, Type: {room['room_type']})"
            for room in context.get('rooms', [])
        ])

        if 'preferences' in context:
            print_data("\n  Saved Preferences", context['preferences'])
        else:
            print(f"  {YELLOW}No saved preferences found{RESET}")

    except Exception as e:
        print_error(f"Get user context failed: {e}")
        return False

    # Test 3b: Get context for user 2 (John Smith)
    print_test("\nGetting context for user 2 (John Smith)...")
    try:
        context = tools.get_user_context(user_id=2)
        print_success(f"User: {context.get('user_name')}")
        print_data("  Rooms", [
            room['room_name'] for room in context.get('rooms', [])
        ])

    except Exception as e:
        print_error(f"Get user 2 context failed: {e}")
        return False

    return True


def test_save_user_context(tools):
    """Test 4: Save user context"""
    print_header("TEST 4: Save User Context")

    print_test("Saving preferences for test user...")
    try:
        tools.save_user_context(
            user_id=999,
            preferences={
                "language": "en",
                "tone": "professional",
                "timezone": "UTC+8"
            },
            expertise=["finance", "data analysis", "forecasting"],
            conversation_memory=["Discussed Q4 planning on 2025-01-15"]
        )
        print_success("User context saved successfully")

    except Exception as e:
        print_error(f"Save failed: {e}")
        return False

    # Verify it was saved
    print_test("Retrieving saved context to verify...")
    try:
        context = tools.get_user_context(user_id=999)
        print_success("Context retrieved successfully")

        print_data("\n  Preferences", context.get('preferences', {}))
        print_data("\n  Expertise", context.get('expertise', []))
        print_data("\n  Conversation Memory", context.get('conversation_memory', []))

        if context.get('last_updated'):
            print(f"\n  {GREEN}Last Updated:{RESET} {context['last_updated']}")

    except Exception as e:
        print_error(f"Verification failed: {e}")
        return False

    return True


def main():
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}PHASE 1: CampfireTools Direct Testing{RESET}")
    print(f"{BOLD}{CYAN}No Flask, No API - Database Tools Only{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")

    results = []

    # Test 1: Database connection
    tools = test_database_connection()
    if not tools:
        print_error("\n❌ Cannot proceed without database connection")
        return 1

    results.append(("Database Connection", True))

    # Test 2: Search conversations
    results.append(("Search Conversations", test_search_conversations(tools)))

    # Test 3: User context
    results.append(("User Context Retrieval", test_user_context(tools)))

    # Test 4: Save context
    results.append(("Save User Context", test_save_user_context(tools)))

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"{status}  {test_name}")

    print(f"\n{BOLD}Results: {passed}/{total} tests passed{RESET}")

    if passed == total:
        print(f"\n{GREEN}🎉 All Phase 1 tests passed!{RESET}")
        print(f"{GREEN}✓ Database access works{RESET}")
        print(f"{GREEN}✓ Tools function correctly{RESET}")
        print(f"{GREEN}✓ Ready for Phase 2 (Flask testing){RESET}\n")
        return 0
    else:
        print(f"\n{RED}⚠️  Some tests failed. Fix issues before proceeding.{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
