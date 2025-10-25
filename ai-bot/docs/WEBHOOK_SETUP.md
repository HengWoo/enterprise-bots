# Webhook Setup Guide for Multiple Bots

**Purpose:** Configure Campfire webhooks for all 3 AI bots (Financial Analyst, Technical Assistant, Briefing Assistant)

---

## Current Status

| Bot | Name | bot_key | Webhook Status |
|-----|------|---------|----------------|
| financial_analyst | 财务分析师 | `2-CsheovnLtzjM` | ✅ Active |
| technical_assistant | 技术助手 | `null` | ⏳ Needs setup |
| briefing_assistant | 日报助手 | `null` | ⏳ Needs setup |

---

## Why Multiple Bots Need Separate Webhooks

**Current Architecture:**
- FastAPI receives webhooks at `/webhook/{bot_id}`
- Each bot has different tools and capabilities
- Bot selection based on which Campfire bot user was mentioned

**Example:**
- User mentions `@财务分析师` → Campfire sends webhook to `/webhook/financial_analyst`
- User mentions `@技术助手` → Campfire sends webhook to `/webhook/technical_assistant`
- User mentions `@日报助手` → Campfire sends webhook to `/webhook/briefing_assistant`

---

## Step-by-Step Setup

### Step 1: Create Bot Users in Campfire

**For Technical Assistant (技术助手):**

1. Log into Campfire as admin: https://chat.smartice.ai
2. Go to **Settings** → **Bots**
3. Click **New Bot**
4. Fill in details:
   - **Name:** `技术助手`
   - **Username:** `technical_assistant` (or `tech`)
   - **Description:** `Technical support and code analysis assistant`
5. Click **Create Bot**
6. **Copy the bot_key** (format: `X-XXXXXXXXX`)
7. Update `bots/technical_assistant.json`:
   ```json
   {
     "bot_id": "technical_assistant",
     "bot_key": "X-XXXXXXXXX",  // ← Paste here
     ...
   }
   ```

**For Briefing Assistant (日报助手):**

1. In Campfire, go to **Settings** → **Bots**
2. Click **New Bot**
3. Fill in details:
   - **Name:** `日报助手`
   - **Username:** `briefing_assistant` (or `briefing`)
   - **Description:** `Daily briefing generation and historical search assistant`
4. Click **Create Bot**
5. **Copy the bot_key** (format: `Y-YYYYYYYYY`)
6. Update `bots/briefing_assistant.json`:
   ```json
   {
     "bot_id": "briefing_assistant",
     "bot_key": "Y-YYYYYYYYY",  // ← Paste here
     ...
   }
   ```

### Step 2: Configure Webhooks in Campfire

**For each bot, configure the webhook URL:**

**Technical Assistant:**
- **Bot:** 技术助手
- **Webhook URL:** `http://128.199.175.50:5000/webhook/technical_assistant`
- **Events:** Message created (when bot is mentioned)

**Briefing Assistant:**
- **Bot:** 日报助手
- **Webhook URL:** `http://128.199.175.50:5000/webhook/briefing_assistant`
- **Events:** Message created (when bot is mentioned)

**Financial Analyst (already configured):**
- **Bot:** 财务分析师
- **Webhook URL:** `http://128.199.175.50:5000/webhook/financial_analyst`
- **Events:** Message created (when bot is mentioned)

### Step 3: Update Bot Configs Locally

After getting the bot_keys from Campfire:

```bash
cd /Users/heng/Development/campfire/ai-bot

# Edit technical_assistant.json
# Replace "bot_key": null with "bot_key": "X-XXXXXXXXX"

# Edit briefing_assistant.json
# Replace "bot_key": null with "bot_key": "Y-YYYYYYYYY"
```

### Step 4: Test Each Bot Locally

```bash
# Start FastAPI server (if not running)
cd /Users/heng/Development/campfire/ai-bot
FASTAPI_PORT=5002 TESTING=true CAMPFIRE_DB_PATH=./tests/fixtures/test.db \
  uv run uvicorn src.app_fastapi:app --reload --port 5002

# Test Technical Assistant
curl -X POST http://localhost:5002/webhook/technical_assistant \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {"id": 1, "name": "Test User", "email_address": "test@example.com"},
    "room": {"id": 1, "name": "Test Room"},
    "content": "<p>@技术助手 介绍一下你的功能</p>"
  }'

# Test Briefing Assistant
curl -X POST http://localhost:5002/webhook/briefing_assistant \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {"id": 1, "name": "Test User", "email_address": "test@example.com"},
    "room": {"id": 1, "name": "Test Room"},
    "content": "<p>@日报助手 生成昨天的日报</p>"
  }'
```

Expected output:
```
[BotManager] 📋 Loading bot configurations...
[BotManager] ✅ Loaded: financial_analyst (财务分析师)
[BotManager] ✅ Loaded: technical_assistant (技术助手)
[BotManager] ✅ Loaded: briefing_assistant (日报助手)
[BotManager] ✅ Loaded: default (AI Assistant)
[BotManager] 📊 Total bots loaded: 4
```

### Step 5: Deploy to Production

After verifying locally:

```bash
# Rebuild Docker image with updated bot configs
cd /Users/heng/Development/campfire/ai-bot
docker buildx build --platform linux/amd64 \
  -t hengwoo/campfire-ai-bot:0.2.3 \
  -t hengwoo/campfire-ai-bot:latest .

# Push to Docker Hub
docker push hengwoo/campfire-ai-bot:0.2.3
docker push hengwoo/campfire-ai-bot:latest

# Deploy on server (via DigitalOcean console)
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:latest
docker-compose up -d
docker logs -f campfire-ai-bot
```

### Step 6: Verify in Production

Test each bot in a Campfire room:

```
@财务分析师 介绍一下你的功能
@技术助手 介绍一下你的功能
@日报助手 介绍一下你的功能
```

Expected behavior:
- Each bot responds with their specialized introduction
- Check logs to confirm webhook routing works:
  ```bash
  docker logs campfire-ai-bot | grep "webhook"
  ```

---

## Webhook URL Format

All bots use the same FastAPI server but different endpoints:

```
Base URL: http://128.199.175.50:5000

Financial Analyst:    /webhook/financial_analyst
Technical Assistant:  /webhook/technical_assistant
Briefing Assistant:   /webhook/briefing_assistant
Default/Fallback:     /webhook (uses default.json)
```

---

## Troubleshooting

### Issue: Bot responds but uses wrong configuration

**Problem:** Webhook is configured but bot uses default behavior

**Solution:**
1. Check `bot_key` in JSON matches Campfire bot_key
2. Verify webhook URL includes correct `/webhook/{bot_id}` path
3. Check FastAPI logs for bot selection:
   ```
   [FastAPI] 🎯 Selected bot: briefing_assistant
   ```

### Issue: Webhook returns 404 Not Found

**Problem:** FastAPI can't find the bot configuration

**Solution:**
1. Verify JSON file exists: `ls bots/{bot_id}.json`
2. Check `bot_id` matches filename (without .json)
3. Restart FastAPI to reload configs:
   ```bash
   docker-compose restart campfire-ai-bot
   ```

### Issue: Multiple bots respond to same mention

**Problem:** Misconfigured webhooks causing duplicate responses

**Solution:**
1. Check Campfire webhook settings - each bot should have ONE webhook
2. Verify webhook URLs are different for each bot
3. Check for conflicting bot mentions in message

---

## Bot Selection Logic

FastAPI determines which bot to use based on:

1. **URL path** (highest priority): `/webhook/technical_assistant` → loads `technical_assistant.json`
2. **Query parameter**: `/webhook?bot_id=briefing_assistant` → loads `briefing_assistant.json`
3. **bot_key matching**: If webhook payload includes bot_key, match against configs
4. **Default fallback**: If no match, uses `default.json`

---

## Security Considerations

**Bot Keys are Sensitive:**
- ✅ Store in JSON config files (not committed to git if sensitive)
- ✅ Use environment variables for production keys (optional)
- ❌ Never expose bot_keys in public repositories
- ❌ Don't share bot_keys in documentation

**Webhook Security:**
- Current: No authentication (internal network)
- Future: Add webhook signature verification (Campfire supports HMAC)

---

## Cost Implications

**With 3 bots active:**

**Scenario 1: Low usage (100 messages/month per bot)**
- 300 total messages/month
- Estimated cost: $5-10/month

**Scenario 2: Medium usage (500 messages/month per bot)**
- 1500 total messages/month
- Estimated cost: $25-35/month

**Scenario 3: High usage (2000 messages/month per bot)**
- 6000 total messages/month
- Estimated cost: $100-150/month

**Cost Control:**
- Briefing bot uses automatic generation (1 message/day = 30/month)
- Financial analyst is used for complex queries (higher cost per message)
- Technical assistant can use Haiku model (cheaper) for simple queries

---

## Next Steps After Setup

1. **Announce to team:**
   ```
   🎉 New AI assistants available!

   - @财务分析师 - Financial analysis and reporting
   - @技术助手 - Technical support and code review
   - @日报助手 - Daily briefings and historical search

   Try them out by mentioning them in any room!
   ```

2. **Monitor usage:**
   - Check logs: `docker logs -f campfire-ai-bot`
   - Monitor API costs in Anthropic dashboard
   - Track which bots are most popular

3. **Iterate on prompts:**
   - Based on usage patterns, refine system prompts
   - Adjust tool availability per bot
   - Optimize response formats

---

## Summary Checklist

- [ ] Create bot users in Campfire (技术助手, 日报助手)
- [ ] Copy bot_keys from Campfire
- [ ] Update `bots/technical_assistant.json` with bot_key
- [ ] Update `bots/briefing_assistant.json` with bot_key
- [ ] Configure webhooks in Campfire (3 total)
- [ ] Test locally with curl commands
- [ ] Rebuild Docker image with updated configs
- [ ] Deploy to production
- [ ] Verify all 3 bots respond correctly
- [ ] Announce to team
- [ ] Monitor logs and usage

---

**Last Updated:** October 15, 2025
**Version:** 0.2.3
**Status:** Ready for production webhook setup
