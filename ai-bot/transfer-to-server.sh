#!/bin/bash
# Transfer Campfire AI Bot to DigitalOcean Server
# Author: Wu Heng | Date: 2025-10-07

set -e  # Exit on error

SERVER="root@128.199.175.50"
IMAGE_FILE="campfire-ai-bot-1.0.4.tar.gz"

echo "========================================="
echo "Campfire AI Bot - Server Transfer Script"
echo "========================================="
echo ""

# Check if image file exists
if [ ! -f "$IMAGE_FILE" ]; then
    echo "❌ Error: $IMAGE_FILE not found!"
    echo "Please run this script from /Users/heng/Development/campfire/ai-bot/"
    exit 1
fi

echo "✅ Found: $IMAGE_FILE ($(ls -lh $IMAGE_FILE | awk '{print $5}'))"
echo ""

# Test SSH connection
echo "🔍 Testing SSH connection to $SERVER..."
if ssh -o ConnectTimeout=5 $SERVER "echo 'SSH connection successful'" 2>/dev/null; then
    echo "✅ SSH connection working!"
    echo ""

    # Method 1: Direct SCP Transfer
    echo "📦 Transferring files via SCP..."
    echo ""

    # Transfer Docker image
    echo "1️⃣ Transferring Docker image ($IMAGE_FILE)..."
    scp -v $IMAGE_FILE $SERVER:/root/
    echo "✅ Docker image transferred"
    echo ""

    # Create ai-service directory on server
    echo "2️⃣ Creating /root/ai-service/ directory..."
    ssh $SERVER "mkdir -p /root/ai-service"
    echo "✅ Directory created"
    echo ""

    # Transfer configuration files
    echo "3️⃣ Transferring configuration files..."
    scp docker-compose.production.yml $SERVER:/root/ai-service/docker-compose.yml
    scp .env.production.template $SERVER:/root/ai-service/.env
    echo "✅ Configuration files transferred"
    echo ""

    # Transfer documentation
    echo "4️⃣ Transferring documentation..."
    scp PRODUCTION_DEPLOYMENT_GUIDE.md $SERVER:/root/
    scp DEPLOYMENT_SUCCESS.md $SERVER:/root/
    scp TROUBLESHOOTING.md $SERVER:/root/
    echo "✅ Documentation transferred"
    echo ""

    # Create AI knowledge directories
    echo "5️⃣ Creating AI knowledge directories..."
    ssh $SERVER "mkdir -p /root/ai-knowledge/user_contexts /root/ai-knowledge/processed_files"
    echo "✅ Directories created"
    echo ""

    echo "========================================="
    echo "✅ Transfer Complete!"
    echo "========================================="
    echo ""
    echo "Next steps:"
    echo "1. SSH to server: ssh $SERVER"
    echo "2. Load Docker image:"
    echo "   cd /root"
    echo "   docker load < $IMAGE_FILE"
    echo "3. Configure .env file:"
    echo "   cd /root/ai-service"
    echo "   nano .env"
    echo "   (Add your Anthropic API key)"
    echo "4. Start service:"
    echo "   docker-compose up -d"
    echo ""
    echo "📖 See PRODUCTION_DEPLOYMENT_GUIDE.md for detailed instructions"
    echo ""

else
    echo "❌ SSH connection failed!"
    echo ""
    echo "This is likely due to Cloudflare VPN blocking SSH."
    echo ""
    echo "Alternative transfer methods:"
    echo ""
    echo "Method A: Disable Cloudflare VPN temporarily"
    echo "  1. Disconnect from Cloudflare VPN"
    echo "  2. Run this script again"
    echo ""
    echo "Method B: Use DigitalOcean console + cloud storage"
    echo "  1. Upload files to cloud storage (Dropbox/Google Drive)"
    echo "  2. Access DigitalOcean console at:"
    echo "     https://cloud.digitalocean.com/"
    echo "  3. Download files to server using wget"
    echo ""
    echo "Method C: Use temporary HTTP server (local network only)"
    echo "  1. Start HTTP server:"
    echo "     python3 -m http.server 8080"
    echo "  2. Get your local IP:"
    echo "     ifconfig | grep 'inet ' | grep -v 127.0.0.1"
    echo "  3. From DigitalOcean console:"
    echo "     wget http://YOUR_IP:8080/$IMAGE_FILE"
    echo ""

    exit 1
fi
