# Agentic Plan Loading - True Progressive Disclosure

**Problem:** "Load on-demand" still loads entire 45KB file into context ❌

**Solution:** Use Task agents to search and extract only needed sections ✅

---

## The Problem with Simple "Load On-Demand"

### What We Said
```markdown
| User Request | Load This File |
|--------------|----------------|
| "Work on v0.5.0" | plans/v0.5.0/ROADMAP.md |
```

### What Actually Happens
```python
# Claude uses Read tool
Read(file_path="plans/v0.5.0/ROADMAP.md")

# Result: ENTIRE 45KB file loaded into context
# Context usage: 6.7k → 51.7k tokens
# Problem not solved! ❌
```

---

## Solution 1: Task Agent for Selective Loading ✅

### How It Works

**User request:** "Implement verification input validation"

**Claude's internal process:**
```markdown
1. Check CLAUDE.md: "Current sprint: v0.5.0 Verification"
2. Recognize: Need verification implementation details
3. Use Task agent to extract ONLY verification section
4. Load ~2-3k tokens instead of 45k
```

**Task agent call:**
```python
Task(
  subagent_type="Explore",
  description="Extract verification section from v0.5.0 plan",
  prompt="""
  Search plans/v0.5.0/ROADMAP.md for:
  - Verification module implementation steps
  - Input validation details
  - Testing requirements

  Extract ONLY the verification section.
  Do NOT return the entire document.
  Summarize in 500-1000 lines max.
  """,
  model="haiku"  # Fast, cheap for extraction
)
```

**Task agent returns:**
```markdown
# Verification Module Implementation

## Architecture
[2k tokens of verification-specific content]

## Input Validation
[1k tokens of validation steps]

## Testing
[500 tokens of test requirements]

Total: ~3.5k tokens instead of 45k
```

### Benefits
- ✅ Load only relevant section (92% token savings)
- ✅ Fast (Haiku agent, <5 seconds)
- ✅ Can query different sections as needed
- ✅ No manual file splitting required
- ✅ Works with existing ROADMAP.md

### Drawbacks
- ⚠️ Requires Task agent call (5-10 second latency)
- ⚠️ Additional API cost (~$0.001 per query)
- ⚠️ Relies on agent's extraction quality

---

## Solution 2: Structured Plan Files ✅

### File Structure

```
plans/v0.5.0/
├── ROADMAP.md              # 🎯 Overview (5k tokens)
│   ├── Phase summaries
│   ├── Timeline
│   └── Links to detailed phases
│
├── phase1-verification.md  # 📋 Verification details (10k tokens)
│   ├── Architecture
│   ├── Implementation steps
│   ├── Testing criteria
│   └── Acceptance gates
│
├── phase2-codegen.md       # 📋 Code generation (8k tokens)
├── phase3-testing.md       # 📋 Testing infrastructure (7k tokens)
└── phase4-pilot.md         # 📋 Pilot validation (5k tokens)
```

### Loading Pattern

**Scenario 1: High-level planning**
```markdown
User: "What's the v0.5.0 plan?"

Claude loads:
- plans/v0.5.0/ROADMAP.md (overview, 5k tokens)

Response:
"v0.5.0 has 4 phases:
1. Verification (complete)
2. Code Generation (in progress)
3. Testing (next)
4. Pilot (planned)

For details on any phase, ask me to load that phase plan."
```

**Scenario 2: Implementation work**
```markdown
User: "Implement verification input validation"

Claude loads:
- plans/v0.5.0/phase1-verification.md (10k tokens)

Response:
[Detailed verification implementation steps]
```

**Scenario 3: Phase transition**
```markdown
User: "Start work on code generation phase"

Claude loads:
- plans/v0.5.0/phase2-codegen.md (8k tokens)

Response:
[Detailed code generation steps]
```

### CLAUDE.md Updates

```markdown
## 🎯 Current Work

**Sprint:** v0.5.0 Phase 2 - Code Generation
**Plan overview:** plans/v0.5.0/ROADMAP.md (5k tokens)
**Current phase:** plans/v0.5.0/phase2-codegen.md (8k tokens)

### Loading Guide
- Overview of all phases: Read plans/v0.5.0/ROADMAP.md
- Verification details: Read plans/v0.5.0/phase1-verification.md
- Code generation details: Read plans/v0.5.0/phase2-codegen.md
- Testing details: Read plans/v0.5.0/phase3-testing.md
- Pilot details: Read plans/v0.5.0/phase4-pilot.md
```

### Benefits
- ✅ Human-readable structure
- ✅ No API calls needed (direct file read)
- ✅ Load only relevant phase (10k vs 45k)
- ✅ Easy to maintain and update
- ✅ Clear separation of concerns

### Drawbacks
- ⚠️ Requires splitting existing 45KB file
- ⚠️ Manual effort to organize
- ⚠️ Need to keep files in sync

---

## Solution 3: GitHub Issues (Zero Context) ✅

### Structure

**Milestone:** v0.5.0 Phase 1 - Verification

**Issues:**
```
#15: Implement input validation layer
#16: Add calculation verification
#17: Build result verification
#18: Integrate LLM judge
#19: Create verification config system
#20: Write 170+ test cases
```

**Each issue contains:**
```markdown
## Task: Implement Input Validation Layer

**Phase:** Phase 1 - Verification
**Estimate:** 4 hours
**Dependencies:** None
**Priority:** High

### Acceptance Criteria
- [ ] Validate data types (strings, numbers, dates)
- [ ] Check value ranges
- [ ] Verify required fields present
- [ ] Return clear error messages

### Implementation Steps
1. Create src/verification/validators.py
2. Define ValidationError exception
3. Implement type validators
4. Add range validators
5. Write 40 test cases

### Reference
- Detailed plan: plans/v0.5.0/phase1-verification.md (section 3.1)
- Architecture: DESIGN.md (verification module)
```

### CLAUDE.md Updates

```markdown
## 🎯 Current Work

**Sprint:** v0.5.0 Phase 1 - Verification (Week 2 of 3)

### This Week's Tasks
1. ✅ Input validation layer (#15) - COMPLETE
2. 🔄 Calculation verification (#16) - IN PROGRESS
3. 📋 Result verification (#17) - NEXT
4. 📋 LLM judge integration (#18) - BLOCKED (waiting for API key)

**View all:** `gh issue list --milestone "v0.5.0 Phase 1"`
**Current task:** `gh issue view 16`
```

### Query Pattern

```bash
# Claude can run this when needed
gh issue view 16

# Returns (200 tokens):
# Title: Add calculation verification
# Body: [Detailed task description]
# Status: In Progress
# Assignee: You
# Labels: phase/verification, priority/high
```

### Benefits
- ✅ **Zero context overhead** (query only when needed)
- ✅ Collaborative (team can see progress)
- ✅ Links to code, PRs, commits
- ✅ Built-in task management
- ✅ Can use GitHub MCP for queries

### Drawbacks
- ⚠️ Requires GitHub setup
- ⚠️ Network latency for queries
- ⚠️ Not suitable for detailed implementation docs

---

## Recommended Hybrid: All Three! 🎯

### Tier 1: CLAUDE.md (Always loaded, ~3.5k tokens)
```markdown
## 🎯 Current Work

**Sprint:** v0.5.0 Phase 2 - Code Generation (Week 1 of 2)
**Goal:** Template-based safe code generation

### This Week
- Implement financial analysis template (#21)
- Add operations analytics template (#22)
- Build SQL report template (#23)

**Plan structure:**
- Overview: plans/v0.5.0/ROADMAP.md (5k)
- Current phase: plans/v0.5.0/phase2-codegen.md (8k)
- Tasks: GitHub #21-#23 (query as needed)
```

### Tier 2: Phase Overview (Load when needed, ~5k tokens)
```markdown
# plans/v0.5.0/ROADMAP.md

## v0.5.0 Overview

### Phases
1. ✅ Verification (3 weeks) - COMPLETE
2. 🔄 Code Generation (2 weeks) - IN PROGRESS
3. 📋 Testing (1 week) - NEXT
4. 📋 Pilot (1 week) - PLANNED

### Current: Phase 2
**Detailed plan:** phase2-codegen.md
**Issues:** #21-#25
**Status:** 40% complete
```

### Tier 3: Detailed Phase (Load when implementing, ~8k tokens)
```markdown
# plans/v0.5.0/phase2-codegen.md

## Code Generation Architecture
[8k tokens of detailed implementation]
```

### Tier 4: Task Details (Query individual, ~0.2k tokens)
```bash
gh issue view 21
# Returns 200 tokens of specific task details
```

### Tier 5: Agentic Search (For complex queries, variable)
```python
# If user asks: "How does financial template validation work?"
Task(
  prompt="Extract financial template validation section from phase2-codegen.md"
)
# Returns 1-2k tokens of specific subsection
```

---

## Implementation Steps

### Immediate (Today)
1. Split plans/v0.5.0/ROADMAP.md into 5 files:
   - ROADMAP.md (overview, 5k tokens)
   - phase1-verification.md (10k tokens)
   - phase2-codegen.md (8k tokens)
   - phase3-testing.md (7k tokens)
   - phase4-pilot.md (5k tokens)

2. Update CLAUDE.md loading instructions

3. Test loading pattern:
   ```markdown
   User: "Work on code generation"
   Claude: Reads phase2-codegen.md (8k tokens only)
   ```

### Optional (This week)
1. Create GitHub milestone: "v0.5.0 Phase 2"
2. Break phase2-codegen.md into 5-10 issues
3. Add issue references to CLAUDE.md
4. Test `gh issue view` workflow

### Future (As needed)
1. Use Task agent for complex subsection queries
2. Add GitHub MCP for richer issue integration
3. Create issue templates for phases

---

## Context Budget Comparison

### Before (Loading entire ROADMAP)
```
Essential docs: 6.7k tokens
ROADMAP.md (if loaded): +45k tokens
Total: 51.7k tokens (26% of context)
```

### After (Structured files)
```
Essential docs: 6.7k tokens
Overview (if needed): +5k tokens
Current phase (if needed): +8k tokens
Total: 19.7k tokens (10% of context)

Savings: 32k tokens (16%)
```

### After (With agentic search)
```
Essential docs: 6.7k tokens
Task agent extraction: +2k tokens (specific section)
Total: 8.7k tokens (4.4% of context)

Savings: 43k tokens (21.5%)
```

### After (With GitHub Issues)
```
Essential docs: 6.7k tokens
Issue query: +0.2k tokens (one task)
Total: 6.9k tokens (3.5% of context)

Savings: 44.8k tokens (22.4%)
```

---

## Decision Matrix

| Approach | Context Savings | Setup Effort | Query Speed | Best For |
|----------|----------------|--------------|-------------|----------|
| **Structured Files** | 16% | Medium | Instant | Human readability |
| **Task Agent** | 21.5% | Low | 5-10s | Large existing docs |
| **GitHub Issues** | 22.4% | High | 2-3s | Team collaboration |
| **Hybrid (All 3)** | 22.4% | High | Variable | Maximum flexibility |

---

**Recommendation:** Start with **Structured Files** (immediate benefit, low risk), then optionally add **GitHub Issues** for task tracking.

**Document Version:** 1.0
**Created:** 2025-10-30
**Status:** 🎯 PROPOSED - Awaiting decision
