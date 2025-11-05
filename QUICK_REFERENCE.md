# Campfire AI Bot - Quick Reference

**Current Production:** v0.4.0.2 ✅
**Last Updated:** October 30, 2025

---

## Quick Commands

### Local Development

```bash
# Test locally (from ai-bot directory)
cd /Users/heng/Development/campfire/ai-bot
PYTHONPATH=/Users/heng/Development/campfire/ai-bot \
  TESTING=true \
  CAMPFIRE_URL=https://chat.smartice.ai \
  uv run python src/app_fastapi.py

# Test webhook
curl -X POST http://localhost:8000/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":1,"name":"Test"},"room":{"id":1,"name":"Test"},"content":"介绍一下你的功能"}'
```

### Docker Deployment

```bash
# Build (local machine)
docker buildx build --platform linux/amd64 \
  -t hengwoo/campfire-ai-bot:X.X.X \
  -t hengwoo/campfire-ai-bot:latest .

# Push to Docker Hub
docker push hengwoo/campfire-ai-bot:X.X.X
docker push hengwoo/campfire-ai-bot:latest

# Deploy on server (via DigitalOcean console)
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:latest
docker-compose up -d
docker logs -f campfire-ai-bot
```

### Health Checks

```bash
# Service health
curl http://localhost:5000/health

# Test bot posting
curl -d 'Test message' \
  https://chat.smartice.ai/rooms/1/2-CsheovnLtzjM/messages

# Database query (read-only)
sqlite3 /var/once/campfire/db/production.sqlite3 -readonly
```

---

## CI/CD Pipeline (GitHub Actions)

**Status:** ✅ Fully automated with manual approval gates

### 1. Build and Push New Version

```bash
# Navigate to: https://github.com/HengWoo/enterprise-bots/actions
# Select: "Build and Push to Docker Hub" workflow
# Click: "Run workflow"
# Enter version: v0.4.X
# Wait ~5-10 minutes for completion
```

### 2. Deploy to Production

```bash
# Navigate to: https://github.com/HengWoo/enterprise-bots/actions
# Select: "Deploy to Production" workflow
# Click: "Run workflow"
# Enter version: v0.4.X (or latest)
# Wait for approval request
# Click: "Review deployments" → "Approve and deploy"
# Wait ~2-3 minutes for deployment + health checks
```

### Rollback Procedures

**Automatic Rollback:**
- Deployment failures trigger automatic rollback to v0.4.0.2
- No manual intervention required

**Manual Rollback:**
```bash
# Via GitHub Actions:
# Navigate to: https://github.com/HengWoo/enterprise-bots/actions
# Select: "Deploy to Production" workflow
# Enter version: v0.4.0.2 (or any stable version)
# Approve deployment

# Or via SSH:
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:0.4.0.2
docker-compose up -d
```

---

## Infrastructure

**Server:** DigitalOcean Droplet (128.199.175.50)
- Domain: https://chat.smartice.ai
- OS: Ubuntu 25.04 x64 (2GB RAM, 1 vCPU)

**AI Service:** `/root/ai-service/`
- Framework: FastAPI + Claude Agent SDK
- Model: claude-haiku-4-5-20251001
- Ports: 8000 (internal), 5000 (external)

**File Locations:**
```
/root/ai-service/                      # FastAPI app
/root/ai-service/.env                  # API keys
/root/ai-knowledge/user_contexts/      # User preferences
/root/ai-knowledge/company_kb/         # Knowledge base
/var/once/campfire/db/production.sqlite3  # Campfire DB (read-only)
```

---

## See Also

- **CLAUDE.md** - Project memory and current status
- **DESIGN.md** - System architecture
- **ARCHITECTURE_QUICK_REFERENCE.md** - One-page system overview
- **VERSION_HISTORY.md** - Complete version history (docs/reference/)
- **TROUBLESHOOTING.md** - Common issues and solutions (docs/reference/)
- **CICD_GUIDE.md** - Complete CI/CD documentation (.github/)
- **ANTHROPIC_BEST_PRACTICES_ROADMAP.md** - v0.5.0 implementation plan

---

**Last Updated:** October 30, 2025
**Production Status:** v0.4.0.2 ✅
