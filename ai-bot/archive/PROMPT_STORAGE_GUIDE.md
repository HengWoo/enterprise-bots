# Prompt Storage and Management Guide

**Last Updated:** 2025-10-19
**Purpose:** Document where bot prompts are stored and how to iterate on them

---

## 📁 Prompt Storage Locations

### 1. Bot Configuration Files (Primary Storage)

**Location:** `bots/*.json`

**Structure:**
```
ai-bot/
├── bots/
│   ├── financial_analyst.json      ← 财务分析师 prompts
│   ├── technical_assistant.json    ← 技术助手 prompts
│   ├── personal_assistant.json     ← 个人助理 prompts
│   └── briefing_assistant.json     ← 日报助手 prompts
```

**Content:** Each JSON file contains:
- `bot_id` - Unique identifier
- `bot_key` - Campfire API key
- `name` - Display name
- `system_prompt` - **THE MAIN PROMPT** (stored as escaped string)
- `model_config` - Model settings
- `tools_enabled` - Available tools
- `capabilities` - Feature flags
- `settings` - Bot-specific settings

**Example Structure:**
```json
{
  "bot_id": "financial_analyst",
  "bot_key": "2-CsheovnLtzjM",
  "name": "财务分析师",
  "system_prompt": "你是一个专业的财务分析师AI助手...",  // ← THIS IS THE PROMPT
  "model_config": { ... },
  "tools_enabled": [ ... ],
  "capabilities": { ... }
}
```

---

## 🔍 Current Bot Prompts

### Financial Analyst (财务分析师)

**File:** `bots/financial_analyst.json` (line 16)

**Prompt Sections:**
1. **Role Definition** - "你是一个专业的财务分析师AI助手"
2. **Core Capabilities** - 7 specialized areas (报表分析, 指标诊断, 投资建议, etc.)
3. **Working Principles** - Language, professionalism, data citation
4. **Knowledge Base Guide** - When and how to use company KB
5. **Communication Transparency** - Tool usage explanation rules
6. **Response Formatting** - HTML formatting requirements
7. **Tool Selection Guide (NEW v0.3.0)** - Dual MCP system (Financial + Skills)

**Key Features:**
- ✅ Hierarchical Complementary System (both Financial MCP and Skills MCP)
- ✅ Clear tool separation (analysis vs. creation)
- ✅ Multi-step workflow examples
- ✅ Progressive skill loading principles

---

### Technical Assistant (技术助手)

**File:** `bots/technical_assistant.json` (line 16)

**Prompt Sections:**
1. **Role Definition** - "你是一个专业的技术助手AI"
2. **Core Capabilities** - Technical support, troubleshooting, documentation
3. **Working Principles** - English-focused, clear explanations
4. **Knowledge Base Access** - Technical docs and guides
5. **Response Formatting** - Code blocks, technical diagrams

**Key Features:**
- ✅ English + Chinese bilingual support
- ✅ Code-focused responses
- ✅ Technical documentation expertise

---

### Personal Assistant (个人助理)

**File:** `bots/personal_assistant.json` (line 16)

**Prompt Sections:**
1. **Role Definition** - "你是一个专业的个人助手AI"
2. **Core Capabilities** - Task management, reminders, notes, preferences
3. **Tool Usage Rules** - How to use personal productivity tools
4. **Privacy Principles** - DM usage, data isolation
5. **Response Formatting** - HTML tables for tasks, emojis for clarity
6. **Skills Loading Guide (v0.3.0)** - Progressive disclosure for document processing

**Key Features:**
- ✅ Skills MCP integration (docx/xlsx/pptx creation)
- ✅ Progressive skill loading
- ✅ Privacy-focused design

---

### Briefing Assistant (日报助手)

**File:** `bots/briefing_assistant.json` (line 16)

**Prompt Sections:**
1. **Role Definition** - "你是一个专业的日报生成助手"
2. **Core Capabilities** - Daily briefing generation, historical search
3. **Briefing Structure** - Standardized format (summary, highlights, files, decisions)
4. **Knowledge Base Storage** - Where briefings are saved
5. **Response Formatting** - Markdown for briefings, HTML for chat

**Key Features:**
- ✅ AI-powered intelligent summaries
- ✅ Automated cron job support
- ✅ Historical briefing search

---

## 🛠 Template Files (Secondary Storage)

### Skills Guidance Template

**Location:** `src/templates/skills_guidance.txt`

**Purpose:** Reusable prompt section for progressive skill loading

**Content:**
- List of available tools (list_skills, load_skill, load_skill_file)
- Progressive loading principles
- Workflow examples
- Decision checklist

**Usage:** Inserted into bot system_prompt during configuration load

**Bots Using This Template:**
- ✅ Personal Assistant (personal_assistant.json)
- ✅ Financial Analyst (financial_analyst.json) - Modified version in Tool Selection Guide

---

## 🔄 How Prompts are Loaded

### Loading Process (Runtime)

```
1. FastAPI starts (src/app_fastapi.py)
   ↓
2. BotManager initializes (src/bot_manager.py)
   ↓
3. For each bot webhook endpoint:
   a. Load bot config from bots/{bot_id}.json
   b. Parse system_prompt field (escaped newlines → actual newlines)
   c. Store in BotConfig object
   ↓
4. When webhook receives request:
   a. CampfireAgent.__init__() receives BotConfig
   b. Passes system_prompt to ClaudeAgentOptions
   c. Agent SDK sends to Claude API
```

**Code Reference:**

**`src/bot_manager.py` (lines 20-60):**
```python
def load_bot_config(self, bot_id: str) -> BotConfig:
    """Load bot configuration from JSON file"""
    config_path = BOTS_DIR / f"{bot_id}.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # system_prompt is read directly from JSON
    return BotConfig(
        bot_id=config['bot_id'],
        system_prompt=config['system_prompt'],  # ← Loaded here
        ...
    )
```

**`src/campfire_agent.py` (lines 90-100):**
```python
options = ClaudeAgentOptions(
    model=self.bot_config.model,
    system_prompt=self.bot_config.system_prompt,  # ← Used here
    mcp_servers=mcp_servers,
    ...
)
```

---

## ✏️ How to Iterate on Prompts

### Method 1: Direct JSON Editing (Recommended)

**Step 1:** Edit the bot JSON file
```bash
cd /Users/heng/Development/campfire/ai-bot
vim bots/financial_analyst.json
```

**Step 2:** Update the `system_prompt` field (line 16)
- Use `\n` for newlines
- Use `\"` for quotes inside strings
- Keep JSON valid (use a JSON validator)

**Step 3:** Test locally
```bash
# Kill any running instances
pkill -f "uv run python src/app_fastapi.py"

# Start fresh instance
TESTING=true CAMPFIRE_URL=https://chat.smartice.ai uv run python src/app_fastapi.py

# Test webhook
curl -X POST http://localhost:8000/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":1,"name":"Test"},"room":{"id":1,"name":"Test"},"content":"介绍一下你的功能"}'
```

**Step 4:** Check logs for prompt loading
```bash
# Look for these log lines:
[INFO] Loading bot config: financial_analyst
[INFO] Loaded bot: 财务分析师 (Financial Analyst)
```

---

### Method 2: Template-Based Editing (For Shared Sections)

**When to Use:**
- Editing skills guidance shared across multiple bots
- Updating common formatting rules
- Standardizing tool usage patterns

**Step 1:** Edit the template
```bash
vim src/templates/skills_guidance.txt
```

**Step 2:** Manually copy updated content to bot JSON files
- Or create a script to inject template into bots

**Note:** Currently no automatic template injection - must manually copy content

---

### Method 3: Python Script for Bulk Updates

**Use Case:** Update all bots with same change

**Example Script:**
```python
import json
from pathlib import Path

BOTS_DIR = Path("bots")

def update_all_bots(section_to_add: str):
    """Add a new section to all bot prompts"""
    for bot_file in BOTS_DIR.glob("*.json"):
        with open(bot_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Append new section
        config['system_prompt'] += f"\n\n{section_to_add}"

        with open(bot_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"Updated {bot_file.name}")

# Usage:
new_section = "## New Feature\nDescription here..."
update_all_bots(new_section)
```

---

## 📊 Prompt Version Tracking

### Current Versions (v0.3.0 - Skills Integration)

| Bot | Version | Last Updated | Key Changes |
|-----|---------|--------------|-------------|
| **Financial Analyst** | v0.3.0 | 2025-10-19 | Added dual MCP tool selection guide |
| **Technical Assistant** | v0.2.4 | 2025-10-16 | Knowledge base integration |
| **Personal Assistant** | v0.3.0 | 2025-10-19 | Added skills progressive loading |
| **Briefing Assistant** | v0.2.4.2 | 2025-10-16 | AI-powered briefing generation |

### Changelog for v0.3.0 (Skills Integration)

**Financial Analyst:**
- ✅ Added `skills_progressive_disclosure: true` capability
- ✅ Added "工具选择指南（双MCP系统）" section (122 lines)
- ✅ Documented Financial MCP vs. Skills MCP usage
- ✅ Added multi-step workflow examples
- ✅ Added tool conflict prevention rules
- ✅ Added progressive loading principles

**Personal Assistant:**
- ✅ Added "专业技能加载机制" section from template
- ✅ Progressive skill loading workflows
- ✅ Decision checklist for skill loading

---

## 🎯 Best Practices for Prompt Iteration

### 1. Always Test Locally First

```bash
# Start local server
TESTING=true CAMPFIRE_URL=https://chat.smartice.ai uv run python src/app_fastapi.py

# Test each bot
curl -X POST http://localhost:8000/webhook/financial_analyst -H "Content-Type: application/json" -d '...'
curl -X POST http://localhost:8000/webhook/personal_assistant -H "Content-Type: application/json" -d '...'
```

### 2. Use HTML Formatting Consistently

**Why:** Campfire renders HTML, not Markdown

**Example:**
```
❌ Bad: Use **bold** and ## Headings (Markdown)
✅ Good: Use <strong>bold</strong> and <h2>Headings</h2> (HTML)
```

### 3. Keep Prompts Organized by Sections

**Recommended Structure:**
1. Role definition (1-2 sentences)
2. Core capabilities (numbered list)
3. Working principles (bullet points)
4. Tool usage guides (specific sections for each tool category)
5. Response formatting requirements
6. Examples and workflows

### 4. Version Control Your Prompts

```bash
# Before making changes
git add bots/*.json
git commit -m "v0.2.4 prompts (baseline before v0.3.0 changes)"

# After making changes
git add bots/*.json
git commit -m "v0.3.0: Add dual MCP tool selection guide"
```

### 5. Document Prompt Changes

**In CLAUDE.md:** Add to version history table
**In Git Commit:** Explain what changed and why

---

## 🚀 Deployment Process

### After Prompt Updates

**Step 1:** Test locally (see above)

**Step 2:** Build Docker image
```bash
cd /Users/heng/Development/campfire/ai-bot
docker buildx build --platform linux/amd64 \
  -t hengwoo/campfire-ai-bot:0.3.0 \
  -t hengwoo/campfire-ai-bot:latest .
```

**Step 3:** Push to Docker Hub
```bash
docker push hengwoo/campfire-ai-bot:0.3.0
docker push hengwoo/campfire-ai-bot:latest
```

**Step 4:** Deploy on production server
```bash
# SSH to server or use DigitalOcean console
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:latest
docker-compose up -d
docker logs -f campfire-ai-bot
```

**Step 5:** Verify in production
```bash
# Check bot loads correctly
docker logs campfire-ai-bot | grep "Loading bot config"
docker logs campfire-ai-bot | grep "Loaded Skills MCP"

# Test in Campfire
# Send test message to each bot
```

---

## 🔍 Troubleshooting Prompt Issues

### Issue 1: Bot doesn't follow new prompt

**Symptom:** Bot behavior doesn't reflect recent prompt changes

**Check:**
1. ✅ JSON file saved correctly?
2. ✅ Server restarted after changes?
3. ✅ Docker image rebuilt with new code?
4. ✅ Production pulled latest image?

**Solution:**
```bash
# Verify JSON is valid
cat bots/financial_analyst.json | jq .

# Check bot config loading in logs
docker logs campfire-ai-bot | grep "Loading bot config: financial_analyst"
```

---

### Issue 2: JSON Parse Error

**Symptom:** Bot fails to load with JSON parse error

**Common Causes:**
- Unescaped quotes in system_prompt
- Missing comma between fields
- Invalid escape sequences

**Solution:**
```bash
# Validate JSON
cat bots/financial_analyst.json | jq .

# If invalid, fix errors and retry
```

---

### Issue 3: Prompt Too Long

**Symptom:** Bot responses truncated or context limit errors

**Check:**
- System prompt length (aim for <5000 tokens)
- Combined with conversation history, stays under Claude's limit

**Solution:**
- Move detailed examples to separate knowledge base documents
- Use progressive disclosure (load details only when needed)
- Simplify formatting instructions

---

## 📚 Related Files

- `src/bot_manager.py` - Bot configuration loading logic
- `src/campfire_agent.py` - Agent initialization with system prompt
- `src/templates/skills_guidance.txt` - Reusable skill loading template
- `CLAUDE.md` - Project overview and version history
- `SKILLS_INTEGRATION_PLAN.md` - Skills MCP implementation plan

---

**Next Steps:**
- Iterate on prompts based on production usage
- Add more workflow examples as use cases emerge
- Consider splitting very long prompts into modular sections
- Track prompt effectiveness metrics (response quality, tool usage accuracy)
