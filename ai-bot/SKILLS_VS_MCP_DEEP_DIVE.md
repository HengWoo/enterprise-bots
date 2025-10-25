# Skills vs MCP: Deep Technical Comparison

**Date:** 2025-10-18
**Purpose:** Explain in detail why MCPs work via Agent SDK but Skills don't

---

## Part 1: How MCPs Work via Agent SDK

### MCP Architecture (What We Successfully Use)

```
┌─────────────────────────────────────────────────────────┐
│  Python Code (src/campfire_agent.py)                    │
│                                                          │
│  mcp_servers = {                                        │
│      "campfire": campfire_mcp_server,  # SDK MCP       │
│      "fin-report-agent": {             # External MCP   │
│          "transport": "stdio",                          │
│          "command": "uv",                               │
│          "args": ["run", "python", "run_mcp_server.py"] │
│      }                                                   │
│  }                                                       │
│                                                          │
│  options = ClaudeAgentOptions(                          │
│      mcp_servers=mcp_servers,  ← EXPLICIT PARAMETER    │
│      ...                                                 │
│  )                                                       │
│                                                          │
│  client = ClaudeSDKClient(options=options)              │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  Claude Agent SDK (claude_agent_sdk)                    │
│                                                          │
│  1. Receives mcp_servers configuration                  │
│  2. Spawns MCP server subprocesses (stdio transport)    │
│  3. Connects to MCP servers via JSON-RPC protocol       │
│  4. Calls server's list_tools() method                  │
│  5. Registers tools in Claude's available tools list    │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  Claude Code CLI Subprocess                             │
│                                                          │
│  Tools Available to Claude:                             │
│  ✅ search_conversations (from campfire MCP)            │
│  ✅ get_user_context (from campfire MCP)                │
│  ✅ save_user_preference (from campfire MCP)            │
│  ✅ get_excel_info (from financial MCP)                 │
│  ✅ analyze_excel (from financial MCP)                  │
│  ... (all MCP tools immediately available)              │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  Claude API Call                                        │
│                                                          │
│  User: "Search for messages about budget"               │
│  System: [List of available tools including             │
│           search_conversations]                          │
│  Claude: I'll use search_conversations tool             │
│  → Tool call happens immediately ✅                     │
└─────────────────────────────────────────────────────────┘
```

**Key Point:** MCPs are **EXPLICITLY REGISTERED** via the `mcp_servers` parameter. The SDK knows about them before the conversation even starts.

---

## Part 2: How Skills Work in Interactive CLI

### Interactive CLI Skill Architecture (What Doesn't Work via SDK)

```
┌─────────────────────────────────────────────────────────┐
│  User Types Command in Terminal                         │
│                                                          │
│  $ claude                                               │
│  > I need to create a Word document                     │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  Claude Code CLI (Interactive Mode)                     │
│                                                          │
│  1. Reads ~/.claude/settings.json:                      │
│     {                                                    │
│       "enabledPlugins": {                               │
│         "document-skills@anthropic-agent-skills": true  │
│       }                                                  │
│     }                                                    │
│                                                          │
│  2. Discovers plugin at:                                │
│     ~/.claude/plugins/marketplaces/                     │
│       anthropic-agent-skills/document-skills/           │
│                                                          │
│  3. Reads plugin's marketplace.json:                    │
│     {                                                    │
│       "plugins": [{                                     │
│         "name": "document-skills",                      │
│         "skills": [                                     │
│           "./document-skills/docx",                     │
│           "./document-skills/xlsx",                     │
│           ...                                           │
│         ]                                               │
│       }]                                                │
│     }                                                    │
│                                                          │
│  4. CREATES "Skill" TOOL dynamically:                   │
│     function: Skill(skill_name: string)                 │
│     description: "Load a skill's content on-demand"     │
│                                                          │
│  5. Registers Skill tool with Claude API                │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  Claude API Call (Interactive Session)                  │
│                                                          │
│  User: "I need to create a Word document"               │
│  System: [Available tools include: ..., Skill]          │
│                                                          │
│  Claude thinks: "I need docx expertise"                 │
│  Claude: <tool_use name="Skill">                        │
│            <skill_name>docx</skill_name>                │
│          </tool_use>                                     │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  Skill Tool Execution (CLI-Side)                        │
│                                                          │
│  1. Receives skill_name = "docx"                        │
│  2. Locates skill directory:                            │
│     ~/.claude/plugins/.../document-skills/docx/         │
│  3. Reads SKILL.md file (~10KB):                        │
│     ---                                                  │
│     name: docx                                          │
│     description: "Comprehensive document creation..."   │
│     ---                                                  │
│     # DOCX creation, editing, and analysis              │
│     ## Creating a new Word document                     │
│     - Read docx-js.md (~500 lines)                      │
│     - Use Document, Paragraph, TextRun components       │
│     ...                                                  │
│  4. Injects entire SKILL.md content into context        │
│  5. Returns to Claude: "Skill loaded successfully"      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  Claude API Call (Turn 2 - With Skill Content)         │
│                                                          │
│  System: [Now includes SKILL.md content in context]     │
│  Claude: "Based on the docx skill workflow, I'll        │
│           first read docx-js.md for syntax rules..."    │
│                                                          │
│  → Claude has FULL skill knowledge ✅                   │
│  → References specific workflows from SKILL.md          │
└─────────────────────────────────────────────────────────┘
```

**Key Point:** Skills are **LAZILY LOADED** via a special "Skill" tool. The tool reads and injects skill content only when needed (progressive disclosure).

---

## Part 3: What Happens via Agent SDK

### Agent SDK Skill Attempt (What We Tried)

```
┌─────────────────────────────────────────────────────────┐
│  Python Code (src/campfire_agent.py)                    │
│                                                          │
│  options = ClaudeAgentOptions(                          │
│      setting_sources=["project"],  # ← Enable skills   │
│      cwd="/path/to/project",       # ← .claude/ here   │
│      ...                                                 │
│  )                                                       │
│                                                          │
│  client = ClaudeSDKClient(options=options)              │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  Claude Agent SDK                                       │
│                                                          │
│  1. Spawns Claude CLI subprocess with:                  │
│     --cwd /path/to/project                              │
│     (other SDK parameters...)                           │
│                                                          │
│  2. CLI subprocess starts up...                         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  Claude CLI Subprocess (Non-Interactive Mode)           │
│                                                          │
│  1. ✅ Reads project/.claude/settings.json:             │
│     {                                                    │
│       "enabledPlugins": {                               │
│         "document-skills@...": true                     │
│       }                                                  │
│     }                                                    │
│                                                          │
│  2. ✅ Discovers plugin at marketplace location         │
│                                                          │
│  3. ✅ Loads plugin configuration                       │
│                                                          │
│  4. ❌ BUT: Does NOT create "Skill" tool               │
│     Why? Non-interactive mode doesn't expose            │
│     interactive-only tools to SDK API                   │
│                                                          │
│  5. ❌ Result: Plugin enabled, but no way to            │
│              load skill content                         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  Claude API Call (via SDK)                              │
│                                                          │
│  User: "I need to create a Word document"               │
│  System: [Available tools: search_conversations,        │
│           get_user_context, ... NO SKILL TOOL ❌]       │
│                                                          │
│  Claude thinks: "I should help create a Word document"  │
│  Claude: "I can help you create a Word document..."     │
│          (Generic response - no skill content)          │
│                                                          │
│  → Claude does NOT reference SKILL.md content           │
│  → No mention of docx-js, pandoc, OOXML workflows       │
└─────────────────────────────────────────────────────────┘
```

**Key Point:** Plugin system works (settings read, plugins discovered), but the **Skill tool is not available** in SDK mode, so skill content never gets loaded.

---

## Part 4: Evidence from Our Testing

### Test 1: Before .claude/settings.json

**Setup:**
- No settings.json in project
- Plugin NOT enabled

**Request:**
```json
{
  "content": "I need to create a Word document (.docx) for a business proposal."
}
```

**Bot Response:**
```
抱歉，我目前无法直接创建Word文档(.docx文件)。

However, I can help you in other ways:
- Draft the proposal content in text format
- Provide structure and outline suggestions
- Help with content organization
...
```

**Analysis:** Bot explicitly says it CANNOT create Word documents.

---

### Test 2: After .claude/settings.json (Plugin Enabled)

**Setup:**
- Created `.claude/settings.json`:
  ```json
  {
    "enabledPlugins": {
      "document-skills@anthropic-agent-skills": true
    }
  }
  ```

**Request:**
```json
{
  "content": "I need to create a Word document (.docx) for a business proposal."
}
```

**Bot Response:**
```
👋 您好！很高兴为您服务！

我看到您需要创建一个商业提案的Word文档（.docx文件）。
我确实可以帮您完成这个任务！

📝 我可以为您提供的服务

作为个人助手，我可以帮您：
- ✅ 创建专业的Word文档 - 包含格式化、标题、段落、表格等
- ✅ 设计文档结构 - 根据商业提案的最佳实践
...
```

**Analysis:**
- ✅ Bot NOW SAYS it CAN create Word documents (behavior change!)
- ❌ But response is GENERIC - no specific workflows mentioned
- ❌ No mention of: docx-js, pandoc, OOXML, Document library, etc.

---

### Test 3: What SHOULD Happen if Skill Loaded

**Expected Response (if skill content was actually loaded):**

```
我可以帮您创建专业的Word文档！

根据文档技能工作流程，我需要：

1️⃣ **创建新文档流程：**
   - 使用 docx-js 库
   - 必须先阅读 docx-js.md 文件（约500行）了解完整语法
   - 使用 Document, Paragraph, TextRun 组件构建

2️⃣ **文档结构：**
   ```javascript
   const { Document, Paragraph, TextRun, Packer } = require('docx');
   const doc = new Document({
     sections: [{
       properties: {},
       children: [
         new Paragraph({
           children: [new TextRun({text: "商业提案", bold: true})]
         })
       ]
     }]
   });
   ```

让我为您创建一个结构化的商业提案文档...
```

**Why This SHOULD Happen:**
- The docx SKILL.md file EXPLICITLY says:
  > "When creating a new Word document from scratch, use **docx-js**"
  > "**MANDATORY - READ ENTIRE FILE**: Read `docx-js.md` (~500 lines)"

**Why This DOESN'T Happen:**
- Skill content (SKILL.md) is NEVER loaded into the conversation
- Bot only knows it's "supposed to help with documents" (from plugin metadata)
- Bot has NO ACCESS to the actual workflows and instructions

---

## Part 5: The "Skill" Tool - Deep Dive

### What is the Skill Tool?

The Skill tool is a **special meta-tool** that exists in interactive Claude Code CLI:

```typescript
// Conceptual representation (not actual code)
interface SkillTool {
  name: "Skill";
  description: "Load a skill's content on-demand for progressive disclosure";

  inputSchema: {
    type: "object",
    properties: {
      skill_name: {
        type: "string",
        description: "Name of skill to load (e.g., 'docx', 'xlsx', 'pdf')",
        enum: ["docx", "xlsx", "pptx", "pdf", ...] // From enabled plugins
      }
    },
    required: ["skill_name"]
  }
}

async function executeSkillTool(skill_name: string): Promise<string> {
  // 1. Locate skill directory
  const skillPath = findSkillPath(skill_name);
  // e.g., ~/.claude/plugins/.../document-skills/docx/

  // 2. Read SKILL.md
  const skillContent = await readFile(`${skillPath}/SKILL.md`);

  // 3. Parse YAML frontmatter
  const { name, description, metadata } = parseYAML(skillContent);

  // 4. Return ENTIRE file content to inject into context
  return skillContent; // ~10KB for docx skill
}
```

### How Claude Decides to Use Skill Tool

Claude is PROMPTED to use the Skill tool when it detects relevant keywords:

```
System: You have access to a Skill tool that can load specialized
        knowledge on-demand. Use it when you need expertise in:
        - Document processing (.docx, .xlsx, .pptx, .pdf files)
        - Specialized workflows (data analysis, web testing, etc.)

        Available skills:
        - docx: Word document creation and editing
        - xlsx: Excel spreadsheet analysis
        - pptx: PowerPoint presentation creation
        - pdf: PDF manipulation and extraction

User: I need to create a Word document

Claude thinks: Keywords detected: "Word document", "create"
               Available skill: "docx" matches this domain
               Decision: Call Skill tool with skill_name="docx"
```

### Why This Tool Isn't Available via SDK

**Interactive CLI Mode:**
```
claude (binary) → Interactive REPL
                → Full tool ecosystem
                → Includes: Skill, Read, Write, Edit, Bash, etc.
                → User-facing features
```

**SDK Subprocess Mode:**
```
claude (binary) → Subprocess for API integration
                → Limited tool ecosystem
                → Only: MCPs + explicitly registered tools
                → Programmatic interface
```

The Skill tool is considered a **user-facing feature**, not part of the programmatic API surface.

**Design Philosophy:**
- Interactive tools (Skill, Read, Write, Edit, Bash) = For human users
- Programmatic tools (MCPs) = For automated systems
- SDK only exposes programmatic interface

---

## Part 6: Why MCPs Work But Skills Don't

### Comparison Table

| Aspect | MCPs | Skills |
|--------|------|--------|
| **Registration** | Explicit via `mcp_servers` parameter | Implicit via plugin system |
| **Availability** | Always available after registration | Only via Skill tool |
| **Tool Discovery** | Direct: SDK calls `list_tools()` | Lazy: Skill tool loads content |
| **Content Loading** | Immediate (at startup) | On-demand (when Skill called) |
| **Token Optimization** | No (all tools always available) | Yes (load only needed skills) |
| **SDK Exposure** | Full (ClaudeAgentOptions parameter) | None (interactive-only) |
| **Configuration** | Code-based (Python dict) | File-based (.claude/settings.json) |
| **Tool Type** | External server (JSON-RPC) | Built-in CLI feature |

### Architecture Diagrams

**MCP Architecture (Works):**
```
SDK Parameter → MCP Server Subprocess → Tools Available Immediately
     ↓                    ↓                        ↓
mcp_servers      stdio transport              list_tools()
(Python dict)    (JSON-RPC)                   (returns tool schemas)
```

**Skill Architecture (Doesn't Work via SDK):**
```
Plugin Config → CLI Reads Settings → Skill Tool Created → Load Content
     ↓                  ↓                    ↓                  ↓
.claude/        enabledPlugins        Interactive only    On-demand
settings.json   recognized            NOT in SDK mode     SKILL.md
```

### Code-Level Comparison

**MCP Registration (src/campfire_agent.py:125-143):**
```python
# EXPLICIT parameter in ClaudeAgentOptions
mcp_servers = {
    "campfire": campfire_mcp_server,  # ← Direct registration
    "fin-report-agent": {
        "transport": "stdio",
        "command": "uv",
        "args": ["run", "python", "run_mcp_server.py"]
    }
}

options = ClaudeAgentOptions(
    mcp_servers=mcp_servers,  # ← PASSED AS PARAMETER
    ...
)
```

**Skill Registration (doesn't exist in SDK):**
```python
# NO skill parameter in ClaudeAgentOptions
options = ClaudeAgentOptions(
    setting_sources=["project"],  # ← Tells CLI to read settings
    # But NO skill_plugins parameter!
    # SDK doesn't have a way to explicitly register skills
    ...
)
```

**What setting_sources Does:**
```python
# setting_sources=["project"] means:
# 1. CLI subprocess will read .claude/settings.json ✅
# 2. CLI will discover enabled plugins ✅
# 3. CLI will load plugin metadata ✅
# 4. BUT: CLI won't create Skill tool in SDK mode ❌
```

---

## Part 7: Proof of Plugin Recognition

### File System Evidence

**Global Plugin Location:**
```bash
$ ls -la ~/.claude/plugins/marketplaces/anthropic-agent-skills/
total 0
drwxr-xr-x@ 20 heng  staff  640 Oct 18 08:08 .
drwxr-xr-x@  3 heng  staff   96 Oct 18 08:08 ..
-rw-r--r--@  1 heng  staff 1234 Oct 18 08:08 .claude-plugin/marketplace.json
drwxr-xr-x@  6 heng  staff  192 Oct 18 08:08 document-skills/
   ├── docx/SKILL.md      (10,150 bytes)
   ├── xlsx/SKILL.md
   ├── pptx/SKILL.md
   └── pdf/SKILL.md
```

**Project Configuration:**
```bash
$ cat .claude/settings.json
{
  "enabledPlugins": {
    "document-skills@anthropic-agent-skills": true
  }
}
```

**SDK Configuration (src/campfire_agent.py:160-174):**
```python
print(f"[Skills] Working directory: {cwd_path}")
print(f"[Skills] setting_sources: {options_dict['setting_sources']}")

# Output from test logs:
# [Skills] Working directory: /Users/heng/Development/campfire/ai-bot
# [Skills] setting_sources: ['project']
```

### Behavioral Evidence

**Test Results Summary:**

| Test | Plugin Config | Bot Says Can Help | References Skill Content |
|------|---------------|-------------------|--------------------------|
| 1 | ❌ No settings.json | ❌ No | ❌ N/A |
| 2 | ✅ Settings enabled | ✅ Yes | ❌ No |
| 3 (expected) | ✅ With Skill tool | ✅ Yes | ✅ Yes |

**Conclusion:**
- Row 1 → 2: Plugin recognition WORKS (behavior changed)
- Row 2 → 3: Skill content loading DOESN'T WORK (no skill references)

---

## Part 8: The Missing Link - Skill Tool in SDK Exports

### SDK Export Analysis

```python
from claude_agent_sdk import *

# All exported classes and functions:
['ClaudeSDKClient', 'ClaudeAgentOptions', 'create_sdk_mcp_server',
 'Message', 'AssistantMessage', 'UserMessage', 'SystemMessage',
 'ToolUseBlock', 'TextBlock', 'ThinkingBlock', 'ToolResultBlock',
 'McpServerConfig', 'Transport', 'PermissionMode', 'SettingSource',
 ...]

# NO "Skill" or skill-related exports
```

### What WOULD Be Needed for SDK Skill Support

**Hypothetical SDK Design (if skills were supported):**

```python
# Option A: Explicit skill parameter
options = ClaudeAgentOptions(
    skills=["docx", "xlsx"],  # ← Explicit skill registration
    ...
)

# Option B: Skill loading API
client = ClaudeSDKClient(options)
client.load_skill("docx")  # ← Load skill content programmatically

# Option C: Skill as MCP
skill_mcp = {
    "transport": "builtin",
    "skill_name": "docx"
}
options = ClaudeAgentOptions(
    mcp_servers={"docx-skill": skill_mcp},
    ...
)
```

**But none of these exist in current SDK (v0.1.4).**

---

## Summary: The Complete Picture

### What We Learned

1. **Plugin System Works:**
   - `.claude/settings.json` is read ✅
   - Plugins are discovered and recognized ✅
   - Bot behavior changes (acknowledges capability) ✅

2. **Skill Content Doesn't Load:**
   - No "Skill" tool in SDK mode ❌
   - SKILL.md content never injected into context ❌
   - Bot can't reference specific workflows ❌

3. **Why This Happens:**
   - Skills designed for interactive CLI (progressive disclosure)
   - Skill tool is interactive-only, not exposed to SDK
   - MCPs work because they're explicitly registered via SDK parameters

4. **Architectural Difference:**
   ```
   MCPs:    Explicit registration → Tools immediately available
   Skills:  Implicit discovery → Requires Skill tool → Not in SDK
   ```

### The Fundamental Issue

**Skills are a UI feature (for interactive use), not an API feature (for programmatic use).**

The Claude Code CLI has two modes:
- **Interactive mode**: Full ecosystem (Skill, Read, Write, Edit, Bash, etc.)
- **Subprocess mode** (SDK): Limited ecosystem (only MCPs + explicit tools)

Skills were designed for interactive use, where:
- User types in natural language
- Claude decides when to load skills
- Skill tool fetches content on-demand
- User sees progressive disclosure benefits

This doesn't map well to programmatic usage via SDK, where:
- Everything should be deterministic
- Tools should be explicitly registered
- No interactive "decisions" about loading
- Predictable token usage preferred

---

## Implications for Our Project

1. **Plugin recognition proves SDK is working correctly**
   - Our configuration is right
   - CLI subprocess is functioning
   - setting_sources parameter works

2. **But skill content won't load without Skill tool**
   - Need alternative approach
   - Can't wait for SDK to add skill support
   - Must implement workaround

3. **Options going forward:**
   - Option 1: Manual skill content in system prompts (simple)
   - Option 2: Hybrid (SDK for normal, CLI for documents)
   - Option 3: Wait for SDK support (unknown timeline)
   - Option 4: Custom MCP (significant effort)

---

**This explains why your logic was correct (plugin system works) but the outcome differs (skill content doesn't load).**
