# Knowledge Base & Long-Form Documents - Quick Reference

**Document Location:** `/home/user/enterprise-bots/CODEBASE_ANALYSIS.md`

---

## Current System Overview

### Knowledge Base Structure
```
knowledge-base/
├── claude-code/              # 4.7K lines (Claude Code Tutor)
│   ├── llm.txt              # Main LLM-optimized reference
│   ├── getting-started/     # Quickstart guides
│   ├── workflows/           # Common task workflows
│   └── configuration/       # Setup guides
│
└── operations/              # 633 lines (Operations Assistant)
    └── llm.txt              # Operations analytics guide
```

### File-Based Prompt System

```
prompts/
├── bots/                    # Bot personalities (Layer 1 - Always loaded)
│   ├── personal_assistant.md    (~200 lines, ~4K tokens)
│   ├── financial_analyst.md
│   └── ... 6 more bots
│
├── configs/                 # Bot metadata (Layer 3 - Configuration only)
│   ├── personal_assistant.yaml
│   └── ... 7 more bots
│
└── shared/                  # Reusable sections
    ├── security_rules.md
    └── html_formatting.md
```

### Skills Architecture

```
.claude/skills/             # Layer 2 - On-demand loading
├── knowledge-base/SKILL.md      (~400 lines)
├── personal-productivity/       (~600 lines)
├── financial-analysis/          (~400 lines)
├── code-generation/             (~500 lines)
└── presentation-generation/     (~400 lines)
```

---

## Key Patterns Identified

### Pattern 1: LLM.txt Consolidation
**Best for:** Comprehensive references that fit in context
- Single consolidated file (~4-5K lines)
- Clear navigation structure
- Optimal for AI consumption
- **Examples:** `knowledge-base/claude-code/llm.txt`, `knowledge-base/operations/llm.txt`

### Pattern 2: Three-Layer Architecture
**Layer 1:** Bot Personality (always loaded, ~4K tokens)
- Bot identity, high-level capabilities
- Skills loading instructions
- Response formatting rules

**Layer 2:** Skills (on-demand, ~5-8K tokens each)
- Detailed workflows, examples
- Load only when needed
- Token savings: 63-98%

**Layer 3:** Configuration (metadata only)
- Tool mappings, model settings
- Minimal overhead

### Pattern 3: Knowledge Base Integration
**Separate Concerns:**
- **System Prompt:** Bot personality, when to use knowledge
- **Knowledge Base:** External searchable reference
- **Bot Tools:** 4 core knowledge base tools
  1. `search_knowledge_base()` - Keyword search
  2. `read_knowledge_document()` - Full document read
  3. `list_knowledge_documents()` - Browse available docs
  4. `store_knowledge_document()` - Create new docs

### Pattern 4: Template Variables
**Dynamic Context Injection:**
```markdown
# Bot Personality
今天的日期：$current_date
当前用户：$user_name
当前房间：$room_name
```
- Substituted at runtime
- Enables personalized responses
- No hardcoded values

---

## Key Python Modules

| Module | Purpose | Key Functions |
|--------|---------|---|
| `src/prompt_loader.py` | Load & substitute .md prompts | `load_bot_prompt()`, `load_shared_section()` |
| `src/skills_manager.py` | Discover & load skills | `load_skill()`, `discover_skills()`, `get_skill_metadata()` |
| `src/bot_manager.py` | Load bot configurations | `BotManager()`, `BotConfig` |
| `src/campfire_agent.py` | Agent SDK wrapper | `_get_system_prompt()`, `_get_allowed_tools_for_bot()` |
| `src/tools/campfire_tools.py` | Knowledge base tools | `search_knowledge_base()`, `read_knowledge_document()`, etc. |

---

## Current Bot Status

### File-Based Prompts Implemented
- ✅ **personal_assistant** - Fully migrated to YAML + .md
- ✅ **cc_tutor** (Claude Code Tutor) - Fully migrated to YAML + .md

### Still Using Legacy JSON
- ⏳ technical_assistant
- ⏳ financial_analyst
- ⏳ operations_assistant
- ⏳ briefing_assistant
- ⏳ menu_engineer

---

## Request/Response Flow

```
1. User Message in Campfire
   ↓
2. Webhook to FastAPI (app_fastapi.py)
   ↓
3. BotManager loads bot config from YAML/JSON
   ↓
4. CampfireAgent._get_system_prompt()
   - PromptLoader loads prompts/bots/{bot_id}.md
   - Template variables substituted
   - Result: ~4K token system prompt
   ↓
5. Claude Agent SDK Execution
   ↓
6. If complex task needed:
   - Agent calls load_skill("skill_id")
   - SkillsManager loads .claude/skills/{skill_id}/SKILL.md
   - Skill content (~5-8K tokens) appended to context
   ↓
7. If knowledge base query:
   - Agent calls search_knowledge_base(query)
   - Returns matching documents
   - Agent reads full content if needed
   ↓
8. Response generated and posted back to Campfire
```

---

## Token Efficiency Analysis

### Simple Query (70% of requests)
- Load: Bot personality only (~4K tokens)
- Skip: Skills, knowledge base
- Total: ~4K tokens
- **Savings vs monolithic:** 63-98%

### Complex Workflow (30% of requests)
- Load: Bot personality + 1-2 Skills
- Total: ~15-20K tokens
- **Acceptable overhead:** Skills needed for task

### Knowledge Base Query
- Load: Bot personality + knowledge-base skill
- Fetch: Specific documents on-demand
- Total: ~8-10K tokens + document content

---

## Best Practices for Long-Form Documents

### Structure
1. **Use llm.txt format** for comprehensive references
2. **Organize hierarchically** with clear headings
3. **Include quick navigation** at the start
4. **Provide concrete examples**
5. **Add metadata** (timestamps, versions)

### Token Management
1. **Separate concerns:** Personality vs. reference knowledge
2. **Use three-layer architecture:** Always + on-demand + metadata
3. **Load selectively:** Only what's needed
4. **Cache results:** SkillsManager caches loaded skills

### Accessibility
1. **Table of contents** for large documents
2. **Section links** for easy navigation
3. **Consistent formatting:** Headings, lists, code blocks
4. **Quick start sections** for each topic

### Maintainability
1. **Separate files by domain:** One KB per knowledge area
2. **Configuration in YAML:** Keep tool lists separate from prompts
3. **Version your knowledge:** Track last updated dates
4. **Test templates:** Ensure variable substitution works

---

## Configuration Example

### Bot Config (YAML)
```yaml
# prompts/configs/my_bot.yaml
bot_id: my_bot
name: My Bot

# Point to file-based prompt
system_prompt_file: my_bot.md

tools:
  builtin:
    - WebSearch
    - Read
    - Skill        # Enable native Agent SDK skills
  
  campfire:
    - search_conversations
    - search_knowledge_base  # Enable knowledge base access
    - read_knowledge_document
    - my_custom_tool

capabilities:
  knowledge_base_access: true
```

### Bot Personality (Markdown)
```markdown
# prompts/bots/my_bot.md
你是一个专业的...

**当前环境：**
- 今天：$current_date
- 用户：$user_name

## 能力

### 知识库访问
需要查询知识库时，使用 `load_skill("knowledge-base")` 加载工作流...

## 使用详细工作流
需要复杂任务时：
- 使用 `load_skill("skill_id")` 获取详细步骤
```

### Skill Definition
```markdown
# .claude/skills/my_skill/SKILL.md
---
name: my-skill
description: "Does something useful..."
version: 1.0.0
---

# My Skill

## Quick Start
...

## Core Capabilities
...

## Usage Workflows
...
```

---

## Next Steps / Future Improvements

### High Priority
1. **Vector Search Enhancement** - Add embeddings for semantic search
2. **Knowledge Update System** - Version control for documents
3. **Dynamic Knowledge Loading** - Auto-load based on query

### Medium Priority
1. **Multi-Language Support** - Localize prompts and knowledge
2. **Knowledge Linking** - Cross-references between documents
3. **Automated KB Updates** - Smart sync with source systems

### Low Priority
1. **Knowledge Graph** - Visualize document relationships
2. **Usage Analytics** - Track which knowledge gets used
3. **AI-Powered Summarization** - Auto-generate summaries

---

## File Locations (Development)

**Root:** `/home/user/enterprise-bots/ai-bot/`

| Path | Purpose |
|------|---------|
| `src/prompt_loader.py` | Prompt loading (287 lines) |
| `src/skills_manager.py` | Skills discovery (416 lines) |
| `src/bot_manager.py` | Bot config loading |
| `prompts/bots/` | Bot personalities (.md files) |
| `prompts/configs/` | Bot metadata (.yaml files) |
| `prompts/shared/` | Reusable text fragments |
| `.claude/skills/` | Skills definitions (SKILL.md files) |
| `knowledge-base/` | Long-form documentation |
| `bots/` | Legacy JSON configs (deprecated) |

---

## References

- **Full Analysis:** `/home/user/enterprise-bots/CODEBASE_ANALYSIS.md`
- **Architecture Design:** `/home/user/enterprise-bots/DESIGN.md`
- **Project Memory:** `/home/user/enterprise-bots/CLAUDE.md`
- **Migration Guide:** `/home/user/enterprise-bots/ai-bot/prompts/MIGRATION_SUMMARY.md`

