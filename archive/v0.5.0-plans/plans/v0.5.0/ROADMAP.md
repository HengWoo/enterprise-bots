# v0.5.0 Implementation Plan - Overview

**Project:** Campfire AI Bot System Improvements
**Status:** Phase 1 Complete (84%), Ready for Pilot Validation
**Start Date:** 2025-10-30
**Estimated Completion:** 6-8 weeks

---

## Quick Navigation

This plan is split into focused sections for progressive disclosure:

| Section | File | Size | Load When |
|---------|------|------|-----------|
| **Overview** | `OVERVIEW.md` | ~400 lines | Planning/high-level review |
| **Phase 1** | `PHASE1_CRITICAL_GAPS.md` | ~750 lines | Working on verification/codegen/testing |
| **Phase 2** | `PHASE2_OPTIMIZATIONS.md` | ~290 lines | Working on performance/monitoring |
| **Phase 3** | `PHASE3_ADVANCED.md` | ~510 lines | Working on semantic search/compaction |

**Total:** 1,610 lines (was single 45KB file)
**Average phase:** ~8-10k tokens (vs 45k for full document)

---

## Executive Summary

### Current State: Grade B+ (85/100)
- ✅ **Excellent:** Context management, subagent architecture, MCP integration
- ⚠️ **Needs improvement:** Verification, code generation, testing infrastructure
- ⚡ **Missing:** LLM-as-judge, semantic search, explicit compaction

### Target State: Grade A+ (95/100)
- ✅ All verification loops operational
- ✅ Code generation with linting feedback
- ✅ Comprehensive testing infrastructure
- ✅ Performance monitoring and optimization
- ✅ Advanced features (semantic search, compaction, visual feedback)

---

## Migration Strategy: Pilot-First

### Pilot Bot: `personal_assistant`
- Already pilot for file-based prompts (proven migration path)
- Medium complexity (21 tools)
- Has Skills MCP integration
- Active user base for real-world validation

### Validation Gates (Must Pass Before Full Migration)
1. ✅ Verification catches ≥3 real errors in production
2. ✅ Code generation used successfully in ≥5 requests
3. ✅ Test suite detects ≥1 regression before production
4. ✅ CI/CD pipeline ≥95% pass rate over 1 week
5. ✅ Performance impact ≤10% latency increase

### Full Migration (7 Remaining Bots)
**Priority order:**
1. financial_analyst (critical calculations)
2. operations_assistant (complex analytics)
3. technical_assistant (code generation)
4. menu_engineer (profitability verification)
5. briefing_assistant (lower complexity)
6. cc_tutor (knowledge base focus)
7. default (simplest)

---

## Phase Breakdown

### Phase 1: Critical Gaps ✅ COMPLETE (84%)
**Duration:** Weeks 1-2 (10-13 days)
**Effort:** 24-34 hours
**Status:** Implementation done, pilot validation ready
**Detailed plan:** `PHASE1_CRITICAL_GAPS.md`

**Components:**
1. ✅ **Verification System** (179 tests, 77% coverage)
   - Layer 1: Rules-based validation
   - Layer 2: Visual feedback
   - Layer 3: LLM-as-judge (deferred to Phase 2)

2. ✅ **Code Generation** (12 tests passing)
   - Template-based safe generation
   - Linting integration (ruff + mypy)
   - Sandboxed execution

3. ✅ **Testing Infrastructure** (3 critical paths)
   - Agent behavior tests
   - CI/CD integration
   - Regression detection

**Next:** Pilot validation (1 week)

---

### Phase 2: Optimizations 📋 PLANNED
**Duration:** Weeks 5-6 (7-10 days after Phase 1 validation)
**Effort:** 16-24 hours
**Detailed plan:** `PHASE2_OPTIMIZATIONS.md`

**Components:**
1. **Performance Optimization**
   - Caching strategies
   - Parallel execution
   - Response streaming

2. **Monitoring & Observability**
   - Structured logging
   - Performance metrics
   - Cost tracking

3. **LLM-as-Judge Integration**
   - Quality evaluation
   - STAR framework validation
   - Recommendation scoring

---

### Phase 3: Advanced Features 📋 PLANNED
**Duration:** Weeks 7-10 (15-20 days)
**Effort:** 30-40 hours
**Detailed plan:** `PHASE3_ADVANCED.md`

**Components:**
1. **Semantic Search**
   - Embedding generation
   - Vector database integration
   - Knowledge base enhancement

2. **Context Management**
   - Explicit compaction
   - Conversation summarization
   - Memory optimization

3. **Advanced Features**
   - Visual analysis
   - Multi-modal workflows
   - Enhanced collaboration

---

## Current Sprint (Week 1 of 1)

### Phase 1 Pilot Validation
**Goal:** Validate verification + code generation with real workflows
**Bot:** personal_assistant
**Duration:** 1 week

**Tasks:**
1. 🚀 Deploy personal_assistant with verification enabled
2. 🧪 Test 5 real workflows:
   - Financial analysis with calculations
   - Report generation with formatting
   - Data queries with validation
   - Code generation scenarios
   - Multi-step operations
3. 📝 Document failures → write regression tests
4. ✅ Validate all 5 success gates
5. 📊 Make Go/No-Go decision

**Success Criteria:**
- All 5 validation gates pass
- No critical bugs discovered
- Performance acceptable (<10% overhead)
- User feedback positive

**If gates pass:** → Phase 1 full rollout (7 remaining bots)
**If gates fail:** → Phase 1.1 bug fixes and retry

---

## Quick Reference

### File Loading Guide

**For high-level planning:**
```bash
Read(file_path="plans/v0.5.0/OVERVIEW.md")  # ~400 lines
```

**For implementation work:**
```bash
# Working on verification/codegen/testing
Read(file_path="plans/v0.5.0/PHASE1_CRITICAL_GAPS.md")  # ~750 lines

# Working on performance/monitoring
Read(file_path="plans/v0.5.0/PHASE2_OPTIMIZATIONS.md")  # ~290 lines

# Working on semantic search/compaction
Read(file_path="plans/v0.5.0/PHASE3_ADVANCED.md")  # ~510 lines
```

**For task details:**
```bash
# If using GitHub Issues (optional)
gh issue view 15  # Specific task details (~200 tokens)
```

---

## Success Metrics

**Phase 1 (Pilot):**
- ✅ Verification: ≥3 errors caught in production
- ✅ Code generation: ≥5 successful uses
- ✅ Testing: ≥1 regression detected
- ✅ CI/CD: ≥95% pass rate
- ✅ Performance: ≤10% latency increase

**Phase 1 (Full Rollout):**
- All 8 bots migrated successfully
- Zero critical bugs in production
- User satisfaction maintained/improved

**Phase 2:**
- 30% reduction in response latency
- 50% reduction in context usage
- LLM-as-judge integrated

**Phase 3:**
- Semantic search operational
- Context compaction working
- Grade A+ achieved (95/100)

---

## Risk Management

**High Risk:**
- Verification false positives → Pilot will reveal
- Code generation unsafe → Sandboxing + linting mitigates
- Performance degradation → Monitoring + optimization in Phase 2

**Medium Risk:**
- Testing infrastructure unstable → CI/CD integration validates
- LLM-as-judge cost → Use Haiku, cache responses

**Low Risk:**
- User adoption → Pilot-first approach minimizes
- Documentation gaps → Incremental updates

---

## Documentation Structure

```
plans/v0.5.0/
├── ROADMAP.md                      # This file (overview + index)
├── OVERVIEW.md                     # Executive summary + strategy
├── PHASE1_CRITICAL_GAPS.md         # Verification + codegen + testing
├── PHASE2_OPTIMIZATIONS.md         # Performance + monitoring + LLM judge
└── PHASE3_ADVANCED.md              # Semantic search + compaction
```

**Loading strategy:**
- Load ROADMAP.md for planning/status checks (~5k tokens)
- Load specific phase file when implementing (~8-10k tokens)
- Never load all files at once (would be 45k tokens)

---

**For detailed implementation steps, load the appropriate phase file above.**

**Last Updated:** 2025-10-30
**Next Milestone:** Phase 1 Pilot Validation (1 week)
**Status:** Ready to deploy
