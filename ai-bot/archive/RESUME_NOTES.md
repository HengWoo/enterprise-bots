# Resume Notes - Campfire AI Bot Project

**Last Updated:** 2025-10-14
**Current Version:** v1.0.15 (pending deployment)
**Production Version:** v1.0.14 (has empty response bug)

---

## 🎯 Current Status

**Problem:** v1.0.14 in production has critical bug - Financial Analyst bot returns empty "..." messages when asked to analyze financial reports.

**Root Cause:** Missing `max_turns` parameter in Agent SDK config limits agent to 1 turn, stopping after tool calls without generating final text response.

**Solution:** Added `max_turns=10` to `ClaudeAgentOptions` in v1.0.15

**Status:** Code ready, needs local testing before deployment

---

## 📁 Key Documents (Read These First)

1. **DEPLOYMENT_PLAN_v1.0.15.md** - Complete step-by-step deployment plan with local testing
2. **v1.0.15-CHANGELOG.md** - Technical details of the fix
3. **v1.0.14-CHANGELOG.md** - Race condition fix (already deployed)
4. **CLAUDE.md** - Project overview and infrastructure
5. **DESIGN.md** - System architecture

---

## 🔧 Changes in v1.0.15 (Ready for Deployment)

### Code Changes
1. **src/campfire_agent.py** (Line 131)
   - Added `max_turns=10` to `ClaudeAgentOptions`
   - Allows agent to continue after tool calls and generate final response

2. **Dockerfile**
   - Updated version to 1.0.15
   - Updated description

3. **Documentation**
   - Created `DEPLOYMENT_PLAN_v1.0.15.md`
   - Created `v1.0.15-CHANGELOG.md`
   - Updated this file (RESUME_NOTES.md)

### No Breaking Changes
- General questions still work
- Streaming (v1.0.13) still works
- Request queue (v1.0.14) still works

---

## 🚀 Next Steps (In Order)

### Phase 1: Local Build & Test (MANDATORY)
```bash
cd /Users/heng/Development/campfire/ai-bot

# Build locally
docker buildx build --platform linux/amd64 \
  -t campfire-ai-bot:1.0.15-local .

# Run local container
docker run --rm -p 5002:5000 \
  --env-file .env.test.husanai \
  -v /tmp/campfire-files:/campfire-files \
  campfire-ai-bot:1.0.15-local

# Test general question
curl -X POST http://localhost:5002/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":1,"name":"Test"},"room":{"id":1,"name":"Test"},"content":"介绍一下你的功能"}'

# Test financial analysis (THE FIX)
curl -X POST http://localhost:5002/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":1,"name":"Test"},"room":{"id":1,"name":"Test"},"content":"分析野百灵5-8月报表"}'
```

**Expected in logs:**
```
[Agent SDK] Received: ToolUseBlock
[Agent SDK] Received: AssistantMessage  ← MUST APPEAR!
[Agent Message] 根据Excel文件分析...
```

### Phase 2: Push to Docker Hub (Only if Phase 1 passes)
```bash
# Build with tags
docker buildx build --platform linux/amd64 \
  -t hengwoo/campfire-ai-bot:1.0.15 \
  -t hengwoo/campfire-ai-bot:latest .

# Push both tags
docker push hengwoo/campfire-ai-bot:1.0.15
docker push hengwoo/campfire-ai-bot:latest
```

### Phase 3: Deploy to Production
```bash
# On DigitalOcean server (via console)
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:latest
docker-compose up -d
docker logs -f campfire-ai-bot
```

### Phase 4: Test in Production
```
@财务分析师 分析野百灵5-8月报表
```

Expected: Full financial analysis, NOT "..."

---

## 📊 Version History

| Version | Feature | Status | Issues |
|---------|---------|--------|--------|
| v1.0.7  | Conversation history + debug logging | Deployed | - |
| v1.0.8-1.0.12 | Various iterations | Deployed & cleaned | - |
| v1.0.13 | Streaming responses | Deployed | Race conditions |
| v1.0.14 | Request queue system | **Currently in production** | ⚠️ Empty responses after tool calls |
| v1.0.15 | max_turns fix | **Ready for deployment** | None identified |

---

## 🔍 Production Server Status

**Docker Images (Cleaned):**
- `latest` (1.0.14) - Currently running
- `1.0.12` - Kept for rollback
- All older versions removed (freed ~3-4GB)

**Environment:**
- Server: DigitalOcean Droplet (128.199.175.50)
- URL: https://chat.smartice.ai
- Database: `/var/once/campfire/db/production.sqlite3`
- Files: `/campfire-files/`

---

## 🐛 Known Issues

### v1.0.14 (Production)
**Issue:** Empty "..." responses when bot calls MCP tools
**Affected:** Financial analysis requests only (general questions work fine)
**Fix:** v1.0.15 adds `max_turns=10`
**Workaround:** None - must deploy v1.0.15

---

## 💡 Key Learnings

1. **Always test locally first** - Would have caught this bug immediately
2. **Read SDK documentation carefully** - Missing one parameter caused critical bug
3. **Clean up old Docker images** - Saves disk space and confusion
4. **Use version tags consistently** - Makes rollback easier

---

## 📝 Quick Reference Commands

### Local Testing
```bash
# Build and test locally
cd /Users/heng/Development/campfire/ai-bot
docker buildx build --platform linux/amd64 -t campfire-ai-bot:1.0.15-local .
docker run --rm -p 5002:5000 --env-file .env.test.husanai \
  -v /tmp/campfire-files:/campfire-files campfire-ai-bot:1.0.15-local
```

### Production Deployment
```bash
# On server
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:latest
docker-compose up -d
docker logs -f campfire-ai-bot
```

### Monitoring
```bash
# Health check
curl http://localhost:5000/health

# Queue stats
curl http://localhost:5000/queue/stats

# Cache stats
curl http://localhost:5000/cache/stats
```

---

## 📞 Emergency Rollback

If v1.0.15 fails in production:

```bash
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:1.0.14
docker-compose up -d
```

Note: Rollback returns to empty response bug state

---

## 🎯 Success Criteria

v1.0.15 deployment successful when:

- [ ] Local tests pass (both general + financial analysis)
- [ ] Docker Hub push successful
- [ ] Production deployment successful
- [ ] Health check passes
- [ ] General questions work in Campfire
- [ ] **Financial analysis generates full responses** (NOT "...")
- [ ] Production logs show AssistantMessage after ToolUseBlock
- [ ] No errors in logs
- [ ] Performance acceptable (<30 seconds)

---

**Ready for deployment when you are!**

See `DEPLOYMENT_PLAN_v1.0.15.md` for detailed step-by-step instructions.
