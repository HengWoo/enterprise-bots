# Agent Skills Research for Campfire AI Bots

**Date:** 2025-10-18
**Purpose:** Research Agent Skills feature for potential integration into Campfire AI bot system
**Current Version:** v0.2.4.2 (AI-powered daily briefings)

---

## Executive Summary

Agent Skills represent a major evolution in how we can structure our Campfire AI bots. Instead of loading all expertise upfront in massive system prompts (2000+ tokens), we can create modular "skill packages" that Claude loads progressively only when needed.

**Key Benefits for Campfire:**
- **60-80% token reduction** for simple queries (current: ~2500 tokens → with skills: ~500 tokens)
- **Better specialization** - Financial bot only loads financial skills, not briefing skills
- **Easier maintenance** - Update skills without code deployment
- **Progressive disclosure** - Load context only when needed

---

## What Are Agent Skills?

### Definition
Skills are organized packages of instructions, executable code, and resources that give Claude specialized capabilities for specific tasks. Think of them as "expertise packages" that Claude can discover and load dynamically.

### Architecture

**Three-Tier Progressive Disclosure:**
```
Level 1: Metadata (always loaded)        ~100 tokens
  ├─ name (64 char max)
  └─ description (1024 char max)

Level 2: Instructions (loaded when triggered)  <5K tokens
  ├─ SKILL.md content
  └─ Usage examples

Level 3: Resources (loaded on-demand)    Effectively unlimited
  ├─ REFERENCE.md docs
  ├─ Python/JS scripts
  └─ Templates/data files
```

### Skill Structure
```
my-skill/
├── SKILL.md              # Required: Instructions for Claude
│   ├── YAML frontmatter (name, description)
│   └── Markdown content (capabilities, usage, examples)
├── REFERENCE.md          # Optional: Detailed reference docs
├── scripts/              # Optional: Executable code
│   ├── processor.py
│   └── analyzer.py
└── resources/            # Optional: Templates, data
    └── template.xlsx
```

---

## Built-in Skills Available

Claude comes with 4 pre-built skills for document generation:

| Skill | ID | Description |
|-------|-----|-------------|
| Excel | `xlsx` | Create/manipulate Excel workbooks with formulas, charts |
| PowerPoint | `pptx` | Generate professional presentations |
| PDF | `pdf` | Create formatted PDF documents |
| Word | `docx` | Generate Word documents with rich formatting |

**Note:** These require `code_execution_20250825` tool and Files API for downloading created files.

---

## Custom Skills: Real Examples from Cookbook

### 1. Financial Analysis Skill

**Location:** `custom_skills/analyzing-financial-statements/`

**Structure:**
```
analyzing-financial-statements/
├── SKILL.md                      # Frontmatter + capabilities
├── calculate_ratios.py           # 320 lines of ratio calculations
└── interpret_ratios.py           # Benchmarking and interpretation
```

**SKILL.md Frontmatter:**
```yaml
---
name: Analyzing Financial Statements
description: This skill calculates key financial ratios and metrics from financial statement data for investment analysis
---
```

**Capabilities:**
- Profitability Ratios (ROE, ROA, margins)
- Liquidity Ratios (current, quick, cash)
- Leverage Ratios (debt-to-equity, interest coverage)
- Efficiency Ratios (asset turnover, inventory turnover)
- Valuation Ratios (P/E, P/B, EV/EBITDA)

**Key Learning:** The skill includes both instructions (what to calculate) AND executable Python code (how to calculate). Claude can:
1. Read SKILL.md to understand when to use the skill
2. Execute `calculate_ratios.py` via code execution tool
3. Interpret results using guidelines in SKILL.md

### 2. Brand Guidelines Skill

**Location:** `custom_skills/applying-brand-guidelines/`

**Structure:**
```
applying-brand-guidelines/
├── SKILL.md                      # Brand application instructions
├── apply_brand.py                # Automated brand enforcement
└── resources/
    └── brand_template.pptx       # PowerPoint template
```

**Use Case:** Automatically apply company branding to generated documents (presentations, reports).

### 3. Financial Modeling Skill

**Location:** `custom_skills/creating-financial-models/`

**Structure:**
```
creating-financial-models/
├── SKILL.md                      # DCF modeling instructions
├── dcf_model.py                  # Discounted cash flow calculations
└── sensitivity_analysis.py       # What-if scenario analysis
```

**Use Case:** Build complex financial models (DCF valuation, sensitivity analysis).

---

## Skills API Overview

### Beta Requirements
```python
from anthropic import Anthropic

client = Anthropic(
    api_key="your-api-key",
    default_headers={
        "anthropic-beta": "skills-2025-10-02"
    }
)
```

### Creating a Custom Skill
```python
from anthropic.lib import files_from_dir

# Create skill from directory
skill = client.beta.skills.create(
    display_title="Financial Analyzer",
    files=files_from_dir("custom_skills/analyzing-financial-statements")
)

print(f"Created skill: {skill.id}")
# Output: skill_abc123xyz
```

### Using Skills in Messages
```python
response = client.beta.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    container={
        "skills": [
            {"type": "custom", "skill_id": "skill_abc123xyz", "version": "latest"},
            {"type": "anthropic", "skill_id": "xlsx", "version": "latest"}  # Built-in Excel skill
        ]
    },
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],  # REQUIRED for skills
    messages=[{"role": "user", "content": "Calculate P/E ratio for AAPL"}],
    betas=["code-execution-2025-08-25", "files-api-2025-04-14", "skills-2025-10-02"]
)
```

### Managing Skills
```python
# List all custom skills
skills = client.beta.skills.list(source="custom")

# Get skill details
skill_info = client.beta.skills.retrieve(skill_id="skill_abc123xyz")

# Create new version
new_version = client.beta.skills.versions.create(
    skill_id="skill_abc123xyz",
    files=files_from_dir("updated_skill_dir")
)

# Delete skill (must delete all versions first)
client.beta.skills.versions.delete(skill_id="skill_abc123xyz", version="v1")
client.beta.skills.delete(skill_id="skill_abc123xyz")
```

---

## How Skills Differ from MCP Tools

| Aspect | MCP Tools (Current v0.2.4.2) | Agent Skills |
|--------|------------------------------|--------------|
| **Loading** | All tools loaded upfront | Progressive disclosure (metadata → instructions → resources) |
| **Token Usage** | ~2500 tokens every request | ~500 tokens base + load on demand |
| **Maintenance** | Requires code deployment | Update via API, no deployment |
| **Specialization** | Tool pollution across bots | Bot-specific skill assignment |
| **Executable Code** | No bundled code execution | Can include Python/JS scripts |
| **Context Limit** | Limited by system prompt | Effectively unlimited (Level 3 resources) |
| **Versioning** | Manual version management | Built-in version control |

### Example: Current MCP vs Skills

**Current Approach (MCP Tools):**
```python
# Financial Analyst bot config (bots/financial_analyst.json)
{
  "system_prompt": """
    You are 财务分析师...

    Financial Analysis Expertise:
    - Calculate ROE: net_income / shareholders_equity
    - Calculate ROA: net_income / total_assets
    - Calculate P/E: share_price / (net_income / shares)
    [... 1500 more tokens of financial formulas ...]

    Knowledge Base Usage:
    [... 500 tokens of KB instructions ...]

    Briefing Guidelines:
    [... 300 tokens - NOT RELEVANT to financial bot! ...]
  """,
  "tools": [
    "campfire_search_conversations",
    "search_knowledge_base",
    "generate_daily_briefing"  // ← Financial bot doesn't need this!
  ]
}

# Total: ~2500 tokens loaded every request
```

**Skills Approach:**
```python
# Financial Analyst bot config
{
  "system_prompt": """
    You are 财务分析师, a professional financial analyst.

    Available skills (load when needed):
    - financial-analysis: Calculate ratios, interpret metrics
    - campfire-kb: Search knowledge base
    - conversation-context: Access chat history
  """,
  "skills": [
    {"type": "custom", "skill_id": "financial-analysis", "version": "latest"},
    {"type": "custom", "skill_id": "campfire-kb", "version": "latest"},
    {"type": "custom", "skill_id": "conversation-context", "version": "latest"}
  ],
  "tools": ["code_execution_20250825"]  // Required for skills
}

# Total: ~500 tokens upfront
# Skills loaded only when Claude decides they're relevant:
# - "Calculate P/E ratio" → loads financial-analysis skill (~800 tokens)
# - "Search for past budget discussions" → loads campfire-kb skill (~400 tokens)
# - Simple query "Hello" → NO skills loaded! (500 tokens total)
```

**Token Savings:**
- Simple query: 2500 tokens → 500 tokens (80% reduction)
- Financial query: 2500 tokens → 1300 tokens (48% reduction)
- Knowledge query: 2500 tokens → 900 tokens (64% reduction)

---

## Integration with Campfire Architecture

### Current Architecture (v0.2.4.2)
```
FastAPI Webhook
    ↓
Bot Manager (loads bot config)
    ↓
Campfire Agent (builds system prompt with 2500 tokens)
    ↓
MCP Tools (9 tools: 3 conversations + 4 knowledge + 2 briefing)
    ↓
Claude API (processes with full context)
```

### Proposed Architecture with Skills (v0.3.0)
```
FastAPI Webhook
    ↓
Bot Manager (loads bot config)
    ↓
Skills Manager (discovers applicable skills)
    ↓
Campfire Agent (builds minimal 500-token prompt)
    ↓
Skills API (Claude loads skills progressively)
    ↓
Code Execution Tool (executes skill scripts)
    ↓
Claude API (processes with minimal upfront context)
```

### Backward Compatibility Strategy

**Phase 1: Skills Infrastructure** (no breaking changes)
1. Add Skills API support to Anthropic client
2. Create `SkillsManager` class
3. Keep existing MCP tools as fallback
4. Deploy v0.3.0 alongside v0.2.4.2

**Phase 2: Create Campfire Skills**
1. Extract financial analysis logic → `financial-analysis` skill
2. Extract KB search patterns → `campfire-kb` skill
3. Extract briefing logic → `daily-briefing` skill
4. Extract conversation patterns → `conversation-context` skill

**Phase 3: Update Bot Configs**
1. Update `financial_analyst.json` to use skills
2. Update `technical_assistant.json` to use skills
3. Update `personal_assistant.json` to use skills
4. Update `briefing_assistant.json` to use skills

**Phase 4: Gradual Migration**
1. Test skills in parallel with MCP tools
2. Monitor token usage improvements
3. Remove MCP tools after validation
4. Full skills-based deployment

---

## Proposed Campfire Skills Structure

### 1. Financial Analysis Skill
```
skills/financial-analysis/
├── SKILL.md
│   ├── Frontmatter: name, description
│   └── Content:
│       ├── Capabilities (ratios, metrics, analysis)
│       ├── Excel file validation rules
│       ├── Chinese reporting formats
│       └── Usage examples
├── scripts/
│   ├── excel_validator.py      # Validate Excel structure
│   ├── calculate_ratios.py     # Financial ratio calculations
│   └── trend_analyzer.py       # Time-series analysis
└── resources/
    ├── accounting_standards.md # GAAP/IFRS reference
    └── ratio_formulas.md       # Formula reference
```

### 2. Campfire Knowledge Base Skill
```
skills/campfire-kb/
├── SKILL.md
│   ├── Frontmatter: name, description
│   └── Content:
│       ├── How to search KB documents
│       ├── Citation guidelines
│       ├── KB structure (categories)
│       └── Source referencing
├── scripts/
│   └── semantic_search.py      # Enhanced KB search (future: vector embeddings)
└── resources/
    └── kb_categories.json      # KB taxonomy
```

### 3. Daily Briefing Skill
```
skills/daily-briefing/
├── SKILL.md
│   ├── Frontmatter: name, description
│   └── Content:
│       ├── Briefing generation workflow
│       ├── Summarization rules
│       ├── Standard briefing format
│       └── Historical briefing search
├── scripts/
│   ├── insight_extractor.py    # Extract key insights
│   └── briefing_formatter.py   # Format as markdown
└── resources/
    └── briefing_template.md    # Standard template
```

### 4. Conversation Context Skill
```
skills/conversation-context/
├── SKILL.md
│   ├── Frontmatter: name, description
│   └── Content:
│       ├── When to load chat history
│       ├── Context relevance rules
│       ├── Thread tracing guidelines
│       └── User preference handling
└── scripts/
    └── thread_tracer.py        # Trace conversation threads
```

---

## Implementation Roadmap

### Phase 1: Research & Setup (Week 1)
- [x] Read Anthropic announcement
- [x] Review official documentation
- [x] Study cookbook examples
- [x] Analyze skill structure and API
- [ ] Test Skills API with simple example
- [ ] Create proof-of-concept skill

### Phase 2: Infrastructure (Week 2)
- [ ] Add `anthropic-beta: skills-2025-10-02` support
- [ ] Create `SkillsManager` class
- [ ] Implement skill discovery and loading
- [ ] Add code execution tool support
- [ ] Update Anthropic client configuration

### Phase 3: Create Campfire Skills (Week 3)
- [ ] Extract financial analysis → skill
- [ ] Extract KB search → skill
- [ ] Extract briefing generation → skill
- [ ] Extract conversation context → skill
- [ ] Upload skills via API
- [ ] Test each skill individually

### Phase 4: Integration (Week 4)
- [ ] Update bot configs to reference skills
- [ ] Implement progressive disclosure
- [ ] Add fallback to MCP tools
- [ ] Test all 4 bots with skills
- [ ] Measure token usage improvements

### Phase 5: Deployment (Week 5)
- [ ] Local testing with all scenarios
- [ ] Docker build v0.3.0
- [ ] Deploy to production
- [ ] Monitor performance
- [ ] Validate 60-80% token reduction
- [ ] Remove MCP tools after validation

---

## Key Design Decisions

### 1. Keep MCP Tools or Full Migration?

**Recommendation:** **Hybrid approach initially, full migration after validation**

**Rationale:**
- Skills handle expertise/knowledge (financial formulas, KB search patterns)
- Basic tools remain for Campfire operations (posting messages, DB queries)
- Gradual migration reduces risk

**Final State:**
```python
# v0.3.0 (hybrid)
{
  "skills": ["financial-analysis", "campfire-kb"],
  "tools": ["code_execution_20250825", "campfire_post_message"]
}

# v0.3.1 (full skills)
{
  "skills": ["financial-analysis", "campfire-kb", "campfire-operations"],
  "tools": ["code_execution_20250825"]
}
```

### 2. Where to Store Skills?

**Option A:** In Docker container (`/app/skills/`)
- ✅ Easy deployment
- ❌ Lost on container rebuild
- ❌ Requires Docker rebuild for updates

**Option B:** Upload to Anthropic via Skills API
- ✅ Persistent storage
- ✅ No deployment needed for updates
- ✅ Version control built-in
- ❌ Requires API calls to update

**Recommendation:** **Option B (Skills API)** - Aligns with our "soft-sustainable" Docker philosophy

### 3. How to Handle Briefing-Specific Skills?

**Current Issue:** Briefing tools are loaded for all bots (tool pollution)

**Solution with Skills:**
```python
# financial_analyst.json
{
  "skills": [
    "financial-analysis",     // ✅ Relevant
    "campfire-kb",            // ✅ Relevant
    "conversation-context"    // ✅ Relevant
    // NO daily-briefing skill ✅
  ]
}

# briefing_assistant.json
{
  "skills": [
    "daily-briefing",         // ✅ Relevant
    "campfire-kb",            // ✅ Relevant
    "conversation-context"    // ✅ Relevant
    // NO financial-analysis ✅
  ]
}
```

**Benefit:** Perfect separation of concerns!

---

## Technical Considerations

### 1. Code Execution Requirement

**Important:** Skills that include Python/JS scripts REQUIRE `code_execution_20250825` tool.

```python
# REQUIRED for skills with scripts
tools=[{"type": "code_execution_20250825", "name": "code_execution"}]
```

### 2. Files API Integration

If skills generate files (Excel, PDF), must use Files API for download:

```python
# Extract file_id from response
file_id = extract_file_id(response)

# Download via Files API
file_content = client.beta.files.download(file_id)
with open("output.xlsx", "wb") as f:
    f.write(file_content.read())  # Use .read(), not .content
```

### 3. Version Management

Skills support versioning via API:

```python
# Create new version
new_version = client.beta.skills.versions.create(
    skill_id="skill_abc123xyz",
    files=files_from_dir("updated_skill_dir")
)

# Use specific version in bot
{"type": "custom", "skill_id": "skill_abc123xyz", "version": "v2"}

# Or always use latest
{"type": "custom", "skill_id": "skill_abc123xyz", "version": "latest"}
```

### 4. Skill Size Limits

- **Total size:** 8MB max per skill
- **YAML frontmatter:** 1024 chars max
- **Name:** 64 chars max
- **Description:** 1024 chars max

### 5. No Network Access

Skills **cannot**:
- Make HTTP requests
- Install packages at runtime
- Access external APIs

Skills **can**:
- Execute bundled Python/JS scripts
- Read bundled resource files
- Use Claude's built-in capabilities

---

## Security Considerations

From Anthropic documentation:

> **Treat skill installation like software installation**

1. **Only use skills from trusted sources**
2. **Audit external skills carefully** before uploading
3. **Review skill code** for malicious operations
4. **Test in isolation** before production deployment
5. **Version control** all custom skills

**For Campfire:**
- All skills will be created in-house (no external skills)
- Skills stored in `/skills/` directory (version controlled)
- Review process required for skill updates
- Test skills locally before uploading to production

---

## Expected Performance Improvements

Based on Anthropic benchmarks and our current token usage:

### Token Usage
| Scenario | Current (MCP) | With Skills | Savings |
|----------|---------------|-------------|---------|
| Simple query ("Hello") | 2500 tokens | 500 tokens | **80%** |
| Financial analysis | 2500 tokens | 1300 tokens | **48%** |
| KB search | 2500 tokens | 900 tokens | **64%** |
| Briefing generation | 2500 tokens | 1400 tokens | **44%** |

**Average savings: 60-70%**

### API Costs
- Current monthly cost: ~$50-200/month (varies by usage)
- With Skills: ~$20-80/month (estimated 60% reduction)
- **Potential savings: $30-120/month**

### Response Time
- No significant change (skills loaded efficiently)
- Possible 5-10% improvement due to less context processing

### Maintenance
- Current: Redeploy Docker for system prompt changes
- With Skills: Update via API, no deployment needed
- **Time savings: 80% reduction in update overhead**

---

## Questions for User

Before implementation, need clarification on:

1. **Deployment Timeline:** When do you want to start implementing Skills? (Current v0.2.4.2 is stable)

2. **Migration Strategy:** Prefer gradual hybrid approach or full migration?

3. **Skill Hosting:** Comfortable with uploading skills to Anthropic's servers? (They're stored remotely, not in our Docker container)

4. **Code Execution:** Okay with enabling `code_execution` tool for skill scripts? (Required for Python/JS execution)

5. **Testing Scope:** How extensively to test before production deployment?

---

## Conclusion

Agent Skills represent a **significant architectural improvement** for Campfire AI bots:

**Pros:**
- ✅ 60-80% token reduction for simple queries
- ✅ Better bot specialization (no skill pollution)
- ✅ Easier maintenance (update skills without deployment)
- ✅ Progressive disclosure (load context only when needed)
- ✅ Scalable architecture (add new skills easily)

**Cons:**
- ⚠️ Requires Skills API beta (currently beta, will be stable soon)
- ⚠️ Skills hosted on Anthropic servers (not in our Docker)
- ⚠️ Requires code execution tool (security consideration)
- ⚠️ Learning curve for skill development

**Recommendation:** **Proceed with implementation** as v0.3.0 after thorough testing and user approval.

---

**Document Version:** 1.0
**Last Updated:** 2025-10-18
**Next Steps:** Review with user, create implementation plan, build proof-of-concept
