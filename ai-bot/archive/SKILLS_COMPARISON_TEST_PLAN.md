# Agent Skills Integration - Comparison Test Plan

**Purpose:** Compare v0.2.4.2 (without skills) vs v0.3.0 (with skills) to verify token savings and ensure no regressions.

**Date:** October 18, 2025

---

## Strategy: Side-by-Side Comparison

We'll use **Git branches** to maintain both versions and test them in parallel.

### Setup: Create Comparison Branch

```bash
# Current state: v0.3.0 with Agent Skills
git status  # Should show modified files

# Create a branch for the new implementation
git checkout -b feature/agent-skills-v0.3.0

# Commit the changes
git add .
git commit -m "feat: Add Agent Skills integration (v0.3.0)

- Add .claude/skills/ directory with 4 comprehensive skills
- Update Agent SDK config with setting_sources=['project']
- Update Dockerfile to v0.3.0 with .claude/ copy
- Skills: Financial Analysis, Knowledge Base, Conversations, Daily Briefing

Expected benefits:
- 60-80% token reduction on simple queries
- 40-50% token reduction on complex queries
- Progressive disclosure: skills load only when relevant"

# Now we can switch between versions easily
```

---

## Comparison Method 1: Git Checkout Testing

### Test Baseline (v0.2.4.2 - Without Skills)

```bash
# Switch to baseline version
git checkout main  # Or the commit before skills integration

# Verify version
grep 'version="' ai-bot/Dockerfile
# Should show: version="0.2.4.2"

# Verify no skills directory
ls -la ai-bot/.claude/skills/
# Should show: No such file or directory

# Verify agent config
grep 'setting_sources' ai-bot/src/campfire_agent.py
# Should show: Nothing (setting_sources not present)

# Run baseline tests
cd ai-bot
TESTING=true CAMPFIRE_URL=https://chat.smartice.ai uv run python src/app_fastapi.py
# Server runs on http://localhost:8000

# Test queries (see Test Scenarios below)
# Record token usage from logs
```

### Test New Version (v0.3.0 - With Skills)

```bash
# Switch to skills branch
git checkout feature/agent-skills-v0.3.0

# Verify version
grep 'version="' ai-bot/Dockerfile
# Should show: version="0.3.0"

# Verify skills exist
ls -la ai-bot/.claude/skills/
# Should show: 4 skill directories

# Verify agent config
grep 'setting_sources' ai-bot/src/campfire_agent.py
# Should show: "setting_sources": ["project"]

# Run new version tests
cd ai-bot
TESTING=true CAMPFIRE_URL=https://chat.smartice.ai uv run python src/app_fastapi.py
# Server runs on http://localhost:8000

# Test same queries
# Record token usage from logs
# Compare with baseline
```

---

## Comparison Method 2: Docker Container Testing

### Build Both Versions as Separate Images

```bash
# Build baseline (v0.2.4.2)
git checkout main
docker build -t hengwoo/campfire-ai-bot:0.2.4.2 ai-bot/

# Build new version (v0.3.0)
git checkout feature/agent-skills-v0.3.0
docker build -t hengwoo/campfire-ai-bot:0.3.0 ai-bot/

# Now you have both images available
docker images | grep campfire-ai-bot
# Should show:
# hengwoo/campfire-ai-bot   0.3.0     [hash]   [size]
# hengwoo/campfire-ai-bot   0.2.4.2   [hash]   [size]
```

### Run Baseline Container

```bash
# Stop any running containers
docker-compose down

# Modify docker-compose.yml temporarily to use 0.2.4.2
# Or use direct docker run:
docker run --rm -it \
  --name campfire-ai-bot-baseline \
  -p 5000:8000 \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -e CAMPFIRE_URL=https://chat.smartice.ai \
  -v $(pwd)/ai-knowledge:/app/ai-knowledge \
  hengwoo/campfire-ai-bot:0.2.4.2

# Test queries and record results
```

### Run New Version Container

```bash
# Stop baseline
docker stop campfire-ai-bot-baseline

# Run new version
docker run --rm -it \
  --name campfire-ai-bot-skills \
  -p 5000:8000 \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -e CAMPFIRE_URL=https://chat.smartice.ai \
  -v $(pwd)/ai-knowledge:/app/ai-knowledge \
  hengwoo/campfire-ai-bot:0.3.0

# Test same queries and compare
```

---

## Test Scenarios

### Scenario 1: Simple Query (Should show 60-80% token reduction)

**Query:** "Hello" or "你好"

**Expected Behavior:**
- **v0.2.4.2 (Baseline):** Loads full system prompt + all tool definitions (~2500 tokens)
- **v0.3.0 (Skills):** Loads only skill metadata (~500 tokens), no full skill content

**How to Verify:**
```bash
# Send test request
curl -X POST http://localhost:5000/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {"id": 1, "name": "Test User"},
    "room": {"id": 1, "name": "Test Room"},
    "content": "Hello"
  }'

# Check logs for token usage
docker logs campfire-ai-bot-baseline 2>&1 | grep -i "tokens"
# vs
docker logs campfire-ai-bot-skills 2>&1 | grep -i "tokens"
```

**Record Results:**
```
Baseline:  Input: _____ tokens | Output: _____ tokens | Total: _____ tokens
Skills:    Input: _____ tokens | Output: _____ tokens | Total: _____ tokens
Savings:   ______%
```

### Scenario 2: Financial Query (Should show 40-50% token reduction)

**Query:** "Calculate ROE for 野百灵" or "分析财务报表"

**Expected Behavior:**
- **v0.2.4.2:** Loads full system prompt + all tool definitions (~2500 tokens)
- **v0.3.0:** Loads skill metadata + campfire-financial-analysis SKILL.md (~1300 tokens)

**Test Request:**
```bash
curl -X POST http://localhost:5000/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {"id": 1, "name": "Test User"},
    "room": {"id": 1, "name": "Test Room"},
    "content": "Calculate ROE for our restaurant"
  }'
```

**Record Results:**
```
Baseline:  Input: _____ tokens | Output: _____ tokens | Total: _____ tokens
Skills:    Input: _____ tokens | Output: _____ tokens | Total: _____ tokens
Savings:   ______%
```

### Scenario 3: Knowledge Base Query

**Query:** "What's our expense reimbursement policy?"

**Expected Behavior:**
- **v0.2.4.2:** Loads full system prompt (~2500 tokens)
- **v0.3.0:** Loads metadata + campfire-kb SKILL.md (~900 tokens)

**Test Request:**
```bash
curl -X POST http://localhost:5000/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {"id": 1, "name": "Test User"},
    "room": {"id": 1, "name": "Test Room"},
    "content": "What is our expense reimbursement policy?"
  }'
```

### Scenario 4: Conversation Search

**Query:** "What did we discuss yesterday?"

**Expected Behavior:**
- **v0.2.4.2:** Loads full system prompt (~2500 tokens)
- **v0.3.0:** Loads metadata + campfire-conversations SKILL.md (~800 tokens)

### Scenario 5: Daily Briefing

**Query:** "Generate yesterday's briefing"

**Expected Behavior:**
- **v0.2.4.2:** Loads full system prompt (~2500 tokens)
- **v0.3.0:** Loads metadata + campfire-daily-briefing SKILL.md (~1000 tokens)

### Scenario 6: Mixed Query (Multiple Skills Needed)

**Query:** "Search past financial discussions and generate a summary"

**Expected Behavior:**
- **v0.2.4.2:** Loads full system prompt (~2500 tokens)
- **v0.3.0:** Loads metadata + financial + conversations skills (~1800 tokens)

### Scenario 7: Non-Matching Query (No Skills Triggered)

**Query:** "What's the weather like?"

**Expected Behavior:**
- Both versions should behave similarly (general knowledge response)
- **v0.3.0** may still save tokens by loading only metadata

---

## Token Usage Measurement

### Method 1: Application Logs

The Agent SDK logs token usage. Look for lines like:

```
[Agent SDK] Input tokens: 2456
[Agent SDK] Output tokens: 324
[Agent SDK] Total tokens: 2780
```

### Method 2: Anthropic API Dashboard

Check the Anthropic Console (console.anthropic.com):
- Go to API Usage
- Compare request costs between test periods
- Look for per-request token counts

### Method 3: Add Logging to Code (Temporary)

Add to `src/campfire_agent.py` after API calls:

```python
# Temporary logging for comparison testing
import logging
logger = logging.getLogger(__name__)

# After agent response
logger.info(f"[TOKEN USAGE] Input: {response.usage.input_tokens}, "
           f"Output: {response.usage.output_tokens}, "
           f"Total: {response.usage.input_tokens + response.usage.output_tokens}")
```

---

## Comparison Checklist

### Functional Verification (No Regressions)

Test that all existing features still work:

- [ ] **Financial Analysis:** Excel file processing works
- [ ] **MCP Tools:** All 9 tools (3 base + 4 KB + 2 briefing) accessible
- [ ] **Financial MCP:** 16 financial tools work correctly
- [ ] **Conversations:** Search and user context functions
- [ ] **Knowledge Base:** Search, read, list, store operations
- [ ] **Daily Briefing:** Generation and search
- [ ] **Multi-turn:** Agent can handle complex multi-step queries
- [ ] **Sessions:** Hot/warm/cold paths work
- [ ] **Progress Milestones:** Real-time updates display

### Performance Verification (Expected Improvements)

- [ ] **Simple queries:** 60-80% token reduction
- [ ] **Complex queries:** 40-50% token reduction
- [ ] **Skills load correctly:** Only when descriptions match
- [ ] **No false triggers:** Skills don't load inappropriately
- [ ] **Response quality:** Same or better than baseline

### Quality Verification

- [ ] **Response accuracy:** Same quality as before
- [ ] **Response completeness:** No missing information
- [ ] **Response time:** Similar or better latency
- [ ] **Error handling:** Same or better error messages

---

## Results Recording Template

### Test Execution Log

```markdown
## Test Run: [Date/Time]

**Environment:**
- Git branch: feature/agent-skills-v0.3.0 vs main
- Docker image: 0.3.0 vs 0.2.4.2
- Test method: [Local/Docker]

### Scenario 1: Simple Query ("Hello")

**Baseline (v0.2.4.2):**
- Input tokens: _____
- Output tokens: _____
- Total: _____
- Response time: _____ seconds
- Response quality: [Same/Better/Worse]

**Skills (v0.3.0):**
- Input tokens: _____
- Output tokens: _____
- Total: _____
- Response time: _____ seconds
- Response quality: [Same/Better/Worse]
- Skills loaded: [None/List]

**Comparison:**
- Token savings: _____%
- Time delta: _____ seconds
- Quality: [✅ No regression / ⚠️ Issue found]

### Scenario 2: Financial Query
[Repeat same structure...]

### Overall Assessment

**Token Savings Achieved:**
- Simple queries: ____% (target: 60-80%)
- Complex queries: ____% (target: 40-50%)

**Functionality:**
- Regressions found: [Yes/No]
- New issues: [List or None]

**Recommendation:**
- [ ] Proceed with deployment
- [ ] Needs investigation
- [ ] Rollback required
```

---

## Quick Comparison Script

Create a helper script to automate testing:

```bash
#!/bin/bash
# compare_versions.sh

echo "=== Campfire AI Bot - Skills Comparison Test ==="

# Test query
QUERY=${1:-"Hello"}

echo ""
echo "Testing query: '$QUERY'"
echo ""

# Test baseline
echo "--- Baseline (v0.2.4.2) ---"
git checkout main > /dev/null 2>&1
cd ai-bot
uv run python -c "
import requests
response = requests.post('http://localhost:5000/webhook/financial_analyst', json={
    'creator': {'id': 1, 'name': 'Test'},
    'room': {'id': 1, 'name': 'Test'},
    'content': '$QUERY'
})
print(f'Status: {response.status_code}')
"
cd ..

echo ""
echo "--- Skills (v0.3.0) ---"
git checkout feature/agent-skills-v0.3.0 > /dev/null 2>&1
cd ai-bot
uv run python -c "
import requests
response = requests.post('http://localhost:5000/webhook/financial_analyst', json={
    'creator': {'id': 1, 'name': 'Test'},
    'room': {'id': 1, 'name': 'Test'},
    'content': '$QUERY'
})
print(f'Status: {response.status_code}')
"
cd ..

echo ""
echo "Check logs above for token usage comparison"
```

**Usage:**
```bash
chmod +x compare_versions.sh
./compare_versions.sh "Hello"
./compare_versions.sh "Calculate ROE"
./compare_versions.sh "What's our policy on expenses?"
```

---

## Decision Criteria

### Proceed with Deployment if:
- ✅ Token savings meet targets (>50% on simple, >30% on complex)
- ✅ No functional regressions
- ✅ Response quality maintained or improved
- ✅ All tests pass

### Investigate Further if:
- ⚠️ Token savings below 50% on simple queries
- ⚠️ Skills load incorrectly (false positives/negatives)
- ⚠️ Response quality degraded
- ⚠️ Some tests fail

### Rollback if:
- ❌ Critical functionality broken
- ❌ Severe performance degradation
- ❌ Token usage actually increases
- ❌ Major quality issues

---

## Rollback Plan (If Needed)

If issues are found with v0.3.0:

```bash
# Quick rollback to v0.2.4.2
git checkout main

# Rebuild and deploy baseline
docker build -t hengwoo/campfire-ai-bot:latest ai-bot/
docker push hengwoo/campfire-ai-bot:latest

# Deploy to production
ssh root@128.199.175.50  # Or use DigitalOcean console
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:latest
docker-compose up -d
```

---

## Next Steps After Comparison

1. **Document results** in this file (fill in the template above)
2. **Share findings** with team for review
3. **Make deployment decision** based on criteria
4. **Proceed to production** if all criteria met
5. **Monitor production** for 24-48 hours after deployment

---

**Author:** Claude Code
**Date:** October 18, 2025
**Status:** Ready for testing
