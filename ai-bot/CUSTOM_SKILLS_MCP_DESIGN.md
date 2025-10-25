# Custom Skills MCP: Building Skills as Tools

**Date:** 2025-10-18
**Purpose:** Design a Custom Skills MCP to enable progressive disclosure of skill content via Agent SDK
**User Insight:** "Skills by itself are just tools. I'm thinking if we can extract the skills_content and build them as tools."

---

## Core Concept

**User's Key Observation:**
> "Skills by itself are just tools. As far as I understand, the agents can decide what tools to use with the current SDK functionality already."

**The Idea:**
Instead of injecting ALL skill content into system prompts (+100% token usage), create an MCP server that loads skill content on-demand as tools. This achieves progressive disclosure WITHIN the Agent SDK architecture.

---

## Architecture Comparison

### Current Approach (Manual Skill Content)

```python
# System prompt includes ALL skill content upfront
system_prompt = f"""
你是一个专业的个人助手AI...

--- BEGIN DOCX SKILL (2,000 tokens) ---
{docx_skill_content}
--- END DOCX SKILL ---

--- BEGIN XLSX SKILL (2,500 tokens) ---
{xlsx_skill_content}
--- END XLSX SKILL ---

--- BEGIN PPTX SKILL (2,000 tokens) ---
{pptx_skill_content}
--- END PPTX SKILL ---
"""
# Total: +6,500 tokens per request (whether needed or not)
```

**Token Usage:**
- Base prompt: 2,500 tokens
- With 3 skills: 9,000 tokens
- **Cost:** +$19.50/month (1,000 requests)

---

### Custom Skills MCP Approach (Progressive Disclosure)

```python
# System prompt references skills WITHOUT full content
system_prompt = """
你是一个专业的个人助手AI...

当需要处理特定文档类型时，使用 load_skill 工具获取专业知识：
- Word文档: load_skill(skill_name="docx")
- Excel文档: load_skill(skill_name="xlsx")
- PowerPoint文档: load_skill(skill_name="pptx")

只在实际需要时加载技能内容。
"""
# Total: 2,700 tokens (only +200 tokens)

# Skill content loaded on-demand via MCP tool
```

**Token Usage (Typical Request):**
- Base prompt: 2,500 tokens
- Skill reference: +200 tokens
- When docx skill needed: +2,000 tokens (only that skill)
- **Average:** ~4,700 tokens (only 88% increase vs. 260% for manual)

**Token Usage (No Skill Needed):**
- Base prompt: 2,500 tokens
- Skill reference: +200 tokens
- **Total:** 2,700 tokens (only 8% increase!)

**Cost Estimate:**
- 70% of requests need no skill: 2,700 tokens × 700 = 1.89M tokens
- 20% need docx skill: 4,700 tokens × 200 = 0.94M tokens
- 10% need xlsx skill: 5,200 tokens × 100 = 0.52M tokens
- **Total:** 3.35M tokens vs. 9M tokens (manual approach)
- **Savings:** 63% fewer tokens = $16.95/month savings

---

## Implementation Design

### Custom Skills MCP Server

**File:** `skills-mcp/server.py`

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import os
import json

server = Server("campfire-skills")

# Skills directory
SKILLS_DIR = "/app/.claude/skills"

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available skill-related tools"""
    return [
        types.Tool(
            name="list_skills",
            description="List all available skills and their descriptions",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        types.Tool(
            name="load_skill",
            description="Load a skill's expertise and workflows on-demand. Only call this when you need specific expertise (e.g., user asks about Word documents → load docx skill).",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "Name of skill to load (e.g., 'docx', 'xlsx', 'pptx')"
                    }
                },
                "required": ["skill_name"]
            }
        ),
        types.Tool(
            name="load_skill_file",
            description="Load additional detailed files from a skill (third level of detail). Only use after loading the main skill if you need more specific information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "Name of skill"
                    },
                    "file_name": {
                        "type": "string",
                        "description": "File to load (e.g., 'docx-js.md', 'ooxml.md')"
                    }
                },
                "required": ["skill_name", "file_name"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Execute tool calls"""

    if name == "list_skills":
        return await list_available_skills()

    elif name == "load_skill":
        skill_name = arguments["skill_name"]
        return await load_skill_content(skill_name)

    elif name == "load_skill_file":
        skill_name = arguments["skill_name"]
        file_name = arguments["file_name"]
        return await load_additional_file(skill_name, file_name)

    else:
        raise ValueError(f"Unknown tool: {name}")

async def list_available_skills() -> list[types.TextContent]:
    """List all skills in .claude/skills/"""
    skills = []

    for dir_name in os.listdir(SKILLS_DIR):
        skill_path = os.path.join(SKILLS_DIR, dir_name)
        skill_md = os.path.join(skill_path, "SKILL.md")

        if os.path.isdir(skill_path) and os.path.exists(skill_md):
            # Parse YAML frontmatter for metadata
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract name and description from frontmatter
                if content.startswith('---'):
                    frontmatter = content.split('---')[1]
                    # Simple parsing (you'd use yaml.safe_load in production)
                    name = dir_name
                    description = "Skill for document processing"

                    skills.append(f"- **{name}**: {description}")

    result = "Available Skills:\n" + "\n".join(skills)
    return [types.TextContent(type="text", text=result)]

async def load_skill_content(skill_name: str) -> list[types.TextContent]:
    """Load main SKILL.md content"""
    skill_path = os.path.join(SKILLS_DIR, f"document-skills-{skill_name}")
    skill_md = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skill_md):
        return [types.TextContent(
            type="text",
            text=f"Error: Skill '{skill_name}' not found"
        )]

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Return skill content
    result = f"""
# {skill_name.upper()} Skill Loaded

{content}

---
**Note:** This skill may reference additional files. Use `load_skill_file` if you need more details.
"""

    return [types.TextContent(type="text", text=result)]

async def load_additional_file(skill_name: str, file_name: str) -> list[types.TextContent]:
    """Load additional skill files (docx-js.md, ooxml.md, etc.)"""
    skill_path = os.path.join(SKILLS_DIR, f"document-skills-{skill_name}")
    file_path = os.path.join(skill_path, file_name)

    if not os.path.exists(file_path):
        return [types.TextContent(
            type="text",
            text=f"Error: File '{file_name}' not found in {skill_name} skill"
        )]

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    result = f"""
# {file_name} (from {skill_name} skill)

{content}
"""

    return [types.TextContent(type="text", text=result)]

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## Integration with Agent SDK

### Update `src/campfire_agent.py`

```python
# Add Custom Skills MCP to mcp_servers
mcp_servers = {
    # Existing MCPs
    "campfire": campfire_mcp_server,

    # External Financial MCP
    "fin-report-agent": {
        "transport": "stdio",
        "command": "uv",
        "args": ["run", "--directory", "/app/financial-mcp", "python", "run_mcp_server.py"]
    },

    # NEW: Custom Skills MCP (progressive disclosure)
    "skills": {
        "transport": "stdio",
        "command": "uv",
        "args": ["run", "--directory", "/app/skills-mcp", "python", "server.py"]
    }
}

# Update system prompt to reference skills MCP
system_prompt = """
你是一个专业的个人助手AI...

## 专业技能加载机制

当需要处理特定类型文档时，使用以下工具按需加载专业知识：

1. **list_skills** - 查看所有可用技能
2. **load_skill** - 加载特定技能的专业知识
   - Word文档处理: `load_skill(skill_name="docx")`
   - Excel表格处理: `load_skill(skill_name="xlsx")`
   - PowerPoint处理: `load_skill(skill_name="pptx")`

3. **load_skill_file** - 加载技能的详细文档
   - 示例: `load_skill_file(skill_name="docx", file_name="docx-js.md")`

## 重要原则

- **只在需要时加载技能** - 不要预加载所有技能
- **先判断需求** - 用户提到Word文档时才加载docx技能
- **渐进式详细** - 先加载SKILL.md，需要更多细节时再加载具体文件

示例工作流：
用户："请帮我创建一个Word文档"
你的思考：需要Word文档处理能力 → 调用 load_skill("docx") → 获得专业知识 → 执行任务
"""

options = ClaudeAgentOptions(
    model=self.bot_config.model,
    system_prompt=system_prompt,
    mcp_servers=mcp_servers,  # Includes skills MCP
    allowed_tools=allowed_tools,
    permission_mode='default',
    cwd=project_root,
    cli_path="/Users/heng/.claude/local/claude",
    max_turns=30
)
```

---

## Conversation Flow Examples

### Example 1: User Needs Word Document Help

**User:** "请帮我创建一个商业提案Word文档"

**Agent Reasoning:**
```
User needs Word document creation → I need docx expertise
→ Call load_skill(skill_name="docx")
```

**Tool Call:**
```json
{
  "tool": "load_skill",
  "arguments": {
    "skill_name": "docx"
  }
}
```

**MCP Returns:** 2,000 tokens of docx skill content

**Agent Response:** Uses skill knowledge to guide user through document creation

**Token Usage:**
- Base prompt: 2,700 tokens
- load_skill call: +2,000 tokens
- **Total:** 4,700 tokens (vs. 9,000 with manual approach)

---

### Example 2: General Question (No Skill Needed)

**User:** "今天天气怎么样？"

**Agent Reasoning:**
```
General question about weather → No document processing needed
→ No skill loading required
```

**Agent Response:** Answers directly without loading skills

**Token Usage:**
- Base prompt: 2,700 tokens
- **Total:** 2,700 tokens (vs. 9,000 with manual approach)
- **Savings:** 70% fewer tokens!

---

### Example 3: User Needs Deep Expertise

**User:** "我需要在Word文档中实现跟踪修改功能，保留原始RSID"

**Agent Reasoning:**
```
Complex Word document task → Load docx skill
→ Skill mentions ooxml.md for tracked changes
→ Need more detail → Load ooxml.md file
```

**Tool Calls:**
1. `load_skill(skill_name="docx")` → 2,000 tokens
2. `load_skill_file(skill_name="docx", file_name="ooxml.md")` → 2,500 tokens

**Token Usage:**
- Base prompt: 2,700 tokens
- load_skill: +2,000 tokens
- load_skill_file: +2,500 tokens
- **Total:** 7,200 tokens

**Still Better Than Manual:** Manual would include ALL 3 skills (9,000 tokens), this loads only what's needed (7,200 tokens)

---

## Comparison: Manual vs Custom MCP vs Skills API

| Aspect | Manual Skills | Custom Skills MCP | Skills API (Direct) |
|--------|--------------|-------------------|---------------------|
| **Token Usage (No Skill)** | 9,000 | 2,700 | 2,500 |
| **Token Usage (1 Skill)** | 9,000 | 4,700 | 4,500 |
| **Token Usage (3 Skills)** | 9,000 | 7,200 | 7,000 |
| **Progressive Disclosure** | ❌ No | ✅ Yes | ✅ Yes |
| **Agent SDK Compatible** | ✅ Yes | ✅ Yes | ❌ No |
| **MCP Tools Work** | ✅ Yes | ✅ Yes | ❌ No |
| **Session Management** | ✅ SDK | ✅ SDK | ❌ Manual |
| **Hooks & Permissions** | ✅ SDK | ✅ SDK | ❌ Manual |
| **Development Time** | 2-3 hours | 1 week | 2-3 weeks |
| **Maintenance** | Medium | Medium | High |
| **Cost/Month** | $22.50 | $11.25 | $10.50 |

---

## Implementation Effort

### Phase 1: Basic MCP Server (Week 1)

**Tasks:**
1. Create `skills-mcp/` directory structure
2. Implement `list_skills` tool
3. Implement `load_skill` tool (SKILL.md only)
4. Test with docx skill

**Deliverable:** Working MCP that loads docx skill on-demand

---

### Phase 2: Advanced Loading (Week 2)

**Tasks:**
1. Implement `load_skill_file` tool
2. Parse YAML frontmatter for metadata
3. Add error handling
4. Test with all 3 skills (docx, xlsx, pptx)

**Deliverable:** Complete progressive disclosure (3 levels)

---

### Phase 3: Integration & Testing (Week 3)

**Tasks:**
1. Update `campfire_agent.py` with skills MCP
2. Update system prompts (all 4 bots)
3. Test token usage vs. manual approach
4. Deploy to production

**Deliverable:** Production-ready Custom Skills MCP

---

## Advantages Over Manual Approach

### 1. Token Optimization (63% Savings)

**Manual:**
```python
# ALWAYS includes all 3 skills
system_prompt = base + docx_skill + xlsx_skill + pptx_skill
# 9,000 tokens per request
```

**Custom MCP:**
```python
# Loads only what's needed
- No skill: 2,700 tokens (70% of requests)
- 1 skill: 4,700 tokens (25% of requests)
- 2+ skills: 7,200 tokens (5% of requests)
# Average: 3,350 tokens (63% savings!)
```

---

### 2. Maintainability

**Manual:**
```python
# Skill content hardcoded in system prompts
system_prompt = f"""
你是一个专业的个人助手AI...

{docx_skill_content}  # Copied and pasted
{xlsx_skill_content}  # Copied and pasted
{pptx_skill_content}  # Copied and pasted
"""
```

**Custom MCP:**
```python
# Skills live in .claude/skills/ directory
# System prompt just references them
system_prompt = """
使用 load_skill 工具按需加载技能
"""
# Easy to update: just modify SKILL.md files
```

---

### 3. Scalability

**Manual:**
- Adding 4th skill: +2,000 tokens → 11,000 tokens per request
- Adding 10 skills: 25,000 tokens per request (context window issues!)

**Custom MCP:**
- Adding 4th skill: Base still 2,700 tokens
- Adding 10 skills: Base still 2,700 tokens
- Load only what's needed: 2,700 to ~7,000 tokens

---

### 4. Agent Decision Making

**Manual:**
```
Agent sees ALL skill content upfront
→ Cognitive overload
→ May reference wrong skill
→ Wastes tokens on irrelevant content
```

**Custom MCP:**
```
Agent reads: "Use load_skill when needed"
→ Makes intelligent decision
→ Loads only relevant skill
→ Focused attention on task
```

---

## Risks & Mitigation

### Risk 1: Extra Tool Call Latency

**Problem:** Each `load_skill` call adds ~2-3 seconds

**Mitigation:**
- Cache loaded skills in conversation context
- Only load once per conversation
- Accept latency tradeoff for token savings

### Risk 2: Agent Forgets to Load Skills

**Problem:** Agent tries to answer without loading skill first

**Mitigation:**
```python
system_prompt = """
## CRITICAL RULE

BEFORE processing any document request:
1. Check if you have the required skill loaded
2. If not, MUST call load_skill first
3. Never guess or provide incomplete information

Example:
❌ Wrong: User asks about Word → You guess the answer
✅ Right: User asks about Word → load_skill("docx") → Use skill knowledge
"""
```

### Risk 3: MCP Server Crashes

**Problem:** Skills MCP fails, no skill content available

**Mitigation:**
- Fallback to base knowledge (without skill expertise)
- Log errors for debugging
- Health check endpoint

---

## Success Metrics

### Token Usage Goals

**Before (Manual Skills):**
- Average: 9,000 tokens/request
- Cost: $22.50/month (1,000 requests)

**After (Custom Skills MCP):**
- Average: 3,350 tokens/request
- Cost: $11.25/month (1,000 requests)
- **Target: 60%+ token reduction ✅**

### Response Quality Goals

**Metrics:**
1. Agent loads correct skill 95%+ of time
2. Agent references skill workflows in responses
3. No hallucinated document processing steps
4. Skill content accuracy matches manual approach

### Performance Goals

1. `load_skill` tool call: < 3 seconds
2. Total response time: < 15 seconds (same as manual)
3. MCP server uptime: 99.9%

---

## Migration Path

### From Manual Skills (Current)

**Step 1:** Build Custom Skills MCP (Week 1-2)

**Step 2:** Test in Parallel (Week 3)
```python
# Test both approaches simultaneously
manual_bot = CampfireAgent(bot_config_manual)
mcp_bot = CampfireAgent(bot_config_mcp)

# Compare:
# - Token usage
# - Response quality
# - Latency
```

**Step 3:** Gradual Rollout (Week 4)
1. Deploy to Personal Assistant bot only
2. Monitor for 3 days
3. If successful, deploy to all bots
4. Remove manual skill content from system prompts

---

## Future Enhancements

### Enhancement 1: Skill Metadata Caching

```python
# Cache skill metadata to speed up list_skills
@server.list_resources()
async def list_resources():
    """List skills as resources (faster than tool calls)"""
    return [
        Resource(uri=f"skill://docx", name="docx", description="..."),
        Resource(uri=f"skill://xlsx", name="xlsx", description="..."),
    ]
```

### Enhancement 2: Smart Skill Recommendations

```python
# Analyze user message and recommend skills
@server.call_tool()
async def recommend_skills(arguments: dict) -> list[types.TextContent]:
    """Analyze user message and suggest relevant skills"""
    user_message = arguments["message"]

    recommendations = []
    if "word" in user_message.lower() or ".docx" in user_message:
        recommendations.append("docx")
    if "excel" in user_message.lower() or ".xlsx" in user_message:
        recommendations.append("xlsx")

    return [types.TextContent(
        type="text",
        text=f"Recommended skills: {', '.join(recommendations)}"
    )]
```

### Enhancement 3: Skill Usage Analytics

```python
# Track which skills are used most
skill_usage_stats = {
    "docx": 45,  # 45% of skill loads
    "xlsx": 30,
    "pptx": 25
}

# Could pre-warm frequently used skills
```

---

## Conclusion

**User's Insight Was Correct:**
> "Skills by itself are just tools. I'm thinking if we can extract the skills_content and build them as tools."

This Custom Skills MCP approach:

✅ **Works with Agent SDK** - Uses MCP architecture
✅ **Progressive Disclosure** - Loads only needed content
✅ **Token Optimization** - 63% savings vs. manual approach
✅ **Keeps SDK Benefits** - Sessions, hooks, permissions, MCPs
✅ **Better Than API Skills** - No need to abandon Agent SDK
✅ **Scalable** - Can add unlimited skills without token explosion

**Recommendation:** Implement Custom Skills MCP as "Option B+" (better than manual, works with SDK)

**Timeline:**
- Week 1-2: Build MCP server
- Week 3: Integration and testing
- Week 4: Production deployment
- **Total: 1 month to production**

**ROI:**
- Development: 1 week
- Token savings: $11.25/month
- Maintenance: Same as manual approach
- **Worth it if we plan to add 5+ skills**

---

**This approach achieves the best of both worlds: Agent SDK benefits + Skills API-like progressive disclosure.**
