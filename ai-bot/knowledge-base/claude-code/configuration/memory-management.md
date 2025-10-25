# Memory Management

> Learn how to manage Claude Code's memory across sessions with CLAUDE.md files

## Memory System Overview

Claude Code remembers your preferences across sessions using CLAUDE.md files stored at different locations, forming a hierarchical structure.

**Key Concept:** All memory files are automatically loaded into Claude Code's context when launched. Higher priority memories are loaded first, providing a foundation for more specific memories.

## Four Memory Types

### 1. Enterprise Policy (Highest Priority)

**Location:**
- macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`
- Linux: `/etc/claude-code/CLAUDE.md`
- Windows: `C:\ProgramData\ClaudeCode\CLAUDE.md`

**Purpose:** Organization-wide instructions managed by IT/DevOps

**Use Cases:**
- Company coding standards
- Security policies
- Compliance requirements
- Mandatory practices

**Shared With:** All users in organization

**Who Controls:** IT/DevOps administrators

### 2. Project Memory

**Location:** `./CLAUDE.md` or `./.claude/CLAUDE.md` (project root)

**Purpose:** Team-shared instructions for the project

**Use Cases:**
- Project architecture
- Coding standards
- Common workflows
- Build/test commands
- Naming conventions

**Shared With:** Team members via source control

**Who Controls:** Team (checked into git)

### 3. User Memory

**Location:** `~/.claude/CLAUDE.md`

**Purpose:** Personal preferences for all projects

**Use Cases:**
- Code styling preferences
- Personal tooling shortcuts
- Preferred patterns
- Individual workflow

**Shared With:** Just you (all projects)

**Who Controls:** You

### 4. Project Memory (Local) - Deprecated

**Location:** `./CLAUDE.local.md`

**Purpose:** Personal project-specific preferences

**Status:** **Deprecated** - Use CLAUDE.md imports instead (see below)

**Use Cases:** (Historical)
- Your sandbox URLs
- Preferred test data
- Local development settings

**Replacement:** Use imports in CLAUDE.md to reference personal files in `~/.claude/`

**Shared With:** Just you (current project)

## CLAUDE.md Imports

CLAUDE.md files can import additional files using `@path/to/import` syntax.

**Example:**
```markdown
See @README for project overview and @package.json for available npm commands.

# Additional Instructions
- git workflow @docs/git-instructions.md
```

**Import Features:**
- Both relative and absolute paths allowed
- Import files from user's home directory for individual instructions
- Replaces deprecated CLAUDE.local.md functionality
- Works better across multiple git worktrees

**Personal Preferences Example:**
```markdown
# Individual Preferences
- @~/.claude/my-project-instructions.md
```

**Avoiding Collisions:**
- Imports not evaluated inside markdown code spans
- Imports not evaluated inside code blocks

```markdown
This will NOT be imported: `@anthropic-ai/claude-code`

```python
# This will NOT be imported
import @some-package
```
```

**Recursive Imports:**
- Imported files can recursively import additional files
- Maximum depth: 5 hops
- View loaded memory files: `/memory` command

## How Claude Looks Up Memories

**Discovery Process:**

1. **Upward Recursion:** Starting in cwd, Claude Code recurses up to (but not including) root directory `/`
2. **File Reading:** Reads any CLAUDE.md or CLAUDE.local.md files found
3. **Subtree Discovery:** Also discovers CLAUDE.md nested in subtrees under current working directory
4. **Lazy Loading:** Subtree memories only included when Claude reads files in those subtrees

**Example:**
```
/my-project/
├── CLAUDE.md              # Loaded at startup
├── foo/
│   ├── CLAUDE.md          # Loaded at startup (if cwd is /my-project/foo/bar/)
│   └── bar/
│       ├── CLAUDE.md      # Loaded at startup (if cwd is /my-project/foo/bar/)
│       └── (working dir)
└── src/
    └── utils/
        └── CLAUDE.md      # Loaded only when reading files in src/utils/
```

## Quick Memory Management

### Add Memory with `#` Shortcut

Fastest way to add a memory:

```
# Always use descriptive variable names
```

You'll be prompted to select which memory file to store this in.

**Best for:**
- Quick preferences
- One-line rules
- Simple reminders

### Edit Memory with `/memory`

Use `/memory` slash command to open any memory file in your system editor.

**Best for:**
- Extensive additions
- Reorganizing memories
- Reviewing all memories
- Complex instructions

### Initialize Project Memory with `/init`

Bootstrap a CLAUDE.md for your codebase:

```
> /init
```

Creates a starter CLAUDE.md with project-specific information.

**Best for:**
- New projects
- Projects without existing CLAUDE.md
- Quick setup

## Setting Up Project Memory

**What to Include:**

1. **Frequently Used Commands**
   ```markdown
   # Build and Test Commands
   - Build: npm run build
   - Test: npm test
   - Lint: npm run lint
   - Deploy: npm run deploy:prod
   ```

2. **Code Style Preferences**
   ```markdown
   # Code Style
   - Use 2-space indentation
   - Prefer arrow functions over function declarations
   - Use descriptive variable names (no single letters except loops)
   - Maximum line length: 100 characters
   ```

3. **Architectural Patterns**
   ```markdown
   # Architecture
   - Follow MVC pattern
   - Use dependency injection for services
   - Keep components under 200 lines
   - Separate business logic from UI components
   ```

4. **Naming Conventions**
   ```markdown
   # Naming Conventions
   - Files: kebab-case (my-component.ts)
   - Classes: PascalCase (MyComponent)
   - Functions: camelCase (myFunction)
   - Constants: UPPER_SNAKE_CASE (MAX_RETRIES)
   ```

5. **Project-Specific Patterns**
   ```markdown
   # API Patterns
   - All API calls go through services/api.ts
   - Use async/await, not promises
   - Error handling via try-catch
   - Return types always explicitly defined
   ```

## Organization-Level Memory Management

Enterprise organizations can deploy centrally managed CLAUDE.md files.

**Setup Steps:**

1. **Create enterprise memory file:**
   - macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`
   - Linux/WSL: `/etc/claude-code/CLAUDE.md`
   - Windows: `C:\ProgramData\ClaudeCode\CLAUDE.md`

2. **Deploy via configuration management:**
   - MDM (Mobile Device Management)
   - Group Policy
   - Ansible
   - Chef/Puppet
   - Other enterprise tools

**What to Include:**
- Company-wide coding standards
- Security requirements
- Compliance policies
- Mandatory tooling
- Standard practices

## Memory Best Practices

### Be Specific

❌ **Too Vague:** "Format code properly"

✅ **Specific:** "Use 2-space indentation for all JavaScript files"

### Use Structure

**Format as Bullet Points:**
```markdown
# Code Quality
- Run ESLint before committing
- Maintain test coverage above 80%
- Document all public APIs with JSDoc
```

**Group Related Memories:**
```markdown
# Git Workflow
- Create feature branches from main
- Use conventional commits
- Squash commits before merging
- Delete branches after merging

# Testing Standards
- Write tests before implementation (TDD)
- Test file name: component.test.ts
- Mock external dependencies
- Aim for 90% coverage
```

### Review Periodically

- **Monthly:** Review for outdated information
- **After major changes:** Update architectural patterns
- **New team members:** Verify clarity of instructions
- **Project evolution:** Ensure memories reflect current practices

### Examples of Good Memories

**Build Commands:**
```markdown
# Development Commands
- Start dev server: npm run dev (port 3000)
- Run tests: npm test (or npm run test:watch for watch mode)
- Build for production: npm run build
- Preview production build: npm run preview
```

**Code Patterns:**
```markdown
# Error Handling Pattern
- Always wrap async operations in try-catch
- Log errors with context: logger.error('Operation failed', { context, error })
- Return user-friendly error messages
- Never expose stack traces to users
```

**API Conventions:**
```markdown
# API Response Format
All API endpoints return:
{
  success: boolean,
  data?: any,
  error?: { code: string, message: string }
}
```

## Memory Hierarchy Summary

**Precedence Order (highest to lowest):**

1. **Enterprise Policy** → Cannot be overridden
2. **Project Memory** → Shared with team
3. **User Memory** → Personal across all projects
4. **Imports** → Can reference personal files

**Loading Order:**
- Memories loaded from root to current directory
- Higher-priority memories loaded first
- Subtree memories loaded on-demand

## Troubleshooting

**Issue:** Claude not following my preferences
**Solution:** Check memory is in correct file with `/memory`, verify specificity

**Issue:** Too many conflicting memories
**Solution:** Review with `/memory`, remove or consolidate redundant items

**Issue:** Team members not following project patterns
**Solution:** Document in project CLAUDE.md, check file is in git

**Issue:** Personal preferences overriding team standards
**Solution:** Project memory has higher priority than user memory - check which file contains the rule

**Issue:** Can't find where a memory is stored
**Solution:** Use `/memory` to view all loaded memory files

## Quick Reference

**Add quick memory:**
```
# Your memory here
```

**Edit memories:**
```
> /memory
```

**Initialize project memory:**
```
> /init
```

**View loaded memories:**
```
> /memory
```

**Memory file locations:**
- Enterprise: `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS)
- Project: `./CLAUDE.md` or `./.claude/CLAUDE.md`
- User: `~/.claude/CLAUDE.md`
- Deprecated: `./CLAUDE.local.md` (use imports instead)

---

**Last Updated:** 2025-10-21
**Recommended:** Use project CLAUDE.md for team-shared patterns, user CLAUDE.md for personal preferences
