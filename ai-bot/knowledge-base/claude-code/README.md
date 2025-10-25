# Claude Code Knowledge Base

> Curated documentation for the Claude Code Tutor bot

## Overview

This knowledge base provides comprehensive documentation for learning and using Claude Code. It is designed to power the **Claude Code Tutor** bot in the Campfire AI Bot system.

**Purpose:** Help users learn Claude Code from scratch, master common workflows, and leverage advanced features.

**Target Users:** Developers, technical teams, and anyone interested in AI-assisted coding tools.

**Last Updated:** 2025-10-21

---

## Structure

```
claude-code/
├── llm.txt                           # Main knowledge base index (LLM-optimized)
├── README.md                         # This file
├── getting-started/
│   └── quickstart.md                 # Installation, setup, first steps
├── workflows/
│   └── common-workflows.md           # Step-by-step guides for common tasks
├── tools/                            # (Future) Tool-specific guides
├── mcp/                              # (Future) MCP integration guides
└── troubleshooting/                  # (Future) Common issues and solutions
```

---

## Key Files

### llm.txt

**Purpose:** Main knowledge base index optimized for LLM consumption

**Contents:**
- Project overview and key capabilities
- Quick navigation to all resources
- Installation and setup instructions
- Essential commands reference
- Common workflows summary
- Advanced features guide
- Configuration and customization
- Best practices and learning path
- Troubleshooting tips

**Format:** Follows [llm.txt standard](https://llmstxt.cloud/) for optimal AI assistant consumption

**Usage:** The Claude Code Tutor bot will use this file to provide comprehensive answers about Claude Code.

### getting-started/quickstart.md

**Purpose:** Get users up and running with Claude Code in 5-10 minutes

**Contents:**
- Installation options (npm, homebrew, native)
- First-time setup and login
- Starting first session
- Asking first questions
- Making first code changes
- Git integration basics
- Essential commands
- Pro tips for beginners

**Target Audience:** Complete beginners to Claude Code

### workflows/common-workflows.md

**Purpose:** Detailed step-by-step guides for common development tasks

**Contents:**
- Understanding new codebases
- Fixing bugs efficiently
- Code refactoring
- Using specialized subagents
- Plan Mode for safe exploration
- Working with tests
- Creating pull requests
- Handling documentation
- Working with images
- File and directory references
- Extended thinking
- Resuming conversations
- Git worktrees for parallel sessions
- Unix-style CLI usage
- Custom slash commands
- Asking Claude about capabilities

**Target Audience:** Users ready to dive into practical workflows

---

## Usage in Claude Code Tutor Bot

### Bot Configuration

**Bot ID:** `claude_code_tutor`
**Bot Name:** "Claude Code 导师"
**Model:** `claude-haiku-4-5-20251001`

**System Prompt:**
```
You are an expert Claude Code tutor helping users learn and master Claude Code,
Anthropic's official CLI for AI-powered coding assistance.

Your knowledge base contains:
- Official Claude Code documentation
- Installation and setup guides
- Common workflows and best practices
- Advanced features and customization

When answering questions:
1. Assess user's experience level (beginner/intermediate/advanced)
2. Provide clear, actionable instructions with examples
3. Reference specific sections of the knowledge base
4. Encourage hands-on practice
5. Explain tradeoffs between different approaches
6. Stay current - Claude Code features evolve

Be friendly, patient, and encouraging. Help users build confidence with Claude Code.
```

**Tools Enabled:**
- `search_conversations` - Search Campfire history
- `query_knowledge_base` - Search this knowledge base
- `read_knowledge_document` - Read full documentation files
- `list_knowledge_documents` - List available guides

### Knowledge Base Tools Usage

**When user asks general questions:**
```python
# Use query_knowledge_base to search
query_knowledge_base("how to install claude code")
```

**When user needs specific guide:**
```python
# Read full document
read_knowledge_document("claude-code/getting-started/quickstart.md")
read_knowledge_document("claude-code/workflows/common-workflows.md")
```

**When user asks "what can you help with":**
```python
# List all available documents
list_knowledge_documents("claude-code/")
```

---

## Content Guidelines

### Writing Style

- **Clear and Concise:** Use simple language, avoid jargon where possible
- **Action-Oriented:** Focus on what users should do, not just what features exist
- **Examples First:** Show examples before explaining theory
- **Progressive Disclosure:** Start simple, introduce complexity gradually
- **Inclusive:** Write for diverse skill levels and backgrounds

### Document Structure

Each guide should include:

1. **Overview** - What this guide covers
2. **Prerequisites** - What users need before starting
3. **Steps** - Clear, numbered steps with code examples
4. **Tips** - Best practices and pro tips
5. **Next Steps** - Where to go after completing this guide

### Code Examples

- Use realistic examples that users can adapt
- Include both commands and expected output
- Provide context for why you'd use each feature
- Show common variations and alternatives

---

## Expansion Plan

### Phase 1: Core Documentation ✅ (Complete)

- [x] llm.txt index
- [x] Quickstart guide
- [x] Common workflows

### Phase 2: Tool Guides (Planned)

Create detailed guides for each built-in tool:

- `tools/websearch.md` - Using WebSearch for research
- `tools/webfetch.md` - Fetching web content
- `tools/file-operations.md` - Read, Write, Edit tools
- `tools/bash.md` - Shell command execution
- `tools/grep-glob.md` - File and content searching

### Phase 3: MCP Integration (Planned)

Guides for Model Context Protocol:

- `mcp/what-is-mcp.md` - MCP overview and benefits
- `mcp/common-servers.md` - Popular MCP servers
- `mcp/creating-mcp-servers.md` - Building custom servers
- `mcp/best-practices.md` - MCP integration patterns

### Phase 4: Advanced Topics (Planned)

Deep dives into advanced features:

- Subagent creation and customization
- Extended thinking strategies
- Enterprise configuration
- Security and compliance
- Performance optimization
- CI/CD integration patterns

### Phase 5: Troubleshooting (Planned)

Common issues and solutions:

- Authentication problems
- Model access issues
- Performance troubleshooting
- Git integration errors
- MCP connection issues
- Error message reference

---

## Maintenance

### Update Schedule

- **Weekly:** Review for accuracy against latest Claude Code version
- **Monthly:** Add new features and capabilities
- **Quarterly:** Refresh examples and best practices
- **As Needed:** Fix errors, clarify confusing sections

### Sources

All content is derived from:

1. **Official Documentation:** https://docs.claude.com/en/docs/claude-code
2. **GitHub Repository:** https://github.com/anthropics/claude-code
3. **Community Feedback:** Discord, GitHub Issues
4. **Real Usage:** Campfire team experiences

### Version Tracking

Document updates in `llm.txt` metadata:

```
**Last Updated:** YYYY-MM-DD
**Source Version:** Claude Code vX.Y.Z
**Documentation Version:** vX.Y
```

---

## Contributing

### Adding New Content

1. **Identify Gap:** What question can't users get answered?
2. **Research:** Check official docs, test features hands-on
3. **Draft Content:** Follow structure and style guidelines
4. **Review:** Test with real users if possible
5. **Update Index:** Add to llm.txt navigation and TOC
6. **Deploy:** Update bot configuration if needed

### Quality Checklist

- [ ] Accurate - verified against latest Claude Code version
- [ ] Clear - simple language, no unnecessary jargon
- [ ] Complete - covers the topic thoroughly
- [ ] Actionable - includes examples and step-by-step instructions
- [ ] Tested - examples work as written
- [ ] Linked - referenced in llm.txt index
- [ ] Formatted - follows Markdown best practices

---

## Support

**For Questions:**
- Ask the Claude Code Tutor bot in Campfire
- Check official docs at https://docs.claude.com
- Join the community Discord

**For Issues:**
- GitHub: https://github.com/anthropics/claude-code/issues
- Campfire internal feedback channels

---

## License

This knowledge base is maintained for internal use in the Campfire AI Bot system. Content is derived from official Anthropic documentation and licensed for educational and internal business purposes.

**Official Source:** https://docs.claude.com/en/docs/claude-code

---

**Maintained by:** Campfire AI Team
**Project Docs:** CLAUDE.md, DESIGN.md, IMPLEMENTATION_PLAN.md
**Last Updated:** 2025-10-21
