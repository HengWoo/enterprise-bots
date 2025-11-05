# Skills Architecture Discovery & Cleanup (Nov 3, 2025)

## 🔍 Key Discoveries

### 1. Native Anthropic Skills ARE Filesystem-Based

**Initial Assumption (WRONG):** Native skills (xlsx, docx, pdf, pptx) were built-in model capabilities.

**Reality:** Native skills are SKILL.md files stored at `~/.claude/plugins/marketplaces/anthropic-agent-skills/document-skills/`

**Evidence:**
- Test query showed skills loaded from filesystem path
- Skills have identical format to our custom skills (YAML frontmatter + markdown)
- Both use same workflows (markitdown, ooxml scripts, pandoc, etc.)

### 2. Skills Architecture

**Two Discovery Paths:**
```
Agent SDK with setting_sources=["user", "project"]
├─ User-level: ~/.claude/plugins/marketplaces/anthropic-agent-skills/
│  └─ docx/, pptx/, xlsx/, pdf/ (4 document skills)
│
└─ Project-level: .claude/skills/
   └─ Custom SmartICE skills (7 skills)
```

**Format (Identical for Both):**
```yaml
---
name: skill-name
description: "..."
version: 1.0.0  # optional
license: MIT     # optional
---

# Skill Content in Markdown
```

### 3. Anthropic's Official Skills Repository

**Reference:** https://github.com/anthropics/claude-cookbooks/tree/main/skills/custom_skills/analyzing-financial-statements

**Our Setup vs Anthropic's:**
- ✅ We use YAML frontmatter correctly
- ✅ We use markdown content correctly
- ⚠️ We have MORE metadata (version, author, category, priority) than Anthropic's examples
- ✅ Our structure is valid and follows best practices

## 🧹 Cleanup Performed (Nov 3, 2025)

### Removed Duplicate Skills

**Problem:** We had duplicate document skills competing with Anthropic's native ones.

**Action:** Deleted from `.claude/skills/`:
- `document-skills-docx` (duplicate of ~/.claude/plugins/.../docx)
- `document-skills-pptx` (duplicate of ~/.claude/plugins/.../pptx)

**Reason:**
- Anthropic's versions are maintained and auto-updated
- Reduces confusion about which skill is loaded
- Our versions were based on Anthropic's anyway (minimal differences)

### Skill Inventory After Cleanup & Renaming ✅

**Native Anthropic Skills (User-level):** 4 skills
1. xlsx - Spreadsheet processing
2. docx - Word document processing
3. pdf - PDF manipulation
4. pptx - PowerPoint processing

**SmartICE Custom Skills (Project-level):** 7 skills (all renamed ✅)
1. conversation-search ✅ (formerly campfire-conversations)
2. daily-briefing ✅ (formerly campfire-daily-briefing)
3. financial-analysis ✅ (formerly campfire-financial-analysis)
4. knowledge-base ✅ (formerly campfire-kb)
5. code-generation ✅
6. personal-productivity ✅
7. presentation-generation ✅

**Total Skills Available:** 11 skills (4 native + 7 custom)

## ✅ Completed Actions (Nov 3, 2025)

### 1. Rename Skills to Remove "Campfire" Prefix - COMPLETE ✅

**Goal:** Make skills system-agnostic (SmartICE-specific, not Campfire-specific)

**Completed Renames:**
```bash
✅ campfire-conversations → conversation-search
✅ campfire-daily-briefing → daily-briefing
✅ campfire-financial-analysis → financial-analysis
✅ campfire-kb → knowledge-base
```

**Updated:** All `name:` fields in SKILL.md YAML frontmatter updated to match directory names

### 2. Test Skills Discovery - NEXT

Verify personal_assistant can discover all 11 skills:
- 4 native (xlsx, docx, pdf, pptx)
- 7 custom (renamed to generic names)

### 3. Update Bot Prompts - PENDING

Update `prompts/bots/personal_assistant.md` to reference new skill names if needed.

## 🎯 Benefits of This Architecture

1. **Maintenance:** Anthropic maintains document skills (xlsx, docx, pdf, pptx)
2. **Updates:** Native skills get Anthropic's improvements automatically
3. **Clarity:** Clear separation between platform skills vs custom SmartICE skills
4. **Best Practices:** Follows Anthropic's official skills pattern exactly
5. **Flexibility:** Can add/remove custom skills without affecting native ones

## 📚 References

- **Anthropic Skills Docs:** https://docs.claude.com/en/docs/claude-code/skills
- **Anthropic Skills Cookbook:** https://github.com/anthropics/claude-cookbooks/tree/main/skills/custom_skills
- **Agent SDK Docs:** https://docs.claude.com/en/api/agent-sdk/skills

---

**Last Updated:** November 3, 2025 22:05 SGT
**Status:** ✅ Cleanup complete, ✅ Renaming complete, Skills discovery testing next
