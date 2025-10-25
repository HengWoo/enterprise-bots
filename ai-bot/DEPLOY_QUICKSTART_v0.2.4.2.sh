#!/bin/bash
# Quick Deployment Script for v0.2.4.2
# Run this on production server via DigitalOcean console
# Version: v0.2.4.2 - Daily Briefing Permission + Date Query Fix

echo "============================================================"
echo "🚀 v0.2.4.2 Deployment - Daily Briefing Fixes"
echo "============================================================"
echo ""

# Step 1: Pull new image
echo "Step 1: Pulling new Docker image..."
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:0.2.4.2
docker pull hengwoo/campfire-ai-bot:latest
echo "✅ Images pulled"
echo ""

# Step 2: Start container
echo "Step 2: Starting container..."
docker-compose up -d
sleep 5
echo "✅ Container started"
echo ""

# Step 3: Check health
echo "Step 3: Checking health..."
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

# Step 4: Test daily briefing script
echo "Step 4: Testing daily briefing script..."
docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py
echo ""

# Step 5: Verify briefing file
echo "Step 5: Checking for generated briefing..."
BRIEFING_DATE=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)
docker exec campfire-ai-bot ls -lh /app/ai-knowledge/briefings/ 2>/dev/null || echo "⚠️  Briefings directory not accessible"
echo ""

# Step 6: Show cron setup instructions
echo "============================================================"
echo "Step 6: Cron Job Setup (if not already configured)"
echo "============================================================"
echo ""
echo "To set up automated daily briefings at 9:00 AM:"
echo "  sudo crontab -e"
echo ""
echo "Add this line:"
echo "  0 9 * * * docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py >> /var/lib/docker/volumes/ai-service_ai-knowledge/_data/logs/briefing-cron.log 2>&1"
echo ""
echo "Verify cron job:"
echo "  sudo crontab -l | grep briefing"
echo ""

# Step 7: Summary
echo "============================================================"
echo "✅ Deployment Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Monitor logs: docker logs -f campfire-ai-bot"
echo "  2. Test all 4 bots in Campfire"
echo "  3. Set up cron job (see instructions above)"
echo "  4. Monitor first cron execution tomorrow at 9:00 AM"
echo ""
echo "Troubleshooting:"
echo "  - Health check: curl http://localhost:8000/health"
echo "  - Bot status: curl http://localhost:8000/health | grep version"
echo "  - Daily briefing test: docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py"
echo ""
echo "Documentation: See DEPLOYMENT_v0.2.4.2.md for full details"
echo ""
