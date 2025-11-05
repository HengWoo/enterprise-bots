# Bot Migration Tracker - File-Based Prompts + Native Skills

**Goal:** Migrate all 7 active bots to file-based prompts following Anthropic's three-layer architecture

**Status:** 2/7 Complete (28.6%)
**Estimated Remaining:** 11.5 hours
**Started:** November 4, 2025

---

## Why File-Based Prompts?

**Current Problem:**
- Native skills (`setting_sources=["user", "project"]`) are enabled globally in campfire_agent.py
- "Skill" tool available to all bots via default builtin tools
- However, bots using legacy JSON configs don't know WHEN or HOW to use skills
- They need Layer 1 prompts to instruct Claude on skill usage

**Anthropic's Three-Layer Architecture:**
- **Layer 1:** Bot personality (prompts/bots/*.md) - Always loaded, teaches bot to use skills
- **Layer 2:** Skills (.claude/skills/*/SKILL.md) - Loaded on-demand via Skill tool
- **Layer 3:** Configuration (prompts/configs/*.yaml) - Metadata only

**Benefits:**
- Bots can autonomously load skills when needed
- Token efficiency (20% savings on simple queries)
- Better maintainability
- Follows Anthropic best practices

---

## Migration Progress

### ✅ Completed (2/7)

| Bot | Status | Completed | Files Created | Notes |
|-----|--------|-----------|---------------|-------|
| **personal_assistant** | ✅ DONE | Nov 2, 2025 | personal_assistant.md (327 lines)<br>personal_assistant.yaml | First migration pilot<br>Native skills working |
| **cc_tutor** | ✅ DONE | Nov 3, 2025 | cc_tutor.md (~200 lines)<br>claude_code_tutor.yaml | 2nd migration<br>Skill tool added |

---

### ⏳ Pending (5/7)

#### 1. technical_assistant (Estimated: 1.5 hours)

**Current State:**
- JSON config: `bots/technical_assistant.json` (~4,700 characters)
- Tools: 15 total (base Campfire + knowledge base)
- No specialized MCP servers

**Migration Tasks:**
- [ ] Extract system_prompt to `prompts/bots/technical_assistant.md`
- [ ] Add skill usage instructions (document-skills-*, knowledge-base skill)
- [ ] Create `prompts/configs/technical_assistant.yaml`
- [ ] Add "Skill" to builtin tools
- [ ] Test with webhook

**Success Criteria:**
- Bot loads from .md file ✅
- Bot can autonomously use document-skills when user uploads files ✅
- Template variables working ($current_date, etc.) ✅

---

#### 2. briefing_assistant (Estimated: 2 hours)

**Current State:**
- JSON config: `bots/briefing_assistant.json` (~5,800 characters)
- Tools: 17 total (base + briefing tools: generate_daily_briefing, search_briefings)
- Specialized: Briefing generation workflows

**Migration Tasks:**
- [ ] Extract system_prompt to `prompts/bots/briefing_assistant.md`
- [ ] Add skill usage instructions (daily-briefing skill)
- [ ] Consider creating briefing-generation skill (~400 lines) if workflows are complex
- [ ] Create `prompts/configs/briefing_assistant.yaml`
- [ ] Test briefing generation + search

**Success Criteria:**
- Bot loads from .md file ✅
- Briefing generation working ✅
- Historical briefing search working ✅

---

#### 3. menu_engineer (Estimated: 2 hours)

**Current State:**
- JSON config: `bots/menu_engineer.json` (~6,200 characters)
- Tools: 20 total (base + menu engineering: 5 RPC tools)
- Specialized: Boston Matrix profitability analysis

**Migration Tasks:**
- [ ] Extract system_prompt to `prompts/bots/menu_engineer.md`
- [ ] Add skill usage instructions (document-skills-* for reports)
- [ ] Consider creating menu-engineering skill (~500 lines) for Boston Matrix workflows
- [ ] Create `prompts/configs/menu_engineer.yaml`
- [ ] Test profitability analysis

**Success Criteria:**
- Bot loads from .md file ✅
- Boston Matrix categorization working ✅
- Profitability reports working ✅

---

#### 4. operations_assistant (Estimated: 2.5 hours)

**Current State:**
- JSON config: `bots/operations_assistant.json` (~8,900 characters - longest!)
- Tools: 28 total (base + Supabase: 3 query tools + 10 RPC analytics)
- Specialized: STAR framework, operations analytics
- Knowledge base: 633-line operations.md file

**Migration Tasks:**
- [ ] Extract system_prompt to `prompts/bots/operations_assistant.md`
- [ ] **Create operations-analytics skill** (~600 lines) - STAR framework, RPC workflows
- [ ] Add skill usage instructions (operations-analytics, document-skills-*)
- [ ] Create `prompts/configs/operations_assistant.yaml`
- [ ] Test Supabase queries + analytics RPC functions

**Success Criteria:**
- Bot loads from .md file ✅
- STAR framework analysis working ✅
- All 10 RPC analytics functions working ✅
- Operations skill loaded on-demand ✅

**Notes:**
- This is the most complex migration (largest prompt, most tools)
- Will create a new custom skill for operations workflows

---

#### 5. financial_analyst (Estimated: 2.5 hours)

**Current State:**
- JSON config: `bots/financial_analyst.json` (~9,400 characters - 2nd longest!)
- Tools: 35 total (base + Financial MCP: 17 tools)
- Specialized: Excel analysis, financial validation workflows
- Most complex tool set

**Migration Tasks:**
- [ ] Extract system_prompt to `prompts/bots/financial_analyst.md`
- [ ] Add skill usage instructions (financial-analysis skill, document-skills-xlsx)
- [ ] Verify financial-analysis skill is comprehensive (~600 lines exists)
- [ ] Create `prompts/configs/financial_analyst.yaml`
- [ ] Test Excel analysis + all 17 Financial MCP tools

**Success Criteria:**
- Bot loads from .md file ✅
- All 17 Financial MCP tools accessible ✅
- Excel analysis workflows working ✅
- Financial validation working ✅

**Notes:**
- This is the 2nd most complex migration
- Financial-analysis skill already exists and is comprehensive

---

## Code Cleanup Tasks

### Delete Unused Default Bot

**Reason:** `bots/default.json` has `bot_key: null`, was never deployed

**Tasks:**
- [ ] Delete `bots/default.json`
- [ ] Update `src/bot_manager.py` fallback logic:
  - Change fallback from `default` to `personal_assistant`
  - Line ~45: `fallback_bot_id = "personal_assistant"` (or remove fallback entirely)
- [ ] Test BotManager with non-existent bot_id to verify fallback

**Estimated:** 15 minutes

---

## Testing Checklist (Per Bot)

After each migration:

- [ ] Bot loads from .md file (check logs: `[Prompts] ✅ Loaded file-based prompt`)
- [ ] Template variables substituted ($current_date, $user_name, $room_name)
- [ ] YAML config parsed correctly
- [ ] All tools accessible (check tool count matches)
- [ ] Skill tool available in builtin tools
- [ ] Bot can autonomously load skills when appropriate
- [ ] Webhook test passes
- [ ] No regressions in existing functionality

**Webhook Test Command:**
```bash
curl -X POST http://localhost:8000/webhook/{bot_id} \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":1,"name":"Test"},"room":{"id":2,"name":"Test"},"content":"简单介绍你自己"}'
```

---

## Timeline Estimate

| Task | Estimate | Running Total |
|------|----------|---------------|
| Delete default bot | 15 min | 0.25h |
| Migrate technical_assistant | 1.5h | 1.75h |
| Migrate briefing_assistant | 2h | 3.75h |
| Migrate menu_engineer | 2h | 5.75h |
| Create operations-analytics skill | 1h | 6.75h |
| Migrate operations_assistant | 2.5h | 9.25h |
| Migrate financial_analyst | 2.5h | 11.75h |
| **TOTAL** | **~12 hours** | |

**Contingency:** Add 20% buffer = ~14 hours realistic estimate

---

## Migration Order (Recommended)

1. **Delete default bot** (15 min) - Quick cleanup
2. **technical_assistant** (1.5h) - Simplest migration, good warmup
3. **briefing_assistant** (2h) - Moderate complexity
4. **menu_engineer** (2h) - Moderate complexity
5. **Create operations-analytics skill** (1h) - Prepare for operations migration
6. **operations_assistant** (2.5h) - Complex, needs new skill
7. **financial_analyst** (2.5h) - Most complex, save for last

---

## Success Metrics

**Completion Criteria:**
- ✅ All 7 active bots using file-based prompts
- ✅ All bots have "Skill" tool in builtin tools
- ✅ All bots tested with webhooks
- ✅ No regressions in existing functionality
- ✅ Documentation updated (CLAUDE.md, DESIGN.md)

**Quality Criteria:**
- Bot personalities clear and concise (~200-300 lines Layer 1)
- Skills loaded on-demand (not in main prompt)
- Template variables used consistently
- YAML configs follow personal_assistant pattern
- All tests passing

---

## Skills Inventory

**Anthropic Plugin Skills (Available Globally):**
- document-skills-docx
- document-skills-pptx
- document-skills-pdf
- document-skills-xlsx

**Custom Project Skills (in .claude/skills/):**
- code-generation (~500 lines)
- conversation-search (~400 lines)
- daily-briefing (~400 lines)
- financial-analysis (~600 lines)
- knowledge-base (~400 lines)
- personal-productivity (~577 lines)
- presentation-generation (~404 lines)

**Skills to Create:**
- operations-analytics (~600 lines) - STAR framework, Supabase RPC workflows

---

## Notes

**Key Insight from User:**
> "because not all the bots have migrated to file based prompts (anthropic best practises) like personal_assistant, the skills are not actually correctly implemented. lets make plan so migrate all other bots to file based prompt like personal_assistant."

**Lesson Learned:**
- Simply having "Skill" tool available isn't enough
- Bots need Layer 1 prompts that teach them WHEN and HOW to use skills
- This is why Anthropic's three-layer architecture is critical

**Documentation:**
- See `prompts/MIGRATION_SUMMARY.md` for three-layer architecture details
- See `prompts/bots/personal_assistant.md` for reference implementation
- See `prompts/configs/personal_assistant.yaml` for config structure

---

**Last Updated:** November 4, 2025
**Tracker Version:** 1.0
**Maintained By:** Development Team
