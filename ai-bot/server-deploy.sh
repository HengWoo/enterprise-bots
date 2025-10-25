#!/bin/bash
# Deploy Campfire AI Bot on DigitalOcean Server
# Run this script ON THE SERVER (128.199.175.50)
# Author: Wu Heng | Date: 2025-10-07

set -e

echo "========================================="
echo "Campfire AI Bot - Server Deployment"
echo "========================================="
echo ""

# Configuration
DOCKERHUB_IMAGE="hengwoo/campfire-ai-bot:1.0.4"
LOCAL_IMAGE="campfire-ai-bot:1.0.4"

# Step 1: Pull image from Docker Hub
echo "📦 Step 1: Pulling image from Docker Hub..."
docker pull $DOCKERHUB_IMAGE
echo "✅ Image pulled successfully"
echo ""

# Step 2: Tag locally
echo "🏷️  Step 2: Tagging image locally..."
docker tag $DOCKERHUB_IMAGE $LOCAL_IMAGE
echo "✅ Image tagged as: $LOCAL_IMAGE"
echo ""

# Step 3: Verify image
echo "🔍 Step 3: Verifying image..."
docker images | grep campfire-ai-bot
echo ""

# Step 4: Create directories
echo "📁 Step 4: Creating directories..."
mkdir -p /root/ai-service
mkdir -p /root/ai-knowledge/user_contexts
mkdir -p /root/ai-knowledge/processed_files
echo "✅ Directories created"
echo ""

# Step 5: Create docker-compose.yml
echo "📝 Step 5: Creating docker-compose.yml..."
cat > /root/ai-service/docker-compose.yml << 'EOF'
version: '3.8'

services:
  ai-bot:
    image: campfire-ai-bot:1.0.4
    container_name: campfire-ai-bot
    restart: unless-stopped
    ports:
      - "5000:5000"
    env_file:
      - .env
    environment:
      - FLASK_PORT=5000
      - FLASK_HOST=0.0.0.0
      - TESTING=false
      - LOG_LEVEL=INFO
    volumes:
      - /var/once/campfire/db:/campfire-db:ro
      - /var/once/campfire/files:/campfire-files:ro
      - /root/ai-knowledge:/app/ai-knowledge
    network_mode: bridge
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "5"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
EOF
echo "✅ docker-compose.yml created"
echo ""

# Step 6: Create .env template
echo "📝 Step 6: Creating .env file..."
cat > /root/ai-service/.env << 'EOF'
# IMPORTANT: Replace YOUR_API_KEY_HERE with your actual Anthropic API key
ANTHROPIC_API_KEY=YOUR_API_KEY_HERE

# Campfire Configuration
CAMPFIRE_DB_PATH=/campfire-db/production.sqlite3
CAMPFIRE_FILES_PATH=/campfire-files
CAMPFIRE_URL=https://chat.smartice.ai

# AI Knowledge Base
CONTEXT_DIR=/app/ai-knowledge/user_contexts
PROCESSED_FILES_DIR=/app/ai-knowledge/processed_files

# Financial MCP
FINANCIAL_MCP_PATH=/app/financial-mcp

# Application Settings
TESTING=false
LOG_LEVEL=INFO
FLASK_PORT=5000
FLASK_HOST=0.0.0.0
EOF
echo "✅ .env file created"
echo ""

# Step 7: Verify Campfire database access
echo "🔍 Step 7: Verifying Campfire database access..."
if [ -f "/var/once/campfire/db/production.sqlite3" ]; then
    echo "✅ Campfire database found"
    ls -lh /var/once/campfire/db/production.sqlite3
else
    echo "⚠️  WARNING: Campfire database not found at /var/once/campfire/db/production.sqlite3"
    echo "   Make sure Campfire is running"
fi
echo ""

# Step 8: Remind about API key
echo "========================================="
echo "⚠️  IMPORTANT: Configure API Key"
echo "========================================="
echo ""
echo "Before starting the service, you MUST add your Anthropic API key:"
echo ""
echo "  nano /root/ai-service/.env"
echo ""
echo "Replace this line:"
echo "  ANTHROPIC_API_KEY=YOUR_API_KEY_HERE"
echo ""
echo "With your actual key:"
echo "  ANTHROPIC_API_KEY=sk-ant-api03-xxxxx..."
echo ""
echo "Then save and exit (Ctrl+X, Y, Enter)"
echo ""
echo "========================================="
echo "Next Steps:"
echo "========================================="
echo ""
echo "1. Edit .env file:"
echo "   nano /root/ai-service/.env"
echo ""
echo "2. Start the service:"
echo "   cd /root/ai-service"
echo "   docker-compose up -d"
echo ""
echo "3. Check status:"
echo "   docker ps | grep campfire-ai-bot"
echo ""
echo "4. Check health:"
echo "   curl http://localhost:5000/health"
echo ""
echo "5. View logs:"
echo "   docker logs -f campfire-ai-bot"
echo ""
echo "========================================="
echo "✅ Deployment preparation complete!"
echo "========================================="
echo ""
