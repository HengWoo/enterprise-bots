"""
Live test for process_image_tool with real Vision API call
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools.image_decorators import _process_image_impl

async def test_live_image():
    """Test with real image and Vision API"""

    # Check for test image
    test_image = "/tmp/campfire-test/test_image.jpeg"

    if not os.path.exists(test_image):
        print("❌ Test image not found at", test_image)
        print("Creating test image first...")
        return

    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not set")
        print("Please set your API key to run live test")
        return

    # Get image info
    file_size = os.path.getsize(test_image) / 1024
    print("=" * 70)
    print("🔥 LIVE IMAGE PROCESSING TEST")
    print("=" * 70)
    print(f"Image path: {test_image}")
    print(f"Image size: {file_size:.1f}KB")
    print("")
    print("🤖 Calling Claude Vision API...")
    print("-" * 70)

    # Call the implementation
    result = await _process_image_impl({
        "file_path": test_image,
        "question": "Describe this image briefly in one sentence. What do you see?"
    })

    print("")
    print("📊 VISION API RESPONSE:")
    print("=" * 70)
    print(result)
    print("=" * 70)

    # Check if successful
    if "Error" in result:
        print("\n❌ Test FAILED - Error in response")
        return False
    else:
        print("\n✅ Test PASSED - Image successfully analyzed")
        return True

if __name__ == "__main__":
    success = asyncio.run(test_live_image())
    sys.exit(0 if success else 1)
