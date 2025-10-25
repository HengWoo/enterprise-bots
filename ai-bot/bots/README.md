# Bot Configurations

This directory contains JSON configuration files for different AI bot personalities.

## How It Works

Each bot has its own JSON configuration file that defines:
- **Personality:** System prompt and behavior
- **Model:** Which Claude model to use
- **Settings:** Temperature, max tokens, thinking budget
- **Tools:** Which capabilities to enable
- **Language:** Preferred languages

When a webhook is received, Flask determines which bot to use and loads its configuration.

## Bot Selection Priority

1. **URL path:** `POST /webhook/financial_analyst`
2. **Query parameter:** `POST /webhook?bot_id=financial_analyst`
3. **ENV bot_key match:** Matches `BOT_KEY` from `.env` file
4. **Default:** Uses `default.json` configuration

## Available Bots

### financial_analyst.json
**财务分析师** - Financial Analyst
- **Model:** claude-3-5-haiku-20241022
- **Bot Key:** `2-CsheovnLtzjM`
- **Language:** Chinese (primary), English
- **Specialization:** Financial analysis, reporting, forecasting
- **Temperature:** 1.0 (creative)

### technical_assistant.json
**技术助手** - Technical Assistant
- **Model:** claude-3-5-haiku-20241022
- **Bot Key:** (not configured)
- **Language:** English (primary), Chinese
- **Specialization:** Software engineering, code review, debugging
- **Temperature:** 0.7 (balanced)

### default.json
**AI Assistant** - General Purpose
- **Model:** claude-3-5-haiku-20241022
- **Bot Key:** (not configured)
- **Language:** English, Chinese
- **Specialization:** General assistance
- **Temperature:** 1.0

## Creating a New Bot

1. **Copy an existing configuration:**
   ```bash
   cp financial_analyst.json my_new_bot.json
   ```

2. **Edit the configuration:**
   ```json
   {
     "bot_id": "my_new_bot",
     "bot_key": "your-bot-key-here",
     "name": "My Bot Name",
     "display_name": "My Bot (Display Name)",
     "description": "What this bot does",

     "model_config": {
       "model": "claude-3-5-haiku-20241022",
       "temperature": 1.0,
       "max_tokens": 4096
     },

     "system_prompt": "You are a helpful assistant specialized in...",

     "tools_enabled": [
       "search_conversations",
       "get_user_context"
     ]
   }
   ```

3. **Restart Flask** - Changes are loaded on startup:
   ```bash
   pkill -f "python.*src/app.py"
   uv run python src/app.py
   ```

4. **Test the bot:**
   ```bash
   curl -X POST http://localhost:5001/webhook/my_new_bot \
     -H "Content-Type: application/json" \
     -d '{
       "creator": {"id": 1, "name": "Test User", "email_address": "test@example.com"},
       "room": {"id": 1, "name": "Test Room"},
       "content": "<p>@bot Hello!</p>"
     }'
   ```

## Configuration Reference

### Required Fields

- `bot_id` (string): Unique identifier for this bot
- `name` (string): Bot name
- `system_prompt` (string): Instructions for the AI

### Model Configuration

```json
"model_config": {
  "model": "claude-3-5-haiku-20241022",  // or "claude-sonnet-4-5-20250929"
  "temperature": 1.0,                     // 0.0 (deterministic) to 1.0 (creative)
  "max_tokens": 4096,                     // Maximum response length
  "thinking": {
    "enabled": false,                     // Enable extended thinking (Sonnet 4.5+ only)
    "budget_tokens": 10000                // Thinking token budget
  }
}
```

### Available Models

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| `claude-3-5-haiku-20241022` | ⚡⚡⚡ Fast | 💰 Cheap | General tasks, quick responses |
| `claude-sonnet-4-5-20250929` | ⚡⚡ Moderate | 💰💰💰 Expensive | Complex reasoning, extended thinking |

### Tools Available

- `search_conversations` - Search past messages
- `get_user_context` - Get user preferences and history
- `query_knowledge_base` - Search company knowledge
- `process_file` - Analyze uploaded files

### Language Settings

```json
"languages": ["zh-CN", "en"],      // Supported languages
"default_language": "zh-CN"        // Default response language
```

## Examples

### Simple Bot (Minimal)
```json
{
  "bot_id": "simple_bot",
  "bot_key": null,
  "name": "Simple Bot",
  "system_prompt": "You are a helpful assistant.",
  "model_config": {
    "model": "claude-3-5-haiku-20241022",
    "temperature": 1.0,
    "max_tokens": 2048
  }
}
```

### Advanced Bot (Full Features)
```json
{
  "bot_id": "advanced_analyst",
  "bot_key": "3-ABcDEfGH",
  "name": "Advanced Analyst",
  "display_name": "Advanced Financial Analyst AI",
  "description": "Expert financial analysis with extended thinking",

  "model_config": {
    "model": "claude-sonnet-4-5-20250929",
    "temperature": 0.8,
    "max_tokens": 8192,
    "thinking": {
      "enabled": true,
      "budget_tokens": 20000
    }
  },

  "system_prompt": "You are an advanced financial analyst...",

  "tools_enabled": [
    "search_conversations",
    "get_user_context",
    "query_knowledge_base",
    "process_file"
  ],

  "languages": ["en", "zh-CN"],
  "default_language": "en",

  "capabilities": {
    "file_analysis": true,
    "conversation_memory": true,
    "user_personalization": true,
    "knowledge_base_access": true
  }
}
```

## Testing Different Bots

```bash
# Test financial analyst
curl -X POST http://localhost:5001/webhook/financial_analyst -H "Content-Type: application/json" -d '...'

# Test technical assistant
curl -X POST http://localhost:5001/webhook/technical_assistant -H "Content-Type: application/json" -d '...'

# Test default bot
curl -X POST http://localhost:5001/webhook -H "Content-Type: application/json" -d '...'
```

## Hot Reload

Currently, bot configurations are loaded on Flask startup. To reload after making changes:

```bash
# Kill and restart Flask
pkill -f "python.*src/app.py"
uv run python src/app.py
```

**Future:** Add `/admin/reload-bots` endpoint for hot reload without restart.

## Best Practices

1. **Use descriptive bot_ids** - Use lowercase with underscores: `financial_analyst`
2. **Write clear system prompts** - Be specific about the bot's role and capabilities
3. **Choose appropriate models** - Use Haiku for speed, Sonnet for quality
4. **Set reasonable max_tokens** - Balance response length with cost
5. **Test thoroughly** - Test each bot before deploying to production
6. **Version control** - Keep bot configs in git to track changes

## Troubleshooting

### Bot not found
- Check that JSON file exists in `/bots/` directory
- Verify `bot_id` matches filename (without .json)
- Restart Flask to reload configurations

### Invalid configuration
- Validate JSON syntax: `cat bots/my_bot.json | jq`
- Check required fields are present
- Review Flask logs for error messages

### Wrong bot responding
- Check URL path or query parameter
- Verify `BOT_KEY` in `.env` matches desired bot
- Check Flask logs to see which bot was selected

## Cost Optimization

**Tips for reducing API costs:**
- Use Haiku for most tasks (80% cheaper than Sonnet)
- Set `max_tokens` to minimum needed
- Disable thinking for simple queries
- Use lower temperature for factual responses (0.3-0.7)

---

**Last Updated:** 2025-10-06
