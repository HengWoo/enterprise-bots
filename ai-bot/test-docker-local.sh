#!/bin/bash
# Simple Local Docker Testing Script
# Test existing Docker image locally without Campfire or production database

set -e

cd "$(dirname "$0")"

echo "=========================================="
echo "Local Docker Testing for Financial MCP"
echo "=========================================="
echo ""

# Load .env if exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if image exists
IMAGE="hengwoo/campfire-ai-bot:1.0.10"
echo "1️⃣  Checking if Docker image exists..."
if docker image inspect $IMAGE &>/dev/null; then
    echo "   ✅ Image $IMAGE found"
else
    echo "   ❌ Image not found. Please build it first:"
    echo "      docker buildx build --platform linux/amd64 -t $IMAGE ."
    exit 1
fi

# Stop and remove existing test container if running
echo ""
echo "2️⃣  Cleaning up any existing test container..."
docker rm -f ai-bot-test 2>/dev/null || true

# Run the container
echo ""
echo "3️⃣  Starting Docker container..."
docker run -d \
  --name ai-bot-test \
  -p 5002:5000 \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  -e ANTHROPIC_BASE_URL="https://husanai.com" \
  -e CAMPFIRE_URL="https://chat.smartice.ai" \
  -e BOT_KEY="2-CsheovnLtzjM" \
  -e CAMPFIRE_DB_PATH="/app/tests/fixtures/test.db" \
  -e CONTEXT_DIR="/app/ai-knowledge/user_contexts" \
  -e TESTING="true" \
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
curl -s http://localhost:5002/health | jq . || echo "   ⚠️  Health check failed"

# Check if uvx is available in container
echo ""
echo "6️⃣  Checking if uvx is available in container..."
docker exec ai-bot-test bash -c 'which uvx && uvx --version' || echo "   ⚠️  uvx not found (this might be the issue!)"

# Test Financial MCP subprocess manually
echo ""
echo "7️⃣  Testing Financial MCP subprocess manually..."
docker exec ai-bot-test bash -c '
cd /app/financial-mcp
echo "Testing: uv run python run_mcp_server.py --help"
timeout 5s uv run python run_mcp_server.py --help 2>&1 | head -10
' || echo "   ⚠️  MCP server startup failed or timed out"

# Send test webhook to list tools
echo ""
echo "8️⃣  Sending webhook to ask bot to list tools..."
RESPONSE=$(curl -s -X POST http://localhost:5002/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "user": {"id": 1, "name": "Test User"},
    "room": {"id": 1, "name": "Test Room"},
    "message": {
      "id": 1,
      "body": {
        "plain": "Please list all your available tools and their names",
        "html": "<p>Please list all your available tools and their names</p>"
      }
    }
  }')

echo "   Response: $RESPONSE"

# Wait for processing
echo ""
echo "9️⃣  Waiting for bot to process (15 seconds)..."
sleep 15

# Check logs for tool registration
echo ""
echo "🔟 Checking logs for MCP tool registration..."
echo ""
echo "=== Campfire MCP Tools ==="
docker logs ai-bot-test 2>&1 | grep -i "mcp__campfire" | tail -5

echo ""
echo "=== Financial MCP Tools ==="
docker logs ai-bot-test 2>&1 | grep -i "mcp__fin-report-agent" | tail -5 || echo "   ❌ NO Financial MCP tools found in logs!"

echo ""
echo "=== Tool Call Logs ==="
docker logs ai-bot-test 2>&1 | grep -i "Tool Call" | tail -10

echo ""
echo "=== Full Recent Logs ==="
docker logs ai-bot-test 2>&1 | tail -50

echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="
echo ""
echo "Container is still running for further inspection."
echo "Commands:"
echo "  - View logs: docker logs -f ai-bot-test"
echo "  - Exec into container: docker exec -it ai-bot-test bash"
echo "  - Stop container: docker stop ai-bot-test"
echo "  - Remove container: docker rm ai-bot-test"
echo ""
