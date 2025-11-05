# Documentation Archive

**Last Updated:** 2025-10-30

This directory contains historical documentation that has been superseded, completed, or is no longer actively needed for day-to-day development.

---

## Purpose

These documents are preserved for:
- Historical context and audit trails
- Understanding past decisions and migrations
- Reference for similar future work
- Debugging legacy issues if they resurface

---

## Archive Categories

### ✅ Completed Migrations & Implementations

**These projects are finished and deployed:**
- `AGENT_SDK_MIGRATION_COMPLETE.md` - Migration from custom SDK to official Agent SDK (v0.2.0)
- `MCP_INTEGRATION_COMPLETE.md` - Model Context Protocol integration (v0.2.0)
- `IMPLEMENTATION_COMPLETE.md` - Initial FastAPI implementation
- `TESTING_COMPLETE.md` - Comprehensive testing phase
- `FILE_ANALYSIS_TEST_RESULTS.md` - File upload and analysis testing

---

### 🐛 Resolved Issues

**These bugs/issues were fixed in production:**
- `PDF_INFINITE_LOOP_ISSUE.md` ✅ Fixed in v0.3.0.1
- `PDF_FIX_DEPLOYMENT.md` ✅ Deployed
- `CONVERSATION_MEMORY_FIX.md` ✅ Fixed
- `SUPABASE_TABLE_FIX.md` ✅ Fixed

---

### 📜 Old Version Documentation

**Superseded by current versions:**
- `v1.0.14-CHANGELOG.md`, `v1.0.15-CHANGELOG.md` - Flask-era changelogs
- `V1.0.8_STRUCTURE_REVIEW.md`, `V1.0.8_TEST_RESULTS.md` - Early architecture reviews
- `HOTFIX_v0.2.4.md` - Emergency fixes (now in main CLAUDE.md)
- `DEPLOYMENT_v0.2.4.2.md` - Historical deployment record
- `DEPLOYMENT_STATUS.md` - Outdated snapshot (current status in CLAUDE.md)

---

### 📊 Deployment Records

**Historical deployment documentation:**
- `DEPLOYMENT_READY_v0.3.0.1.md`
- `V0.3.0.1_DEPLOYMENT_READY.md`
- `DEPLOYMENT_v0.3.0.1.md`
- `ANNOUNCEMENT_v0.3.0.1_CN.md`
- `V0.4.0_LOCAL_TEST_RESULTS.md`
- `V0.4.0_TEST_RESULTS.md`
- `V0.4.0_PRE_DEPLOYMENT_CHECKLIST.md`
- `DOCUMENTATION_UPDATES_V0.4.0.md`
- `DOCX_PROCESSING_FEATURE_V0.4.0.md`
- `SECURITY_FIXES_V0.4.0.md`
- `PRODUCTION_DEPLOYMENT_GUIDE.md` (**Archived 2025-10-30** - Outdated v1.0.4 manual deployment, superseded by CI/CD)
- `LOCAL_TESTING_GUIDE.md` (**Archived 2025-10-30** - v0.3.0.1 specific testing, superseded by current workflows)

---

### 🔬 Investigation & Analysis

**Research documents that informed architectural decisions:**

**Skills MCP Investigation (10 files):**
- `AGENT_SKILLS_FINAL_INVESTIGATION.md`
- `SKILLS_API_DISCOVERY.md`
- `SKILLS_INTEGRATION_COMPLETE_ANALYSIS.md`
- `SKILLS_VS_MCP_DEEP_DIVE.md`
- `HYBRID_APPROACH_SKILLS_SDK.md`
- `CUSTOM_SKILLS_MCP_DESIGN.md`
- `FINAL_SKILLS_RECOMMENDATION.md`
- `SKILLS_INTEGRATION_PLAN.md`
- `SKILLS_COMPARISON_TEST_PLAN.md`
- `SKILLS_CHANGES_SUMMARY.md`

**Decision:** Progressive skill disclosure via Skills MCP (not Agent SDK Skills API)

**Architecture Analysis (5 files):**
- `CLAUDE_SDK_WEBHOOK_ARCHITECTURE_ANALYSIS.md` - Webhook vs Agent patterns
- `SDK_PATTERN_COMPARISON.md` - Different SDK usage patterns
- `FASTAPI_MIGRATION_DESIGN.md` - Flask → FastAPI migration plan
- `CLAUDE_CLI_MISTAKE_ANALYSIS.md` - Learnings from CLI integration
- `CLAUDE_ZOMBIE_ANALYSIS.md` - Process management issues
- `MCP_INCOMPATIBILITY_EXAMPLES.md` - MCP tool compatibility research

---

### 📋 Guides & Best Practices

**Moved to archive (still useful, but not primary reference):**
- `AGENT_SDK_INTEGRATION_GUIDE.md` - Agent SDK integration patterns
- `AGENT_SDK_PRACTICAL_GUIDE.md` - Practical SDK usage
- `PROMPT_STORAGE_GUIDE.md` - Prompt engineering storage
- `REGISTRY_COMPARISON.md` - Docker registry comparisons
- `MULTI_LLM_PROVIDER_GUIDE.md` - Multi-provider support design
- `LOCAL_DOCKER_TEST_RESULTS.md` - Local Docker testing
- `RESUME_NOTES.md` - Session resumption notes
- `OPTIMIZATION_BACKLOG.md` - Future optimization ideas
- `DAILY_BRIEFING_SETUP.md` - Briefing automation setup (replaced by cron)

---

### 🧪 Test Results & Phase Documentation

**Historical test runs:**
- `PHASE1_TEST_RESULTS.md` - Multi-bot collaboration Phase 1
- `PHASE2_TEST_RESULTS.md` - Multi-bot collaboration Phase 2
- `QUICK_LOCAL_TEST.md` - Quick test procedures

---

### 📊 Database Analysis

**One-time database quality audit:**
- `DATABASE_QUALITY_ASSESSMENT_REPORT.md`
- `DATABASE_QUALITY_VISUAL_SUMMARY.md`
- `DATABASE_QUALITY_QUICK_REFERENCE.md`
- `DATABASE_QUALITY_REPORT_INDEX.md`
- `README_DATABASE_QUALITY_REPORT.md`

---

### 🚀 Feature Implementation Records

**Historical implementation documentation:**
- `FINANCIAL_MCP_INTEGRATION.md` - Financial MCP setup (now in DESIGN.md)
- `MENU_ENGINEERING_IMPLEMENTATION.md` - Menu engineering bot implementation
- `SUPABASE_SCHEMA.md` - Supabase schema documentation
- `SUPABASE_DEPLOYMENT_GUIDE.md` - Supabase setup guide

---

### 🎭 Miscellaneous

- `renewable_energy_presentation.md` - Example presentation file (test artifact)

---

## Active Documentation

**For current project information, see:**

**Core Documentation (Root `/campfire/`):**
1. `CLAUDE.md` - Project memory and current status
2. `DESIGN.md` - System architecture
3. `IMPLEMENTATION_PLAN.md` - Deployment procedures

**Reference Documentation (Root `/ai-bot/`):**
4. `V0.4.0_DOCUMENT_PROCESSING_ARCHITECTURE.md` - PDF/Image/DOCX/PPTX workflows
5. `TROUBLESHOOTING.md` - Common issues and solutions
6. `LOCAL_TESTING_GUIDE.md` - Local development
7. `PRODUCTION_DEPLOYMENT_GUIDE.md` - Deployment best practices
8. `OPERATIONS_ASSISTANT_ENHANCEMENT.md` - Analytics framework
9. `MENU_ENGINEERING_TECHNICAL_SUMMARY.md` - Boston Matrix analysis
10. `MANUAL_TESTING_GUIDE.md` - Manual testing procedures
11. `README.md` - Project overview

---

## Retrieval

If you need information from archived docs:
1. Check if the topic is covered in current documentation first
2. Search this directory for the relevant file
3. Consider whether the archived doc needs to be updated and moved back to root

---

**Total Archived Files:** 71 (66 from Oct 27 + 2 from Oct 30 + 3 supporting docs)
**Archive Dates:**
- October 27, 2025: Initial consolidation (66 files)
- October 30, 2025: Deployment guide cleanup (2 files)
**Reason:** Documentation consolidation to reduce noise and keep only essential active documentation
