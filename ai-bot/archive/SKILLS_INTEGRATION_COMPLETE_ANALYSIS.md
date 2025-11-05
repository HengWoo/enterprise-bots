# Skills Integration: Complete Analysis & Recommendations

**Date:** 2025-10-18
**Status:** Investigation Complete
**Purpose:** Comprehensive comparison of all skills integration approaches

---

## Executive Summary

After thorough investigation, we've identified **FOUR viable approaches** to skills integration, each with distinct tradeoffs:

| Approach | Works With SDK | Progressive Disclosure | Token Savings | Development Time | Recommendation |
|----------|---------------|----------------------|---------------|------------------|----------------|
| **A. Direct Messages API** | ❌ No | ✅ Yes | ✅ Best | 2-3 weeks | ❌ Loses too much |
| **B. Manual Skill Content** | ✅ Yes | ❌ No | ❌ Worst | 2-3 hours | ⚠️ Quick MVP |
| **C. Custom Skills MCP** | ✅ Yes | ✅ Yes | ✅ Good | 1 week | ✅ **RECOMMENDED** |
| **D. Wait for SDK Update** | ✅ Yes | ✅ Yes | ✅ Best | Unknown | ⏳ Monitor |

**Final Recommendation:** **Option C - Custom Skills MCP**

---

## The Four Approaches in Detail

### Option A: Direct Messages API (Skills API)

**How It Works:**
```python
# Upload skills via API
client = anthropic.Anthropic(api_key=API_KEY)
skill_id = client.skills.create(name="docx", files={"SKILL.md": content})

# Use in Messages API
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    skills=[skill_id],  # Skills API support
    messages=[...]
)
```

**Pros:**
- ✅ Official Skills API support
- ✅ Full progressive disclosure (3 levels)
- ✅ Token optimization (60-80% reduction)
- ✅ Cloud-managed skills (versioning, updates)

**Cons:**
- ❌ **Loses Agent SDK completely**
  - No stateful session management
  - No MCP servers (9 tools lost)
  - No hooks/permissions system
  - No subagents
- ❌ Must rebuild session persistence
- ❌ 2-3 weeks development time
- ❌ High maintenance burden

**Verdict:** ❌ **Not Worth It** - Losing SDK benefits is too costly

---

### Option B: Manual Skill Content in System Prompts

**How It Works:**
```python
# Extract skill content
docx_skill = read_file(".claude/skills/document-skills-docx/SKILL.md")

# Inject into system prompt
system_prompt = f"""
你是一个专业的个人助手AI...

--- BEGIN DOCX SKILL ---
{docx_skill}  # 2,000 tokens
--- END DOCX SKILL ---

--- BEGIN XLSX SKILL ---
{xlsx_skill}  # 2,500 tokens
--- END XLSX SKILL ---
"""

# Use with Agent SDK (no other changes)
options = ClaudeAgentOptions(system_prompt=system_prompt, ...)
```

**Pros:**
- ✅ Simple implementation (2-3 hours)
- ✅ Keeps ALL Agent SDK benefits
- ✅ Works with current SDK version
- ✅ Gets skill expertise immediately

**Cons:**
- ❌ No progressive disclosure (ALL skills loaded upfront)
- ❌ High token usage (+100% increase)
- ❌ Cost: +$7.50/month → **$22.50/month with 3 skills**
- ❌ Doesn't scale (10 skills = 25,000 tokens!)

**Token Usage:**
```
Base prompt: 2,500 tokens
+ docx skill: 2,000 tokens
+ xlsx skill: 2,500 tokens
+ pptx skill: 2,000 tokens
----------------------------
Total: 9,000 tokens/request (always)
```

**Verdict:** ⚠️ **Good for MVP** - Quick start, but doesn't scale

---

### Option C: Custom Skills MCP (Progressive Disclosure via MCP Tools) ✅

**How It Works:**
```python
# Create Custom Skills MCP server
@server.call_tool()
async def load_skill(arguments: dict) -> list[TextContent]:
    """Load skill content on-demand"""
    skill_name = arguments["skill_name"]  # e.g., "docx"
    skill_path = f".claude/skills/document-skills-{skill_name}/SKILL.md"
    content = read_file(skill_path)
    return [TextContent(type="text", text=content)]

# Add to Agent SDK mcp_servers
mcp_servers = {
    "campfire": campfire_mcp_server,
    "fin-report-agent": {...},
    "skills": {  # NEW: Custom Skills MCP
        "transport": "stdio",
        "command": "uv",
        "args": ["run", "--directory", "/app/skills-mcp", "python", "server.py"]
    }
}

# Update system prompt
system_prompt = """
你是一个专业的个人助手AI...

当需要处理特定文档时，使用 load_skill 工具：
- Word文档: load_skill(skill_name="docx")
- Excel文档: load_skill(skill_name="xlsx")

只在实际需要时加载技能。
"""

# Agent loads skills on-demand via MCP tool calls
```

**Pros:**
- ✅ **Progressive Disclosure** - Loads only needed skills
- ✅ **Works with Agent SDK** - Uses MCP architecture
- ✅ **Token Optimization** - 63% savings vs. manual
- ✅ **Keeps SDK Benefits** - Sessions, hooks, MCPs, permissions
- ✅ **Scalable** - Add unlimited skills without token explosion
- ✅ **Maintainable** - Skills in .claude/skills/ directory

**Cons:**
- ❌ 1 week development time
- ❌ Extra tool call latency (+2-3 seconds)
- ❌ Requires custom MCP server maintenance

**Token Usage (Progressive):**
```
No skill needed (70% of requests):
  Base prompt: 2,700 tokens
  Total: 2,700 tokens

One skill needed (25% of requests):
  Base prompt: 2,700 tokens
  + load_skill("docx"): 2,000 tokens
  Total: 4,700 tokens

Multiple skills (5% of requests):
  Base prompt: 2,700 tokens
  + load_skill("docx"): 2,000 tokens
  + load_skill("xlsx"): 2,500 tokens
  Total: 7,200 tokens

Average: 3,350 tokens (63% savings vs. manual!)
```

**Cost Analysis:**
```
Manual Approach:
  9,000 tokens × 1,000 requests = 9M tokens
  Cost: $27/month (input only)

Custom Skills MCP:
  3,350 tokens × 1,000 requests = 3.35M tokens
  Cost: $10.05/month (input only)

Savings: $16.95/month (63% reduction)
```

**Verdict:** ✅ **RECOMMENDED** - Best balance of benefits

---

### Option D: Wait for Agent SDK Update

**Hypothetical Future API:**
```python
# If SDK adds skills parameter in v0.2.0+
options = ClaudeAgentOptions(
    skills=["docx", "xlsx"],  # ← Future parameter
    mcp_servers=mcp_servers,
    ...
)
```

**Pros:**
- ✅ Official SDK support
- ✅ Progressive disclosure
- ✅ Zero custom development
- ✅ Keeps all SDK benefits

**Cons:**
- ❌ Unknown timeline (may never happen)
- ❌ No work gets done while waiting
- ❌ Requires SDK v0.2.0+ when released

**Verdict:** ⏳ **Monitor but Don't Wait** - Can migrate later

---

## Detailed Comparison: Manual vs. Custom MCP

### Scenario 1: User Asks About Word Documents

**User Message:** "请帮我创建一个商业提案Word文档"

**Option B (Manual Skills):**
```
Request:
  System prompt: 9,000 tokens (includes ALL skills)
  User message: 50 tokens
  Total: 9,050 tokens

Response:
  Uses docx skill knowledge (was already loaded)

Cost: $0.027 (input only)
```

**Option C (Custom MCP):**
```
Request 1 (Initial):
  System prompt: 2,700 tokens
  User message: 50 tokens
  Total: 2,750 tokens

Agent Decision: "Need docx skill" → load_skill(skill_name="docx")

Request 2 (With Skill):
  Previous context: 2,750 tokens
  load_skill response: 2,000 tokens
  Total: 4,750 tokens

Response:
  Uses docx skill knowledge (loaded on-demand)

Cost: $0.014 (input only)

Savings: $0.013 per request (48% cheaper!)
```

---

### Scenario 2: User Asks General Question

**User Message:** "今天天气怎么样？"

**Option B (Manual Skills):**
```
Request:
  System prompt: 9,000 tokens (includes ALL skills - WASTED!)
  User message: 20 tokens
  Total: 9,020 tokens

Response:
  Answers without using any skill knowledge

Cost: $0.027 (input only)
```

**Option C (Custom MCP):**
```
Request:
  System prompt: 2,700 tokens
  User message: 20 tokens
  Total: 2,720 tokens

Agent Decision: "No skill needed" → Answers directly

Response:
  Answers without loading any skills

Cost: $0.008 (input only)

Savings: $0.019 per request (70% cheaper!)
```

---

### Scenario 3: Complex Multi-Skill Request

**User Message:** "分析这个Excel报表并生成Word总结报告"

**Option B (Manual Skills):**
```
Request:
  System prompt: 9,000 tokens (ALL skills)
  User message: 100 tokens
  Total: 9,100 tokens

Response:
  Uses docx + xlsx skill knowledge (both were loaded)

Cost: $0.027 (input only)
```

**Option C (Custom MCP):**
```
Request 1:
  System prompt: 2,700 tokens
  User message: 100 tokens
  Total: 2,800 tokens

Agent Decision: "Need xlsx and docx skills"

Request 2 (Load xlsx):
  Previous: 2,800 tokens
  load_skill("xlsx"): 2,500 tokens
  Total: 5,300 tokens

Request 3 (Load docx):
  Previous: 5,300 tokens
  load_skill("docx"): 2,000 tokens
  Total: 7,300 tokens

Response:
  Uses both skills (loaded on-demand)

Cost: $0.022 (input only)

Savings: $0.005 per request (19% cheaper)
Note: Less savings here because we needed both skills
```

---

## Why Custom MCP Works Better Than Manual

### 1. Token Efficiency

**Manual:** ALWAYS pays for all skills
```python
# Every request includes:
- Base prompt: 2,500 tokens
- docx skill: 2,000 tokens (even if not needed)
- xlsx skill: 2,500 tokens (even if not needed)
- pptx skill: 2,000 tokens (even if not needed)
= 9,000 tokens (100% of requests)
```

**Custom MCP:** Pays only for what's needed
```python
# Distribution of requests:
- 70% need no skill: 2,700 tokens
- 25% need 1 skill: 4,700 tokens
- 5% need 2+ skills: 7,200 tokens
= Average: 3,350 tokens (63% savings!)
```

---

### 2. Cognitive Load

**Manual:** Agent sees ALL content upfront
```
Agent receives:
- Base instructions: 500 words
- docx skill: 1,000 words
- xlsx skill: 1,200 words
- pptx skill: 900 words
= 3,600 words to process (cognitive overload)

Risk: May confuse skills or reference wrong information
```

**Custom MCP:** Agent learns as needed
```
Agent receives:
- Base instructions: 500 words
- Skill loading guidance: 100 words
= 600 words to process initially

When docx needed:
- Receives docx skill: 1,000 words
- Focused attention on relevant content
= Better accuracy
```

---

### 3. Scalability

**Manual:** Doesn't scale beyond 5 skills
```python
# With 10 skills
system_prompt = (
    base_prompt +
    docx_skill + xlsx_skill + pptx_skill +
    pdf_skill + image_skill + video_skill +
    audio_skill + code_skill + data_skill + web_skill
)
# = ~25,000 tokens (approaching context limits!)
```

**Custom MCP:** Scales to unlimited skills
```python
# With 10 skills
system_prompt = """
使用 load_skill 工具加载以下技能之一：
docx, xlsx, pptx, pdf, image, video, audio, code, data, web
"""
# = 2,700 tokens (same as before!)

# Agent loads only what's needed
```

---

### 4. Maintenance

**Manual:** Update requires changing system prompts
```python
# Skill content changes
# Must update:
1. Extract new content from .claude/skills/
2. Update bots/personal_assistant.json
3. Update bots/financial_analyst.json
4. Update bots/technical_assistant.json
5. Rebuild Docker image
6. Redeploy to production
```

**Custom MCP:** Update requires changing skill files only
```python
# Skill content changes
# Just update:
1. Edit .claude/skills/document-skills-docx/SKILL.md
2. Restart MCP server (automatic in Docker)
# System prompts unchanged
# No Docker rebuild needed
```

---

## Why NOT Direct Messages API?

### MCP Architecture Incompatibility

**The Fundamental Problem:**

Agent SDK MCPs run as **live subprocesses** with stdin/stdout communication:
```python
# Agent SDK Architecture
ClaudeSDKClient
    ↓ spawns
Claude CLI subprocess (Rust binary)
    ↓ manages via stdin/stdout pipes
MCP Server subprocesses (Python/Node)
    ↓ tools execute in subprocess
Results via stdout → CLI → SDK → Your code
```

Direct Messages API expects **static tool schemas** with HTTP communication:
```python
# Direct API Architecture
Your Python Code
    ↓ HTTP POST
Anthropic Cloud API
    ↓ returns tool_use
Your Python Code (YOU execute tool)
    ↓ HTTP POST result
Anthropic Cloud API
```

**Cannot Mix Them:**
- SDK MCPs are processes on your machine with pipes
- Direct API is cloud-based with HTTP requests
- No way to share MCP server subprocesses between them

**To Use Direct API + Skills:**
- Would lose all 9 MCP tools (conversations, context, knowledge base, briefing, financial)
- Must reimplement as native Python functions
- 2-3 weeks development effort
- High ongoing maintenance

**Not Worth It:** Skills benefit doesn't justify losing SDK benefits

---

## Implementation Roadmap

### Recommended: Custom Skills MCP (Option C)

**Phase 1: Prototype (Week 1)**

**Day 1-2: Basic MCP Server**
```python
# skills-mcp/server.py
@server.call_tool()
async def load_skill(arguments: dict):
    """Load SKILL.md content"""
    skill_name = arguments["skill_name"]
    content = read_skill_md(skill_name)
    return [TextContent(type="text", text=content)]
```

**Day 3-4: Integration**
```python
# src/campfire_agent.py
mcp_servers["skills"] = {
    "transport": "stdio",
    "command": "uv",
    "args": ["run", "--directory", "/app/skills-mcp", "python", "server.py"]
}
```

**Day 5: Testing**
- Test with docx skill
- Verify token usage
- Measure latency

**Deliverable:** Working prototype with docx skill

---

**Phase 2: Full Implementation (Week 2)**

**Day 1-2: Advanced Features**
```python
@server.call_tool()
async def list_skills():
    """List all available skills"""
    ...

@server.call_tool()
async def load_skill_file(arguments: dict):
    """Load additional skill files (3rd level)"""
    ...
```

**Day 3-4: All Skills**
- Add xlsx skill
- Add pptx skill
- Test all 3 skills

**Day 5: System Prompts**
- Update all 4 bot configs
- Add skill loading guidance
- Test multi-bot scenario

**Deliverable:** Complete Custom Skills MCP

---

**Phase 3: Production (Week 3)**

**Day 1-2: Docker Integration**
```dockerfile
# Dockerfile
COPY skills-mcp/ /app/skills-mcp/
RUN cd /app/skills-mcp && uv sync
```

**Day 3: Testing**
- Local testing with full workflow
- Performance testing
- Token usage validation

**Day 4: Deployment**
```bash
docker build -t hengwoo/campfire-ai-bot:0.3.0 .
docker push hengwoo/campfire-ai-bot:0.3.0
# Deploy to production
```

**Day 5: Monitoring**
- Verify skills loading correctly
- Monitor token usage
- Collect user feedback

**Deliverable:** Production deployment

---

**Phase 4: Optimization (Week 4)**

**Metrics Collection:**
- Skill usage frequency (which skills loaded most)
- Token savings actual vs. estimated
- Response latency vs. manual approach
- User satisfaction

**Optimizations:**
- Cache frequently loaded skills
- Pre-warm popular skills
- Optimize SKILL.md content
- Add skill usage analytics

**Deliverable:** Optimized production system

---

## Success Metrics

### Token Usage Goals

| Metric | Manual Approach | Custom MCP Target | Result |
|--------|----------------|-------------------|--------|
| **No Skill Needed** | 9,000 tokens | 2,700 tokens | ✅ 70% reduction |
| **One Skill** | 9,000 tokens | 4,700 tokens | ✅ 48% reduction |
| **Multiple Skills** | 9,000 tokens | 7,200 tokens | ✅ 20% reduction |
| **Average** | 9,000 tokens | 3,350 tokens | ✅ 63% reduction |

### Cost Goals

| Period | Manual Approach | Custom MCP Target | Savings |
|--------|----------------|-------------------|---------|
| **Per Request** | $0.027 | $0.010 | $0.017 |
| **1,000 Requests** | $27 | $10 | $17 |
| **Monthly (Estimate)** | $27 | $10 | $17/month |

### Quality Goals

1. **Skill Loading Accuracy:** Agent loads correct skill 95%+ of time
2. **Response Quality:** Same as manual approach (no regression)
3. **Workflow Adherence:** Agent follows skill workflows correctly
4. **No Hallucinations:** Agent doesn't guess without loading skill

### Performance Goals

1. **load_skill Latency:** < 3 seconds per call
2. **Total Response Time:** < 18 seconds (vs. 15s manual, +3s acceptable)
3. **MCP Server Uptime:** 99.9%

---

## Risk Assessment

### Risk Matrix

| Risk | Probability | Impact | Mitigation | Severity |
|------|-----------|--------|------------|----------|
| **Agent forgets to load skill** | Medium | High | Strong system prompt guidance | 🔴 High |
| **MCP server crashes** | Low | Medium | Fallback to base knowledge | 🟡 Medium |
| **Extra latency unacceptable** | Low | Medium | Cache loaded skills | 🟡 Medium |
| **Token savings don't materialize** | Low | High | Measure and optimize | 🟡 Medium |
| **Development takes longer** | Medium | Low | Start with prototype | 🟢 Low |

### Mitigation Strategies

**Risk 1: Agent Forgets to Load Skill**

**Mitigation:**
```python
system_prompt = """
## CRITICAL RULE: Skill Loading

BEFORE answering any document processing question:
1. Check: Do I have the required skill loaded?
2. If NO: MUST call load_skill first
3. If YES: Use skill knowledge to answer

Examples:
❌ WRONG: User asks "创建Word文档" → You guess the steps
✅ RIGHT: User asks "创建Word文档" → load_skill("docx") → Follow skill workflows
"""
```

**Risk 2: MCP Server Crashes**

**Mitigation:**
```python
# Fallback handler
try:
    skill_content = await load_skill("docx")
except Exception as e:
    logger.error(f"Skills MCP failed: {e}")
    # Fallback to base knowledge (without skill expertise)
    return "I can help, but I don't have access to my specialized document processing workflows right now."
```

---

## Final Recommendation

### Use Custom Skills MCP (Option C) ✅

**Reasons:**

1. **Best Balance:**
   - ✅ Works with Agent SDK (keeps all benefits)
   - ✅ Progressive disclosure (63% token savings)
   - ✅ Scalable (add unlimited skills)
   - ✅ Maintainable (skills in .claude/skills/)

2. **Acceptable Tradeoffs:**
   - ⚠️ 1 week development (vs. 2-3 hours manual)
   - ⚠️ +2-3s latency per skill load
   - ⚠️ Custom MCP maintenance

3. **Future-Proof:**
   - Can migrate to SDK skills API when available
   - Architecture matches Skills API pattern
   - Easy to add new skills

4. **ROI:**
   - Development: 1 week
   - Savings: $17/month
   - Break-even: ~1.5 months
   - Long-term value: High (scales to 10+ skills)

---

## Alternative: Start with Manual (Option B), Migrate Later

**If Time-Constrained:**

**Week 1:** Deploy Manual Skills (Option B)
- 2-3 hours implementation
- Get skills working immediately
- Accept higher token cost temporarily

**Week 2-4:** Build Custom Skills MCP (Option C)
- Develop in parallel
- Test thoroughly
- Measure actual token usage

**Week 5:** Migration
- Deploy Custom Skills MCP
- Remove manual skill content
- Monitor and optimize

**Benefit:** Get skills working NOW, optimize later

---

## Conclusion

After comprehensive investigation, we've answered both your questions:

### Question 1: Why are MCPs and Direct API incompatible?

**Answer:** MCP servers are **live subprocess processes** with stdin/stdout communication (local), while Direct Messages API expects **static tool schemas** with HTTP communication (cloud). They use fundamentally different architectures and cannot share tool implementations.

**Evidence:** See `MCP_INCOMPATIBILITY_EXAMPLES.md` for detailed code examples.

---

### Question 2: Can we build skills as MCP tools?

**Answer:** ✅ **YES!** This is the Custom Skills MCP approach (Option C).

**How:** Create an MCP server that exposes `load_skill` and `load_skill_file` tools, enabling progressive disclosure within Agent SDK architecture.

**Benefits:**
- ✅ 63% token savings vs. manual approach
- ✅ Works with Agent SDK (keeps all benefits)
- ✅ Scales to unlimited skills
- ✅ Better than Direct API approach (doesn't lose SDK)

**Evidence:** See `CUSTOM_SKILLS_MCP_DESIGN.md` for complete implementation design.

---

**Your insight was correct:** Skills are just tools, and we CAN build them as MCP tools to get progressive disclosure while keeping Agent SDK benefits.

**Next Step:** Implement Custom Skills MCP (1 week development, 63% token savings, scalable to 10+ skills).
