---
name: knowledge-base
description: Searches and retrieves company knowledge base documents including policies, procedures, financial standards, and technical guides. Use when users ask about company policies, official standards, approval workflows, or want to reference authoritative documentation. Supports searching by keywords, listing documents by category, reading full content, and storing new official documents.
---

# Campfire Knowledge Base

## Quick Start

When users ask about company policies, procedures, or official standards:

1. **Search** - Use `search_knowledge_base` to find relevant documents
2. **List** - Use `list_knowledge_documents` to browse available docs
3. **Read** - Use `read_knowledge_document` to get full content
4. **Cite** - Always reference the source document in your response
5. **Store** (if needed) - Use `store_knowledge_document` to create new official docs

## Core Capabilities

### Knowledge Base Structure

The company knowledge base is organized into categories:

**policies/** - Company policies and guidelines
- Financial reporting standards
- Expense reimbursement policies
- HR policies
- Security policies

**procedures/** - Operational procedures and workflows
- Approval workflows
- Onboarding procedures
- IT support procedures
- Document submission processes

**financial/** - Financial standards and classifications
- Account classification standards
- Financial metrics definitions
- Industry benchmarks
- Reporting templates

**technical/** - Technical documentation and guides
- System usage guides
- Tool documentation
- API references
- Campfire bot usage guides

### Available Tools (4 Knowledge Base Tools)

**1. search_knowledge_base**
- Search documents by keywords or phrases
- Filter by category (policies, procedures, financial, technical)
- Returns top N results (default: 3) with relevance ranking
- Provides document path, title, excerpt, and category

**2. read_knowledge_document**
- Read full content of a specific document
- Requires document path (e.g., 'policies/financial-reporting-standards.md')
- Returns complete markdown content
- Use after search to get detailed information

**3. list_knowledge_documents**
- Browse all available documents
- Optional category filter
- Returns document paths, titles, sizes, and last modified dates
- Useful when user wants to "see what's available"

**4. store_knowledge_document**
- Create new knowledge base documents
- Requires category, title, and content
- Optional author attribution
- Returns confirmation and document path

## ⚡ Efficient Search with Code Execution (RECOMMENDED)

**Based on Anthropic's "Code Execution with MCP" best practices**

For documents larger than 1000 lines, use code execution to filter content BEFORE returning to model context. This achieves **85-95% token savings**!

### Helper Functions Available

Located in `helpers/filter_document.py`:

**1. search_and_extract()** - High-level search with automatic filtering
```python
from helpers.filter_document import search_and_extract

results = search_and_extract(
    query="MCP configuration settings",
    category="claude-code",
    context_lines=10,
    max_results=3
)

# Returns only relevant sections (~200 lines) instead of full docs (4700 lines)!
# Token savings: 95%
```

**2. extract_section()** - Extract specific sections by keywords
```python
from helpers.filter_document import extract_section

section = extract_section(
    document_path="claude-code/llm.txt",
    keywords=["MCP", "integration", "configuration"],
    context_lines=10,
    max_sections=5
)

# Processes 4.7K line document, returns only matching sections
```

**3. extract_by_headings()** - Extract by markdown headings
```python
from helpers.filter_document import extract_by_headings

sections = extract_by_headings(
    document_path="claude-code/llm.txt",
    heading_keywords=["MCP", "Integration"],
    include_subheadings=True
)

# Returns complete sections with proper structure
```

**4. get_document_outline()** - Get document structure (headings only)
```python
from helpers.filter_document import get_document_outline

outline = get_document_outline("claude-code/llm.txt")

# Minimal token cost - only heading structure
# Use to decide which sections to extract
```

### When to Use Each Approach

| Scenario | Recommended Approach | Token Cost | Savings |
|----------|---------------------|------------|---------|
| **Large docs (>1000 lines)** | `search_and_extract()` | ~200-500 | 85-95% |
| **Specific query** | `extract_section()` with keywords | ~200-400 | 90-95% |
| **Structured extraction** | `extract_by_headings()` | ~300-600 | 85-90% |
| **Browse structure** | `get_document_outline()` | ~50-100 | 98% |
| **Small docs (<500 lines)** | Direct `read_knowledge_document()` | ~500 | N/A |
| **Browse available docs** | `list_knowledge_documents()` | ~100 | N/A |

### Code Execution Workflow (Recommended Pattern)

**For large knowledge base queries (e.g., Claude Code documentation at 4.7K lines):**

```python
# STEP 1: Get document outline (minimal tokens)
from helpers.filter_document import get_document_outline
outline = get_document_outline("claude-code/llm.txt")
print(outline)  # ~50 tokens vs 4700!

# STEP 2: Based on outline, extract specific sections
from helpers.filter_document import extract_by_headings
sections = extract_by_headings(
    document_path="claude-code/llm.txt",
    heading_keywords=["MCP", "Configuration"],  # What user asked about
    include_subheadings=True
)
print(sections)  # ~300 tokens vs 4700!

# STEP 3: Answer user question with filtered content
# [Provide answer based on filtered sections]

# Total token cost: ~350 tokens instead of 4700 (93% savings!)
```

**For general queries across knowledge base:**

```python
# ONE-STEP approach - search and filter automatically
from helpers.filter_document import search_and_extract

results = search_and_extract(
    query="expense reimbursement approval process",
    category="policies",
    context_lines=10,
    max_results=3
)

# Processes:
# 1. Searches knowledge base (metadata only)
# 2. Extracts relevant sections from top results
# 3. Returns filtered content (~200 lines total)

for result in results:
    print(f"Source: {result['path']}")
    print(result['relevant_excerpt'])  # Only relevant parts!
```

### Performance Comparison

**Before (Direct read):**
```python
# OLD approach - loads entire document
doc = read_knowledge_document("claude-code/llm.txt")
# Cost: 4700 tokens
# Time: ~2 seconds to process in model
```

**After (Code execution filtering):**
```python
# NEW approach - filter before returning to model
from helpers.filter_document import search_and_extract
results = search_and_extract(query="MCP integration", category="claude-code")
# Cost: ~200-300 tokens (only relevant sections)
# Time: ~0.2 seconds to process in model
# Savings: 95% tokens, 90% latency
```

## Usage Workflows

### Workflow 1: Answering Policy Questions

**NEW (Code Execution - Recommended):**
```python
User: "What's our expense reimbursement policy?"

# Use code execution for efficient filtering
from helpers.filter_document import search_and_extract

results = search_and_extract(
    query="expense reimbursement",
    category="policies",
    max_results=1
)

# Returns only relevant sections, not full document!
if results and results[0].get('relevant_excerpt'):
    print(f"According to our Expense Reimbursement Policy ({results[0]['path']}):")
    print(results[0]['relevant_excerpt'])

    # Token cost: ~200 tokens (filtered)
    # vs 1000+ tokens (full document)
```

**OLD (Direct read - Use only for small documents):**
```
Step 1: Search for relevant documents
→ search_knowledge_base(query="expense reimbursement", category="policies")

Step 2: If found, read the full document
→ read_knowledge_document(path="policies/expense-reimbursement.md")

Step 3: Provide answer with citation
→ "According to our Expense Reimbursement Policy (policies/expense-reimbursement.md):
   [Summarize key points]

   Full policy available at: policies/expense-reimbursement.md"
```

### Workflow 2: Browsing Available Documentation

```
User: "What policies do we have?"

Step 1: List documents in policies category
→ list_knowledge_documents(category="policies")

Step 2: Present organized summary
→ "We have the following company policies:

   Financial Policies:
   - Financial Reporting Standards (policies/financial-reporting-standards.md)
   - Expense Reimbursement (policies/expense-reimbursement.md)

   To read any policy, just ask me about it!"
```

### Workflow 3: Multi-Document Research

```
User: "How do approval workflows work for financial reports?"

Step 1: Search for approval workflow procedures
→ search_knowledge_base(query="approval workflow", category="procedures")

Step 2: Search for financial reporting standards
→ search_knowledge_base(query="financial reporting", category="policies")

Step 3: Read relevant documents
→ read_knowledge_document(path="procedures/approval-workflows.md")
→ read_knowledge_document(path="policies/financial-reporting-standards.md")

Step 4: Synthesize information from multiple sources
→ "The approval workflow for financial reports involves:

   According to Approval Workflows (procedures/approval-workflows.md):
   [Workflow steps]

   And per Financial Reporting Standards (policies/financial-reporting-standards.md):
   [Reporting requirements]

   Sources:
   - procedures/approval-workflows.md
   - policies/financial-reporting-standards.md"
```

### Workflow 4: Creating New Documentation

```
User: "Can you document our new remote work policy?"
[User provides policy details]

Step 1: Confirm with user
→ "I'll create a new policy document. Please confirm:
   Category: policies
   Title: Remote Work Policy
   Content: [show summary]

   Should I proceed?"

Step 2: Store the document
→ store_knowledge_document(
     category="policies",
     title="Remote Work Policy",
     content="[full policy text]",
     author="[user name]"
   )

Step 3: Confirm creation
→ "✅ Remote Work Policy has been created and stored at:
   policies/remote-work-policy.md

   It's now available for all team members to reference."
```

## Search Best Practices

### Effective Search Queries

**Good queries (specific keywords):**
- "expense reimbursement"
- "financial reporting standards"
- "approval workflow"
- "account classification"

**Poor queries (too vague):**
- "policy" (use category filter instead)
- "how to" (be more specific)
- "company rules" (use specific topic)

### Category Filtering

Use category parameter to narrow results:
- `category="policies"` - Company policies only
- `category="procedures"` - Operational procedures only
- `category="financial"` - Financial standards only
- `category="technical"` - Technical documentation only
- `category=None` - Search all categories (default)

### Handling No Results

```python
results = search_knowledge_base(query="xyz policy")

if len(results) == 0:
    # Try alternative searches
    results = search_knowledge_base(query="xyz")  # Broaden query
    results = list_knowledge_documents()  # Show all available

    # Inform user
    "I couldn't find a specific policy about 'xyz'. Here are our available policies: [list]"
```

## Citation Guidelines

### Always Cite Sources

**Format 1: Inline Citation**
```
According to our Financial Reporting Standards (policies/financial-reporting-standards.md),
all reports must include...
```

**Format 2: Reference Section**
```
[Your answer]

Sources:
- Financial Reporting Standards: policies/financial-reporting-standards.md
- Approval Workflows: procedures/approval-workflows.md
```

**Format 3: Direct Quote**
```
As stated in our Expense Reimbursement Policy:

> "All expenses must be submitted within 30 days with original receipts."

(Source: policies/expense-reimbursement.md)
```

### Why Citation Matters

- **Credibility**: Shows answer is based on official documentation
- **Traceability**: Users can verify information themselves
- **Updates**: Users know where to look if policy changes
- **Accountability**: Clear source of authoritative information

## Document Organization

### File Naming Conventions

- Use lowercase with hyphens: `expense-reimbursement.md`
- Be descriptive: `financial-reporting-standards.md` (not `standards.md`)
- Include context: `campfire-bot-usage.md` (not `usage.md`)

### Category Selection Guide

**Choose "policies" when:**
- Document sets company-wide rules
- Applies to all employees
- Requires approval to change
- Examples: HR policies, financial policies, security policies

**Choose "procedures" when:**
- Document describes a process/workflow
- Step-by-step instructions
- Operational how-to guides
- Examples: Approval workflows, onboarding procedures

**Choose "financial" when:**
- Document defines financial standards
- Industry benchmarks or metrics
- Accounting classifications
- Examples: Account codes, ratio definitions, reporting templates

**Choose "technical" when:**
- Document explains technical systems
- Tool/software documentation
- API references, code guides
- Examples: System guides, bot documentation, technical specs

## Common Use Cases

### Use Case 1: Policy Inquiry

**User:** "What's the policy on working from home?"

**Bot Workflow:**
1. `search_knowledge_base(query="work from home", category="policies")`
2. If found: `read_knowledge_document(path="policies/remote-work-policy.md")`
3. Provide clear answer with citation

### Use Case 2: Procedure Lookup

**User:** "How do I submit a financial report for approval?"

**Bot Workflow:**
1. `search_knowledge_base(query="financial report approval", category="procedures")`
2. `read_knowledge_document(path="procedures/approval-workflows.md")`
3. Present step-by-step process with source reference

### Use Case 3: Standard Reference

**User:** "What's the account code for office supplies?"

**Bot Workflow:**
1. `search_knowledge_base(query="account classification office supplies", category="financial")`
2. `read_knowledge_document(path="financial/account-classification.md")`
3. Provide specific account code with context

### Use Case 4: Documentation Discovery

**User:** "What documentation do we have about financial reporting?"

**Bot Workflow:**
1. `search_knowledge_base(query="financial reporting")`
2. `list_knowledge_documents(category="financial")`
3. Present organized list of relevant documents

### Use Case 5: Cross-Reference

**User:** "What's the approval process and who needs to approve expense reports?"

**Bot Workflow:**
1. `search_knowledge_base(query="expense approval")`
2. `read_knowledge_document(path="procedures/approval-workflows.md")`
3. `read_knowledge_document(path="policies/expense-reimbursement.md")`
4. Synthesize information from both sources

## When to Use This Skill

**Trigger Scenarios:**
- User asks "What's our policy on..."
- User wants to know "How do I..." (procedures)
- User references "company standards" or "official guidelines"
- User asks about account codes, classifications, benchmarks
- User wants to "see what policies we have"
- User says "according to company policy..."

**Keywords that should trigger this skill:**
- policy, policies, guideline, guidelines
- procedure, process, workflow
- standard, standards, classification
- official, company, organizational
- documentation, docs, reference
- how to, how do I, what's the process
- account code, account classification
- benchmark, industry standard
- approval, authorization

## Integration with Other Skills

This skill works well with:

**Financial Analysis Skill:**
- Reference financial reporting standards
- Look up account classifications
- Check industry benchmarks
- Cite company financial policies

**Conversations Skill:**
- Find past discussions about specific policies
- See when policies were mentioned
- Track policy-related decisions

**Daily Briefing Skill:**
- Include policy updates in briefings
- Highlight new procedures
- Reference standards in analysis

## Success Criteria

A successful knowledge base interaction should:
- ✅ Find relevant documents quickly (1-2 search attempts)
- ✅ Provide accurate information from official sources
- ✅ Always cite source documents
- ✅ Present information clearly and concisely
- ✅ Offer to read full document if user wants details
- ✅ Help user discover related documentation

## Error Handling

### No Results Found

```
User: "What's the policy on XYZ?"

If search returns nothing:
→ "I couldn't find a specific policy about XYZ. Let me show you our available policies:

   [Call list_knowledge_documents(category="policies")]

   Would you like me to check any of these?"
```

### Ambiguous Query

```
User: "What's the policy?"

Response:
→ "I'd be happy to help! We have policies on several topics:

   [Call list_knowledge_documents(category="policies")]

   Which policy are you interested in?"
```

### Document Not Found

```
If read_knowledge_document fails:
→ "I found a reference to this document, but couldn't access it.
   The document may have been moved or renamed.

   Let me search for similar documents: [run alternative search]"
```

## Knowledge Base Maintenance

### When to Create New Documents

**Create new document when:**
- New company policy is approved
- Process/workflow is formalized
- Standards are updated
- New technical systems are deployed

**Don't create document for:**
- Individual decisions (use briefings instead)
- Temporary announcements
- Personal notes
- Draft/unapproved content

### Document Update Strategy

**Option 1: Update existing document**
- Read current version
- Modify content
- Store with same path (overwrites)
- Document version history in content

**Option 2: Create versioned document**
- Store new version with date suffix
- Example: `expense-reimbursement-2025.md`
- Keep old version for reference

## Example Interactions

### Example 1: Simple Policy Query

```
User: 我们的报销政策是什么？(What's our reimbursement policy?)

Bot:
1. search_knowledge_base(query="报销 reimbursement", category="policies")
2. read_knowledge_document(path="policies/expense-reimbursement.md")
3. Response:

"根据我们的《费用报销政策》(policies/expense-reimbursement.md):

主要规定：
- 所有费用必须在30天内提交，附原始收据
- 需要部门经理批准
- 通过财务系统提交报销申请

详细政策文档：policies/expense-reimbursement.md"
```

### Example 2: Technical Documentation

```
User: How do I use the Campfire bots?

Bot:
1. search_knowledge_base(query="campfire bot usage", category="technical")
2. read_knowledge_document(path="technical/campfire-bot-usage.md")
3. Response:

"Here's how to use Campfire bots (from technical/campfire-bot-usage.md):

To interact with bots:
- @财务分析师 for financial analysis
- @技术助手 for technical help
- @日报助手 for daily briefings

Each bot has specialized capabilities. For full details, see:
technical/campfire-bot-usage.md"
```

---

**Last Updated:** October 18, 2025
**Use Case:** Company knowledge base access for Campfire AI bots
**Progressive Disclosure:** Loads only when users query about policies, procedures, or official documentation
