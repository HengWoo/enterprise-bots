# Hybrid Approach: Agent SDK + Skills API

**Date:** 2025-10-18
**Purpose:** Design architecture combining Agent SDK with direct Skills API usage

---

## Investigation Results

### Finding 1: Agent SDK Has NO Skills Support ❌

**Evidence:**
```python
ClaudeAgentOptions parameters (v0.1.4):
- allowed_tools
- system_prompt
- mcp_servers
- permission_mode
- max_turns
- setting_sources  # For plugin skills (doesn't work)
- extra_args       # Generic CLI args
... NO skills parameter
```

**Conclusion:** Agent SDK (v0.1.4) does NOT expose /v1/skills API functionality.

---

### Finding 2: Skills API Requires Direct Messages API ✅

**Based on documentation:**
- Skills API endpoint: `/v1/skills` (upload/manage)
- Skills referenced in Messages API: `/v1/messages` with `skills` parameter
- Requires Code Execution Tool beta enabled

**Key Insight:** Skills API is separate from Agent SDK's CLI subprocess approach.

---

## Three Architecture Options

### Option A: Pure Direct API (Bypass SDK Entirely)

**Architecture:**
```python
# Upload skills once
import anthropic
client = anthropic.Anthropic(api_key=API_KEY)

# Upload skill
skill_id = client.skills.create(
    name="docx",
    files={"SKILL.md": skill_content}
)

# Use in messages
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    skills=[skill_id],  # Reference uploaded skill
    tools=[...],        # Our MCP tools
    messages=[...]
)
```

**Pros:**
- ✅ Full skills support (progressive disclosure, token optimization)
- ✅ Direct control over API parameters
- ✅ Simpler architecture (one API client)

**Cons:**
- ❌ Lose Agent SDK benefits:
  - Session management (resume parameter)
  - Hooks (PreToolUse, PostToolUse, etc.)
  - Permission system
  - Subagents
  - Auto-context management
- ❌ Have to rebuild session persistence ourselves
- ❌ No CLI subprocess benefits (filesystem access, code execution)

**Verdict:** ❌ Not recommended - losing too much SDK functionality

---

### Option B: Hybrid - SDK with Manual Skill Content

**Architecture:**
```python
# Extract skill content from SKILL.md files
skill_content = extract_skill_instructions("document-skills-docx/SKILL.md")

# Add to system prompt
system_prompt = f"""
你是一个专业的个人助手AI...

{skill_content}  # Inject skill instructions directly

当用户提到Word文档时，请参考上述文档处理工作流程。
"""

# Use Agent SDK as normal
options = ClaudeAgentOptions(
    system_prompt=system_prompt,  # With embedded skills
    mcp_servers=mcp_servers,
    setting_sources=["project"],
    ...
)
```

**Pros:**
- ✅ Keep all Agent SDK benefits (sessions, hooks, permissions)
- ✅ Simple to implement (just text concatenation)
- ✅ No new dependencies or API complexity
- ✅ Works with current Agent SDK version

**Cons:**
- ❌ No progressive disclosure (all content loaded upfront)
- ❌ Higher token usage (~100% increase: 2,500 → 5,000 tokens)
- ❌ Manual skill content maintenance
- ❌ No automatic skill updates from Anthropic

**Verdict:** ✅ Recommended for MVP (Option 1 from previous analysis)

---

### Option C: True Hybrid - SDK + Direct API Calls

**Architecture:**
```python
import anthropic
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

class HybridCampfireAgent:
    def __init__(self):
        # Direct API client for skills management
        self.anthropic_client = anthropic.Anthropic(api_key=API_KEY)

        # Agent SDK client for agent interactions
        self.agent_sdk_client = None

        # Upload skills once at startup
        self.skills = self._upload_skills()

    def _upload_skills(self):
        """Upload skills via direct API"""
        skill_ids = []

        for skill_dir in [".claude/skills/document-skills-docx"]:
            skill_id = self.anthropic_client.skills.create(
                name=skill_name,
                files={"SKILL.md": read_file(f"{skill_dir}/SKILL.md")}
            )
            skill_ids.append(skill_id)

        return skill_ids

    async def process_message(self, user_message, room_id, context):
        """Process message with hybrid approach"""

        # Option C1: Use SDK for everything except final API call
        # Build context using SDK
        sdk_options = ClaudeAgentOptions(
            system_prompt=self.bot_config.system_prompt,
            mcp_servers=mcp_servers,
            setting_sources=["project"],
            ...
        )

        # But make final API call directly to include skills
        messages = self._build_messages_from_context(context)

        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            skills=self.skills,  # ← Skills from direct API
            tools=self._extract_mcp_tools(mcp_servers),  # Convert SDK MCPs
            messages=messages,
            max_tokens=4096
        )

        return response
```

**The Problem with Option C:**

**MCP Servers Don't Work with Direct API!**
- Agent SDK MCPs run as subprocesses managed by CLI
- Direct Messages API can't access these MCP server subprocesses
- Would need to convert MCPs to native tools (major refactoring)

**Complexity:**
```
Agent SDK                     Direct Messages API
    ↓                              ↓
MCP subprocess              Need MCP as native tools
(stdio transport)           (function definitions)
    ↓                              ↓
❌ Incompatible - can't share MCP servers between them
```

**Verdict:** ❌ Not feasible - MCP architecture incompatibility

---

### Option D: Wait for SDK Update (Future)

**Scenario:** Anthropic adds skills support to Agent SDK in v0.2.0+

**Hypothetical API:**
```python
options = ClaudeAgentOptions(
    skills=["docx", "xlsx"],  # ← Future parameter
    mcp_servers=mcp_servers,
    ...
)
```

**Pros:**
- ✅ Would get both SDK benefits AND skills
- ✅ Official support and documentation
- ✅ Optimized integration

**Cons:**
- ❌ Unknown timeline (may never happen)
- ❌ No work gets done while waiting
- ❌ Requires SDK update + our code update

**Verdict:** ⏳ Monitor for updates but don't wait

---

## Detailed Comparison

| Aspect | Pure Direct API | SDK + Manual Skills | True Hybrid | Wait for SDK |
|--------|----------------|---------------------|-------------|--------------|
| **Skills Support** | ✅ Full | ⚠️ Manual | ✅ Full | ✅ Full |
| **Token Optimization** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| **SDK Features** | ❌ Lost | ✅ Keep | ⚠️ Partial | ✅ Keep |
| **MCP Servers** | ❌ Lost | ✅ Work | ❌ Incompatible | ✅ Work |
| **Session Management** | ⚠️ Manual | ✅ SDK | ⚠️ Manual | ✅ SDK |
| **Complexity** | Low | Low | **High** | Low |
| **Timeline** | Now | Now | Now | Unknown |
| **Maintenance** | Medium | Medium | High | Low |

---

## Why True Hybrid Doesn't Work

### The MCP Incompatibility Problem

**Agent SDK Architecture:**
```
ClaudeSDKClient
    ↓
Spawns Claude CLI subprocess
    ↓
CLI manages MCP server subprocesses
    ↓
MCPs communicate via stdio/JSON-RPC
```

**Direct Messages API Architecture:**
```
anthropic.messages.create()
    ↓
Direct HTTP request to Claude API
    ↓
Tools must be native function definitions
    ↓
No subprocess management
```

**The Conflict:**
- Agent SDK MCPs = Live subprocesses managed by CLI
- Direct API tools = Static function definitions in API request
- **Cannot share between them** - fundamentally different architectures

### What Would Be Required for True Hybrid

1. **Extract MCP tools as native functions:**
   ```python
   # Current (SDK):
   mcp_servers = {"campfire": {...}}  # MCP subprocess

   # Would need (Direct API):
   tools = [
       {
           "name": "search_conversations",
           "description": "...",
           "input_schema": {...},
           "function": async def search_conversations(...):  # Actual implementation
               ...
       }
   ]
   ```

2. **Rebuild all MCP functionality:**
   - Reimplement 9 MCP tools as native functions
   - Lose MCP benefits (external servers, stdio transport)
   - Massive refactoring effort

3. **Manage sessions manually:**
   - Track conversation state
   - Implement resume logic
   - Handle context compaction

**Estimated Effort:** 2-3 weeks of development

**Conclusion:** Not worth it for skills support alone

---

## Recommended Approach: Option B (SDK + Manual Skills)

### Implementation Plan

**Step 1: Extract Essential Skill Content**

```python
# scripts/extract_skill_content.py

def extract_docx_skill():
    """Extract key workflows from docx SKILL.md"""
    return """
## Word文档处理专家级工作流程

### 创建新Word文档
使用docx-js库：
1. 必须先阅读docx-js.md文件（~500行）
2. 使用Document, Paragraph, TextRun组件
3. 代码结构示例：
   const { Document, Paragraph, TextRun } = require('docx');
   const doc = new Document({...});

### 编辑现有Word文档
使用Document库（Python OOXML）：
1. 必须先阅读ooxml.md文件（~600行）
2. 工作流：unpack → 修改XML → pack
3. 跟踪修改工作流（适用于法律、商业文档）

... [继续关键工作流程]
"""
```

**Step 2: Add to Bot System Prompts**

```python
# bots/personal_assistant.json

{
  "system_prompt": """
你是一个专业的个人助手AI，名叫「个人助手」。

你的专业能力：
1-5. [现有能力...]
6. 文档处理 - 分析和处理Word文档(.docx文件)

--- BEGIN DOCUMENT SKILLS ---

{extract_docx_skill()}

--- END DOCUMENT SKILLS ---

当用户请求文档处理时，严格遵循上述工作流程。
  """
}
```

**Step 3: Measure Token Impact**

```python
# Test token usage before/after
before = count_tokens(original_system_prompt)
after = count_tokens(system_prompt_with_skills)

print(f"Token increase: {before} → {after} (+{(after-before)/before*100:.1f}%)")
# Expected: ~2,500 → ~5,000 tokens (+100%)
```

**Step 4: Monitor and Optimize**

```python
# Track actual performance
- Response quality (does bot follow skill workflows?)
- Token usage per request
- Cost impact ($15/month → $30/month estimate)
```

---

## Cost-Benefit Analysis

### Option B (SDK + Manual Skills) Costs

**Token Usage:**
- Current: ~2,500 tokens/request
- With skills: ~5,000 tokens/request (+100%)

**Cost Impact:**
- Input tokens: $3 per million
- Current: ~2.5K × 1,000 requests = 2.5M tokens = $7.50/month
- With skills: ~5K × 1,000 requests = 5M tokens = $15/month
- **Increase: +$7.50/month**

**Benefits:**
- Expert-level document processing workflows
- Consistent, high-quality responses
- No refactoring required
- Keeps all SDK benefits

**ROI:** Worth it if document processing is valuable feature

---

## Future Migration Path

**When SDK adds skills support (hypothetical v0.2.0):**

```python
# Current (Option B):
system_prompt = base_prompt + extract_skill_content()

# Future (with SDK skills support):
options = ClaudeAgentOptions(
    system_prompt=base_prompt,  # Back to lean prompt
    skills=["docx", "xlsx"],     # Use SDK skills parameter
    ...
)
```

**Migration Effort:** Low (just remove skill content from prompts)

---

## Final Recommendation

**Use Option B: Agent SDK + Manual Skill Content**

**Why:**
1. ✅ Simplest to implement (text concatenation)
2. ✅ Keeps all SDK benefits (sessions, MCPs, hooks)
3. ✅ Gets skill expertise (even without progressive disclosure)
4. ✅ Acceptable cost increase (+$7.50/month)
5. ✅ Easy to migrate when SDK adds skills support

**When to consider alternatives:**
- If token costs become prohibitive → Optimize skill content
- If skills grow too large → Split into multiple prompts per bot
- If SDK adds skills support → Migrate to native skills
- If we need many skills → Consider custom MCP approach

**Next Steps:**
1. Extract docx skill essentials (~200 lines)
2. Add to personal_assistant.json
3. Test with real Word document requests
4. Measure token usage and response quality
5. Iterate on skill content based on results

---

**This approach balances pragmatism (works now) with future-proofing (easy to migrate).**
