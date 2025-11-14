## Phase 3: Advanced Features (Weeks 7-10)

### Overview
**Goal:** Add semantic search, context compaction, performance monitoring
**Duration:** 15-20 days
**Effort:** 30-40 hours
**Target Version:** v0.6.0

### Component 3.1: Semantic Search for Knowledge Bases

**Problem Statement:**
Agentic search (Grep, Glob) works well but may miss semantically related content. Complex queries benefit from semantic understanding.

**Solution:**
Add semantic search as fallback when agentic search insufficient.

**Implementation:**

1. **Vector Database Integration**
```python
# src/semantic_search/vector_store.py
from sentence_transformers import SentenceTransformer
import chromadb

class SemanticSearchEngine:
    def __init__(self, kb_dir: str):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.PersistentClient(path=f"{kb_dir}/.chroma")

    async def index_knowledge_base(self, kb_dir: str):
        """Index all knowledge base documents."""
        for doc_path in Path(kb_dir).rglob("*.md"):
            content = doc_path.read_text()
            embedding = self.model.encode(content)

            self.chroma_client.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[{"path": str(doc_path)}],
                ids=[str(doc_path)]
            )

    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search knowledge base semantically."""
        query_embedding = self.model.encode(query)

        results = self.chroma_client.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        return [
            {
                "content": doc,
                "path": metadata["path"],
                "relevance": score
            }
            for doc, metadata, score in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
```

2. **Hybrid Search Strategy**
```python
# src/semantic_search/hybrid_search.py
async def search_knowledge_base_hybrid(
    query: str,
    kb_dir: str,
    strategy: str = "agentic_first"
) -> Dict:
    """Hybrid search: agentic first, semantic fallback."""

    # 1. Try agentic search (Grep)
    grep_results = await grep_search(query, kb_dir)

    if len(grep_results) >= 3:
        # Sufficient results from agentic search
        return {"method": "agentic", "results": grep_results}

    # 2. Fall back to semantic search
    semantic_results = await semantic_engine.search(query, top_k=5)

    # 3. Combine and deduplicate
    combined = merge_results(grep_results, semantic_results)

    return {"method": "hybrid", "results": combined}
```

**Integration:**
- cc_tutor: Claude Code knowledge base
- operations_assistant: Operations knowledge base
- financial_analyst: Financial knowledge base (when created)

**Success Metrics:**
- ✅ Semantic search used in 10-20% of KB queries
- ✅ Better results than agentic alone (user feedback)
- ✅ <500ms semantic search latency
- ✅ Index size <100MB for typical KB

---

### Component 3.2: Context Compaction

**Problem Statement:**
Very long conversations (>10 messages) may hit context limits. No explicit compaction strategy currently.

**Solution:**
Automatic summarization of older messages when approaching context limits.

**Implementation:** `src/session_manager.py` (enhancement)

```python
class SessionManager:
    async def compact_context_if_needed(
        self,
        messages: List[Dict],
        max_messages: int = 15,
        max_tokens: int = 100000
    ) -> List[Dict]:
        """Compact context when approaching limits."""

        # Count tokens
        total_tokens = sum(estimate_tokens(msg["content"]) for msg in messages)

        if len(messages) <= max_messages and total_tokens < max_tokens:
            # No compaction needed
            return messages

        # Keep recent messages intact (last 5)
        recent_messages = messages[-5:]

        # Compact older messages
        older_messages = messages[:-5]

        # Summarize with LLM
        summary_prompt = f"""
        Summarize this conversation history concisely:

        {format_messages(older_messages)}

        Preserve:
        - Key decisions made
        - Important data discussed
        - User preferences expressed

        Format as: "Earlier in conversation: ..."
        """

        summary_response = await anthropic_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{"role": "user", "content": summary_prompt}]
        )

        # Create compacted context
        compacted = [
            {
                "role": "system",
                "content": f"[Conversation Summary] {summary_response.content[0].text}"
            }
        ] + recent_messages

        return compacted
```

**Compaction Triggers:**
- Message count > 15
- Token count > 100K (approaching 200K limit)
- Manual trigger via /compact command

**Success Metrics:**
- ✅ No context limit errors in long conversations
- ✅ Preserved key information (test with Q&A)
- ✅ <2s compaction latency
- ✅ 60-80% token reduction after compaction

---

### Component 3.3: Performance Monitoring Dashboard

**Problem Statement:**
No visibility into agent performance metrics. Can't track latency, token usage, error rates, or tool usage over time.

**Solution:**
Telemetry system with metrics dashboard.

**Implementation:**

1. **Metrics Collection:** `src/telemetry/metrics.py`
```python
from dataclasses import dataclass
from datetime import datetime
import prometheus_client as prom

@dataclass
class RequestMetrics:
    bot_id: str
    room_id: int
    user_id: int
    latency_ms: float
    tokens_input: int
    tokens_output: int
    tools_used: List[str]
    error: Optional[str]
    timestamp: datetime

class MetricsCollector:
    def __init__(self):
        # Prometheus metrics
        self.request_latency = prom.Histogram(
            'agent_request_latency_seconds',
            'Request latency in seconds',
            ['bot_id']
        )

        self.token_usage = prom.Counter(
            'agent_tokens_total',
            'Total tokens used',
            ['bot_id', 'direction']  # input/output
        )

        self.tool_calls = prom.Counter(
            'agent_tool_calls_total',
            'Tool calls by bot and tool',
            ['bot_id', 'tool_name']
        )

        self.errors = prom.Counter(
            'agent_errors_total',
            'Errors by bot and type',
            ['bot_id', 'error_type']
        )

    def record_request(self, metrics: RequestMetrics):
        """Record request metrics."""
        self.request_latency.labels(bot_id=metrics.bot_id).observe(
            metrics.latency_ms / 1000
        )

        self.token_usage.labels(
            bot_id=metrics.bot_id,
            direction='input'
        ).inc(metrics.tokens_input)

        self.token_usage.labels(
            bot_id=metrics.bot_id,
            direction='output'
        ).inc(metrics.tokens_output)

        for tool in metrics.tools_used:
            self.tool_calls.labels(
                bot_id=metrics.bot_id,
                tool_name=tool
            ).inc()

        if metrics.error:
            self.errors.labels(
                bot_id=metrics.bot_id,
                error_type=type(metrics.error).__name__
            ).inc()
```

2. **Dashboard:** Grafana + Prometheus

```yaml
# docker-compose.yml (add monitoring stack)
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    volumes:
      - ./monitoring/grafana-dashboards:/etc/grafana/provisioning/dashboards
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

**Dashboard Panels:**
- Request latency (p50, p95, p99) by bot
- Token usage trends (daily, weekly)
- Tool usage heatmap
- Error rates by type
- Success rate by bot
- Cost estimates (tokens × model pricing)

**Alerts:**
- Latency > 30s (p95)
- Error rate > 5%
- Token usage spike (>2x normal)
- Tool failures

**Success Metrics:**
- ✅ All metrics collected (100% coverage)
- ✅ Dashboard accessible and useful
- ✅ Alerts firing correctly
- ✅ Historical data retained (30 days)

---

### Phase 3 Timeline & Milestones

**Week 7-8: Semantic Search**
- Days 1-3: Vector database setup + indexing
- Days 4-5: Hybrid search implementation
- Days 6-7: Integration + testing

**Week 9: Context Compaction**
- Days 1-3: Compaction logic implementation
- Days 4-5: Testing with long conversations

**Week 10: Performance Monitoring**
- Days 1-3: Metrics collection + Prometheus
- Days 4-5: Grafana dashboards + alerts

**Milestone:** Phase 3 complete, advanced features operational

---

### Phase 3 Deliverables

**Advanced Features:**
- Semantic search for 3 knowledge bases
- Context compaction for long conversations
- Performance monitoring dashboard

**Infrastructure:**
- Prometheus metrics collection
- Grafana dashboards
- Alert system

**Documentation:**
- Semantic search guide
- Compaction strategy
- Monitoring playbook

---

## Success Metrics Summary

### Phase 1 Targets
- ✅ Verification catches ≥3 production errors/week
- ✅ Code generation used ≥5 times/week
- ✅ Test suite detects ≥1 regression/month
- ✅ 80%+ code coverage
- ✅ CI/CD stable (≥95% pass rate)
- ✅ Performance impact ≤10% latency

### Phase 2 Targets
- ✅ Tool count reduced 20-30%
- ✅ LLM-as-judge improves quality +15%
- ✅ 5+ MCP servers integrated
- ✅ Token savings 10-15%

### Phase 3 Targets
- ✅ Semantic search used 10-20% of KB queries
- ✅ Zero context limit errors
- ✅ Monitoring dashboard operational
- ✅ <500ms semantic search latency

### Overall System Grade
**Current:** B+ (85/100)
**Target:** A+ (95/100)

---

## Risk Management

### Critical Risks

**Risk 1: Performance Degradation**
- **Impact:** User experience suffers
- **Mitigation:** Benchmark before/after, rollback if >10% slower
- **Monitoring:** Real-time latency metrics

**Risk 2: False Positives in Verification**
- **Impact:** Blocks valid requests
- **Mitigation:** Conservative validation rules, user override option
- **Monitoring:** Track false positive rate

**Risk 3: Code Generation Security**
- **Impact:** Unsafe code execution
- **Mitigation:** Sandbox all execution, lint before run, templates only
- **Monitoring:** Audit generated code, log all executions

**Risk 4: Migration Failures**
- **Impact:** Production bots broken
- **Mitigation:** Pilot-first approach, validation gates, rollback plan
- **Monitoring:** Test coverage, CI/CD status

### Rollback Procedures

**Phase 1 Rollback:**
1. Disable verification decorators
2. Remove code generation from Skills
3. Keep tests but disable in CI
4. Revert bot configs

**Phase 2 Rollback:**
1. Restore original tool counts
2. Disable LLM-as-judge
3. Remove MCP servers from configs

**Phase 3 Rollback:**
1. Fall back to agentic-only search
2. Disable compaction
3. Turn off metrics collection

---

## Documentation & Knowledge Transfer

### Documentation to Create

1. **Implementation Guides** (7 docs)
   - Verification guide
   - Code generation guide
   - Testing guide
   - Tool migration guide
   - LLM-as-judge guide
   - Semantic search guide
   - Monitoring playbook

2. **Checklists** (3 docs)
   - Migration checklist (per bot)
   - Validation gates checklist
   - Rollback procedures

3. **Reference** (4 docs)
   - Best practices summary
   - Anti-patterns to avoid
   - Troubleshooting guide
   - Performance tuning guide

### Knowledge Transfer Sessions

**Week 4:** Phase 1 review and lessons learned
**Week 6:** Phase 2 review and optimization strategies
**Week 10:** Phase 3 review and system overview

---

## Appendix

### A. Tool Count Analysis (Current State)

| Bot | Tool Count | High-Use | Low-Use | Recommendation |
|-----|------------|----------|---------|----------------|
| personal_assistant | 21 | 15 | 6 | Move 6 to Skills |
| financial_analyst | 35 | 20 | 15 | Move 10 to Skills |
| operations_assistant | 28 | 18 | 10 | Move 8 to Skills |
| technical_assistant | 15 | 12 | 3 | Keep as-is |
| menu_engineer | 20 | 15 | 5 | Move 3 to Skills |
| briefing_assistant | 17 | 14 | 3 | Keep as-is |
| cc_tutor | 15 | 12 | 3 | Keep as-is |
| default | 15 | 10 | 5 | Keep as-is |

### B. MCP Server Priorities

| MCP Server | Priority | Bots | Use Cases | Effort |
|------------|----------|------|-----------|--------|
| Slack | High | briefing, operations | Team communication | 2h |
| GitHub | High | technical | Code repo access | 3h |
| Gmail | Medium | personal, briefing | Email automation | 2h |
| Notion | Medium | operations, personal | Knowledge base | 3h |
| Sentry | Medium | technical | Error monitoring | 2h |
| Google Drive | Low | personal, operations | Document storage | 3h |

### C. Validation Gates Detail

**Gate 1: Verification Catches Errors**
- Metric: ≥3 real errors prevented per week
- Test: Production monitoring for 1 week
- Pass criteria: Verification stops ≥3 bad requests

**Gate 2: Code Generation Useful**
- Metric: Used in ≥5 requests per week
- Test: Usage analytics
- Pass criteria: Users find it helpful, code works correctly

**Gate 3: Tests Detect Regressions**
- Metric: ≥1 regression caught per month
- Test: Introduce intentional regression
- Pass criteria: Test suite fails on regression

**Gate 4: CI/CD Stable**
- Metric: ≥95% pass rate over 1 week
- Test: Run CI 20+ times
- Pass criteria: ≤1 flaky test

**Gate 5: Performance Acceptable**
- Metric: ≤10% latency increase
- Test: Before/after benchmarks
- Pass criteria: p95 latency increase <10%

---

**Document Version:** 1.0
**Created:** 2025-10-30
**Last Updated:** 2025-10-30
**Status:** Ready for Phase 1 Implementation
**Next Review:** After Phase 1 pilot validation
