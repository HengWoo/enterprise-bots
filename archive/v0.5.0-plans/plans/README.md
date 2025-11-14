# Implementation Plans

**Purpose:** Detailed roadmaps for major versions/phases
**Strategy:** Structured files for progressive disclosure (load only relevant sections)

---

## Active Plans

### v0.5.0 - Verification + Code Generation + Testing
**Status:** Phase 1 Complete (84%), Pilot Validation Ready
**Files:** 5 files (ROADMAP + OVERVIEW + 3 phase files)
**Total:** ~1,600 lines split into focused sections

**Structure:**
```
plans/v0.5.0/
├── ROADMAP.md                      # Overview + index (~5k tokens)
├── OVERVIEW.md                     # Executive summary + strategy (~2k tokens)
├── PHASE1_CRITICAL_GAPS.md         # Verification + codegen + testing (~10k tokens)
├── PHASE2_OPTIMIZATIONS.md         # Performance + monitoring (~5k tokens)
└── PHASE3_ADVANCED.md              # Semantic search + compaction (~8k tokens)
```

### v0.6.0 - TBD
**Status:** Planning phase
**Plan:** To be created when v0.5.0 completes

---

## When to Load Plans

### ❌ Don't Load Unless:
- User explicitly asks to work on that version
- User asks "what's the v0.X.X plan?"
- Starting implementation work on that phase
- Need specific implementation details

### ✅ Do Load:
- Only the relevant phase file (8-10k tokens)
- NOT all files at once (would be 30k+ tokens)
- ROADMAP.md for overview first (5k tokens)
- Then specific phase as needed

---

## Loading Patterns

### Pattern 1: High-Level Review
```markdown
User: "What's the v0.5.0 plan?"

Load: plans/v0.5.0/ROADMAP.md (~5k tokens)
Response: Overview of all 3 phases, current status, next steps
```

### Pattern 2: Implementation Work
```markdown
User: "Implement verification module"

Load: plans/v0.5.0/PHASE1_CRITICAL_GAPS.md (~10k tokens)
Response: Detailed verification implementation steps
```

### Pattern 3: Phase-Specific Work
```markdown
User: "Optimize performance"

Load: plans/v0.5.0/PHASE2_OPTIMIZATIONS.md (~5k tokens)
Response: Performance optimization details
```

### Pattern 4: Agentic Search (Future)
```markdown
User: "How does LLM-as-judge work?"

Use Task agent to extract subsection:
Task(prompt="Extract LLM-as-judge section from PHASE2_OPTIMIZATIONS.md")
Returns: ~2k tokens of specific subsection
```

---

## Context Savings

### Before (Single 45KB file)
```
Load entire ROADMAP.md: 45k tokens
Context usage: 45k/200k (22.5%)
```

### After (Structured files)
```
Load ROADMAP.md overview: 5k tokens
OR load specific phase: 8-10k tokens
Context usage: 5-10k/200k (2.5-5%)

Savings: 35-40k tokens (17.5-20%)
```

### Future (With agentic search)
```
Load ROADMAP.md: 5k tokens
Extract subsection via Task agent: 2k tokens
Context usage: 7k/200k (3.5%)

Savings: 38k tokens (19%)
```

---

## File Organization Guidelines

### For Each Version (vX.X.X)

**1. ROADMAP.md (Required)**
- Overview and index
- Links to all phase files
- Current sprint status
- Quick reference guide
- ~300-500 lines, ~5k tokens

**2. OVERVIEW.md (Optional)**
- Executive summary
- Migration strategy
- Success criteria
- ~200-400 lines, ~2k tokens

**3. PHASEXX_NAME.md (One per phase)**
- Detailed implementation steps
- Code examples
- Testing requirements
- ~500-1000 lines each, ~8-10k tokens

**4. Completed Phase Docs (After completion)**
- PHASE1_COMPLETE.md (what was done)
- TESTING_RESULTS.md (validation data)
- LESSONS_LEARNED.md (retrospective)

---

## Example Loading Instructions (for CLAUDE.md)

```markdown
**Implementation plans (load only when working on that version):**
- @plans/v0.5.0/ROADMAP.md - v0.5.0 overview (~5k tokens)
- @plans/v0.5.0/PHASE1_CRITICAL_GAPS.md - Verification details (~10k tokens)
- @plans/v0.5.0/PHASE2_OPTIMIZATIONS.md - Performance details (~5k tokens)
- @plans/v0.5.0/PHASE3_ADVANCED.md - Advanced features (~8k tokens)

| User Request | Load This File |
|--------------|----------------|
| "Work on v0.5.0" | plans/v0.5.0/ROADMAP.md (overview) |
| "Implement verification" | plans/v0.5.0/PHASE1_CRITICAL_GAPS.md |
| "Optimize performance" | plans/v0.5.0/PHASE2_OPTIMIZATIONS.md |
```

---

## Future Enhancements

### Option 1: Task Agent Search
Use Task agent to extract specific subsections from large phase files:
```python
Task(
  subagent_type="Explore",
  prompt="Extract verification architecture section from PHASE1_CRITICAL_GAPS.md"
)
```

### Option 2: GitHub Issues Integration
Break down each phase into 5-10 GitHub issues for task-level tracking:
```bash
gh issue view 15  # Returns 200 tokens for specific task
```

### Option 3: Hybrid Approach
- ROADMAP.md: Current sprint overview
- GitHub Issues: Task tracking
- Phase files: Implementation details (load on-demand)
- Task agent: Subsection extraction (for complex queries)

**See:** CONTEXT_MANAGEMENT_STRATEGY.md and AGENTIC_PLAN_LOADING.md for details

---

## Migration from Old Plans

**If you have a large monolithic plan:**

1. Create overview file (ROADMAP.md)
2. Split into phase files based on natural sections
3. Update CLAUDE.md loading instructions
4. Test loading individual phase files
5. Archive old monolithic file (optional)

**Example:**
```bash
# Old structure
plans/v0.5.0/ROADMAP.md (1,610 lines, 45k tokens)

# New structure
plans/v0.5.0/
├── ROADMAP.md (268 lines, 5k tokens)
├── OVERVIEW.md (58 lines, 2k tokens)
├── PHASE1_CRITICAL_GAPS.md (751 lines, 10k tokens)
├── PHASE2_OPTIMIZATIONS.md (288 lines, 5k tokens)
└── PHASE3_ADVANCED.md (513 lines, 8k tokens)

Total: Same content, but load 5-10k at a time instead of 45k
```

---

## Best Practices

### ✅ Do:
- Split plans into focused phase files (500-1000 lines each)
- Create clear navigation in ROADMAP.md
- Document token sizes for context budget planning
- Update CLAUDE.md with loading triggers
- Load only the phase you're working on

### ❌ Don't:
- Load all phase files at once
- Create files >1500 lines (split further)
- Duplicate content across files
- Load plans "just in case"
- Forget to update ROADMAP.md index when adding phases

---

**Last Updated:** 2025-10-30
**Active Plans:** v0.5.0 (structured), v0.6.0 (TBD)
**Pattern:** Progressive disclosure at planning level
