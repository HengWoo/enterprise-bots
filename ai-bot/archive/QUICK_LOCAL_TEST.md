# Quick Local Test - Agent Skills v0.3.0

**Purpose:** Verify Agent Skills are working correctly before Docker build

---

## ✅ Pre-Test Verification

Skills are installed and ready:
```bash
✅ .claude/skills/ directory exists
✅ 4 skills created (financial-analysis, kb, conversations, briefing)
✅ Agent SDK configured with setting_sources=['project']
✅ Dockerfile updated to v0.3.0
✅ Git repository initialized with v0.3.0 commit
```

---

## 🚀 Step 1: Start Local Server

```bash
cd /Users/heng/Development/campfire/ai-bot

# Set environment variables and start server
TESTING=true \
CAMPFIRE_URL=https://chat.smartice.ai \
ANTHROPIC_API_KEY=your_key_here \
uv run python src/app_fastapi.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Server will be available at: `http://localhost:8000`

---

## 🧪 Step 2: Test Scenarios

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

**Expected:** `{"status":"healthy"}`

### Test 2: Simple Query (Should NOT load skills)

```bash
curl -X POST http://localhost:8000/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {"id": 1, "name": "Test User"},
    "room": {"id": 1, "name": "Test Room"},
    "content": "Hello"
  }'
```

**Expected behavior:**
- Bot responds with greeting
- **Check server logs for:** Minimal token usage (~600 tokens)
- **Skills loaded:** None (or just metadata)

### Test 3: Financial Query (SHOULD load financial skill)

```bash
curl -X POST http://localhost:8000/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {"id": 1, "name": "Test User"},
    "room": {"id": 1, "name": "Test Room"},
    "content": "Calculate ROE and explain the formula"
  }'
```

**Expected behavior:**
- Bot explains ROE formula
- **Check server logs for:** Moderate token usage (~1400 tokens)
- **Skills loaded:** `campfire-financial-analysis`

### Test 4: Knowledge Base Query (SHOULD load KB skill)

```bash
curl -X POST http://localhost:8000/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {"id": 1, "name": "Test User"},
    "room": {"id": 1, "name": "Test Room"},
    "content": "What policies do we have in the knowledge base?"
  }'
```

**Expected behavior:**
- Bot lists available policies/procedures
- **Skills loaded:** `campfire-kb`

---

## 📊 Step 3: Verify Skills Loading

**In the server logs, look for:**

```
[Agent Init] 🆕 Starting new session
[Agent SDK] Loading skills from .claude/skills/
[Agent SDK] Skills discovered: 4 skills
  - campfire-financial-analysis
  - campfire-kb
  - campfire-conversations
  - campfire-daily-briefing
```

**For each query, check:**
```
[Agent SDK] Input tokens: XXX
[Agent SDK] Skills loaded for this query: [skill names]
[Agent SDK] Output tokens: XXX
```

---

## ✅ Success Criteria

- [ ] Server starts without errors
- [ ] Health check returns `{"status":"healthy"}`
- [ ] Simple query works (no skills loaded or minimal loading)
- [ ] Financial query loads financial skill
- [ ] KB query loads knowledge base skill
- [ ] Token usage is reasonable (~600 simple, ~1400 financial)

---

## 🐛 Troubleshooting

### Problem: Server won't start

**Solution:** Check dependencies
```bash
cd /Users/heng/Development/campfire/ai-bot
uv sync  # Reinstall dependencies
```

### Problem: "Skills not found" error

**Solution:** Verify skills directory
```bash
ls -la .claude/skills/
# Should show 4 skill directories
```

### Problem: Skills not loading

**Solution:** Check agent config
```bash
grep "setting_sources" src/campfire_agent.py
# Should show: "setting_sources": ["project"]
```

### Problem: Token usage too high

**Possible causes:**
- Skills might not be using progressive disclosure correctly
- Check if all skills are loading (should only load relevant ones)

---

## 📝 Recording Results

Create a simple test log:

```markdown
## Test Run: [Date/Time]

### Test 1: Simple Query ("Hello")
- ✅ Server response: [paste response]
- Token usage: [from logs]
- Skills loaded: [from logs]

### Test 2: Financial Query ("Calculate ROE")
- ✅ Server response: [paste response]
- Token usage: [from logs]
- Skills loaded: [from logs]

### Test 3: KB Query ("What policies...")
- ✅ Server response: [paste response]
- Token usage: [from logs]
- Skills loaded: [from logs]

### Overall:
- Skills working: ✅/❌
- Token reduction observed: ✅/❌
- Ready for Docker build: ✅/❌
```

---

## ⏭️ Next Steps

If all tests pass:
1. ✅ Mark local testing complete
2. Build Docker image (v0.3.0)
3. Deploy to production
4. Monitor production metrics

If tests fail:
1. Review error logs
2. Fix issues
3. Re-run tests
4. Commit fixes

---

**Ready to test!** Start the server and run the curl commands above. 🚀
