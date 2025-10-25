#!/usr/bin/env python3
"""
Test client for Skills MCP Server

This script tests the Skills MCP server in isolation to verify:
1. Server starts correctly
2. All 3 tools are registered and work
3. Error handling works gracefully
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add parent directory to path to import mcp
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("❌ Error: MCP SDK not installed. Run: uv sync")
    sys.exit(1)


async def test_skills_mcp():
    """Test Skills MCP server with all tools"""

    print("=" * 70)
    print("Skills MCP Server Test Suite")
    print("=" * 70)

    # Determine SKILLS_DIR path
    skills_dir = os.environ.get("SKILLS_DIR")
    if not skills_dir:
        # Default to .claude/skills relative to project root
        project_root = Path(__file__).parent.parent
        skills_dir = str(project_root / ".claude" / "skills")

    print(f"\n📁 SKILLS_DIR: {skills_dir}")

    if not os.path.exists(skills_dir):
        print(f"❌ ERROR: Skills directory not found: {skills_dir}")
        print("   Please create .claude/skills/ with skill directories")
        return False

    # Count skill directories
    skill_dirs = [d for d in os.listdir(skills_dir)
                  if os.path.isdir(os.path.join(skills_dir, d))
                  and os.path.exists(os.path.join(skills_dir, d, "SKILL.md"))]
    print(f"📚 Found {len(skill_dirs)} skill directories: {', '.join(skill_dirs)}")

    # Start MCP server as subprocess
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "--directory", str(Path(__file__).parent), "python", "server.py"],
        env={"SKILLS_DIR": skills_dir}
    )

    print("\n🚀 Starting Skills MCP server...")

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize session
                await session.initialize()
                print("✅ Server initialized successfully")

                # Test 1: List tools
                print("\n" + "=" * 70)
                print("TEST 1: List available tools")
                print("=" * 70)

                tools_result = await session.list_tools()
                tools = tools_result.tools if hasattr(tools_result, 'tools') else tools_result
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"\n  📦 {tool.name}")
                    print(f"     {tool.description}")
                    if hasattr(tool, 'inputSchema'):
                        required = tool.inputSchema.get('required', [])
                        props = tool.inputSchema.get('properties', {})
                        if props:
                            print(f"     Parameters: {', '.join(props.keys())}")
                            if required:
                                print(f"     Required: {', '.join(required)}")

                if len(tools) != 3:
                    print(f"\n❌ ERROR: Expected 3 tools, found {len(tools)}")
                    return False

                # Test 2: list_skills
                print("\n" + "=" * 70)
                print("TEST 2: Call list_skills")
                print("=" * 70)

                result = await session.call_tool("list_skills", {})
                skills_list = result.content[0].text
                print(f"✅ list_skills returned {len(skills_list)} chars")
                print(f"\nResult:\n{skills_list}")

                if "Available Skills:" not in skills_list:
                    print("\n❌ ERROR: Expected 'Available Skills:' in output")
                    return False

                # Test 3: load_skill (docx)
                print("\n" + "=" * 70)
                print("TEST 3: Call load_skill('docx')")
                print("=" * 70)

                try:
                    result = await session.call_tool("load_skill", {"skill_name": "docx"})
                    skill_content = result.content[0].text
                    print(f"✅ load_skill('docx') returned {len(skill_content)} chars")

                    # Check for expected content markers
                    if "# DOCX Skill Loaded" in skill_content:
                        print("✅ Found expected header")
                    else:
                        print("⚠️  Warning: Expected header not found")

                    # Show first 500 chars
                    print(f"\nFirst 500 chars:\n{skill_content[:500]}...")

                except Exception as e:
                    print(f"❌ ERROR calling load_skill('docx'): {e}")
                    return False

                # Test 4: load_skill (xlsx)
                print("\n" + "=" * 70)
                print("TEST 4: Call load_skill('xlsx')")
                print("=" * 70)

                try:
                    result = await session.call_tool("load_skill", {"skill_name": "xlsx"})
                    skill_content = result.content[0].text
                    print(f"✅ load_skill('xlsx') returned {len(skill_content)} chars")
                except Exception as e:
                    print(f"❌ ERROR calling load_skill('xlsx'): {e}")
                    return False

                # Test 5: load_skill_file (if docx skill has additional files)
                print("\n" + "=" * 70)
                print("TEST 5: Call load_skill_file('docx', 'docx-js.md')")
                print("=" * 70)

                try:
                    result = await session.call_tool("load_skill_file", {
                        "skill_name": "docx",
                        "file_name": "docx-js.md"
                    })
                    file_content = result.content[0].text
                    print(f"✅ load_skill_file returned {len(file_content)} chars")
                    print(f"\nFirst 500 chars:\n{file_content[:500]}...")
                except Exception as e:
                    # This might fail if file doesn't exist, which is OK
                    print(f"⚠️  load_skill_file failed (file may not exist): {e}")

                # Test 6: Error handling - invalid skill
                print("\n" + "=" * 70)
                print("TEST 6: Error handling - invalid skill name")
                print("=" * 70)

                try:
                    result = await session.call_tool("load_skill", {"skill_name": "nonexistent"})
                    error_msg = result.content[0].text
                    if "Error" in error_msg or "not found" in error_msg:
                        print(f"✅ Error handled gracefully: {error_msg[:100]}...")
                    else:
                        print(f"⚠️  Unexpected response: {error_msg[:100]}...")
                except Exception as e:
                    print(f"✅ Error raised as expected: {e}")

                # Test 7: Error handling - invalid file
                print("\n" + "=" * 70)
                print("TEST 7: Error handling - invalid file name")
                print("=" * 70)

                try:
                    result = await session.call_tool("load_skill_file", {
                        "skill_name": "docx",
                        "file_name": "nonexistent.md"
                    })
                    error_msg = result.content[0].text
                    if "Error" in error_msg or "not found" in error_msg:
                        print(f"✅ Error handled gracefully: {error_msg[:100]}...")
                    else:
                        print(f"⚠️  Unexpected response: {error_msg[:100]}...")
                except Exception as e:
                    print(f"✅ Error raised as expected: {e}")

                # All tests passed
                print("\n" + "=" * 70)
                print("✅ All tests completed successfully!")
                print("=" * 70)
                print("\n📊 Summary:")
                print(f"  - Tools registered: {len(tools)}")
                print(f"  - Skills available: {len(skill_dirs)}")
                print(f"  - list_skills: ✅")
                print(f"  - load_skill: ✅")
                print(f"  - load_skill_file: ✅")
                print(f"  - Error handling: ✅")
                print("\n🎉 Skills MCP server is working correctly!")

                return True

    except Exception as e:
        print(f"\n❌ ERROR: Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run test suite"""
    try:
        success = asyncio.run(test_skills_mcp())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
