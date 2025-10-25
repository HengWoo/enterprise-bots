"""
Test script for process_image_tool
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools.image_decorators import _process_image_impl

async def test_image_processing():
    """Test the process_image_tool function"""

    print("=" * 60)
    print("Testing process_image_tool")
    print("=" * 60)

    # Test 1: File not found
    print("\n📝 Test 1: File not found")
    result1 = await _process_image_impl({
        "file_path": "/nonexistent/path/to/image.jpg",
        "question": "What's in this image?"
    })
    print(f"Result: {result1[:100]}...")
    assert "File not found" in result1, "Should return file not found error"
    print("✅ Test 1 passed")

    # Test 2: Unsupported format
    print("\n📝 Test 2: Unsupported format")
    # Create a dummy .txt file
    test_file = "/tmp/test.txt"
    with open(test_file, 'w') as f:
        f.write("test")
    result2 = await _process_image_impl({
        "file_path": test_file,
        "question": "What's in this image?"
    })
    print(f"Result: {result2[:100]}...")
    assert "Unsupported file format" in result2, "Should return unsupported format error"
    print("✅ Test 2 passed")
    os.remove(test_file)

    # Test 3: Valid JPEG file (but no ANTHROPIC_API_KEY for actual processing)
    print("\n📝 Test 3: Valid JPEG file structure")
    test_image = "/tmp/campfire-test/test_image.jpeg"
    if os.path.exists(test_image):
        # Temporarily remove API key to test error handling
        api_key_backup = os.environ.get("ANTHROPIC_API_KEY")
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]

        result3 = await _process_image_impl({
            "file_path": test_image,
            "question": "Describe this image"
        })
        print(f"Result: {result3[:100]}...")
        assert "ANTHROPIC_API_KEY not found" in result3, "Should return API key error"
        print("✅ Test 3 passed")

        # Restore API key
        if api_key_backup:
            os.environ["ANTHROPIC_API_KEY"] = api_key_backup
    else:
        print("⚠️ Test image not found, skipping test 3")

    # Test 4: With API key (if available)
    print("\n📝 Test 4: With API key (real Vision API call)")
    if os.environ.get("ANTHROPIC_API_KEY") and os.path.exists(test_image):
        file_size = os.path.getsize(test_image) / 1024
        print(f"Image size: {file_size:.1f}KB")

        result4 = await _process_image_impl({
            "file_path": test_image,
            "question": "Briefly describe this image in one sentence."
        })
        print(f"Result: {result4[:200]}...")

        if "Error" not in result4:
            print("✅ Test 4 passed - Vision API call successful")
        else:
            print(f"⚠️ Test 4 - Vision API returned error: {result4}")
    else:
        print("⚠️ No API key or test image, skipping test 4")

    print("\n" + "=" * 60)
    print("✅ All tests completed")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_image_processing())
