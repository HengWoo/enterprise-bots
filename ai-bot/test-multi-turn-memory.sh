#!/bin/bash
# Test multi-turn conversation memory with agent cache
# Verifies that bot remembers context from previous turns

set -e

cd "$(dirname "$0")"

echo "=========================================="
echo "Multi-Turn Conversation Memory Test"
echo "=========================================="
echo ""
echo "This test verifies that the bot remembers context across turns:"
echo "  Turn 1: Provide file path"
echo "  Turn 2: Ask about file WITHOUT providing path again"
echo "  Expected: Bot should remember the file path from Turn 1"
echo ""

# Load .env if exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if image exists
IMAGE="hengwoo/campfire-ai-bot:1.0.11-memory"
echo "1️⃣  Checking if Docker image exists..."
if docker image inspect $IMAGE &>/dev/null; then
    echo "   ✅ Image $IMAGE found"
else
    echo "   ⚠️  Image not found. Building..."
    docker buildx build --platform linux/amd64 -t $IMAGE .
fi

# Stop and remove existing test container if running
echo ""
echo "2️⃣  Cleaning up any existing test container..."
docker rm -f ai-bot-memory-test 2>/dev/null || true

# Run the container
echo ""
echo "3️⃣  Starting Docker container with agent cache..."
docker run -d \
  --name ai-bot-memory-test \
  -p 5003:5000 \
  -v "$(pwd)/ai-knowledge:/app/ai-knowledge" \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  -e ANTHROPIC_BASE_URL="https://husanai.com" \
  -e CAMPFIRE_URL="https://chat.smartice.ai" \
  -e BOT_KEY="2-CsheovnLtzjM" \
  -e CAMPFIRE_DB_PATH="/app/tests/fixtures/test.db" \
  -e CONTEXT_DIR="/app/ai-knowledge/user_contexts" \
  -e TESTING="false" \
  -e LOG_LEVEL="DEBUG" \
  $IMAGE

echo "   ✅ Container started"

# Wait for container to be ready
echo ""
echo "4️⃣  Waiting for container to initialize (10 seconds)..."
sleep 10

# Test health endpoint
echo ""
echo "5️⃣  Testing health endpoint..."
curl -s http://localhost:5003/health | jq . || echo "   ⚠️  Health check failed"

# Check cache stats (should be empty initially)
echo ""
echo "6️⃣  Checking initial cache stats..."
curl -s http://localhost:5003/cache/stats | jq .

# TURN 1: Provide file path
echo ""
echo ""
echo "================================"
echo "TURN 1: Provide File Path"
echo "================================"
curl -s -X POST http://localhost:5003/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "user": {"id": 1, "name": "财务经理"},
    "room": {"id": 1, "name": "财务分析室"},
    "message": {
      "id": 100,
      "body": {
        "plain": "文件路径是：/app/ai-knowledge/0.野百灵（绵阳店）-2025年5-8月财务报表.xlsx，请使用get_excel_info工具查看这个文件的基本信息",
        "html": "<p>文件路径是：/app/ai-knowledge/0.野百灵（绵阳店）-2025年5-8月财务报表.xlsx，请使用get_excel_info工具查看这个文件的基本信息</p>"
      }
    }
  }'

echo ""
echo "Waiting 25 seconds for Turn 1 processing..."
sleep 25

echo ""
echo "Checking logs for Turn 1 response..."
docker logs ai-bot-memory-test 2>&1 | tail -80 | grep -A5 "Agent Message" || echo "No response found"

# Check cache stats (should have 1 agent now)
echo ""
echo "Checking cache stats after Turn 1..."
curl -s http://localhost:5003/cache/stats | jq .

# TURN 2: Ask about file WITHOUT providing path
echo ""
echo ""
echo "================================"
echo "TURN 2: Ask About File (No Path Provided)"
echo "================================"
echo "🔑 KEY TEST: Bot should remember file path from Turn 1"
echo ""
curl -s -X POST http://localhost:5003/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "user": {"id": 1, "name": "财务经理"},
    "room": {"id": 1, "name": "财务分析室"},
    "message": {
      "id": 101,
      "body": {
        "plain": "现在请用read_excel_region工具读取Sheet1的A1到D10区域",
        "html": "<p>现在请用read_excel_region工具读取Sheet1的A1到D10区域</p>"
      }
    }
  }'

echo ""
echo "Waiting 25 seconds for Turn 2 processing..."
sleep 25

echo ""
echo "Checking logs for Turn 2 response..."
docker logs ai-bot-memory-test 2>&1 | tail -80 | grep -A5 "Agent Message" || echo "No response found"

# TURN 3: Further conversation to verify memory
echo ""
echo ""
echo "================================"
echo "TURN 3: Continue Conversation"
echo "================================"
echo "🔑 Bot should still remember context from Turn 1 & 2"
echo ""
curl -s -X POST http://localhost:5003/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "user": {"id": 1, "name": "财务经理"},
    "room": {"id": 1, "name": "财务分析室"},
    "message": {
      "id": 102,
      "body": {
        "plain": "请用calculate工具计算5月和6月的总收入",
        "html": "<p>请用calculate工具计算5月和6月的总收入</p>"
      }
    }
  }'

echo ""
echo "Waiting 25 seconds for Turn 3 processing..."
sleep 25

echo ""
echo "Checking logs for Turn 3 response..."
docker logs ai-bot-memory-test 2>&1 | tail -80 | grep -A5 "Agent Message" || echo "No response found"

# Final cache stats
echo ""
echo ""
echo "================================"
echo "Final Cache Statistics"
echo "================================"
curl -s http://localhost:5003/cache/stats | jq .

# Analysis
echo ""
echo ""
echo "=========================================="
echo "Test Analysis"
echo "=========================================="
echo ""
echo "📊 Checking for conversation memory indicators..."
echo ""

# Check if agent was reused
REUSE_COUNT=$(docker logs ai-bot-memory-test 2>&1 | grep -c "Reusing agent for room" || echo 0)
echo "  Agent Reuse Count: $REUSE_COUNT"
if [ $REUSE_COUNT -ge 2 ]; then
    echo "  ✅ Agent was reused across turns (good!)"
else
    echo "  ❌ Agent was NOT reused (memory fix not working)"
fi

# Check if bot asked for file path in Turn 2 (it shouldn't)
ASKED_FOR_PATH=$(docker logs ai-bot-memory-test 2>&1 | grep -i "文件路径\|file path\|哪个文件\|which file" | grep -c "Turn 2" || echo 0)
if [ $ASKED_FOR_PATH -eq 0 ]; then
    echo "  ✅ Bot did NOT ask for file path in Turn 2 (remembered from Turn 1)"
else
    echo "  ❌ Bot asked for file path in Turn 2 (forgot Turn 1)"
fi

# Check for tool calls
TOOL_CALLS=$(docker logs ai-bot-memory-test 2>&1 | grep -c "Agent Tool Call" || echo 0)
echo ""
echo "  Tool Calls: $TOOL_CALLS"
if [ $TOOL_CALLS -ge 3 ]; then
    echo "  ✅ Multiple tool calls detected across turns"
else
    echo "  ⚠️  Fewer tool calls than expected"
fi

echo ""
echo "=========================================="
echo "Full Conversation Logs"
echo "=========================================="
docker logs ai-bot-memory-test 2>&1 | grep -E "Tool Call|Agent Message|Agent Cache" | tail -50

echo ""
echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="
echo ""
echo "Container is still running for further inspection."
echo "Commands:"
echo "  - View logs: docker logs -f ai-bot-memory-test"
echo "  - Check cache: curl http://localhost:5003/cache/stats | jq ."
echo "  - Clear cache: curl -X POST http://localhost:5003/cache/clear/all"
echo "  - Stop container: docker stop ai-bot-memory-test"
echo "  - Remove container: docker rm ai-bot-memory-test"
echo ""
