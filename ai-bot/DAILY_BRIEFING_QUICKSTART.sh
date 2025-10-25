#!/bin/bash
# Daily Briefing Quick Setup Script
# Run this on production server via DigitalOcean console
# Version: v0.2.4

echo "============================================================"
echo "🚀 Daily Briefing Automation Setup"
echo "============================================================"
echo ""

# Step 1: Create directories
echo "Step 1: Creating knowledge base directories..."
sudo mkdir -p /root/ai-knowledge/briefings
sudo mkdir -p /root/ai-knowledge/user_contexts
sudo mkdir -p /root/ai-knowledge/logs
echo "✅ Directories created"
echo ""

# Step 2: Set permissions
echo "Step 2: Setting permissions (UID 1000 = appuser in container)..."
sudo chown -R 1000:1000 /root/ai-knowledge
sudo chmod -R 755 /root/ai-knowledge
echo "✅ Permissions set"
echo ""

# Step 3: Verify structure
echo "Step 3: Verifying directory structure..."
ls -la /root/ai-knowledge/
echo ""

# Step 4: Test script manually
echo "Step 4: Testing briefing script..."
docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py
echo ""

# Step 5: Check generated briefing
echo "Step 5: Checking generated briefing..."
BRIEFING_DATE=$(date -d "yesterday" +%Y-%m-%d)
if [ -f "/root/ai-knowledge/briefings/briefing_${BRIEFING_DATE}.md" ]; then
    echo "✅ Briefing generated successfully!"
    echo "File: /root/ai-knowledge/briefings/briefing_${BRIEFING_DATE}.md"
    echo ""
    echo "Preview (first 20 lines):"
    head -20 "/root/ai-knowledge/briefings/briefing_${BRIEFING_DATE}.md"
else
    echo "⚠️  Briefing file not found. Check logs above for errors."
fi
echo ""

# Step 6: Show cron setup instructions
echo "============================================================"
echo "Step 6: Cron Job Setup"
echo "============================================================"
echo ""
echo "To set up automated daily briefings, run:"
echo "  sudo crontab -e"
echo ""
echo "Then add this line:"
echo "  0 9 * * * docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py >> /root/ai-knowledge/logs/briefing-cron.log 2>&1"
echo ""
echo "This will generate briefings at 9:00 AM daily."
echo ""
echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Add cron job (see instructions above)"
echo "  2. Monitor first few executions: tail -f /root/ai-knowledge/logs/briefing-cron.log"
echo "  3. Check briefings: ls -lh /root/ai-knowledge/briefings/"
echo ""
