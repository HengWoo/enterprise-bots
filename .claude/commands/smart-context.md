# Smart Context Management

**Purpose:** Optimize project context management through progressive disclosure

**Based on:** Anthropic Cookbook patterns + Campfire AI Bot optimizations (Oct 30, 2025)

---

## What This Command Does

You are a context management expert helping optimize documentation, planning, and prompt structures for minimal token usage while maximizing usefulness.

### Core Principles

1. **Progressive Disclosure** - Load only what's needed, when needed
2. **Structured Files** - Split large files into focused sections
3. **Clear Loading Triggers** - Document when to load each file
4. **Token Budget Awareness** - Keep essential docs <15k tokens

### Your Task

Based on the user's request, help them:

1. **Audit Context Usage**
   - Scan project for large documentation/planning files
   - Identify files >10k tokens that should be split
   - Show current vs optimized context usage

2. **Split Large Files**
   - Detect natural section boundaries (## headings)
   - Create focused files (500-1000 lines each)
   - Generate navigation/index file
   - Preserve all content (no data loss)

3. **Generate Loading Instructions**
   - Create CLAUDE.md loading patterns
   - Document trigger patterns (user request → file to load)
   - Show token sizes for budget planning

4. **Validate Structure**
   - Check if files follow best practices
   - Ensure no file >1500 lines
   - Verify loading instructions exist
   - Confirm progressive disclosure works

---

## Examples from Campfire Project

### Example 1: Planning File Optimization

**Before:**
```
plans/v0.5.0/ROADMAP.md (1,610 lines, 45k tokens)
```

**After:**
```
plans/v0.5.0/
├── ROADMAP.md (267 lines, ~5k tokens) - Overview + index
├── OVERVIEW.md (58 lines, ~2k tokens) - Executive summary
├── PHASE1_CRITICAL_GAPS.md (751 lines, ~10k tokens) - Phase 1 details
├── PHASE2_OPTIMIZATIONS.md (288 lines, ~5k tokens) - Phase 2 details
└── PHASE3_ADVANCED.md (513 lines, ~8k tokens) - Phase 3 details
```

**Savings:** 35-40k tokens (load 5-10k instead of 45k)

### Example 2: Documentation Consolidation

**Before:**
```
Root directory:
- IMPLEMENTATION_PLAN.md (252 lines, deployment procedures)
- PRODUCTION_DEPLOYMENT_GUIDE.md (697 lines, outdated v1.0.4)
- LOCAL_TESTING_GUIDE.md (638 lines, version-specific)
```

**After:**
```
Root directory:
- QUICK_REFERENCE.md (134 lines, current commands only)

Archive:
- ai-bot/archive/PRODUCTION_DEPLOYMENT_GUIDE.md
- ai-bot/archive/LOCAL_TESTING_GUIDE.md
```

**Savings:** 1,453 lines removed, 91.6% reduction

### Example 3: Bot Prompts (Progressive Disclosure)

**Structure:**
```
prompts/
├── bots/
│   └── personal_assistant.md (200 lines, always loaded)
├── skills/
│   ├── presentation-generation/ (404 lines, on-demand)
│   ├── document-skills-pptx/ (485 lines, on-demand)
│   └── personal-productivity/ (577 lines, on-demand)
└── configs/
    └── personal_assistant.yaml (metadata)
```

**Token savings:** 20% for simple queries, 70% of traffic

---

## Workflow

### Step 1: Understand User's Goal

Ask clarifying questions:
- What are you trying to optimize? (docs, plans, prompts, all)
- What's the problem? (context bloat, slow loading, unclear structure)
- Do you want automatic splitting or manual guidance?

### Step 2: Analyze Current State

Use tools to scan:
```bash
# Find large files
find . -name "*.md" -type f -exec wc -l {} + | sort -rn | head -20

# Estimate token counts (rough: 1 line ≈ 30 tokens)
# Large file: >500 lines (15k tokens)
# Should split: >1000 lines (30k tokens)

# Check structure
grep -E "^#{1,3} " large_file.md  # Find section headings
```

### Step 3: Propose Optimization

Show:
- **Before:** Current structure, token usage
- **After:** Proposed structure, token savings
- **Loading patterns:** When to load each file
- **Impact:** Context savings, maintainability

### Step 4: Execute (if approved)

1. Split files using section boundaries
2. Create navigation/index files
3. Update CLAUDE.md loading instructions
4. Update project README files
5. Verify no content lost

### Step 5: Document Changes

Create summary:
- What was changed
- Context savings achieved
- New loading patterns
- Verification steps

---

## Best Practices Reference

### File Size Guidelines

- **Essential docs (always loaded):** <500 lines each, <15k total
- **Reference docs (on-demand):** 500-1000 lines each
- **Planning files:** 500-1000 lines per phase
- **Archive:** Any size (searched, not loaded)

### Structure Patterns

**Documentation:**
```
Root:
├── CLAUDE.md (project memory, <500 lines)
├── DESIGN.md (architecture, <500 lines)
├── QUICK_REFERENCE.md (commands, <200 lines)

Reference:
├── docs/reference/
│   ├── VERSION_HISTORY.md (complete history)
│   ├── TROUBLESHOOTING.md (solutions)
│   └── FEATURE_X_ARCHITECTURE.md (details)

Archive:
└── ai-bot/archive/ (historical docs)
```

**Planning:**
```
plans/vX.X.X/
├── ROADMAP.md (overview, 300-500 lines)
├── OVERVIEW.md (summary, 200-400 lines)
├── PHASE1_NAME.md (details, 500-1000 lines)
├── PHASE2_NAME.md (details, 500-1000 lines)
└── PHASE3_NAME.md (details, 500-1000 lines)
```

**Prompts:**
```
prompts/
├── bots/ (always loaded, 200 lines)
├── skills/ (on-demand, 400-600 lines each)
└── configs/ (metadata, YAML)
```

### Loading Instructions Template

```markdown
## 📚 Documentation Map

**Essential docs (always loaded):**
- @FILE.md - Description

**Reference docs (read when needed):**
- @docs/reference/FILE.md - Description

| User Request Pattern | Load This File |
|---------------------|----------------|
| "Deploy to production" | @QUICK_REFERENCE.md |
| "What changed in vX.X?" | @docs/reference/VERSION_HISTORY.md |
```

---

## Tools to Use

1. **Bash** - File operations, line counts, section extraction
2. **Read** - Read files to understand structure
3. **Write** - Create new split files
4. **Edit** - Update CLAUDE.md, README files
5. **Grep** - Find section boundaries, search patterns
6. **Glob** - Find files matching patterns

---

## Output Format

### Context Audit Report
```markdown
# Context Management Audit

## Current State
- Essential docs: 52k tokens (26% of context)
- Large files found: 3
  - plans/v0.5.0/ROADMAP.md (45k tokens)
  - IMPLEMENTATION_PLAN.md (2k tokens)
  - docs/reference/LONG_DOC.md (15k tokens)

## Optimization Opportunities
1. Split ROADMAP.md into phases (save 35k tokens)
2. Rename IMPLEMENTATION_PLAN.md (misleading name)
3. Archive outdated deployment guides (save 10k tokens)

## Estimated Savings
- Total: 45k tokens (22.5% of context)
- Session start: 6.7k tokens (was 51.7k)
```

### Split Proposal
```markdown
# Split Proposal: plans/v0.5.0/ROADMAP.md

## Current
- 1,610 lines
- ~45k tokens
- Sections: Overview, Phase 1, Phase 2, Phase 3, Appendices

## Proposed Structure
plans/v0.5.0/
├── ROADMAP.md (overview + index, ~5k tokens)
├── PHASE1_CRITICAL_GAPS.md (~10k tokens)
├── PHASE2_OPTIMIZATIONS.md (~5k tokens)
└── PHASE3_ADVANCED.md (~8k tokens)

## Loading Patterns
| User Request | Load File | Tokens |
|--------------|-----------|--------|
| "What's the plan?" | ROADMAP.md | 5k |
| "Implement verification" | PHASE1_CRITICAL_GAPS.md | 10k |
| "Optimize performance" | PHASE2_OPTIMIZATIONS.md | 5k |

## Savings
- Before: Load 45k tokens always
- After: Load 5-10k tokens per file
- **Savings: 35-40k tokens (17.5-20%)**
```

---

## Success Criteria

After optimization:
- ✅ Context usage <30% at session start
- ✅ Essential docs <15k tokens total
- ✅ No single file >1500 lines
- ✅ Clear loading instructions in CLAUDE.md
- ✅ Progressive disclosure working

---

## References

- CONTEXT_MANAGEMENT_STRATEGY.md - Overall strategy
- AGENTIC_PLAN_LOADING.md - Advanced patterns (Task agent, GitHub Issues)
- Anthropic Cookbook - Progressive disclosure patterns
- Campfire optimizations (Oct 2025) - Real-world examples

---

**Remember:** The goal is maximum usefulness with minimum token usage. Every file loaded should be immediately needed for the current task.
