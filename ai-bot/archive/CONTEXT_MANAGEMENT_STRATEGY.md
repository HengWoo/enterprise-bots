# Context Management Strategy

**Principle:** Progressive disclosure at ALL levels - prompts, documentation, AND planning

---

## The Problem

**Current state:**
- ✅ Bot prompts: 3-layer progressive disclosure (personality → skills → dynamic)
- ❌ Documentation: Still loading too much upfront
- ❌ Planning: ANTHROPIC_BEST_PRACTICES_ROADMAP.md (45KB) referenced but rarely needed

**Result:** 59% context usage before any actual work starts

---

## Solution: Multi-Tiered Everything

### 1. Documentation Tiers (IMPLEMENTED ✅)

**Tier 1: Essential (always loaded)**
- CLAUDE.md - Project status + active plan
- DESIGN.md - System architecture
- QUICK_REFERENCE.md - Quick commands

**Tier 2: Reference (load on-demand)**
- VERSION_HISTORY.md
- TROUBLESHOOTING.md
- Feature-specific docs

**Tier 3: Archive (search as needed)**
- Historical documents
- Version-specific testing

---

### 2. Planning Tiers (NEW 🔜)

#### Tier 1: Active Plan (CLAUDE.md)
**Content:** Current sprint only (100-200 lines max)
```markdown
## 🎯 Current Sprint

**Phase:** v0.5.0 Pilot Validation
**Duration:** 1 week (Nov 1-7)
**Status:** Ready to start

### This Week's Tasks
1. Deploy personal_assistant with verification enabled
2. Test 5 real workflows (finance analysis, report generation, etc.)
3. Document failures → write regression tests
4. Validate 5 gates (error catching, code gen, CI/CD, performance, regression)

**Next Week:** Go/No-Go decision for v0.5.0 full rollout

**Detailed plan:** See plans/v0.5.0/ROADMAP.md
**Task tracking:** See GitHub Issues #15-#20
```

#### Tier 2: Phase Plans (plans/vX.X.X/ROADMAP.md)
**When loaded:** Only when actively working on that version
**Content:** Detailed implementation steps for entire phase
**Example:** `plans/v0.5.0/ROADMAP.md` (move ANTHROPIC_BEST_PRACTICES_ROADMAP.md here)

**Loading trigger:**
```markdown
| User Request | Load This File |
|--------------|----------------|
| "Work on v0.5.0" | plans/v0.5.0/ROADMAP.md |
| "Continue verification implementation" | plans/v0.5.0/ROADMAP.md |
| "What's the v0.6.0 plan?" | plans/v0.6.0/ROADMAP.md |
```

#### Tier 3: GitHub Issues (search/query as needed)
**When used:** Task-level tracking and collaboration
**Content:**
- Task breakdown (issues)
- Acceptance criteria
- Progress updates
- Code references

**Access methods:**
1. GitHub CLI (`gh issue list`, `gh issue view`)
2. Task agent with GitHub MCP
3. Direct links from CLAUDE.md

---

### 3. Code Context (IMPLEMENTED ✅)

**Already optimized:**
- Read files on-demand only
- Use Grep/Glob for discovery
- Task agent for complex searches
- Never load entire codebase

---

## Proposed Structure

```
/campfire/
├── CLAUDE.md                    # Active plan (Tier 1)
├── DESIGN.md                    # Architecture (Tier 1)
├── QUICK_REFERENCE.md           # Commands (Tier 1)
├── CONTEXT_MANAGEMENT_STRATEGY.md  # This file
│
├── plans/                       # Phase plans (Tier 2)
│   ├── v0.5.0/
│   │   ├── ROADMAP.md          # Full v0.5.0 plan (45KB)
│   │   ├── PHASE1_COMPLETE.md  # Completed phase docs
│   │   └── TESTING_CRITERIA.md
│   ├── v0.6.0/
│   │   └── ROADMAP.md
│   └── README.md               # Plan index
│
├── docs/reference/              # Reference docs (Tier 2)
│   ├── VERSION_HISTORY.md
│   ├── TROUBLESHOOTING.md
│   └── V0.4.0_DOCUMENT_PROCESSING_ARCHITECTURE.md
│
└── ai-bot/archive/              # Archive (Tier 3)
    └── (71 historical files)
```

---

## GitHub Issues Integration

### Strategy

**Use GitHub Issues for:**
- ✅ Task-level tracking (not loaded in context)
- ✅ Collaboration and status updates
- ✅ Linking code to requirements
- ✅ Milestone tracking

**Don't use GitHub Issues for:**
- ❌ Replacing CLAUDE.md (too slow to query every session)
- ❌ Architectural documentation (belongs in DESIGN.md)
- ❌ Command reference (belongs in QUICK_REFERENCE.md)

### Proposed GitHub Issues Structure

**Milestones:**
- v0.5.0 Pilot Validation
- v0.5.0 Full Rollout
- v0.6.0 Planning

**Labels:**
- `phase/verification` - Verification module work
- `phase/codegen` - Code generation work
- `phase/testing` - Testing infrastructure
- `type/bug` - Bugs and fixes
- `type/enhancement` - New features
- `priority/high` - Immediate attention

**Issue Templates:**
```markdown
## v0.5.0 Task: [Task Name]

**Phase:** Pilot Validation
**Estimate:** X hours
**Dependencies:** #issue-number

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

### Implementation Notes
- Detail 1
- Detail 2

### Testing
- [ ] Test case 1
- [ ] Test case 2

**Detailed plan:** See plans/v0.5.0/ROADMAP.md (section X)
```

### Access Pattern

**From CLAUDE.md:**
```markdown
## 🎯 Current Sprint

**GitHub Issues:** #15, #16, #17, #18, #19, #20
**View all:** `gh issue list --milestone "v0.5.0 Pilot Validation"`
```

**When Claude needs details:**
```bash
# Claude can run this
gh issue view 15

# Or Claude can use GitHub MCP (if available)
# Or user provides issue number when requesting work
```

---

## CLAUDE.md New Structure (Proposed)

### Current Section (Concise)
```markdown
## 🎯 Current Work

**Sprint:** v0.5.0 Pilot Validation (Week 1 of 1)
**Status:** Ready to start
**Goal:** Validate verification + code generation with personal_assistant bot

### This Week (Nov 1-7)
1. 🚀 Deploy personal_assistant with verification enabled
2. 🧪 Test 5 real workflows (GitHub: #15-#19)
3. 📝 Document failures → regression tests
4. ✅ Validate 5 success gates
5. 📊 Go/No-Go decision

**Next sprint:** v0.5.0 Full Rollout (if gates pass)

**Details:**
- Full roadmap: `plans/v0.5.0/ROADMAP.md`
- Task tracking: GitHub issues #15-#20
- Implementation: 179 tests passing, 77% coverage
```

### Planning History (Minimal)
```markdown
## 📋 Planning History

**Recent sprints:**
- v0.4.1 (Oct 29): File-based prompts ✅ COMPLETE
- v0.4.0.2 (Oct 27): Documentation consolidation ✅ DEPLOYED
- v0.5.0 Phase 1 (Oct 30): Verification + codegen ✅ READY FOR PILOT

**Upcoming:**
- v0.5.0 Pilot (Nov 1-7): Validation week
- v0.5.0 Rollout (Nov 8+): If pilot succeeds
- v0.6.0 Planning (TBD)

**See:** `docs/reference/VERSION_HISTORY.md` for complete history
```

---

## Implementation Steps

### Phase 1: Restructure Planning (Immediate)
1. Create `plans/` directory structure
2. Move ANTHROPIC_BEST_PRACTICES_ROADMAP.md → `plans/v0.5.0/ROADMAP.md`
3. Create concise active plan in CLAUDE.md (100-200 lines max)
4. Update CLAUDE.md loading instructions

### Phase 2: GitHub Issues (Optional but recommended)
1. Create GitHub milestones (v0.5.0 Pilot, v0.5.0 Rollout, etc.)
2. Break down v0.5.0 ROADMAP into 5-10 issues
3. Add issue references to CLAUDE.md
4. Test `gh` CLI integration

### Phase 3: Agentic Search (Future enhancement)
1. Consider Task agent for searching large planning docs
2. Or use GitHub MCP for issue queries
3. Or use Grep with specific patterns

---

## Best Practices (From Research)

### 1. Progressive Disclosure (Anthropic Cookbook)
- ✅ Don't load everything upfront
- ✅ Load on-demand based on task
- ✅ Use clear trigger patterns

### 2. Separation of Concerns
- ✅ Status in CLAUDE.md (what's happening now)
- ✅ Architecture in DESIGN.md (how system works)
- ✅ Detailed plans in plans/ (how to implement)
- ✅ Tasks in GitHub (what needs doing)

### 3. Context Budget Management
- ✅ Essential docs: <15k tokens
- ✅ Reference docs: Load one at a time
- ✅ Planning docs: Load only active phase
- ✅ Keep 40%+ context free for code work

### 4. Searchability
- ✅ Clear file naming (VERSION_HISTORY.md not versions.md)
- ✅ Consistent structure (## sections)
- ✅ Metadata (dates, versions, status)
- ✅ Links between documents

---

## Success Metrics

**Good context management:**
- 📊 Context usage <30% at session start
- 📊 Essential docs <15k tokens
- 📊 Can work on any version without loading others
- 📊 Clear what to load for any task

**Bad context management:**
- ❌ Context >50% before work starts
- ❌ Loading "just in case" documentation
- ❌ Planning docs always in memory
- ❌ Unclear what to load for tasks

---

## Example Session Start

**User:** "Let's work on v0.5.0 pilot validation"

**Claude loads:**
1. CLAUDE.md (always loaded) - sees "v0.5.0 Pilot Validation"
2. `plans/v0.5.0/ROADMAP.md` (on-demand) - gets detailed implementation steps
3. GitHub issues #15-#20 (if needed) - gets task-level details

**Total context:** ~20-25k tokens (still 75%+ free for code)

---

**Document Version:** 1.0
**Created:** 2025-10-30
**Status:** 🎯 PROPOSED - Awaiting implementation
