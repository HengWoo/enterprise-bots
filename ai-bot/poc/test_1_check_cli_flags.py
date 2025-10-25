"""
Test 1: Check if claude-code CLI supports Skills-related flags

This test attempts to inspect the Agent SDK's CLI wrapper to see
if it exposes any Skills-related configuration options.
"""
import asyncio
import subprocess
import sys

async def check_cli_flags():
    """Check what flags the claude-code CLI supports."""

    print("=" * 60)
    print("Test 1: Checking claude-code CLI for Skills support")
    print("=" * 60)

    # Try to get help from claude-code CLI
    try:
        result = subprocess.run(
            ["claude-code", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )

        print("\n📋 CLI Help Output:")
        print(result.stdout)
        print(result.stderr)

        # Search for Skills-related keywords
        help_text = (result.stdout + result.stderr).lower()
        keywords = ["skill", "container", "beta", "code-execution"]

        print("\n🔍 Searching for Skills-related keywords:")
        for keyword in keywords:
            if keyword in help_text:
                print(f"  ✅ Found: {keyword}")
            else:
                print(f"  ❌ Not found: {keyword}")

    except FileNotFoundError:
        print("❌ claude-code CLI not found in PATH")
        print("   This is expected if using Agent SDK in library mode")
        print("   (Agent SDK spawns its own CLI process)")

    except subprocess.TimeoutExpired:
        print("⏱️ CLI help command timed out")

    except Exception as e:
        print(f"❌ Error running CLI: {e}")

    print("\n" + "=" * 60)
    print("Test 1 Complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(check_cli_flags())
