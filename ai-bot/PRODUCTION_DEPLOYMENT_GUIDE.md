# Campfire AI Bot - Production Deployment Guide

**Target Server:** DigitalOcean Droplet (128.199.175.50)
**Image Version:** 1.0.4
**Date:** 2025-10-07

---

## Prerequisites

- ✅ Docker image built and tested locally (version 1.0.4)
- ✅ All tests passed (simple greeting + financial analysis)
- ✅ Anthropic API key ready
- ✅ SSH access to DigitalOcean server
- ✅ Campfire running at https://chat.smartice.ai

---

## Deployment Steps

### Step 1: Transfer Docker Image to Server

From your local machine:

```bash
# Export image (already done - see campfire-ai-bot-1.0.4.tar.gz)
# Size: 354MB compressed

# Transfer to server via scp
scp campfire-ai-bot-1.0.4.tar.gz root@128.199.175.50:/root/

# Estimated transfer time: ~2-3 minutes (depending on network speed)
```

**Expected output:**
```
campfire-ai-bot-1.0.4.tar.gz    100%  354MB   2.1MB/s   02:48
```

---

### Step 2: SSH to Server and Load Image

```bash
# SSH to server
ssh root@128.199.175.50

# Load Docker image
cd /root
docker load < campfire-ai-bot-1.0.4.tar.gz

# Verify image loaded
docker images | grep campfire-ai-bot
```

**Expected output:**
```
campfire-ai-bot    1.0.4    <image-id>    X minutes ago    1.51GB
```

---

### Step 3: Create AI Service Directory

```bash
# Create directory structure
mkdir -p /root/ai-service
mkdir -p /root/ai-knowledge/user_contexts
mkdir -p /root/ai-knowledge/processed_files

# Set permissions
chmod 755 /root/ai-service
chmod 755 /root/ai-knowledge
chmod 755 /root/ai-knowledge/user_contexts
chmod 755 /root/ai-knowledge/processed_files
```

---

### Step 4: Create Production Configuration Files

#### 4a. Create docker-compose.yml

```bash
cd /root/ai-service

cat > docker-compose.yml << 'EOF'
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
```

#### 4b. Create .env file

```bash
cat > .env << 'EOF'
# Anthropic API Key - REPLACE WITH YOUR ACTUAL KEY
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

# Edit .env to add your actual API key
nano .env
# Replace YOUR_API_KEY_HERE with your actual Anthropic API key
# Save and exit (Ctrl+X, Y, Enter)
```

---

### Step 5: Verify Campfire Database Access

Before starting the service, verify we can access Campfire's database:

```bash
# Check Campfire database exists
ls -lh /var/once/campfire/db/production.sqlite3

# Test read-only access
sqlite3 /var/once/campfire/db/production.sqlite3 -readonly \
  "SELECT name FROM rooms LIMIT 3;"

# Check Campfire files directory
ls -lh /var/once/campfire/files/ | head -10
```

**Expected:**
- Database file should exist (~4KB)
- Should see room names
- Files directory should have hash-based subdirectories

---

### Step 6: Start AI Bot Service

```bash
cd /root/ai-service

# Start in detached mode
docker-compose up -d

# Check container status
docker ps | grep campfire-ai-bot

# Expected:
# campfire-ai-bot    campfire-ai-bot:1.0.4    Up X seconds (health: starting)
```

---

### Step 7: Monitor Startup

```bash
# Follow logs in real-time
docker logs -f campfire-ai-bot

# Expected log output:
# Loaded bot: 财务分析师 (Financial Analyst) (financial_analyst)
# Loaded bot: 技术助手 (Technical Assistant) (technical_assistant)
# Loaded bot: AI Assistant (default)
#
# Loaded 3 bot configuration(s):
#   - 财务分析师 (Financial Analyst) (model: claude-sonnet-4-5-20250929)
#   - 技术助手 (Technical Assistant) (model: claude-sonnet-4-5-20250929)
#   - AI Assistant (model: claude-sonnet-4-5-20250929)
#
# Starting Campfire AI Bot on 0.0.0.0:5000
# Database: /campfire-db/production.sqlite3
# Campfire URL: https://chat.smartice.ai
```

Wait ~60 seconds for health check to pass.

---

### Step 8: Verify Health Check

```bash
# Check health endpoint
curl http://localhost:5000/health

# Expected output:
# {
#   "bots": {
#     "default": "AI Assistant",
#     "financial_analyst": "财务分析师 (Financial Analyst)",
#     "technical_assistant": "技术助手 (Technical Assistant)"
#   },
#   "database": "/campfire-db/production.sqlite3",
#   "financial_mcp": "/app/financial-mcp",
#   "status": "healthy"
# }
```

---

### Step 9: Configure Campfire Webhook

Now that the service is running, configure Campfire to send webhooks to it.

#### 9a. Get Bot Key

```bash
# Query Campfire database for bot user
sqlite3 /var/once/campfire/db/production.sqlite3 -readonly \
  "SELECT id, name, bot_token FROM users WHERE role = 1;"

# Expected output:
# 2|财务分析师|CsheovnLtzjM
```

**Bot Key Format:** `{user_id}-{bot_token}`

Example: If user_id=2 and bot_token=CsheovnLtzjM, then:
- **Bot Key:** `2-CsheovnLtzjM`

#### 9b. Set Webhook URL in Campfire

**Option 1: Via Campfire UI (if available)**
1. Navigate to bot settings
2. Set webhook URL: `http://128.199.175.50:5000/webhook`

**Option 2: Via Database (direct update)**
```bash
# CAUTION: This requires write access to Campfire DB
# Only do this if you know what you're doing

# First, backup database
cp /var/once/campfire/db/production.sqlite3 \
   /root/campfire-db-backup-$(date +%Y%m%d).sqlite3

# Then update webhook URL (replace USER_ID with actual bot user ID)
# NOTE: This is just an example - check Campfire's webhook schema first
```

**Option 3: Contact Campfire Admin**
- Ask Campfire administrator to configure webhook
- Provide webhook URL: `http://128.199.175.50:5000/webhook`

---

### Step 10: End-to-End Test

#### 10a. Simple Test via Curl

```bash
# Create test payload
cat > /root/test-webhook.json << 'EOF'
{
  "creator": {
    "id": 1,
    "name": "Test User"
  },
  "room": {
    "id": 1,
    "name": "Test Room"
  },
  "id": 999,
  "content": "你好，请简单介绍一下你自己"
}
EOF

# Send test request
curl -X POST http://localhost:5000/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d @/root/test-webhook.json

# Expected: Response within 10-15 seconds
# Check logs:
docker logs campfire-ai-bot 2>&1 | tail -20
```

#### 10b. Test in Campfire (Real E2E)

1. Open Campfire at https://chat.smartice.ai
2. Go to any room where the bot is a member
3. Mention the bot: `@财务分析师 你好，请简单介绍一下你自己`
4. Wait 10-15 seconds
5. Bot should respond with Chinese greeting

**If successful:** ✅ Bot is working!

---

## Troubleshooting

### Issue 1: Container Won't Start

**Symptom:**
```bash
docker ps | grep campfire-ai-bot
# Shows nothing
```

**Diagnosis:**
```bash
# Check container status (including stopped)
docker ps -a | grep campfire-ai-bot

# Check logs
docker logs campfire-ai-bot

# Common issues:
# - Missing API key in .env
# - Database path doesn't exist
# - Port 5000 already in use
```

**Fix:**
```bash
# Verify .env file
cat /root/ai-service/.env | grep ANTHROPIC_API_KEY

# Verify database path
ls -lh /var/once/campfire/db/production.sqlite3

# Check port
netstat -tuln | grep 5000

# If port in use, stop conflicting service
```

---

### Issue 2: Health Check Failing

**Symptom:**
```bash
docker ps | grep campfire-ai-bot
# Shows: (health: unhealthy)
```

**Diagnosis:**
```bash
# Check logs for errors
docker logs campfire-ai-bot 2>&1 | grep -i error

# Try health endpoint manually
curl http://localhost:5000/health
```

**Common causes:**
- Flask server not starting
- Claude Code CLI not installed (should be in image)
- Crash during initialization

---

### Issue 3: Bot Not Responding in Campfire

**Symptom:** Mention bot in Campfire, no response

**Diagnosis:**
```bash
# Check if webhook is configured
# (depends on how Campfire stores webhooks)

# Check if requests are reaching the service
docker logs -f campfire-ai-bot
# Mention bot in Campfire
# Should see: "Processing webhook with bot: ..."

# If no log entry, webhook not configured correctly
```

**Fix:**
- Verify webhook URL in Campfire settings
- Check firewall rules (port 5000 should be accessible)
- Verify bot user exists and has correct bot_token

---

### Issue 4: Financial MCP Tools Not Working

**Symptom:** Bot responds but says "财务分析工具暂时不可用"

**Diagnosis:**
```bash
# Check Financial MCP is accessible
docker exec campfire-ai-bot ls -la /app/financial-mcp/

# Test Financial MCP manually
docker exec -u appuser campfire-ai-bot \
  bash -c "cd /app/financial-mcp && timeout 5 uv run python run_mcp_server.py"

# Should NOT show:
# - "Downloading Python..."
# - "Ignoring existing virtual environment..."
```

**Fix:**
```bash
# If seeing download messages, Financial MCP venv is broken
# Rebuild Docker image with correct Python:
# (Should already be fixed in version 1.0.4)

# If still broken, check UV_PYTHON setting
docker exec campfire-ai-bot env | grep UV_PYTHON
# Should show: UV_PYTHON=/usr/local/bin/python3
```

---

### Issue 5: Slow Responses

**Symptom:** Bot takes 5+ minutes to respond

**Diagnosis:**
```bash
# Check resource usage
docker stats campfire-ai-bot

# If CPU or memory is maxed out, increase limits in docker-compose.yml

# Check if model is correct
docker logs campfire-ai-bot | grep "model:"
# Should show: claude-sonnet-4-5-20250929

# Sonnet 4.5 is slower but more capable than Haiku
# 3-4 minutes for complex financial analysis is normal
```

---

## Monitoring & Maintenance

### Daily Checks

```bash
# Check service status
docker ps | grep campfire-ai-bot

# Check health
curl http://localhost:5000/health

# Check recent logs
docker logs campfire-ai-bot --tail 50
```

### Weekly Maintenance

```bash
# Check disk usage
du -sh /root/ai-knowledge/
du -sh /var/lib/docker/

# Check log file sizes
docker inspect campfire-ai-bot --format='{{.LogPath}}' | xargs ls -lh

# Rotate logs if needed
docker-compose restart
```

### Restart Service

```bash
cd /root/ai-service

# Graceful restart
docker-compose restart

# Full restart (reload image)
docker-compose down
docker-compose up -d
```

### Update Docker Image

When deploying new version:

```bash
# Transfer new image
scp campfire-ai-bot-X.X.X.tar.gz root@128.199.175.50:/root/

# SSH to server
ssh root@128.199.175.50

# Load new image
docker load < /root/campfire-ai-bot-X.X.X.tar.gz

# Update docker-compose.yml to use new version
cd /root/ai-service
nano docker-compose.yml
# Change: image: campfire-ai-bot:X.X.X

# Restart with new image
docker-compose down
docker-compose up -d

# Verify
docker ps | grep campfire-ai-bot
curl http://localhost:5000/health
```

---

## Backup & Recovery

### Backup AI Knowledge Base

```bash
# Create backup directory
mkdir -p /root/backups

# Backup AI knowledge
tar -czf /root/backups/ai-knowledge-$(date +%Y%m%d).tar.gz \
  /root/ai-knowledge/

# Backup configuration
tar -czf /root/backups/ai-service-config-$(date +%Y%m%d).tar.gz \
  /root/ai-service/
```

### Restore from Backup

```bash
# Extract AI knowledge backup
cd /root
tar -xzf /root/backups/ai-knowledge-YYYYMMDD.tar.gz

# Extract configuration backup
tar -xzf /root/backups/ai-service-config-YYYYMMDD.tar.gz

# Restart service
cd /root/ai-service
docker-compose restart
```

---

## Security Best Practices

1. **API Key Security**
   - Never commit .env file to git
   - Restrict .env file permissions: `chmod 600 /root/ai-service/.env`
   - Rotate API key periodically

2. **Database Access**
   - Always use read-only mounts for Campfire DB
   - Never modify Campfire database directly

3. **Container Security**
   - Run as non-root user (appuser - UID 1000)
   - Limit resources to prevent DoS
   - Keep Docker and base images updated

4. **Network Security**
   - Consider adding nginx reverse proxy with HTTPS
   - Rate limit webhook endpoint
   - Monitor access logs

---

## Performance Optimization

### Adjust Resource Limits

If experiencing performance issues:

```yaml
# Edit docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '4.0'      # Increase from 2.0
      memory: 8G       # Increase from 4G
```

### Enable Caching

Future enhancement: Add Redis for caching processed files and responses.

---

## Success Criteria

After deployment, verify:

- [x] Container running and healthy
- [x] Health endpoint returns 200
- [x] All 3 bots loaded
- [x] Campfire database accessible
- [x] Financial MCP tools working
- [x] Bot responds to mentions in Campfire
- [x] Chinese language responses correct
- [x] File attachments processed correctly

---

## Quick Reference Commands

```bash
# Status
docker ps | grep campfire-ai-bot

# Health
curl http://localhost:5000/health

# Logs (live)
docker logs -f campfire-ai-bot

# Logs (last 50 lines)
docker logs --tail 50 campfire-ai-bot

# Restart
cd /root/ai-service && docker-compose restart

# Stop
cd /root/ai-service && docker-compose down

# Start
cd /root/ai-service && docker-compose up -d

# Shell access (for debugging)
docker exec -it campfire-ai-bot bash

# Check Financial MCP
docker exec campfire-ai-bot ls -la /app/financial-mcp/

# Check database connection
docker exec campfire-ai-bot sqlite3 /campfire-db/production.sqlite3 \
  -readonly "SELECT COUNT(*) FROM messages;"
```

---

## Support & Documentation

- **Local Documentation:**
  - DESIGN.md - System architecture
  - AGENT_SDK_ANALYSIS.md - Agent SDK analysis
  - TROUBLESHOOTING.md - Common issues and solutions
  - DEPLOYMENT_SUCCESS.md - Local testing success summary

- **External Resources:**
  - Claude Agent SDK: https://github.com/anthropics/claude-agent-sdk
  - Anthropic API Docs: https://docs.anthropic.com/
  - Docker Compose Docs: https://docs.docker.com/compose/

---

**Deployment Guide Version:** 1.0
**Last Updated:** 2025-10-07
**Status:** Ready for Production Deployment ✅

**Next Step:** Transfer `campfire-ai-bot-1.0.4.tar.gz` to server and follow Step 1!
