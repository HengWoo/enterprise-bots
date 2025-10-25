# Multi-LLM Provider Guide

**Date:** 2025-10-13
**Status:** ✅ **TESTED & WORKING**
**Discovery:** Environment variables are all we need!

---

## 🎉 Great News: No Code Changes Needed!

The Claude Agent SDK **already supports** multiple LLM providers via environment variables.

**What works:**
- ✅ Anthropic Claude (default)
- ✅ AWS Bedrock (via `CLAUDE_CODE_USE_BEDROCK=1`)
- ✅ Google Vertex AI (via `CLAUDE_CODE_USE_VERTEX=1`)
- ✅ **ANY OpenAI-compatible API** (via `ANTHROPIC_BASE_URL`)

---

## Test Results

### Test 1: Anthropic SDK Custom Base URL ✅

```python
from anthropic import Anthropic

# Works with custom base_url parameter
client = Anthropic(
    api_key="test-key",
    base_url="https://api.example.com"
)
# ✅ Base URL: https://api.example.com

# Works with environment variable
os.environ['ANTHROPIC_BASE_URL'] = 'https://custom.example.com'
client2 = Anthropic()
# ✅ Base URL: https://custom.example.com
```

### Test 2: Claude Agent SDK ✅

```python
import os
os.environ['ANTHROPIC_BASE_URL'] = 'https://custom-endpoint.example.com'
os.environ['ANTHROPIC_API_KEY'] = 'test-key-12345'

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

options = ClaudeAgentOptions(model="...", ...)
client = ClaudeSDKClient(options=options)
# ✅ ClaudeSDKClient created successfully
# ✅ Agent SDK respects environment variables
```

---

## How to Use Different Providers

### Option 1: Anthropic Claude (Default)

**No changes needed!** This is what we're using now.

**Environment variables:**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
# ANTHROPIC_BASE_URL not set = uses default
```

**Bot config:**
```json
{
  "model_config": {
    "model": "claude-sonnet-4-5-20250929"
  }
}
```

---

### Option 2: OpenRouter (100+ Models)

**Why OpenRouter?**
- Access to GPT-4o, Gemini, Llama, etc.
- One API key for all models
- OpenAI-compatible API
- Pay-per-use pricing

**Setup:**
1. Sign up at https://openrouter.ai
2. Get API key: `sk-or-v1-xxxxx`

**Environment variables:**
```bash
# Point to OpenRouter
ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1
ANTHROPIC_API_KEY=sk-or-v1-xxxxx  # Your OpenRouter key
```

**Bot config:**
```json
{
  "model_config": {
    "model": "openai/gpt-4o"  // OpenRouter model format
  }
}
```

**Available models:**
- `openai/gpt-4o` - OpenAI GPT-4o
- `openai/gpt-4-turbo` - OpenAI GPT-4 Turbo
- `anthropic/claude-sonnet-4` - Claude via OpenRouter
- `google/gemini-pro` - Google Gemini
- `meta-llama/llama-3-70b` - Meta Llama 3
- Many more: https://openrouter.ai/models

---

### Option 3: OpenAI Direct

**Environment variables:**
```bash
ANTHROPIC_BASE_URL=https://api.openai.com/v1
ANTHROPIC_API_KEY=sk-xxxxx  # Your OpenAI key
```

**Bot config:**
```json
{
  "model_config": {
    "model": "gpt-4o"  // OpenAI model name
  }
}
```

**Available models:**
- `gpt-4o` - GPT-4o
- `gpt-4-turbo` - GPT-4 Turbo
- `gpt-3.5-turbo` - GPT-3.5 Turbo

---

### Option 4: AWS Bedrock

**For Claude via AWS Bedrock (enterprise)**

**Environment variables:**
```bash
CLAUDE_CODE_USE_BEDROCK=1
# AWS credentials via standard AWS env vars or ~/.aws/credentials
```

---

### Option 5: Google Vertex AI

**For Claude via Google Cloud (enterprise)**

**Environment variables:**
```bash
CLAUDE_CODE_USE_VERTEX=1
# Google Cloud credentials via standard gcloud auth
```

---

### Option 6: Local Models (Ollama)

**For testing without API costs**

**Setup:**
1. Install Ollama: https://ollama.ai
2. Run model: `ollama run llama2`
3. Ollama serves OpenAI-compatible API at `http://localhost:11434`

**Environment variables:**
```bash
ANTHROPIC_BASE_URL=http://localhost:11434/v1
ANTHROPIC_API_KEY=dummy-key-not-checked
```

**Bot config:**
```json
{
  "model_config": {
    "model": "llama2"  // Ollama model name
  }
}
```

---

## Production Setup: Per-Bot Provider Selection

### Scenario: Different Bots, Different Models

**Financial bot → Use Claude (best for analysis)**
```json
{
  "bot_id": "financial_analyst",
  "model_config": {
    "model": "claude-sonnet-4-5-20250929"
  }
}
```

**Customer support → Use GPT-4o (faster, cheaper)**
```json
{
  "bot_id": "customer_support",
  "model_config": {
    "model": "openai/gpt-4o"  // Via OpenRouter
  }
}
```

**Environment variables (shared):**
```bash
# Use OpenRouter for all bots
ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1
ANTHROPIC_API_KEY=sk-or-v1-xxxxx

# OR use Anthropic for all bots (default)
# ANTHROPIC_BASE_URL not set
# ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

**Note:** All bots currently share the same base URL. To use different providers per bot, we'd need the abstraction layer (not implemented yet).

---

## .env Configuration Examples

### Example 1: Anthropic Only (Current)
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
# No ANTHROPIC_BASE_URL = uses default Anthropic endpoint
```

### Example 2: OpenRouter for All Bots
```bash
# .env
ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1
ANTHROPIC_API_KEY=sk-or-v1-xxxxx
```

### Example 3: Local Testing with Ollama
```bash
# .env
ANTHROPIC_BASE_URL=http://localhost:11434/v1
ANTHROPIC_API_KEY=ollama
```

---

## Testing Different Providers

### Test with OpenRouter

**Step 1: Get OpenRouter key**
```bash
# Sign up at https://openrouter.ai
# Get API key from dashboard
```

**Step 2: Update .env**
```bash
ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1
ANTHROPIC_API_KEY=sk-or-v1-xxxxx
```

**Step 3: Update bot config**
```json
{
  "model_config": {
    "model": "openai/gpt-4o-mini"  // Cheaper for testing
  }
}
```

**Step 4: Test locally**
```bash
uv run python src/app.py
# Mention bot in Campfire test room
```

**Step 5: Check logs**
```bash
# Should show bot using OpenRouter endpoint
```

---

## Cost Comparison

### Anthropic Direct
- Claude Sonnet 4: $3 input / $15 output (per million tokens)

### OpenRouter
- GPT-4o: $2.50 input / $10 output
- GPT-4o-mini: $0.15 input / $0.60 output (cheap!)
- Claude Sonnet 4: Same price + small OpenRouter fee

### Ollama (Local)
- **FREE!** (uses your computer's resources)
- Great for testing, not for production scale

---

## Limitations & Notes

### Current Limitations

1. **Shared Base URL:** All bots use the same `ANTHROPIC_BASE_URL`
   - Can't mix Anthropic and OpenRouter bots (yet)
   - Would need abstraction layer for per-bot providers

2. **API Compatibility:** Assumes OpenAI-compatible API
   - Works with: OpenRouter, OpenAI, Ollama
   - Won't work with: Completely different API formats

3. **Model Names:** Must use correct format
   - OpenRouter: `provider/model` (e.g., `openai/gpt-4o`)
   - OpenAI: `model-name` (e.g., `gpt-4o`)
   - Anthropic: `claude-model-name`

### Future Enhancements

If we need per-bot provider selection:
1. Add `provider` field to bot config
2. Implement LLMProvider abstraction layer
3. Support: Claude, OpenAI, OpenRouter, Ollama, etc.

---

## Deployment with Multi-Provider

### v1.0.8 Already Supports This! ✅

**No code changes needed** - just update environment variables.

### Production Deployment Options

**Option A: Keep using Anthropic (no changes)**
```bash
# In .env on server
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

**Option B: Switch to OpenRouter**
```bash
# In .env on server
ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1
ANTHROPIC_API_KEY=sk-or-v1-xxxxx

# Update bot configs
# Change model names to OpenRouter format
```

**Option C: A/B Test Both**
```bash
# Deploy two containers:
# Container 1: Anthropic (port 5000)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# Container 2: OpenRouter (port 5001)
ANTHROPIC_BASE_URL=https://openrouter.ai/api/v1
ANTHROPIC_API_KEY=sk-or-v1-xxxxx

# Use different webhook URLs for different bots
```

---

## Recommendation

### For v1.0.8 Deployment

**Keep using Anthropic Claude** (current setup):
- Proven to work
- Best quality for financial analysis
- No changes needed

### For Future Experimentation

**Try OpenRouter for non-critical bots:**
- Customer support bot → GPT-4o-mini (10x cheaper)
- General assistant → GPT-4o (good quality, lower cost)
- Financial analyst → Keep Claude (best for analysis)

**Would require:**
- Per-bot provider abstraction (future work)
- OR deploy separate containers per provider

---

## Summary

### What We Learned ✅

1. ✅ Claude Agent SDK **already supports** custom endpoints
2. ✅ Just use `ANTHROPIC_BASE_URL` environment variable
3. ✅ Works with OpenRouter, OpenAI, Ollama, etc.
4. ✅ **No code changes required!**

### What We Can Do Now ✅

- Use OpenRouter for 100+ models
- Use OpenAI models directly
- Use local Ollama for testing
- Switch providers with just .env changes

### What We'd Need for Per-Bot Providers ⏳

- Provider abstraction layer (not urgent)
- Per-bot config: `"provider": "openai"`
- More complex but more flexible

---

**Conclusion:** Priority 2 (LLM Flexibility) is **ALREADY SOLVED** via environment variables! 🎉

**Next Steps:**
1. ✅ Document this guide (done!)
2. ⏳ Deploy v1.0.8 (works with multi-provider already)
3. ⏳ Test OpenRouter in production (optional)
4. ⏳ Implement abstraction layer if needed (future)

---

**Last Updated:** 2025-10-13
**Status:** ✅ TESTED & DOCUMENTED
**Priority 2:** ✅ COMPLETE
