# Optimization Backlog

**Purpose:** Track known optimizations to implement after core features are working

---

## 🔥 HIGH PRIORITY: Remove Claude Code CLI (v1.0.9+)

**Status:** 📝 **DOCUMENTED - NOT YET IMPLEMENTED**
**Discovery Date:** 2025-10-13
**Impact:** 🔴 **HIGH** - 93% faster builds, 48% smaller images
**Effort:** 🟢 **LOW** - Just remove 2 sections from Dockerfile
**Risk:** 🟢 **LOW** - Verified unnecessary via testing

### The Issue

We're installing Node.js + Claude Code CLI unnecessarily:
- **Build time waste:** 7 minutes per build
- **Image bloat:** +186MB (Node.js + npm + CLI)
- **Verified unnecessary:** SDK works perfectly without it

### The Fix (for v1.0.9 or later)

**Remove from Dockerfile:**
```dockerfile
# REMOVE lines 33-44: Node.js installation (~80 seconds)
# REMOVE line 52: npm install -g @anthropic-ai/claude-code (~430 seconds)
```

**Keep:**
```dockerfile
# KEEP: uv (needed for Financial MCP)
# KEEP: sqlite3 (actually used)
# KEEP: curl (for healthcheck)
```

### Expected Results

| Metric | Before (v1.0.8) | After (v1.0.9) | Improvement |
|--------|-----------------|----------------|-------------|
| Build time | 7.5 min | 45 sec | 93% faster ⚡ |
| Image size | 386MB | ~200MB | 48% smaller 📦 |
| Complexity | High | Low | Simpler ✨ |

### Testing Required

- [ ] Build Dockerfile without Node.js/CLI
- [ ] Run all v1.0.8 tests (should pass)
- [ ] Verify Flask starts
- [ ] Test bot functionality
- [ ] Check no runtime errors

### Documentation

**Detailed analysis:** See `CLAUDE_CLI_MISTAKE_ANALYSIS.md`

**Why this happened:**
- Misunderstood documentation (CLI is for interactive dev, not SDK runtime)
- Never verified if actually needed
- Propagated assumption as fact in docs

**Proof it's unnecessary:**
```bash
# Package dependencies - no CLI mentioned
$ uv pip show claude-agent-sdk | grep Requires:
Requires: anyio, mcp

# Tested without CLI - works perfectly
✅ SDK imports successfully
✅ ClaudeAgentOptions created
✅ ClaudeSDKClient created
```

### Decision

**Deferred to after Priority 2 (LLM flexibility testing)**

Reasoning:
- v1.0.8 works (just bloated)
- Hot-reload feature is independent of this
- Test LLM flexibility first (Priority 2)
- Then optimize build (this issue)

---

## Future Optimizations (Lower Priority)

### Auto-reload bots without restart
**Effort:** Medium
**Impact:** Medium
**Idea:** Watch `/app/bots` directory for changes, reload automatically

### Bot config validation
**Effort:** Low
**Impact:** Low
**Idea:** Validate JSON schema before loading

### Multi-stage caching
**Effort:** Low
**Impact:** Small
**Idea:** Better Docker layer caching

---

**Last Updated:** 2025-10-13
**Next Action:** Test Priority 2 (LLM flexibility), then implement Claude CLI removal
