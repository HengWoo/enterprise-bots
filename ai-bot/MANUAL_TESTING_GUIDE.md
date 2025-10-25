# Campfire AI Bot - Manual Testing Guide

**Purpose:** Step-by-step manual testing without wasting API calls or hitting rate limits

**Last Updated:** 2025-10-06

---

## Overview

This guide provides **4 incremental testing phases** that allow you to validate the bot's functionality without incurring unnecessary API costs:

1. **Phase 1: Tools Testing** - Test database access (No Flask, No API)
2. **Phase 2: Flask Testing** - Test webhook processing (No real API)
3. **Phase 3: Mock API** - Simulate API responses (No real API)
4. **Phase 4: Real API** - Limited production testing (~$0.06)

Each phase builds on the previous one, allowing you to catch issues early.

---

## Prerequisites

- ✅ uv package manager installed
- ✅ Project dependencies installed (`uv sync --all-extras`)
- ✅ Test database created (`uv run python tests/fixtures/setup_test_db.py`)
- ✅ `.env` file configured

---

## Phase 1: Tools Testing (No API Required)

**Goal:** Verify database access and core tools work independently

**What's tested:**
- ✅ SQLite database connection
- ✅ Conversation search
- ✅ User context retrieval
- ✅ Context saving

**How to run:**
```bash
cd /Users/heng/Development/campfire/ai-bot

# Run Phase 1 tests
chmod +x test_phase1_tools.py
uv run python test_phase1_tools.py
```

**Expected output:**
```
=========================================================
PHASE 1: CampfireTools Direct Testing
No Flask, No API - Database Tools Only
=========================================================

✓ Database connection successful
✓ Found 3 messages containing 'revenue'
✓ User context retrieved successfully
✓ Context saved successfully

Results: 4/4 tests passed
🎉 All Phase 1 tests passed!
```

**If tests fail:**
- Check that test database exists: `./tests/fixtures/test.db`
- Regenerate database: `uv run python tests/fixtures/setup_test_db.py`
- Check file permissions

**Cost:** $0.00 (no API calls)

---

## Phase 2: Flask Webhook Testing (No Real API)

**Goal:** Test webhook processing with fallback responses (no Anthropic API)

**What's tested:**
- ✅ Flask app starts correctly
- ✅ Health endpoint works
- ✅ Webhook payload validation
- ✅ HTML stripping
- ✅ User context integration
- ✅ Error handling

**Setup:**

1. **Configure testing mode:**
   ```bash
   cd /Users/heng/Development/campfire/ai-bot

   # Option A: Use testing environment file
   cp .env.testing .env

   # Option B: Or set environment variable
   export TESTING=true
   ```

2. **Start Flask app:**
   ```bash
   uv run python src/app.py
   ```

   You should see:
   ```
   Starting Campfire AI Bot on 0.0.0.0:5001
   Database: ./tests/fixtures/test.db
   Campfire URL: https://chat.smartice.ai
   ```

3. **In a new terminal, run Phase 2 tests:**
   ```bash
   cd /Users/heng/Development/campfire/ai-bot
   chmod +x test_phase2_flask.py
   uv run python test_phase2_flask.py
   ```

**Expected output:**
```
✓ Flask app is healthy
✓ Webhook processed in 0.23s
✓ Context processed in 0.31s
✓ User context processed
✓ HTML stripped successfully
✓ Invalid payload correctly rejected
✓ Different user handled correctly

Results: 7/7 tests passed
🎉 All Phase 2 tests passed!
```

**Testing mode behavior:**
- Bot responds with echo: "Received your message in [room]: [message]..."
- No actual Anthropic API calls made
- Validates all webhook processing logic

**If tests fail:**
- Ensure Flask app is running on port 5001
- Check that `TESTING=true` in environment
- Verify test database path is correct

**Cost:** $0.00 (no API calls)

---

## Phase 3: Mock API Simulation (No Real API)

**Goal:** Understand how real API would work without making actual calls

**What's covered:**
- 💡 Example API request/response flows
- 💡 Context building demonstration
- 💡 Error handling strategies
- 💡 Cost estimation

**How to run:**
```bash
cd /Users/heng/Development/campfire/ai-bot
chmod +x test_phase3_mock_api.py
uv run python test_phase3_mock_api.py
```

**What this phase does:**
- Shows mock Claude API responses
- Demonstrates how conversation context is built
- Explains error recovery strategies
- Estimates costs for various scenarios

**Example output:**
```
Mock Claude Response:
────────────────────────────────────────────────────────
Based on the Finance Team conversation history, Q3 showed strong performance:

**Revenue Trends:**
- Total revenue: $2.3M (up 12% YoY)
- Enterprise sales: +18% YoY
...
────────────────────────────────────────────────────────

✓ Mock API call simulated successfully
```

**Cost estimates shown:**
- Simple question: ~$0.01 per message
- Financial analysis: ~$0.02 per message
- Long conversation: ~$0.03 per message
- Estimated monthly: $30-50 for moderate usage

**Cost:** $0.00 (no API calls)

---

## Phase 4: Real API Testing (Limited)

**Goal:** Validate production functionality with minimal API usage

**⚠️ WARNING:** This phase uses your real Anthropic API key and costs ~$0.06

**What's tested:**
- 🔴 Real Anthropic Claude API integration
- 🔴 End-to-end message flow
- 🔴 Context awareness with real AI
- 🔴 Production readiness

**Prerequisites:**

1. **Valid API key in `.env`:**
   ```bash
   # Edit .env file
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxx  # Your real key
   TESTING=false                           # IMPORTANT!
   ```

2. **Start Flask in production mode:**
   ```bash
   cd /Users/heng/Development/campfire/ai-bot

   # Make sure TESTING=false
   grep TESTING .env

   # Start Flask
   uv run python src/app.py
   ```

3. **Run Phase 4 tests:**
   ```bash
   # In a new terminal
   cd /Users/heng/Development/campfire/ai-bot
   chmod +x test_phase4_real_api.py
   uv run python test_phase4_real_api.py
   ```

**What happens:**

1. **Confirmation prompt:**
   ```
   ⚠️  REAL API WARNING
   THIS WILL USE YOUR REAL ANTHROPIC API KEY
   AND INCUR ACTUAL COSTS!

   Estimated costs:
     - Test 1: ~$0.01
     - Test 2: ~$0.02
     - Test 3: ~$0.03
     Total: ~$0.06

   Type 'YES' to proceed:
   ```

2. **Tests run (only if you confirm):**
   - Simple greeting (validates API connectivity)
   - Context-aware question (tests conversation search)
   - User context query (tests user data retrieval)

**Expected output:**
```
✓ Response received in 2.34s

🤖 Bot Response:
────────────────────────────────────────────────────────
Hello! I'm your financial analyst AI assistant. How can I
help you with financial analysis or data today?
────────────────────────────────────────────────────────

✓ Real API response detected!

Results: 4/4 tests passed
🎉 All Phase 4 tests passed!
✓ Bot is PRODUCTION READY!
```

**If tests fail:**
- **"This looks like a fallback response"** → Check `TESTING=false` in `.env`
- **"API error"** → Verify API key is valid
- **"Cannot connect"** → Ensure Flask is running on port 5001
- **Rate limit exceeded** → Wait a few minutes and retry

**Cost:** ~$0.06 total

---

## Testing Checklist

Use this checklist to track your progress:

- [ ] **Phase 1 Complete:** All tool tests pass
- [ ] **Phase 2 Complete:** Flask webhook tests pass
- [ ] **Phase 3 Complete:** Mock API demonstrations reviewed
- [ ] **Phase 4 Complete:** Real API tests pass (optional)
- [ ] **Docker Build:** Image builds successfully
- [ ] **Docker Run:** Container runs and health check passes
- [ ] **Production Ready:** All phases successful

---

## Configuration Summary

### Testing Mode (Phase 2)

**File:** `.env.testing` or `.env` with `TESTING=true`

```bash
TESTING=true
ANTHROPIC_API_KEY=sk-ant-test-fake-key-for-testing
CAMPFIRE_DB_PATH=./tests/fixtures/test.db
FLASK_PORT=5001
LOG_LEVEL=DEBUG
```

**Behavior:**
- Fallback responses (no real API calls)
- Echoes user messages
- Logs all requests

### Production Mode (Phase 4)

**File:** `.env` with `TESTING=false`

```bash
TESTING=false
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx  # Real key
CAMPFIRE_DB_PATH=./tests/fixtures/test.db
FLASK_PORT=5001
LOG_LEVEL=INFO
```

**Behavior:**
- Real Claude API calls
- Intelligent responses
- Costs per request

---

## Troubleshooting

### Issue: "Cannot connect to Flask app"

**Solution:**
```bash
# Check if Flask is running
curl http://localhost:5001/health

# If not running, start it
uv run python src/app.py
```

### Issue: "Database connection failed"

**Solution:**
```bash
# Regenerate test database
uv run python tests/fixtures/setup_test_db.py

# Verify it exists
ls -lh tests/fixtures/test.db
```

### Issue: "Fallback responses in Phase 4"

**Solution:**
```bash
# Check TESTING flag
grep TESTING .env

# Should be: TESTING=false
# If not, edit .env and restart Flask
```

### Issue: "API key invalid"

**Solution:**
```bash
# Verify API key format
grep ANTHROPIC_API_KEY .env

# Should start with: sk-ant-api03-
# Get new key from: https://console.anthropic.com/
```

### Issue: "Port already in use"

**Solution:**
```bash
# Find process using port 5001
lsof -i :5001

# Kill the process
kill -9 <PID>

# Or use different port in .env:
FLASK_PORT=5002
```

---

## Next Steps

After completing all testing phases:

1. **Build Docker image:**
   ```bash
   docker build -t campfire-ai-bot:latest .
   ```

2. **Test Docker locally:**
   ```bash
   docker-compose up -d
   curl http://localhost:5001/health
   ```

3. **Deploy to production:**
   - Follow deployment guide in `README.md`
   - Configure webhook in Campfire UI
   - Test end-to-end with real Campfire instance

---

## Quick Reference

| Phase | API Calls | Cost | Duration | Purpose |
|-------|-----------|------|----------|---------|
| Phase 1 | ❌ None | $0.00 | 1 min | Test database tools |
| Phase 2 | ❌ None | $0.00 | 2 min | Test Flask webhook |
| Phase 3 | ❌ None | $0.00 | 2 min | Review mock scenarios |
| Phase 4 | ✅ 3 calls | $0.06 | 5 min | Validate production |

**Total testing cost:** $0.06

**Recommended order:**
1. Phase 1 → Phase 2 → Phase 3 → Phase 4
2. Fix issues at each phase before proceeding
3. Only run Phase 4 when Phases 1-3 pass

---

## Files Reference

```
ai-bot/
├── test_phase1_tools.py          # Phase 1: Tools testing
├── test_phase2_flask.py          # Phase 2: Flask testing
├── test_phase3_mock_api.py       # Phase 3: Mock API
├── test_phase4_real_api.py       # Phase 4: Real API
├── .env.testing                  # Testing mode config
├── .env                          # Production config
└── MANUAL_TESTING_GUIDE.md       # This file
```

---

## Support

If you encounter issues not covered in this guide:

1. Check application logs: `tail -f logs/app.log`
2. Check Flask output in terminal
3. Review `.env` configuration
4. Verify API key is valid
5. Check test database: `sqlite3 tests/fixtures/test.db "SELECT * FROM users;"`

---

**Happy Testing! 🧪**
