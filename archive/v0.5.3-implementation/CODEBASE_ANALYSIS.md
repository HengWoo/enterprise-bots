# Campfire AI Bot - Codebase Structure & Long-Form Document Handling

**Last Updated:** 2025-11-05
**Analysis Focus:** Knowledge base structure, prompt system, skills, and long-form document patterns

---

## 1. Knowledge Base Document Structure

### 1.1 Directory Organization

The knowledge base is stored at `/root/ai-knowledge/company_kb/` (production) or `/home/user/enterprise-bots/ai-bot/knowledge-base/` (development).

```
knowledge-base/
├── claude-code/                           # Claude Code Tutor knowledge base (4.8K lines)
│   ├── llm.txt                           # LLM-optimized main index
│   ├── README.md                         # Guide to this knowledge base
│   ├── getting-started/
│   │   └── quickstart.md                 # Beginner quickstart guide
│   ├── workflows/
│   │   └── common-workflows.md           # Step-by-step task guides
│   ├── configuration/
│   │   ├── settings.md
│   │   ├── vscode.md
│   │   ├── terminal-setup.md
│   │   ├── model-config.md
│   │   └── memory-management.md
│   └── mcp/
│       └── mcp-integration.md
│
└── operations/                           # Operations Assistant knowledge base (633 lines)
    └── llm.txt                           # LLM-optimized guide for operations
```

### 1.2 llm.txt Format (LLM-Optimized Pattern)

**Purpose:** Optimized single-file format for LLM consumption
**Standard:** Follows [llm.txt standard](https://llmstxt.cloud/) for AI assistant-friendly documentation

**Structure:**
```
# Knowledge Base Title

> Tagline describing the knowledge base

## Quick Navigation
- Links to main sections
- Quick reference points

## Core Content Sections
- Detailed workflows
- Reference materials
- Best practices

## Usage Examples
- Code samples
- Real-world scenarios
```

**Key Characteristics:**
- **Single consolidated file:** All essential information in one .txt file
- **LLM-optimized:** Clear structure with headings and sections
- **No code blocks for rendering:** Plain text that works well with token counting
- **Comprehensive:** Complete reference material (4K-5K lines)
- **Self-contained:** Can be directly loaded into bot system prompts

### 1.3 Markdown Organization Pattern

Knowledge base typically split into:
1. **Main index file (llm.txt):** Comprehensive reference for AI consumption
2. **Nested markdown files:** Detailed guides for specific topics
3. **README.md:** Navigation guide for humans

This split allows:
- **Efficient LLM loading:** Load only needed sections into context
- **Token savings:** Main llm.txt (~4K lines) loaded always; sub-files (~2K lines each) loaded on-demand
- **Easy human navigation:** README guides users to specific documents

---

## 2. Prompt System (Three-Layer Architecture)

### 2.1 Layer 1: Bot Personality (Always Loaded)

**Files:** `prompts/bots/{bot_id}.md`

**Characteristics:**
- **Size:** ~200-300 lines (~4-5K tokens)
- **Content:**
  - Bot identity and role
  - High-level capabilities overview
  - Skills loading instructions (when to call `load_skill()`)
  - HTML/response formatting rules
  - Security guidelines
  - Template variables ($current_date, $user_name, $room_name)

**Example (personal_assistant.md):**
```markdown
你是一个专业的个人助手AI，名叫「个人助手」。

**当前环境信息：**
- 今天的日期：$current_date
- 当前用户：$user_name
- 当前房间：$room_name

## 你的专业能力

1. **个人生产力管理**
   - 任务管理 - 创建、查看、完成、删除待办事项
   - 提醒服务 - 设置时间提醒和事件提醒
   ...

## 使用Skills加载专业知识

当用户请求需要专业领域知识时，使用 `load_skill()` 工具加载详细工作流程：

**文档处理Skills：**
- Word文档 → `load_skill("document-skills-docx")`
- PowerPoint → `load_skill("document-skills-pptx")`
```

### 2.2 Layer 2: Skills (On-Demand Loading)

**Files:** `.claude/skills/{skill_id}/SKILL.md`

**Characteristics:**
- **Size:** 400-600 lines per skill (~5-8K tokens)
- **Metadata:** YAML frontmatter with name, description, version
- **Content:** Detailed workflows, examples, best practices
- **Loading:** Called via `load_skill("skill_id")` when needed
- **Token Efficiency:** 63-98% savings when not needed

**Example Structure:**
```yaml
---
name: knowledge-base
description: Searches and retrieves company knowledge base documents...
---

# Campfire Knowledge Base

## Quick Start

When users ask about company policies:
1. **Search** - Use `search_knowledge_base`
2. **List** - Use `list_knowledge_documents`
3. **Read** - Use `read_knowledge_document`

## Core Capabilities
[Detailed workflow information]

## Usage Workflows
[Step-by-step examples]
```

### 2.3 Layer 3: Configuration (Metadata Only)

**Files:** `prompts/configs/{bot_id}.yaml`

**Characteristics:**
- **Purpose:** Bot settings without duplication
- **Content:**
  - Model configuration
  - Tool mappings
  - MCP server list
  - Capabilities flags
  - Reference to file-based prompt (`system_prompt_file`)

**Example (personal_assistant.yaml):**
```yaml
bot_id: personal_assistant
name: 个人助手

system_prompt_file: personal_assistant.md  # Points to prompts/bots/personal_assistant.md

tools:
  builtin:
    - WebSearch
    - WebFetch
    - Read
    - Bash
    - Skill        # Native Agent SDK skills (v0.5.0)
  
  campfire:
    - search_conversations
    - manage_personal_tasks
    - set_reminder

capabilities:
  file_analysis: true
  pptx_support: true
  personal_productivity: true
```

### 2.4 Loading Flow

```
1. App Startup (app_fastapi.py)
   ↓
2. BotManager loads configs
   - Searches: ./bots/*.json + prompts/configs/*.yaml
   - YAML overrides JSON if both exist
   ↓
3. For each bot request:
   - CampfireAgent._get_system_prompt() called
   - Checks for system_prompt_file reference
   - PromptLoader.load_bot_prompt() loads .md file
   - Template variables substituted ($current_date, etc.)
   ↓
4. During conversation:
   - Bot invokes load_skill("skill_id")
   - SkillsManager.load_skill() finds in .claude/skills/
   - SKILL.md loaded and cached
   - Skill content appended to context
```

---

## 3. Skills Implementation

### 3.1 Skills Discovery

**SkillsManager (`src/skills_manager.py`)** handles:
- Automatic discovery from `.claude/skills/` directory
- Metadata extraction from YAML frontmatter
- Content loading with caching
- On-demand progressive disclosure

**Flow:**
```python
# 1. Discover available skills
skills = manager.discover_skills()
# Returns: [SkillMetadata(...), SkillMetadata(...), ...]

# 2. Load specific skill when needed
skill = manager.load_skill("knowledge-base")
# Returns: Skill object with metadata + full content

# 3. Get metadata without loading content
metadata = manager.get_skill_metadata("knowledge-base")
# Lightweight, for UI/listing purposes
```

### 3.2 Skill File Structure

**Directory Layout:**
```
.claude/skills/
├── knowledge-base/
│   ├── SKILL.md              # Main skill file with YAML frontmatter
│   └── (optional) resources/ # Additional supporting files
│
├── financial-analysis/
│   ├── SKILL.md
│   └── reference/
│       ├── ratios.md         # Financial ratio reference
│       └── chinese-formats.md
│
└── personal-productivity/
    ├── SKILL.md
    └── examples/
        └── task-workflows.md
```

**SKILL.md Format:**
```markdown
---
name: knowledge-base
description: "Searches and retrieves company knowledge base documents..."
version: 1.0.0
license: MIT
---

# Skill Title

## Quick Start

[How to use this skill]

## Core Capabilities

[What this skill enables]

## Usage Workflows

[Step-by-step examples]
```

### 3.3 Native Agent SDK Skills (v0.5.0)

**Pattern Change:** Migrated from Skills MCP server to native Agent SDK skills pattern

**Implementation:**
```python
# campfire_agent.py
ClaudeAgentOptions(
    setting_sources=["user", "project"]  # Auto-discover from .claude/skills/
)

builtin_tools = [..., "Skill"]  # Native Skill tool replaces mcp__skills__load_skill
```

**Benefits:**
- ✓ No external MCP server needed
- ✓ Automatic filesystem-based discovery
- ✓ On-demand loading (token efficient)
- ✓ Both plugin and custom skills use same mechanism

---

## 4. Knowledge Base Access Tools

### 4.1 Knowledge Base Tool Set

Located in `src/tools/campfire_tools.py`, provides 4 core tools:

#### Tool 1: `search_knowledge_base(query, category=None, max_results=3)`
- **Purpose:** Keyword search across knowledge base
- **Returns:** List of results with path, title, excerpt, relevance_score
- **Implementation:** 
  - Simple keyword matching (case-insensitive)
  - Relevance scoring based on match frequency
  - Category filtering (optional)

**Example:**
```python
results = campfire_tools.search_knowledge_base(
    query="expense reimbursement",
    category="policies",
    max_results=3
)
# Returns: [
#   {"path": "policies/expense-reimbursement.md", "title": "...", "excerpt": "...", "relevance_score": 2},
#   ...
# ]
```

#### Tool 2: `read_knowledge_document(path)`
- **Purpose:** Read full content of specific document
- **Returns:** Dict with path, title, content, last_updated, category, success
- **Implementation:**
  - Direct file read from knowledge_base_dir/path
  - Title extraction (first H1 heading)
  - Last updated detection (parses "Last Updated:" field)

**Example:**
```python
doc = campfire_tools.read_knowledge_document("policies/expense-reimbursement.md")
# Returns: {
#   "success": True,
#   "path": "policies/expense-reimbursement.md",
#   "title": "Expense Reimbursement Policy",
#   "content": "# Expense Reimbursement Policy\n\n...",
#   "last_updated": "2025-10-01"
# }
```

#### Tool 3: `list_knowledge_documents(category=None)`
- **Purpose:** Browse available documents
- **Returns:** List of document metadata (path, title, category, last_updated)
- **Implementation:**
  - Recursively finds all .md files
  - Extracts metadata from files
  - Sorted by category then title

#### Tool 4: `store_knowledge_document(category, title, content, author=None)`
- **Purpose:** Create new knowledge base documents
- **Returns:** Confirmation with document path
- **Implementation:**
  - Creates category subdirectory if needed
  - Generates filename from title (slugified)
  - Stores as markdown file

### 4.2 Knowledge Base Access Pattern

**Typical Bot Usage (in SKILL.md):**

```markdown
## Quick Start

When users ask about company policies:

1. **Search** - Use `search_knowledge_base` to find relevant documents
   → `search_knowledge_base(query="expense reimbursement", category="policies")`

2. **List** - Use `list_knowledge_documents` to browse available docs
   → `list_knowledge_documents(category="policies")`

3. **Read** - Use `read_knowledge_document` to get full content
   → `read_knowledge_document(path="policies/expense-reimbursement.md")`

4. **Cite** - Always reference the source document in your response
   → "According to our Expense Reimbursement Policy (policies/...):"

5. **Store** (if needed) - Use `store_knowledge_document` to create new official docs
```

---

## 5. Patterns for Handling Long-Form Documents

### 5.1 Pattern 1: LLM.txt Consolidation

**Use Case:** Comprehensive knowledge that fits in context window

**Structure:**
```
# Topic Title

> Brief description

## Quick Navigation
- Section links for easy scanning

## Essential Sections
- Section 1: Detailed content
- Section 2: More detailed content
- Reference: Complete reference material
```

**Files Using This Pattern:**
- `knowledge-base/claude-code/llm.txt` (4,787 lines)
- `knowledge-base/operations/llm.txt` (633 lines)

**Token Efficiency:**
- Single file: ~5-6K tokens
- Loaded entirely, no additional loading overhead
- Optimal for AI consumption (clear structure, no markdown complexity)

### 5.2 Pattern 2: Multi-File Organization with Navigation

**Use Case:** Large knowledge bases that exceed context (needs chunking)

**Structure:**
```
knowledge-base/
├── llm.txt              # Main index (consolidates all)
├── README.md            # Human navigation guide
├── section1/
│   └── file1.md         # ~2K line chunks
├── section2/
│   └── file2.md
└── reference/
    └── lookup.md
```

**Usage:**
1. Load `llm.txt` as primary reference
2. Load specific sub-files on-demand based on user query
3. Each sub-file ~2K lines, can be loaded individually

**Example (Claude Code):**
- `llm.txt` = complete reference
- `getting-started/quickstart.md` = loaded when user asks "how do I start?"
- `workflows/common-workflows.md` = loaded for workflow guidance
- `configuration/*.md` = loaded for setup questions

### 5.3 Pattern 3: Three-Layer Skill Architecture

**Use Case:** Progressive disclosure - expose expertise only when needed

**Layer 1: Bot Personality (always)**
- ~200 lines
- High-level "I know about X"
- Instructions to load skills

**Layer 2: Skills (on-demand)**
- ~500 lines each
- Detailed workflows when user needs it
- Multiple skills, load what's relevant

**Layer 3: Configuration (metadata)**
- Tool mappings and settings
- Minimal information

**Token Savings:**
```
Simple query (70% of requests):
- Load Layer 1 only: ~4K tokens
- Savings: 63-98% vs monolithic prompt

Complex workflow (30% of requests):
- Load Layer 1 + 1-2 Skills: ~15-20K tokens
- Small overhead acceptable
```

### 5.4 Pattern 4: Bot Personality + Knowledge Base Integration

**Pattern:** Separate concerns into distinct systems

**System Prompt (Bot Personality):**
- Bot identity, values, response style
- Instructions on WHEN to use knowledge base tools
- Template variables for context

**Knowledge Base (External System):**
- Factual reference material
- Searchable, indexable
- Separate from prompt

**Bot Can:**
- Search knowledge base when relevant
- Read specific documents
- Cite sources
- Store new knowledge

**Benefits:**
- Prompts don't bloat with reference material
- Knowledge updates don't require bot config changes
- Knowledge reusable across multiple bots

### 5.5 Pattern 5: Chunking for Vector/Semantic Search

**Current Implementation:** Simple keyword search (no embeddings)

**Potential Future Enhancement:**
```
For large documents:
1. Split llm.txt into semantic chunks (~200-300 tokens each)
2. Generate embeddings for each chunk
3. On search:
   - Convert query to embedding
   - Find top-K similar chunks
   - Return chunk references or full chunks

Supports:
- Large documents (10K+ lines)
- Semantic relevance (not just keyword matching)
- Efficient context retrieval
```

---

## 6. Bot Knowledge Access Flow

### 6.1 Full Request Flow

```
1. User Message in Campfire
   ↓
2. Webhook to FastAPI (app_fastapi.py)
   ↓
3. CampfireAgent._get_system_prompt()
   - BotManager loads bot config
   - PromptLoader loads bot personality .md file
   - Template variables substituted
   ↓
4. Claude Agent SDK Execution
   ↓
5. Bot Invokes Tools
   
   a) If user asks about policies:
      - Agent: "I should search the knowledge base"
      - Agent: invoke search_knowledge_base(query="...", category="policies")
      - Tool returns: list of documents
      - Agent reads relevant documents
      
   b) If complex task needed:
      - Agent: "I need detailed workflows"
      - Agent: invoke load_skill("personal-productivity")
      - SkillsManager loads SKILL.md (~500 lines)
      - Agent learns workflows and executes
      
   c) Multi-bot collaboration:
      - Agent: "Financial analysis needed"
      - Agent: invoke Task(bot_id="financial_analyst", ...)
      - Subagent executes with limited tool set
   ↓
6. Response Streamed Back
   ↓
7. Posted to Campfire
```

### 6.2 Tool Integration Points

**campfire_agent.py Integration:**
```python
# Get allowed tools for bot
def _get_allowed_tools_for_bot(self):
    allowed_tools = [
        "WebSearch", "WebFetch", "Read", "Grep", "Glob", "Task", "Skill",
        
        # Knowledge base tools (always available)
        "mcp__campfire__search_knowledge_base",
        "mcp__campfire__read_knowledge_document",
        "mcp__campfire__list_knowledge_documents",
        "mcp__campfire__store_knowledge_document",
        
        # Bot-specific tools
        ...
    ]
```

---

## 7. Configuration Flow

### 7.1 Bot Configuration Precedence

```
1. YAML Config (if exists)
   prompts/configs/{bot_id}.yaml
   ↓
2. JSON Config (fallback)
   bots/{bot_id}.json
   ↓
3. Environment Variables (override)
   BOT_KEY_{BOT_ID} environment variable
```

### 7.2 BotManager Loading Process

```python
# BotManager.__init__()
# 1. Search multiple directories
bots_dirs = ['./bots', 'prompts/configs']

# 2. Load all config files
for bots_dir in bots_dirs:
    json_files = bots_dir.glob('*.json')
    yaml_files = bots_dir.glob('*.yaml')

# 3. Create BotConfig objects
# YAML overrides JSON if both exist

# 4. Return bot_manager.bots dict
# {
#   "personal_assistant": BotConfig(...),
#   "financial_analyst": BotConfig(...),
#   ...
# }
```

---

## 8. Current Implementations

### 8.1 Bots Using File-Based Prompts (v0.4.1+)

| Bot | File-Based | Skills | Status |
|-----|-----------|--------|--------|
| personal_assistant | ✅ Yes | ✅ Native SDK | ✅ Production |
| cc_tutor (Claude Code Tutor) | ✅ Yes | ✅ Native SDK | ✅ Production |
| technical_assistant | ❌ JSON | ⏳ Legacy | ⏳ Pending Migration |
| financial_analyst | ❌ JSON | ⏳ Legacy | ⏳ Pending Migration |
| operations_assistant | ❌ JSON | ⏳ Legacy | ⏳ Pending Migration |
| briefing_assistant | ❌ JSON | ⏳ Legacy | ⏳ Pending Migration |
| menu_engineer | ❌ JSON | ⏳ Legacy | ⏳ Pending Migration |

### 8.2 Knowledge Bases Implemented

| Knowledge Base | Location | Size | Used By |
|---|---|---|---|
| Claude Code | `knowledge-base/claude-code/` | 4.8K lines | cc_tutor |
| Operations | `knowledge-base/operations/` | 633 lines | operations_assistant |

### 8.3 Skills Available

| Skill | Location | Lines | Purpose |
|---|---|---|---|
| knowledge-base | `.claude/skills/knowledge-base/` | ~400 | Search/retrieve company knowledge |
| personal-productivity | `.claude/skills/personal-productivity/` | ~600 | Tasks, reminders, notes workflows |
| financial-analysis | `.claude/skills/financial-analysis/` | ~400 | Financial ratio analysis workflows |
| code-generation | `.claude/skills/code-generation/` | ~500 | Code generation and validation |
| presentation-generation | `.claude/skills/presentation-generation/` | ~400 | HTML presentation creation |

---

## 9. Key Files Reference

| File | Purpose | Size |
|---|---|---|
| `src/prompt_loader.py` | Load and substitute .md prompts | 287 lines |
| `src/skills_manager.py` | Discover and load skills | 416 lines |
| `src/bot_manager.py` | Load bot configurations | 250+ lines |
| `src/campfire_agent.py` | Agent SDK wrapper + integration | 600+ lines |
| `src/tools/campfire_tools.py` | Knowledge base tools implementation | 50K lines |
| `prompts/bots/*.md` | Bot personalities | 200 lines each |
| `.claude/skills/*/SKILL.md` | Skill documentation | 400-600 lines each |
| `prompts/configs/*.yaml` | Bot metadata | 80 lines each |
| `knowledge-base/*/llm.txt` | LLM-optimized knowledge | 4-5K lines each |

---

## 10. Best Practices for Long-Form Documents

### 10.1 Structure
- **Use llm.txt format** for consolidated references (best for LLM consumption)
- **Organize hierarchically** with clear headings and sections
- **Include quick navigation** at the start
- **Provide concrete examples** for each concept

### 10.2 Token Efficiency
- **Separate concerns:** Personality vs. reference knowledge
- **Use three-layer architecture:** Always-loaded + on-demand + metadata
- **Load selectively:** Only include what's needed for current task
- **Cache results:** SkillsManager caches loaded skills

### 10.3 Accessibility
- **Add navigation aids:** Table of contents, section links
- **Use consistent formatting:** Headings, lists, examples
- **Provide summaries:** Quick start sections for each topic
- **Include metadata:** Timestamps, version numbers, source info

### 10.4 Maintainability
- **Separate files by concern:** One knowledge base per domain
- **Use configuration files:** Keep tool lists in YAML, not prompts
- **Version your knowledge:** Track last updated dates
- **Test your templates:** Ensure variable substitution works

---

## 11. Future Improvement Opportunities

### 11.1 Vector Search Enhancement
- Add embeddings for semantic search
- Support chunked retrieval for large documents
- Fallback to keyword search if embedding fails

### 11.2 Knowledge Update System
- Version control for knowledge base documents
- Change tracking and diff viewing
- Approval workflow for new documents

### 11.3 Dynamic Knowledge Loading
- Analyze user query to determine needed knowledge
- Auto-load relevant skills based on conversation context
- Lazy-load knowledge to optimize token usage

### 11.4 Multi-Language Support
- Translate prompts and skills
- Language-aware search
- Localized knowledge bases

### 11.5 Knowledge Linking
- Cross-references between documents
- Automatic "related documents" suggestions
- Knowledge graph visualization

---

## Summary

**Key Insights:**

1. **Three-Layer Architecture** separates concerns:
   - Layer 1: Bot identity (always)
   - Layer 2: Expertise (on-demand)
   - Layer 3: Configuration (metadata)

2. **File-Based Prompts** enable:
   - Cleaner, more maintainable prompts
   - Template variables for dynamic context
   - Progressive disclosure (load only what's needed)

3. **LLM.txt Format** optimized for:
   - AI consumption (clear structure)
   - Token efficiency (single comprehensive file)
   - Easy navigation

4. **Knowledge Base Tools** provide:
   - Searchable reference material
   - Separate from bot personalities
   - Reusable across multiple bots

5. **Skills Management** enables:
   - On-demand knowledge loading
   - Metadata-driven discovery
   - Flexible caching strategies

**Recommended Approach for New Knowledge:**
1. Consolidate in `llm.txt` format
2. Split into `getting-started`, `workflows`, `reference` sections
3. Create SKILL.md wrapper if complex workflows
4. Register tool mappings in YAML config
5. Add to BotManager discovery path

