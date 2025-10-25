# CRITICAL UPDATE: Skills API Discovery

**Date:** 2025-10-18
**Status:** MAJOR NEW FINDING - Skills ARE available via API (different from plugin system!)

---

## 🚨 What We Just Discovered

According to the official Anthropic documentation and web sources:

> **"The new /v1/skills endpoint gives developers programmatic control over custom skill versioning and management, and you can upload your own Skills via the Skills API (/v1/skills endpoints)"**

> **"Developers can add Skills to the Messages API and manage them through a new endpoint called /v1/skills"**

> **"Skills require the Code Execution Tool beta, which provides the secure environment they need to run"**

---

## Three Different Ways to Use Skills

We now understand there are **THREE distinct approaches** to using skills:

### 1. Interactive CLI (Plugin System) - What We Investigated
```
~/.claude/settings.json → Enable plugins → Skill tool loads content
```
- **Works in:** Claude Code CLI (interactive mode)
- **How it works:** Plugin system + Skill tool (progressive disclosure)
- **Our finding:** NOT available via Agent SDK (interactive-only)

### 2. Direct Messages API (Skills API) - What We Just Found! 🎉
```
POST /v1/skills → Upload skill → Reference in Messages API
```
- **Works in:** Direct Claude Messages API calls
- **How it works:** Upload skills via /v1/skills endpoint, reference in messages
- **Status:** This is DIFFERENT from plugin system!

### 3. Agent SDK - Unknown Support
```
ClaudeSDKClient → ??? → Skills support?
```
- **Works in:** Agent SDK (what we use)
- **How it works:** UNCLEAR if SDK supports /v1/skills endpoint
- **Status:** NEEDS INVESTIGATION

---

## Skills API Details (From Search Results)

### API Endpoint
```
/v1/skills
```

### Requirements
- **Code Execution Tool beta** must be enabled
- Skills need secure environment to run

### Limits
- **8 skills maximum** per request
- **8 MB** total upload size for skill bundle
- SKILL.md must be at root with YAML frontmatter

### Skill Structure (Same as Plugin System)
```markdown
---
name: my-skill-name
description: A clear description of what this skill does
---

# Skill content here
```

### Workflow
1. Upload skill via `/v1/skills` endpoint
2. Manage versions via API
3. Reference skills in Messages API calls
4. Skills load with code execution environment

---

## Critical Questions to Answer

### Question 1: Does Agent SDK Support /v1/skills?

**What we know:**
- Agent SDK wraps Claude Code CLI
- Agent SDK has `ClaudeAgentOptions` for configuration
- We haven't seen any `skills` parameter in SDK

**What we need to check:**
- Can we pass skills to Messages API via SDK?
- Does SDK expose /v1/skills management?
- Is there a skills parameter we missed?

### Question 2: Is Skills API Different from Plugin Skills?

**Hypothesis:**
- Plugin skills (local files) = Interactive CLI feature
- API skills (/v1/skills endpoint) = Cloud-based skill management
- These might be TWO DIFFERENT SYSTEMS with similar names!

**Evidence:**
- Plugin skills use `.claude/settings.json` + marketplaces
- API skills use `/v1/skills` endpoint + uploads
- Both use SKILL.md format but different loading mechanisms

### Question 3: How Do We Use Skills with Agent SDK?

**Options:**
1. **If SDK supports /v1/skills:** Use SDK's skill management API
2. **If SDK doesn't support it:** Make direct API calls to /v1/skills alongside SDK
3. **Hybrid approach:** Upload via API, reference in SDK calls

---

## What This Means for Our Project

### If Agent SDK Supports /v1/skills ✅

**Good news:**
- Skills WOULD work programmatically
- Upload skills once, use across all bots
- Get progressive disclosure benefits
- Token optimization works as designed

**Implementation:**
```python
# Upload skill (once)
skill_id = upload_skill_to_api(skill_directory)

# Use in Agent SDK
options = ClaudeAgentOptions(
    skills=[skill_id],  # ← If this parameter exists
    ...
)
```

### If Agent SDK Doesn't Support /v1/skills ❌

**Situation:**
- Skills API exists but SDK doesn't expose it
- Would need direct Messages API calls (bypassing SDK)
- Loses SDK benefits (session management, hooks, etc.)

**Workaround:**
- Stick with Option 1 (manual skill content in system prompts)
- Or use hybrid approach (SDK for most, direct API for skills)

---

## Comparison: Plugin Skills vs API Skills

| Aspect | Plugin Skills | API Skills |
|--------|---------------|------------|
| **Location** | Local files (`~/.claude/plugins/`) | Cloud-uploaded via `/v1/skills` |
| **Discovery** | `.claude/settings.json` enablement | API upload + referencing |
| **Loading** | Skill tool (interactive CLI) | Code execution environment |
| **Scope** | Per-machine (local installation) | Per-account (cloud storage) |
| **Management** | File system | `/v1/skills` API endpoint |
| **Versioning** | Manual (git, file copies) | API-managed versions |
| **Portability** | Must install on each machine | Available everywhere via API |
| **SDK Support** | ❌ No (interactive-only) | ❓ Unknown |

---

## Next Steps: Investigation Plan

### Step 1: Check Agent SDK for Skills API Support

**Action:** Search Agent SDK documentation and exports for skills-related APIs

```python
# Check if these exist in SDK:
from claude_agent_sdk import ClaudeAgentOptions

# Look for:
- skills parameter in ClaudeAgentOptions
- skill upload methods
- /v1/skills endpoint wrappers
```

### Step 2: Test Direct Messages API with Skills

**Action:** Make direct API call to test `/v1/skills` endpoint

```bash
# Upload a skill
curl https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-skill",
    "description": "Test skill upload",
    "content": "..."
  }'

# Use in Messages API
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "skills": ["test-skill"],
    "messages": [...]
  }'
```

### Step 3: Update Our Approach Based on Findings

**If skills work via SDK:**
- Implement v0.3.0 with API skills upload
- Get full progressive disclosure benefits
- Expected 60-80% token reduction

**If skills don't work via SDK:**
- Proceed with Option 1 (manual system prompts)
- Document limitations in AGENT_SKILLS_FINAL_INVESTIGATION.md
- Consider future SDK updates

---

## Why This Changes Everything

### Our Previous Conclusion Was Based on Plugin System Only

**What we investigated:**
- `.claude/settings.json` plugin enablement ✅
- Plugin marketplace discovery ✅
- Skill tool in interactive CLI ✅
- **Conclusion:** Skills don't work via SDK ❌

**What we MISSED:**
- Separate `/v1/skills` API endpoint
- Cloud-based skill management
- Skills API for Messages API
- **New question:** Do skills work via SDK using /v1/skills?

### The Real Question

**Not:** "Can we load plugin skills via SDK?"
**Answer:** No - plugin skills are interactive-only

**But:** "Can we use the Skills API (/v1/skills) via SDK?"
**Answer:** UNKNOWN - needs investigation!

---

## Evidence Summary

### From Official Documentation

**Source:** Claude Docs (https://docs.claude.com/en/api/skills-guide)
- Skills API exists at `/v1/skills`
- Skills work with Messages API
- Skills require Code Execution Tool beta

**Source:** GitHub README (anthropics/skills)
> "You can use Anthropic's pre-built skills, and upload custom skills, via the Claude API."

**Source:** Web Search Results
> "The new /v1/skills endpoint gives developers programmatic control"
> "Developers can add Skills to the Messages API and manage them through /v1/skills"

### What We Still Need to Clarify

1. **Does Agent SDK wrap /v1/skills endpoint?**
   - SDK version: 0.1.4
   - No obvious skills parameter in `ClaudeAgentOptions`
   - But might be hiding in Messages API calls

2. **Is Code Execution Tool compatible with SDK?**
   - Skills require this beta feature
   - Does SDK enable it automatically?
   - Can we pass it as a parameter?

3. **Are there SDK skill examples?**
   - Search SDK documentation
   - Check SDK test files
   - Look for skill-related imports

---

## Conclusion

**We discovered TWO DIFFERENT skill systems:**

1. **Plugin Skills** (local, interactive)
   - ❌ Don't work via Agent SDK
   - ✅ Work in interactive Claude Code CLI
   - Loading mechanism: Skill tool (not available programmatically)

2. **API Skills** (/v1/skills, cloud)
   - ❓ Unknown if work via Agent SDK
   - ✅ Work via direct Messages API
   - Loading mechanism: Code execution environment

**The user was RIGHT to push back** - there IS a way to use skills programmatically (via /v1/skills API), but we need to investigate if the Agent SDK exposes this functionality.

**Next action:** Check Agent SDK for /v1/skills support before concluding skills don't work.
