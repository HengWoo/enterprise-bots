# MCP Integration - Model Context Protocol

> Connect Claude Code to hundreds of external tools and data sources through MCP

## What is MCP?

The Model Context Protocol (MCP) is an open-source standard for AI-tool integrations that gives Claude Code access to external tools, databases, and APIs.

**Official Documentation:** https://modelcontextprotocol.io/introduction

## What You Can Do with MCP

With MCP servers connected, Claude Code can:

- **Implement features from issue trackers**: "Add the feature described in JIRA issue ENG-4521 and create a PR on GitHub"
- **Analyze monitoring data**: "Check Sentry and Statsig to check the usage of feature ENG-4521"
- **Query databases**: "Find emails of 10 random users based on our Postgres database"
- **Integrate designs**: "Update our email template based on the new Figma designs"
- **Automate workflows**: "Create Gmail drafts inviting these users to a feedback session"

## Installing MCP Servers

### Three Installation Methods

**1. Remote HTTP Server (Recommended)**
```bash
# Basic syntax
claude mcp add --transport http <name> <url>

# Example: Connect to Notion
claude mcp add --transport http notion https://mcp.notion.com/mcp

# With authentication
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"
```

**2. Remote SSE Server (Deprecated)**
```bash
# Basic syntax
claude mcp add --transport sse <name> <url>

# Example: Connect to Asana
claude mcp add --transport sse asana https://mcp.asana.com/sse
```

**3. Local stdio Server**
```bash
# Basic syntax
claude mcp add --transport stdio <name> <command> [args...]

# Example: Add Airtable server
claude mcp add --transport stdio airtable --env AIRTABLE_API_KEY=YOUR_KEY \
  -- npx -y airtable-mcp-server
```

**Understanding the "--" Parameter:**
The `--` (double dash) separates Claude's CLI flags from the command passed to the MCP server:
- Before `--`: Claude options (`--env`, `--scope`)
- After `--`: The actual MCP server command

Example:
```bash
claude mcp add --transport stdio myserver --env KEY=value -- python server.py --port 8080
```

### Managing MCP Servers

```bash
# List all configured servers
claude mcp list

# Get details for a specific server
claude mcp get github

# Remove a server
claude mcp remove github

# Check server status (within Claude Code)
/mcp
```

## Popular MCP Servers by Category

**⚠️ Warning:** Use third-party MCP servers at your own risk. Verify their security and trustworthiness, especially those fetching untrusted content (prompt injection risk).

### Development & Testing Tools

- **Sentry**: Monitor errors, debug production issues
  ```bash
  claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
  ```

- **Socket**: Security analysis for dependencies
  ```bash
  claude mcp add --transport http socket https://mcp.socket.dev/
  ```

- **Hugging Face**: Access Hub information and Gradio AI Applications
  ```bash
  claude mcp add --transport http huggingface https://huggingface.co/mcp
  ```

- **Jam**: Debug with AI agents accessing recordings (video, console logs, network)
  ```bash
  claude mcp add --transport http jam https://mcp.jam.dev/mcp
  ```

### Project Management & Documentation

- **Notion**: Read docs, update pages, manage tasks
  ```bash
  claude mcp add --transport http notion https://mcp.notion.com/mcp
  ```

- **Linear**: Issue tracking and project management
  ```bash
  claude mcp add --transport http linear https://mcp.linear.app/mcp
  ```

- **Atlassian**: Manage Jira tickets and Confluence docs
  ```bash
  claude mcp add --transport sse atlassian https://mcp.atlassian.com/v1/sse
  ```

- **Asana**: Interact with Asana workspace
  ```bash
  claude mcp add --transport sse asana https://mcp.asana.com/sse
  ```

- **Monday**: Manage monday.com boards
  ```bash
  claude mcp add --transport sse monday https://mcp.monday.com/sse
  ```

- **Box**: Enterprise content management
  ```bash
  claude mcp add --transport http box https://mcp.box.com/
  ```

- **Fireflies**: Extract insights from meeting transcripts
  ```bash
  claude mcp add --transport http fireflies https://api.fireflies.ai/mcp
  ```

- **Intercom**: Access customer conversations, tickets, and user data
  ```bash
  claude mcp add --transport http intercom https://mcp.intercom.com/mcp
  ```

### Databases & Data Management

- **Airtable**: Read/write records, manage bases and tables
  ```bash
  claude mcp add --transport stdio airtable --env AIRTABLE_API_KEY=YOUR_KEY \
    -- npx -y airtable-mcp-server
  ```

- **HubSpot**: Access and manage CRM data
  ```bash
  claude mcp add --transport http hubspot https://mcp.hubspot.com/anthropic
  ```

- **Daloopa**: High quality fundamental financial data
  ```bash
  claude mcp add --transport http daloopa https://mcp.daloopa.com/server/mcp
  ```

### Payments & Commerce

- **Stripe**: Payment processing and subscriptions
  ```bash
  claude mcp add --transport http stripe https://mcp.stripe.com
  ```

- **PayPal**: PayPal commerce capabilities
  ```bash
  claude mcp add --transport http paypal https://mcp.paypal.com/mcp
  ```

- **Square**: Payments, inventory, orders
  ```bash
  claude mcp add --transport sse square https://mcp.squareup.com/sse
  ```

- **Plaid**: Banking data, financial account linking
  ```bash
  claude mcp add --transport sse plaid https://api.dashboard.plaid.com/mcp/sse
  ```

### Design & Media

- **Figma**: Generate code with full Figma context
  ```bash
  claude mcp add --transport http figma https://mcp.figma.com/mcp
  ```

- **Canva**: Browse, summarize, autofill, generate Canva designs
  ```bash
  claude mcp add --transport http canva https://mcp.canva.com/mcp
  ```

- **invideo**: Video creation capabilities
  ```bash
  claude mcp add --transport sse invideo https://mcp.invideo.io/sse
  ```

- **Cloudinary**: Upload, manage, transform media assets
  (See documentation for specific server URLs)

### Infrastructure & DevOps

- **Cloudflare**: Build applications, analyze traffic, manage security
  (Multiple services, see documentation)

- **Netlify**: Create, deploy, and manage websites
  ```bash
  claude mcp add --transport http netlify https://netlify-mcp.netlify.app/mcp
  ```

- **Vercel**: Search docs, manage projects and deployments
  ```bash
  claude mcp add --transport http vercel https://mcp.vercel.com/
  ```

- **Stytch**: Configure authentication services
  ```bash
  claude mcp add --transport http stytch http://mcp.stytch.dev/mcp
  ```

### Automation & Integration

- **Zapier**: Connect to nearly 8,000 apps
  (Generate user-specific URL at mcp.zapier.com)

- **Workato**: Access applications, workflows via Workato
  (MCP servers are programmatically generated)

### Task Management

- **ClickUp**: Task management, project tracking
  ```bash
  claude mcp add --transport stdio clickup \
    --env CLICKUP_API_KEY=YOUR_KEY --env CLICKUP_TEAM_ID=YOUR_ID \
    -- npx -y @hauptsache.net/clickup-mcp
  ```

**Find More:** [Hundreds more MCP servers on GitHub](https://github.com/modelcontextprotocol/servers) or build your own with the [MCP SDK](https://modelcontextprotocol.io/quickstart/server).

## MCP Installation Scopes

### Local Scope (Default)
- **Location**: Project-specific user settings
- **Accessibility**: Only you, current project only
- **Use Case**: Personal development, experimental configs, sensitive credentials

```bash
# Add a local-scoped server (default)
claude mcp add --transport http stripe https://mcp.stripe.com

# Explicitly specify local scope
claude mcp add --transport http stripe --scope local https://mcp.stripe.com
```

### Project Scope
- **Location**: `.mcp.json` at project root (version controlled)
- **Accessibility**: All team members
- **Use Case**: Team-shared servers, project-specific tools

```bash
# Add a project-scoped server
claude mcp add --transport http paypal --scope project https://mcp.paypal.com/mcp
```

**.mcp.json Format:**
```json
{
  "mcpServers": {
    "shared-server": {
      "command": "/path/to/server",
      "args": [],
      "env": {}
    }
  }
}
```

**Security:** Claude Code prompts for approval before using project-scoped servers. Reset choices with:
```bash
claude mcp reset-project-choices
```

### User Scope
- **Location**: User account settings
- **Accessibility**: You across all projects
- **Use Case**: Personal utilities, dev tools, frequently-used services

```bash
# Add a user server
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic
```

### Scope Hierarchy and Precedence
When servers with the same name exist at multiple scopes:
1. **Local** (highest priority)
2. **Project**
3. **User** (lowest priority)

### Environment Variable Expansion in .mcp.json

Supported syntax:
- `${VAR}` - Expands to environment variable VAR
- `${VAR:-default}` - Uses VAR if set, otherwise uses default

**Expansion locations:** command, args, env, url, headers

**Example:**
```json
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

## Practical Examples

### Example: Monitor Errors with Sentry

```bash
# 1. Add the Sentry MCP server
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# 2. Authenticate
> /mcp

# 3. Debug production issues
> "What are the most common errors in the last 24 hours?"
> "Show me the stack trace for error ID abc123"
> "Which deployment introduced these new errors?"
```

### Example: Connect to GitHub

```bash
# 1. Add the GitHub MCP server
claude mcp add --transport http github https://api.githubcopilot.com/mcp/

# 2. Authenticate if needed
> /mcp

# 3. Work with GitHub
> "Review PR #456 and suggest improvements"
> "Create a new issue for the bug we just found"
> "Show me all open PRs assigned to me"
```

### Example: Query PostgreSQL Database

```bash
# 1. Add the database server
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub \
  --dsn "postgresql://readonly:pass@prod.db.com:5432/analytics"

# 2. Query naturally
> "What's our total revenue this month?"
> "Show me the schema for the orders table"
> "Find customers who haven't made a purchase in 90 days"
```

## Authenticating with Remote MCP Servers

Many cloud-based MCP servers require OAuth 2.0 authentication.

**Steps:**

1. Add the server:
   ```bash
   claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
   ```

2. Use `/mcp` command within Claude Code and follow browser login

**Tips:**
- Authentication tokens are stored securely and refreshed automatically
- Use "Clear authentication" in `/mcp` menu to revoke access
- OAuth authentication works with HTTP servers

## Advanced MCP Features

### Add MCP Servers from JSON

```bash
# HTTP server with JSON
claude mcp add-json weather-api '{"type":"http","url":"https://api.weather.com/mcp","headers":{"Authorization":"Bearer token"}}'

# stdio server with JSON
claude mcp add-json local-weather '{"type":"stdio","command":"/path/to/weather-cli","args":["--api-key","abc123"],"env":{"CACHE_DIR":"/tmp"}}'

# Verify
claude mcp get weather-api
```

### Import from Claude Desktop

```bash
# Import servers (macOS and WSL only)
claude mcp add-from-claude-desktop

# Verify
claude mcp list
```

**Tips:**
- Reads Claude Desktop config from standard location
- Use `--scope user` to add to user configuration
- Imported servers get same names as Claude Desktop
- Duplicate names get numerical suffix (e.g., `server_1`)

### Use Claude Code as MCP Server

```bash
# Start Claude as stdio MCP server
claude mcp serve
```

**Claude Desktop Configuration:**
```json
{
  "mcpServers": {
    "claude-code": {
      "type": "stdio",
      "command": "claude",
      "args": ["mcp", "serve"],
      "env": {}
    }
  }
}
```

## MCP Resources and Prompts

### Reference MCP Resources

Use `@` mentions to reference resources from connected MCP servers:

```
> Can you analyze @github:issue://123 and suggest a fix?
> Please review the API documentation at @docs:file://api/authentication
> Compare @postgres:schema://users with @docs:file://database/user-model
```

**Tips:**
- Resources are automatically fetched when referenced
- Resource paths are fuzzy-searchable in @ mention autocomplete
- Can contain any type of content (text, JSON, structured data)

### Execute MCP Prompts as Slash Commands

MCP servers can expose prompts as slash commands with format `/mcp__servername__promptname`:

```
# List available prompts
> /

# Execute prompt without arguments
> /mcp__github__list_prs

# Execute prompt with arguments
> /mcp__github__pr_review 456
> /mcp__jira__create_issue "Bug in login flow" high
```

## Plugin-Provided MCP Servers

Plugins can bundle MCP servers that activate automatically when the plugin is enabled.

**How It Works:**
- Plugins define MCP servers in `.mcp.json` or `plugin.json`
- Servers start when plugin is enabled
- Plugin MCP tools appear alongside manually configured tools
- Managed through plugin installation (not `/mcp` commands)

**Example Plugin MCP Configuration:**

`.mcp.json` at plugin root:
```json
{
  "database-tools": {
    "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
    "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
    "env": {
      "DB_URL": "${DB_URL}"
    }
  }
}
```

**View Plugin MCP Servers:**
```bash
# Within Claude Code
/mcp
```

**Benefits:**
- Bundled distribution (tools + servers packaged together)
- Automatic setup (no manual MCP configuration)
- Team consistency (everyone gets same tools)

## MCP Output Limits

**Default Settings:**
- Warning threshold: 10,000 tokens
- Maximum default: 25,000 tokens

**Increase Limit:**
```bash
export MAX_MCP_OUTPUT_TOKENS=50000
claude
```

Useful for MCP servers that:
- Query large datasets or databases
- Generate detailed reports
- Process extensive log files

## Enterprise MCP Configuration

Organizations can centrally manage MCP servers and control access.

### Setting Up Enterprise MCP

Deploy `managed-mcp.json` file:

- **macOS**: `/Library/Application Support/ClaudeCode/managed-mcp.json`
- **Windows**: `C:\ProgramData\ClaudeCode\managed-mcp.json`
- **Linux**: `/etc/claude-code/managed-mcp.json`

**Example:**
```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    },
    "sentry": {
      "type": "http",
      "url": "https://mcp.sentry.dev/mcp"
    },
    "company-internal": {
      "type": "stdio",
      "command": "/usr/local/bin/company-mcp-server",
      "args": ["--config", "/etc/company/mcp-config.json"],
      "env": {
        "COMPANY_API_URL": "https://internal.company.com"
      }
    }
  }
}
```

### Restricting MCP Servers

In `managed-settings.json`:

```json
{
  "allowedMcpServers": [
    { "serverName": "github" },
    { "serverName": "sentry" },
    { "serverName": "company-internal" }
  ],
  "deniedMcpServers": [
    { "serverName": "filesystem" }
  ]
}
```

**Allowlist Behavior (`allowedMcpServers`):**
- `undefined`: No restrictions
- `[]`: Complete lockdown
- List of names: Only specified servers allowed

**Denylist Behavior (`deniedMcpServers`):**
- `undefined`: No servers blocked
- `[]`: No servers blocked
- List of names: Specified servers explicitly blocked

**Important:** Denylist takes absolute precedence over allowlist.

## Configuration Tips

**Scope Selection:**
- **Local**: Personal experiments, sensitive credentials for one project
- **Project**: Team-shared tools, project-specific services
- **User**: Personal utilities across all projects

**Windows Users:**
Native Windows (not WSL) requires `cmd /c` wrapper for `npx`:
```bash
claude mcp add --transport stdio my-server -- cmd /c npx -y @some/package
```

**Environment Variables:**
- Use `--env` flags: `--env KEY=value`
- Configure startup timeout: `MCP_TIMEOUT=10000 claude`
- Set output limit: `MAX_MCP_OUTPUT_TOKENS=50000`
- Use `/mcp` for OAuth 2.0 authentication

## Troubleshooting

**Common Issues:**

1. **Connection Closed (Windows)**: Missing `cmd /c` wrapper for npx
2. **Authentication Failed**: Use `/mcp` to re-authenticate
3. **Large Output Warning**: Increase `MAX_MCP_OUTPUT_TOKENS`
4. **Startup Timeout**: Set `MCP_TIMEOUT` environment variable
5. **Project Approval**: Reset with `claude mcp reset-project-choices`

**Getting Help:**
- Check server status: `/mcp`
- View configured servers: `claude mcp list`
- Get server details: `claude mcp get <name>`
- Official docs: https://modelcontextprotocol.io

---

**Last Updated:** 2025-10-21
**For More Information:** See [MCP SDK Documentation](https://modelcontextprotocol.io/quickstart/server)
