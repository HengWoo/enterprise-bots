# Custom Skills MCP: Implementation Plan

**Date:** 2025-10-18
**Purpose:** Complete plan for implementing Custom Skills MCP with progressive disclosure
**Timeline:** 10 days (2 weeks with buffer)
**Expected Outcome:** 63% token reduction, scalable skills system

---

## Table of Contents

1. [Investigation Summary](#investigation-summary)
2. [Key Findings](#key-findings)
3. [Implementation Plan](#implementation-plan)
4. [Success Criteria](#success-criteria)
5. [Rollback Plan](#rollback-plan)

---

## Investigation Summary

### What We Investigated

**Initial Goal:** Integrate Agent Skills into Campfire AI bot project for progressive disclosure and token optimization.

**User's Challenge:** "Our system is wrapped in Claude Code CLI, so when Claude CLI can use it, our agent can use it. MCPs work via this mechanism, skills are file-based like MCPs, so skills should work too."

**Discovery Journey:**

1. **Plugin Skills System** - Found `.claude/settings.json` enables plugin marketplace skills
   - ✅ Bot behavior changed when enabled
   - ❌ Skill content doesn't load via SDK (Skill tool is interactive-only)

2. **Skills API System** - Discovered separate `/v1/skills` endpoint for programmatic skills
   - ✅ Works with Direct Messages API
   - ❌ Agent SDK v0.1.4 doesn't support it

3. **Hybrid Approach Analysis** - Evaluated mixing Agent SDK with Direct API
   - ❌ MCP architecture incompatible with Direct API
   - ❌ Would require 2-3 weeks to reimplement all MCPs

4. **Custom Skills MCP Solution** - User's insight: "Skills are just tools"
   - ✅ Build skills as MCP tools for on-demand loading
   - ✅ Progressive disclosure within Agent SDK architecture
   - ✅ 63% token savings, keeps all SDK benefits

---

## Key Findings

### Finding 1: TWO Skills Systems Exist

**Plugin Skills (Local/Interactive):**
- Location: `~/.claude/plugins/marketplaces/anthropic-agent-skills/`
- Enablement: `.claude/settings.json` with `enabledPlugins`
- Loading: Via "Skill tool" in interactive Claude Code CLI
- **Status:** ❌ Doesn't work via Agent SDK (Skill tool not available programmatically)

**API Skills (Cloud/Programmatic):**
- Endpoint: `/v1/skills` for skill management
- Usage: `/v1/messages` with `skills` parameter
- Requirements: Code Execution Tool beta enabled
- **Status:** ✅ Works but ❌ Agent SDK v0.1.4 doesn't expose it

**Conclusion:** Both skills systems exist but neither work with Agent SDK v0.1.4.

---

### Finding 2: Agent SDK Architecture

**Agent SDK (claude-agent-sdk v0.1.4):**
```python
ClaudeSDKClient
    ↓ spawns subprocess
Claude CLI (Rust binary at ~/.claude/local/claude)
    ↓ manages via stdin/stdout pipes
MCP Server Subprocesses (Python/Node)
    ↓ JSON-RPC communication
Tools execute in subprocess → Results via stdout
```

**ClaudeAgentOptions Parameters:**
- `model` - Model to use
- `system_prompt` - System instructions
- `mcp_servers` - MCP server configurations ✅
- `allowed_tools` - Tool filtering
- `permission_mode` - User permissions
- `max_turns` - Multi-turn conversations
- `setting_sources` - .claude/ directory discovery
- `cwd` - Working directory for CLI
- `cli_path` - Path to Claude CLI binary

**Missing:** No `skills` parameter exists in v0.1.4

---

### Finding 3: MCP vs Direct API Incompatibility

**Why They Can't Work Together:**

**Agent SDK MCPs:**
```python
# Live subprocess processes
mcp_servers = {
    "campfire": campfire_mcp_server,  # SDK-based (in-process)
    "fin-report-agent": {  # External subprocess
        "transport": "stdio",
        "command": "uv",
        "args": ["run", "python", "run_mcp_server.py"]
    }
}

# CLI spawns subprocesses, manages stdin/stdout pipes
# Tools execute in separate processes via JSON-RPC
```

**Direct Messages API:**
```python
# Static tool schemas, HTTP communication
tools = [
    {
        "name": "get_excel_info",
        "description": "...",
        "input_schema": {...}
    }
]

# YOU must implement tool execution manually
response = client.messages.create(tools=tools, ...)
if response.stop_reason == "tool_use":
    result = your_implementation(...)  # No subprocess!
```

**Three Incompatibilities:**

1. **Tool Definition Format**
   - MCP: Live processes with @decorators
   - API: Static JSON schemas

2. **Communication Channel**
   - MCP: stdin/stdout pipes (local)
   - API: HTTP requests (cloud)

3. **Execution Location**
   - MCP: Separate subprocesses
   - API: Your Python process

**Impact:** Cannot share MCP servers between SDK and Direct API. Would need to reimplement all 9 MCP tools as native functions (2-3 weeks effort).

---

### Finding 4: Four Possible Approaches

**Option A: Direct Messages API**
- Use `/v1/skills` endpoint with Direct API
- ❌ Loses all Agent SDK benefits (sessions, 9 MCP tools, hooks, permissions)
- ❌ 2-3 weeks development to reimplement MCPs
- ❌ Not worth it

**Option B: Manual Skill Content**
- Inject skill content into system prompts
- ✅ Simple (2-3 hours)
- ❌ No progressive disclosure (+100% token usage)
- ⚠️ Good for quick MVP

**Option C: Custom Skills MCP (RECOMMENDED)**
- Build MCP server that loads skills on-demand
- ✅ Progressive disclosure (63% token savings)
- ✅ Works with Agent SDK
- ✅ Scalable (10+ skills)
- ✅ 1 week development

**Option D: Wait for SDK Update**
- Hope SDK adds skills support
- ⏳ Unknown timeline
- ⏳ Monitor but don't wait

---

### Finding 5: Custom Skills MCP Solution

**The Insight (User's Idea):**
> "Skills by itself are just tools. I'm thinking if we can extract the skills_content and build them as tools."

**Implementation:**
```python
# Create MCP server with skill loading tools
@server.call_tool()
async def load_skill(arguments: dict) -> list[TextContent]:
    """Load skill content on-demand"""
    skill_name = arguments["skill_name"]  # e.g., "docx"
    skill_path = f".claude/skills/document-skills-{skill_name}/SKILL.md"
    content = read_file(skill_path)
    return [TextContent(type="text", text=content)]

@server.call_tool()
async def load_skill_file(arguments: dict) -> list[TextContent]:
    """Load additional skill files (3rd level of detail)"""
    skill_name = arguments["skill_name"]
    file_name = arguments["file_name"]  # e.g., "docx-js.md"
    file_path = f".claude/skills/document-skills-{skill_name}/{file_name}"
    content = read_file(file_path)
    return [TextContent(type="text", text=content)]
```

**Benefits:**
- ✅ **Progressive Disclosure** - Loads only needed skills (like Skills API)
- ✅ **Works with Agent SDK** - Uses MCP architecture
- ✅ **63% Token Savings** - Average 3,350 vs 9,000 tokens
- ✅ **Keeps SDK Benefits** - All 9 MCP tools, sessions, hooks, permissions
- ✅ **Scalable** - Add unlimited skills without token explosion
- ✅ **$17/month Savings** - vs. manual approach

---

### Finding 6: Token Usage Analysis

**Manual Approach (Option B):**
```
Every request includes ALL skills:
- Base prompt: 2,500 tokens
- docx skill: 2,000 tokens
- xlsx skill: 2,500 tokens
- pptx skill: 2,000 tokens
= 9,000 tokens per request (100% of requests)

Cost: $27/month (1,000 requests)
```

**Custom Skills MCP (Option C):**
```
Progressive loading based on need:

70% of requests need no skill:
  2,700 tokens (base + skill reference)

25% of requests need 1 skill:
  4,700 tokens (base + 1 skill loaded)

5% of requests need 2+ skills:
  7,200 tokens (base + multiple skills)

Average: 3,350 tokens (63% reduction!)

Cost: $10/month (1,000 requests)
Savings: $17/month
```

**Scenario Examples:**

| User Request | Manual | Custom MCP | Savings |
|-------------|--------|------------|---------|
| "今天天气怎么样？" (general) | 9,000 | 2,700 | 70% |
| "创建Word文档" (need docx) | 9,000 | 4,700 | 48% |
| "分析Excel生成Word报告" (2 skills) | 9,000 | 7,200 | 20% |

---

### Finding 7: Current Project Status

**Working Features (v0.2.4.2):**
- ✅ FastAPI + Stateful Sessions (hot/warm/cold paths)
- ✅ Real-time Progress Milestones
- ✅ 4 Specialized Bots (Financial, Technical, Personal, Briefing)
- ✅ 9 MCP Tools:
  - 3 Conversation tools (search, context, save)
  - 4 Knowledge Base tools (search, read, list, store)
  - 2 Briefing tools (generate, search)
- ✅ Financial MCP Server (Excel analysis)

**Existing MCP Servers:**
```python
mcp_servers = {
    "campfire": campfire_mcp_server,  # SDK-based (conversations, context, KB)
    "fin-report-agent": {  # External subprocess (Excel)
        "transport": "stdio",
        "command": "uv",
        "args": ["run", "--directory", "/app/financial-mcp", "python", "run_mcp_server.py"]
    }
}
```

**New Addition:**
```python
mcp_servers["skills"] = {  # Custom Skills MCP (progressive disclosure)
    "transport": "stdio",
    "command": "uv",
    "args": ["run", "--directory", "/app/skills-mcp", "python", "server.py"]
}
```

---

## Implementation Plan

### Phase 1: Setup & Basic MCP Server (Days 1-2)

#### Day 1: Project Structure

**Task 1.1:** Create skills-mcp directory
```bash
mkdir -p skills-mcp
cd skills-mcp
```

**Task 1.2:** Initialize Python project
```bash
uv init
```

**Task 1.3:** Create pyproject.toml
```toml
[project]
name = "campfire-skills-mcp"
version = "0.1.0"
description = "Custom Skills MCP for progressive disclosure"
requires-python = ">=3.11"
dependencies = [
    "mcp>=1.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Task 1.4:** Install dependencies
```bash
uv sync
```

**Deliverable:** Working Python project with MCP SDK installed

---

#### Day 2: Basic Server Implementation

**Task 2.1:** Create server.py skeleton
```python
# skills-mcp/server.py

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("skills-mcp")

server = Server("campfire-skills")

# Skills directory (will be /app/.claude/skills in Docker)
SKILLS_DIR = os.getenv("SKILLS_DIR", "/app/.claude/skills")

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
            description="Load a skill's expertise on-demand. Only call when you need specific expertise (e.g., user asks about Word → load docx skill).",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "Skill to load: 'docx', 'xlsx', or 'pptx'"
                    }
                },
                "required": ["skill_name"]
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Execute tool calls"""

    if name == "list_skills":
        return await list_available_skills()

    elif name == "load_skill":
        skill_name = arguments["skill_name"]
        return await load_skill_content(skill_name)

    else:
        raise ValueError(f"Unknown tool: {name}")

async def list_available_skills() -> list[types.TextContent]:
    """List all skills in .claude/skills/"""
    # TODO: Implement
    return [types.TextContent(type="text", text="Available skills: docx, xlsx, pptx")]

async def load_skill_content(skill_name: str) -> list[types.TextContent]:
    """Load main SKILL.md content"""
    # TODO: Implement
    return [types.TextContent(type="text", text=f"Loaded {skill_name} skill (placeholder)")]

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

**Task 2.2:** Test server locally
```bash
cd skills-mcp
uv run python server.py
# Should start without errors
```

**Deliverable:** Basic MCP server skeleton that starts successfully

---

### Phase 2: Implement Core Tools (Days 3-4)

#### Day 3: list_skills Implementation

**Task 3.1:** Implement skill discovery
```python
async def list_available_skills() -> list[types.TextContent]:
    """List all skills in .claude/skills/"""

    if not os.path.exists(SKILLS_DIR):
        return [types.TextContent(
            type="text",
            text=f"Error: Skills directory not found: {SKILLS_DIR}"
        )]

    skills = []

    for dir_name in os.listdir(SKILLS_DIR):
        skill_path = os.path.join(SKILLS_DIR, dir_name)
        skill_md = os.path.join(skill_path, "SKILL.md")

        if os.path.isdir(skill_path) and os.path.exists(skill_md):
            # Parse YAML frontmatter
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()

                # Extract metadata from frontmatter
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = parts[1]

                        # Simple parsing (extract name and description)
                        name = dir_name
                        description = "Document processing skill"

                        for line in frontmatter.split('\n'):
                            if line.startswith('name:'):
                                name = line.split(':', 1)[1].strip()
                            elif line.startswith('description:'):
                                description = line.split(':', 1)[1].strip()

                        skills.append(f"- **{name}**: {description}")

    if not skills:
        result = "No skills found in .claude/skills/ directory"
    else:
        result = "Available Skills:\n\n" + "\n".join(skills)

    return [types.TextContent(type="text", text=result)]
```

**Task 3.2:** Test list_skills
```bash
# Set SKILLS_DIR to local .claude/skills
SKILLS_DIR=/Users/heng/Development/campfire/ai-bot/.claude/skills uv run python server.py
# Then test via MCP client or manual JSON-RPC
```

**Deliverable:** Working list_skills tool that discovers skills

---

#### Day 4: load_skill Implementation

**Task 4.1:** Implement skill content loading
```python
async def load_skill_content(skill_name: str) -> list[types.TextContent]:
    """Load main SKILL.md content"""

    # Support both formats: "docx" and "document-skills-docx"
    if not skill_name.startswith("document-skills-"):
        skill_name = f"document-skills-{skill_name}"

    skill_path = os.path.join(SKILLS_DIR, skill_name)
    skill_md = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skill_md):
        logger.error(f"Skill not found: {skill_name}")
        return [types.TextContent(
            type="text",
            text=f"Error: Skill '{skill_name}' not found in {SKILLS_DIR}"
        )]

    logger.info(f"Loading skill: {skill_name}")

    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # Return skill content
        result = f"""
# {skill_name.upper()} Skill Loaded

{content}

---
**Note:** This skill may reference additional files. Use `load_skill_file` if you need more specific details from referenced documentation.
"""

        logger.info(f"Successfully loaded skill: {skill_name} ({len(content)} bytes)")

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        logger.error(f"Error loading skill {skill_name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error loading skill '{skill_name}': {str(e)}"
        )]
```

**Task 4.2:** Test load_skill
```bash
# Test with docx skill
SKILLS_DIR=/Users/heng/Development/campfire/ai-bot/.claude/skills uv run python server.py
# Verify it loads document-skills-docx/SKILL.md correctly
```

**Deliverable:** Working load_skill tool that loads SKILL.md content

---

### Phase 3: Advanced Features (Day 5)

#### Day 5: load_skill_file Implementation

**Task 5.1:** Add load_skill_file tool
```python
@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available skill-related tools"""
    return [
        # ... existing tools ...
        types.Tool(
            name="load_skill_file",
            description="Load additional detailed files from a skill (third level of detail). Only use AFTER loading the main skill if you need more specific information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "Skill name (e.g., 'docx')"
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

async def load_additional_file(skill_name: str, file_name: str) -> list[types.TextContent]:
    """Load additional skill files (docx-js.md, ooxml.md, etc.)"""

    # Support both formats
    if not skill_name.startswith("document-skills-"):
        skill_name = f"document-skills-{skill_name}"

    skill_path = os.path.join(SKILLS_DIR, skill_name)
    file_path = os.path.join(skill_path, file_name)

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_name} in {skill_name}")
        return [types.TextContent(
            type="text",
            text=f"Error: File '{file_name}' not found in {skill_name} skill"
        )]

    logger.info(f"Loading skill file: {skill_name}/{file_name}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        result = f"""
# {file_name} (from {skill_name} skill)

{content}
"""

        logger.info(f"Successfully loaded file: {file_name} ({len(content)} bytes)")

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        logger.error(f"Error loading file {file_name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error loading file '{file_name}': {str(e)}"
        )]
```

**Task 5.2:** Update call_tool handler
```python
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
```

**Task 5.3:** Test all three tools
```bash
# Test list_skills, load_skill, load_skill_file
SKILLS_DIR=/Users/heng/Development/campfire/ai-bot/.claude/skills uv run python server.py
# Verify all tools work correctly
```

**Deliverable:** Complete MCP server with all 3 skill tools working

---

### Phase 4: Agent SDK Integration (Days 6-7)

#### Day 6: Add Skills MCP to Configuration

**Task 6.1:** Update src/campfire_agent.py
```python
# Around line 118-143 (MCP servers configuration)

# Add Skills MCP to mcp_servers dictionary
if self.bot_config.capabilities.get('file_analysis'):
    # Skills MCP for progressive disclosure
    mcp_servers["skills"] = {
        "transport": "stdio",
        "command": "uv",
        "args": [
            "run",
            "--directory",
            "/app/skills-mcp",  # Docker path
            "python",
            "server.py"
        ],
        "env": {
            "SKILLS_DIR": "/app/.claude/skills"  # Docker path to skills
        }
    }

    logger.info("Loaded Skills MCP for progressive skill disclosure")
```

**Task 6.2:** Create system prompt guidance template
```python
# Create new file: src/templates/skills_guidance.txt

## 专业技能加载机制 (Progressive Skill Loading)

当需要处理特定类型文档时，使用以下工具按需加载专业知识：

### 可用工具

1. **list_skills** - 查看所有可用技能
   - 示例：`list_skills()`
   - 返回：所有可用技能及其描述

2. **load_skill** - 加载特定技能的专业知识
   - Word文档处理：`load_skill(skill_name="docx")`
   - Excel表格处理：`load_skill(skill_name="xlsx")`
   - PowerPoint处理：`load_skill(skill_name="pptx")`

3. **load_skill_file** - 加载技能的详细文档（第三级详细信息）
   - 示例：`load_skill_file(skill_name="docx", file_name="docx-js.md")`
   - 仅在加载主技能后需要更多细节时使用

### 重要原则

**渐进式加载原则：**
- ❌ **不要预加载所有技能** - 浪费tokens
- ✅ **只在需要时加载** - 用户提到Word文档时才加载docx技能
- ✅ **先判断需求** - 分析用户问题，确定需要哪个技能
- ✅ **渐进式详细** - 先加载SKILL.md，需要时再加载具体文件

### 工作流示例

**示例1：创建Word文档**
```
用户："请帮我创建一个商业提案Word文档"
你的思考：
1. 分析：需要Word文档处理能力
2. 决策：调用 load_skill(skill_name="docx")
3. 获得：docx技能的专业知识（工作流程、库使用、最佳实践）
4. 执行：按照技能指导完成任务
```

**示例2：一般问题（无需技能）**
```
用户："今天天气怎么样？"
你的思考：
1. 分析：一般性问题，不涉及文档处理
2. 决策：无需加载任何技能
3. 执行：直接回答
```

**示例3：复杂文档任务**
```
用户："我需要在Word文档中实现跟踪修改功能，保留原始RSID"
你的思考：
1. 分析：复杂的Word文档任务
2. 决策：先加载 load_skill(skill_name="docx")
3. 发现：技能提到需要参考ooxml.md获取详细信息
4. 决策：加载 load_skill_file(skill_name="docx", file_name="ooxml.md")
5. 执行：使用详细的OOXML知识完成任务
```

### 技能加载检查清单

在回答任何文档处理问题前，先问自己：
- [ ] 这个任务涉及文档处理吗？
- [ ] 我已经加载了所需的技能吗？
- [ ] 我是否需要更详细的技能文件？

**记住：宁可多加载一次技能，也不要凭猜测回答！**
```

**Task 6.3:** Update bot system prompts
```python
# Update bots/personal_assistant.json

{
  "bot_id": "personal_assistant",
  "name": "个人助手",
  "model": "claude-sonnet-4-5-20250929",
  "system_prompt": "你是一个专业的个人助手AI，名叫「个人助手」。\n\n你的专业能力：\n1. 对话搜索 - 搜索历史对话记录\n2. 用户偏好 - 记住用户偏好和习惯\n3. 知识库访问 - 访问公司知识库文档\n4. 文档处理 - 分析和处理Word、Excel、PowerPoint文档\n\n{SKILLS_GUIDANCE}\n\n请严格遵循技能加载原则，确保渐进式加载，避免浪费tokens。",
  "capabilities": {
    "conversation_search": true,
    "user_context": true,
    "knowledge_base": true,
    "file_analysis": true,
    "skills_progressive_disclosure": true
  },
  "allowed_tools": ["all"]
}
```

**Task 6.4:** Load skills guidance in campfire_agent.py
```python
# In CampfireAgent.__init__ or prepare_agent_session

# Load skills guidance template
skills_guidance_path = os.path.join(
    os.path.dirname(__file__),
    "templates",
    "skills_guidance.txt"
)

if os.path.exists(skills_guidance_path):
    with open(skills_guidance_path, 'r', encoding='utf-8') as f:
        skills_guidance = f.read()

    # Replace {SKILLS_GUIDANCE} placeholder in system prompt
    system_prompt = self.bot_config.system_prompt.replace(
        "{SKILLS_GUIDANCE}",
        skills_guidance
    )
else:
    system_prompt = self.bot_config.system_prompt
```

**Deliverable:** Skills MCP integrated into Agent SDK configuration

---

#### Day 7: Local Testing

**Task 7.1:** Test with personal_assistant bot
```bash
cd /Users/heng/Development/campfire/ai-bot

# Start FastAPI server with skills MCP
PYTHONPATH=/Users/heng/Development/campfire/ai-bot \
TESTING=true \
CAMPFIRE_URL=https://chat.smartice.ai \
uv run python src/app_fastapi.py
```

**Task 7.2:** Test skill loading via webhook
```bash
# Test docx skill loading
curl -X POST http://localhost:8000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {"id": 1, "name": "Test User"},
    "room": {"id": 1, "name": "Test Room"},
    "content": "请帮我创建一个商业提案Word文档"
  }'

# Expected behavior:
# 1. Bot receives request
# 2. Bot analyzes: "Need Word document capability"
# 3. Bot calls load_skill(skill_name="docx")
# 4. Skills MCP returns docx skill content
# 5. Bot uses skill knowledge to guide user
```

**Task 7.3:** Verify token usage
```bash
# Check logs for token counts
# Should see:
# - Initial request: ~2,700 tokens
# - After load_skill: ~4,700 tokens
# - Much less than manual approach (9,000 tokens)
```

**Task 7.4:** Test all 3 scenarios
```bash
# Scenario 1: General question (no skill needed)
curl -X POST http://localhost:8000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":1,"name":"Test"},"room":{"id":1,"name":"Test"},"content":"今天天气怎么样？"}'
# Expected: No skill loaded, ~2,700 tokens

# Scenario 2: Word document task (docx skill)
curl -X POST http://localhost:8000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":1,"name":"Test"},"room":{"id":1,"name":"Test"},"content":"创建一个Word文档"}'
# Expected: docx skill loaded, ~4,700 tokens

# Scenario 3: Excel + Word task (2 skills)
curl -X POST http://localhost:8000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":1,"name":"Test"},"room":{"id":1,"name":"Test"},"content":"分析Excel报表并生成Word总结"}'
# Expected: xlsx + docx skills loaded, ~7,200 tokens
```

**Deliverable:** Verified skills MCP working locally with all scenarios

---

### Phase 5: Docker Integration (Day 8)

#### Day 8: Update Dockerfile and docker-compose.yml

**Task 8.1:** Update Dockerfile
```dockerfile
# In Dockerfile, add skills-mcp

# ... existing setup ...

# Copy skills-mcp
COPY skills-mcp/ /app/skills-mcp/

# Install skills-mcp dependencies
WORKDIR /app/skills-mcp
RUN uv sync

# Back to app directory
WORKDIR /app

# ... rest of Dockerfile ...

# Update version label
LABEL version="0.3.0" \
      description="Campfire AI Bot with Custom Skills MCP (Progressive Disclosure)"
```

**Task 8.2:** Verify .claude/skills/ is copied
```dockerfile
# Should already be in Dockerfile:
COPY .claude/ /app/.claude/

# Verify skills are there:
# - /app/.claude/skills/document-skills-docx/
# - /app/.claude/skills/document-skills-xlsx/
# - /app/.claude/skills/document-skills-pptx/
```

**Task 8.3:** Build Docker image
```bash
cd /Users/heng/Development/campfire/ai-bot

docker buildx build --platform linux/amd64 \
  -t hengwoo/campfire-ai-bot:0.3.0 \
  -t hengwoo/campfire-ai-bot:latest \
  .
```

**Task 8.4:** Test Docker image locally
```bash
# Run container locally
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -e TESTING=true \
  -e CAMPFIRE_URL=https://chat.smartice.ai \
  hengwoo/campfire-ai-bot:0.3.0

# Test webhook
curl -X POST http://localhost:8000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":1,"name":"Test"},"room":{"id":1,"name":"Test"},"content":"创建Word文档"}'

# Verify:
# - Skills MCP starts correctly
# - Skills load on-demand
# - No errors in logs
```

**Deliverable:** Working Docker image with Skills MCP

---

### Phase 6: Production Deployment (Days 9-10)

#### Day 9: Deploy to Production

**Task 9.1:** Push to Docker Hub
```bash
docker push hengwoo/campfire-ai-bot:0.3.0
docker push hengwoo/campfire-ai-bot:latest
```

**Task 9.2:** Deploy on production server
```bash
# SSH to server (via DigitalOcean console)
cd /root/ai-service

# Backup current version
docker tag hengwoo/campfire-ai-bot:latest hengwoo/campfire-ai-bot:0.2.4.2-backup

# Pull new version
docker pull hengwoo/campfire-ai-bot:latest

# Stop services
docker-compose down

# Start with new version
docker-compose up -d

# Check logs
docker logs -f campfire-ai-bot
```

**Task 9.3:** Verify skills MCP starts
```bash
# Check logs for:
# - "Loaded Skills MCP for progressive skill disclosure"
# - "Skills MCP server started successfully"
# - No errors about skills directory not found
```

**Task 9.4:** Test in production Campfire
```
1. @个人助手 请帮我创建一个Word文档
   Expected: Bot loads docx skill, provides guidance

2. @个人助手 今天天气怎么样？
   Expected: Bot answers directly without loading skills

3. @个人助手 分析Excel报表并生成Word总结
   Expected: Bot loads xlsx + docx skills, provides guidance
```

**Deliverable:** Skills MCP deployed and working in production

---

#### Day 10: Monitoring & Optimization

**Task 10.1:** Collect metrics
```python
# Add token usage logging to campfire_agent.py

logger.info(f"Token usage - Input: {response.usage.input_tokens}, Output: {response.usage.output_tokens}")

# Monitor for 24 hours:
# - Average tokens per request
# - Skill loading frequency (which skills used most)
# - Response latency
```

**Task 10.2:** Create monitoring dashboard
```bash
# Log analysis script
grep "Token usage" /var/lib/docker/volumes/ai-service_ai-knowledge/_data/logs/app.log | \
  awk '{sum+=$NF} END {print "Average input tokens:", sum/NR}'

# Skill loading stats
grep "load_skill" /var/lib/docker/volumes/ai-service_ai-knowledge/_data/logs/app.log | \
  sort | uniq -c | sort -rn
```

**Task 10.3:** Optimize based on findings
```python
# If docx skill is loaded 80% of time, consider:
# - Pre-warm frequently used skills
# - Cache loaded skills in conversation context
# - Adjust system prompt guidance

# If token savings < 50%, investigate:
# - Are skills being loaded unnecessarily?
# - Is system prompt too verbose?
# - Should we trim skill content?
```

**Deliverable:** Production metrics and optimization plan

---

## Success Criteria

### Phase 1-2: MCP Server (Days 1-4)
- [ ] Skills MCP server starts without errors
- [ ] list_skills returns all 3 skills (docx, xlsx, pptx)
- [ ] load_skill loads SKILL.md content correctly
- [ ] load_skill_file loads additional files (docx-js.md, ooxml.md)

### Phase 3-4: Integration (Days 5-7)
- [ ] Skills MCP added to mcp_servers configuration
- [ ] System prompts updated with skills guidance
- [ ] Local testing shows skills loading on-demand
- [ ] Token usage matches expectations:
  - No skill: ~2,700 tokens
  - 1 skill: ~4,700 tokens
  - 2 skills: ~7,200 tokens

### Phase 5-6: Deployment (Days 8-10)
- [ ] Docker image builds successfully
- [ ] Docker image runs locally with skills MCP
- [ ] Production deployment successful
- [ ] Skills load correctly in production Campfire
- [ ] No regressions in existing functionality

### Overall Success Metrics
- [ ] **Token Reduction:** Average 60%+ reduction vs. manual approach
- [ ] **Cost Savings:** $15+/month savings (estimated)
- [ ] **Skill Loading Accuracy:** 95%+ correct skill selection
- [ ] **Response Quality:** No regression vs. manual approach
- [ ] **Latency:** < 3 seconds per skill load
- [ ] **Uptime:** 99.9% MCP server availability

---

## Rollback Plan

### If Skills MCP Fails in Production

**Step 1: Immediate Rollback (5 minutes)**
```bash
cd /root/ai-service
docker-compose down
docker tag hengwoo/campfire-ai-bot:0.2.4.2-backup hengwoo/campfire-ai-bot:latest
docker-compose up -d
```

**Step 2: Verify Rollback**
```bash
# Test existing bots still work
@财务分析师 列出所有知识库文档
# Should work (no skills involved)
```

**Step 3: Investigate Issue**
```bash
docker logs campfire-ai-bot > /tmp/skills-mcp-failure.log
# Analyze logs for root cause
```

**Step 4: Fix and Redeploy**
- Fix issue locally
- Test thoroughly
- Rebuild Docker image
- Deploy v0.3.1

---

### If Skills Loading Too Slow

**Mitigation 1: Cache Skills in Context**
```python
# In CampfireAgent, add skill caching
if skill_name in conversation_context.get('loaded_skills', []):
    logger.info(f"Skill {skill_name} already loaded in this conversation")
    return  # Don't reload
else:
    # Load skill
    conversation_context['loaded_skills'].append(skill_name)
```

**Mitigation 2: Pre-warm Frequently Used Skills**
```python
# If docx skill is used 80% of time, pre-load it
if bot_id == "personal_assistant":
    # Pre-load docx skill for first request
    await load_skill("docx")
```

---

### If Token Savings Don't Materialize

**Investigation:**
```bash
# Check actual token usage
grep "Token usage" logs/app.log | \
  awk '{print $NF}' | \
  awk '{sum+=$1; count++} END {print "Average:", sum/count}'

# Expected: ~3,350 tokens
# If > 7,000 tokens: Skills being loaded too often
# If > 9,000 tokens: Skills not being used at all (manual fallback?)
```

**Fix:**
- Optimize system prompt (reduce guidance verbosity)
- Trim skill content (remove less useful sections)
- Improve skill loading logic (better detection of when to load)

---

## Documentation to Create

**During Implementation:**
1. `skills-mcp/README.md` - MCP server documentation
2. `skills-mcp/TESTING.md` - Testing guide for skills MCP
3. `DEPLOYMENT_v0.3.0.md` - Deployment guide for v0.3.0
4. `SKILLS_MCP_TROUBLESHOOTING.md` - Common issues and fixes

**After Deployment:**
1. `SKILLS_MCP_METRICS.md` - Production metrics and analysis
2. `SKILLS_MCP_OPTIMIZATION.md` - Optimization recommendations

---

## Files to Archive/Remove After Implementation

**These intermediate research files can be deleted once Custom Skills MCP is deployed:**

1. `AGENT_SKILLS_FINAL_INVESTIGATION.md` - Superseded by this plan
2. `SKILLS_VS_MCP_DEEP_DIVE.md` - Details captured in Key Findings
3. `SKILLS_API_DISCOVERY.md` - Findings consolidated here
4. `HYBRID_APPROACH_SKILLS_SDK.md` - Options documented in Key Findings
5. `FINAL_SKILLS_RECOMMENDATION.md` - Recommendation is Custom Skills MCP
6. `MCP_INCOMPATIBILITY_EXAMPLES.md` - Key examples captured in Finding 3
7. `CUSTOM_SKILLS_MCP_DESIGN.md` - Implementation plan is here

**Keep These Files:**
- `SKILLS_INTEGRATION_PLAN.md` (this file) - Complete reference
- `CLAUDE.md` - Project memory (update with v0.3.0 status)
- `DESIGN.md` - Architecture (update with Skills MCP)
- `IMPLEMENTATION_PLAN.md` - Update with v0.3.0 deployment

---

## Timeline Summary

| Phase | Days | Deliverable | Status |
|-------|------|------------|--------|
| **Phase 1-2: MCP Server** | Days 1-4 | Working Skills MCP with 3 tools | 🎯 Ready |
| **Phase 3-4: Integration** | Days 5-7 | Skills MCP integrated with Agent SDK | 🎯 Ready |
| **Phase 5: Docker** | Day 8 | Docker image with Skills MCP | 🎯 Ready |
| **Phase 6: Production** | Days 9-10 | Deployed and monitored | 🎯 Ready |
| **Total** | **10 days** | **Custom Skills MCP in production** | 🎯 Ready |

**With Buffer: 2 weeks (10 working days + 4 buffer days)**

---

## Expected Outcomes

### Token Usage Reduction
- **Current (Manual):** 9,000 tokens/request
- **After (Custom MCP):** 3,350 tokens/request (average)
- **Reduction:** 63% fewer tokens

### Cost Savings
- **Current (Manual):** $27/month (1,000 requests)
- **After (Custom MCP):** $10/month (1,000 requests)
- **Savings:** $17/month

### Scalability
- **Current (Manual):** Limited to 3-5 skills (token window constraints)
- **After (Custom MCP):** Unlimited skills (progressive disclosure)

### User Experience
- **Same or Better:** Skills load on-demand, no user-visible difference
- **Response Time:** +2-3 seconds per skill load (acceptable)

---

## Next Steps After This Plan

1. **Review Plan** - User reviews and approves plan
2. **Start Implementation** - Begin Phase 1 (Days 1-4)
3. **Clear Context** - Archive intermediate research files
4. **Focus on Execution** - Follow plan step-by-step

---

**This plan consolidates all investigation findings into a single, executable implementation roadmap for Custom Skills MCP with progressive disclosure.**
