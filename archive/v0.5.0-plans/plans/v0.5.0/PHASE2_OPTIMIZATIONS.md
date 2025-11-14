## Phase 2: Optimizations (Weeks 5-6)

### Overview
**Goal:** Optimize tool counts, add LLM-as-judge, expand MCP integrations
**Duration:** 10-12 days
**Effort:** 20-25 hours
**Target Version:** v0.5.1

### Component 2.1: Tool Count Reduction

**Problem Statement:**
Some bots have 28-35 tools, causing token bloat and reducing precision. Many tools rarely used.

**Solution:**
Audit tool usage, move rarely-used tools to Skills (load on-demand).

**Implementation:**

1. **Tool Usage Analytics**
```python
# src/analytics/tool_usage_tracker.py
class ToolUsageTracker:
    def log_tool_call(self, bot_id: str, tool_name: str):
        """Log tool usage for analytics."""
        # Track: frequency, latency, success rate

    def generate_usage_report(self, days: int = 30) -> Dict:
        """Generate tool usage report."""
        # Return: tools by frequency, unused tools, slow tools
```

2. **Tool Migration to Skills**
```markdown
# prompts/skills/financial-ratios/SKILL.md
---
name: financial-ratios
description: "Calculate financial ratios (rarely used, loaded on-demand)"
---

# Financial Ratio Calculations

## Available Ratios
- Current Ratio
- Quick Ratio
- Debt-to-Equity
- Return on Equity
- Profit Margin

## Workflow: Calculate Ratio
1. Load this skill: load_skill("financial-ratios")
2. Call appropriate calculator function
3. Interpret results
```

**Target Reductions:**
- financial_analyst: 35 → 25 tools (move 10 to Skills)
- operations_assistant: 28 → 20 tools (move 8 to Skills)
- Other bots: Minimal changes

**Success Metrics:**
- ✅ 20-30% reduction in tool count for high-tool bots
- ✅ No impact on functionality (Skills loaded on-demand)
- ✅ 10-15% token reduction in base prompts

---

### Component 2.2: LLM-as-Judge for Quality

**Problem Statement:**
Analytical reports (Operations, Financial) lack quality assurance. No automated checking for completeness, logic, or actionability.

**Solution:**
Secondary model evaluates analytical quality before returning to user.

**Implementation:** `src/verification/llm_judge.py`

```python
class LLMJudge:
    """Use secondary model to evaluate output quality."""

    async def judge_operations_analysis(
        self,
        analysis: str,
        context: Dict
    ) -> Dict:
        """Evaluate Operations Assistant STAR analysis."""

        # Create evaluation prompt
        eval_prompt = f"""
        Evaluate this operations analysis for quality:

        Analysis:
        {analysis}

        Context:
        - Metrics: {context['metrics']}
        - Time period: {context['period']}

        Rate on these criteria (1-5):
        1. Completeness (all STAR components present)
        2. Logic (analysis follows from data)
        3. Insights (meaningful patterns identified)
        4. Recommendations (specific, actionable)
        5. Clarity (easy to understand)

        Return JSON:
        {{
          "scores": {{}},
          "passed": true/false,
          "issues": [],
          "suggestions": []
        }}
        """

        # Call Haiku model (fast, cheap for evaluation)
        response = await anthropic_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{"role": "user", "content": eval_prompt}]
        )

        # Parse results
        evaluation = json.loads(response.content[0].text)

        # Decide: Pass through or flag for review
        if evaluation["passed"]:
            return {"approved": True, "quality_score": evaluation["scores"]}
        else:
            return {
                "approved": False,
                "issues": evaluation["issues"],
                "suggestions": evaluation["suggestions"]
            }
```

**Integration Pattern:**
```python
# In operations_assistant workflow
async def generate_weekly_report_tool(args):
    # Generate report
    report = await generate_report(...)

    # Evaluate quality
    judgment = await llm_judge.judge_operations_analysis(
        analysis=report,
        context={"metrics": metrics, "period": "weekly"}
    )

    if judgment["approved"]:
        return {"content": [{"type": "text", "text": report}]}
    else:
        # Revise report based on suggestions
        revised_report = await revise_report(report, judgment["suggestions"])
        return {"content": [{"type": "text", "text": revised_report}]}
```

**Evaluation Criteria:**

**Operations Assistant (STAR Framework):**
- ✅ Situation: Context and baseline present
- ✅ Task: Key metrics identified
- ✅ Analysis: Trends explained with "why"
- ✅ Recommendation: Specific actions with expected outcomes

**Financial Analyst:**
- ✅ Calculations: Accurate and verified
- ✅ Insights: Meaningful patterns identified
- ✅ Context: Compared to benchmarks
- ✅ Recommendations: Actionable financial decisions

**Menu Engineer:**
- ✅ Boston Matrix: Correct categorization
- ✅ Profitability: Accurate calculations
- ✅ Recommendations: Specific pricing/menu changes

**Success Metrics:**
- ✅ Quality score improvement: +15% average
- ✅ User satisfaction: +20% (fewer revisions needed)
- ✅ Latency impact: <2s additional per request
- ✅ False positives: <5% (approved reports that shouldn't be)

---

### Component 2.3: Expand MCP Server Integrations

**Problem Statement:**
Limited external service integrations. Currently only have Campfire, Skills, Financial, Operations. Many workflows require manual API integration.

**Solution:**
Integrate popular MCP servers for common services (Slack, GitHub, Gmail, etc.).

**Target Integrations:**

#### Priority 1: Communication
1. **Slack MCP** - Team communication
   - Post messages to channels
   - Read recent messages
   - Send DMs
   - Search conversations

2. **Gmail MCP** - Email automation
   - Send emails
   - Search inbox
   - Read messages
   - Draft responses

#### Priority 2: Development
3. **GitHub MCP** - Code repository access
   - Read issues/PRs
   - Post comments
   - Get repository info
   - Search code

4. **Sentry MCP** - Error monitoring
   - Get recent errors
   - Analyze error trends
   - Link to issue tracking

#### Priority 3: Knowledge & Data
5. **Notion MCP** - Knowledge base
   - Search pages
   - Read content
   - Create pages (with permissions)

6. **Google Drive MCP** - Document storage
   - List files
   - Read documents
   - Upload files

**Implementation Pattern:**
```yaml
# prompts/configs/technical_assistant.yaml
mcp_servers:
  - campfire
  - skills
  - github        # NEW: Code repository access
  - sentry        # NEW: Error monitoring

tools:
  builtin: [WebSearch, Read, Bash]
  campfire: [search_conversations, get_user_context]
  skills: [load_skill]
  github: [search_code, get_issue, post_comment]  # NEW
  sentry: [get_recent_errors, analyze_trends]     # NEW
```

**Bot-Specific Integrations:**
- **technical_assistant:** GitHub, Sentry
- **operations_assistant:** Notion, Google Drive
- **briefing_assistant:** Slack, Gmail
- **personal_assistant:** Gmail, Google Drive

**Success Metrics:**
- ✅ 5+ new MCP servers integrated
- ✅ Used in ≥10 user requests per week
- ✅ Zero authentication failures
- ✅ <100ms MCP call overhead

---

### Phase 2 Timeline & Milestones

**Week 5: Tool Optimization + LLM Judge**
- Days 1-3: Tool usage analytics + migration to Skills
- Days 4-5: LLM-as-judge implementation + testing

**Week 6: MCP Expansion**
- Days 1-3: Integrate 3 priority MCPs (Slack, GitHub, Gmail)
- Days 4-5: Integration testing + documentation

**Milestone:** Phase 2 complete, system optimized

---

### Phase 2 Deliverables

**Optimizations:**
- Tool count reduced 20-30% for high-tool bots
- LLM-as-judge operational for 3 bot types
- 5+ new MCP servers integrated

**Documentation:**
- Tool migration guide
- LLM-as-judge criteria
- MCP integration patterns

---

