# Claude Code Settings

> Configure Claude Code with settings files, environment variables, and permissions

## Settings File Locations

Claude Code uses hierarchical settings with precedence (highest to lowest):

1. **Enterprise Managed Policies** (highest priority)
   - macOS: `/Library/Application Support/ClaudeCode/managed-settings.json`
   - Linux/WSL: `/etc/claude-code/managed-settings.json`
   - Windows: `C:\ProgramData\ClaudeCode\managed-settings.json`
   - Cannot be overridden by users

2. **Command Line Arguments**
   - Temporary overrides for a specific session

3. **Local Project Settings**
   - `.claude/settings.local.json` (personal, not committed to git)

4. **Shared Project Settings**
   - `.claude/settings.json` (team-shared, in source control)

5. **User Settings** (lowest priority)
   - `~/.claude/settings.json` (personal global settings)

## Accessing Settings

**Interactive Configuration:**
```bash
# Run within Claude Code
/config
```

This opens a tabbed Settings interface for viewing status and modifying configuration.

## Example settings.json

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test:*)",
      "Read(~/.zshrc)"
    ],
    "deny": [
      "Bash(curl:*)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  },
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp"
  },
  "model": "sonnet",
  "includeCoAuthoredBy": true
}
```

## Available Settings

### Core Settings

| Key | Description | Example |
|-----|-------------|---------|
| `apiKeyHelper` | Custom script to generate auth value | `/bin/generate_temp_api_key.sh` |
| `cleanupPeriodDays` | Chat transcript retention (default: 30 days) | `20` |
| `env` | Environment variables for every session | `{"FOO": "bar"}` |
| `includeCoAuthoredBy` | Include "co-authored-by Claude" in git commits (default: true) | `false` |
| `model` | Override default model | `"claude-sonnet-4-5-20250929"` |
| `statusLine` | Custom status line configuration | `{"type": "command", "command": "~/.claude/statusline.sh"}` |
| `outputStyle` | Adjust system prompt output style | `"Explanatory"` |
| `forceLoginMethod` | Restrict login to specific account type | `"claudeai"` or `"console"` |
| `forceLoginOrgUUID` | Auto-select organization during login | `"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"` |

### Permission Settings

| Key | Description | Example |
|-----|-------------|---------|
| `allow` | Permission rules to allow tool use | `["Bash(git diff:*)"]` |
| `ask` | Permission rules to ask for confirmation | `["Bash(git push:*)"]` |
| `deny` | Permission rules to deny tool use | `["WebFetch", "Read(./.env)"]` |
| `additionalDirectories` | Additional working directories | `["../docs/"]` |
| `defaultMode` | Default permission mode | `"acceptEdits"` or `"plan"` or `"normal"` |
| `disableBypassPermissionsMode` | Prevent bypass permissions mode | `"disable"` |

**Permission Modes:**
- **normal**: Ask before every file change (safest)
- **acceptEdits** (auto-accept): Automatically accept changes (faster)
- **plan**: Read-only exploration (safest for analysis)

### MCP Settings

| Key | Description | Example |
|-----|-------------|---------|
| `enableAllProjectMcpServers` | Auto-approve all MCP servers in `.mcp.json` | `true` |
| `enabledMcpjsonServers` | Approve specific MCP servers | `["memory", "github"]` |
| `disabledMcpjsonServers` | Reject specific MCP servers | `["filesystem"]` |
| `useEnterpriseMcpConfigOnly` | Restrict to enterprise-managed MCP only | `true` |
| `allowedMcpServers` | Allowlist of MCP servers (enterprise) | `[{"serverName": "github"}]` |
| `deniedMcpServers` | Denylist of MCP servers (enterprise) | `[{"serverName": "filesystem"}]` |

### AWS Settings (Bedrock)

| Key | Description | Example |
|-----|-------------|---------|
| `awsAuthRefresh` | Custom script to modify `.aws` directory | `"aws sso login --profile myprofile"` |
| `awsCredentialExport` | Custom script outputting JSON with AWS credentials | `"/bin/generate_aws_grant.sh"` |

### Plugin Settings

| Key | Description | Example |
|-----|-------------|---------|
| `enabledPlugins` | Control which plugins are enabled | `{"formatter@company-tools": true}` |
| `extraKnownMarketplaces` | Additional plugin marketplaces | `{"company-tools": {"source": "github", "repo": "company/plugins"}}` |

### Hooks and Extensions

| Key | Description | Example |
|-----|-------------|---------|
| `hooks` | Custom commands before/after tool executions | `{"PreToolUse": {"Bash": "echo 'Running...'"}}` |
| `disableAllHooks` | Disable all hooks | `true` |

## Environment Variables

All environment variables can also be configured in `settings.json` via the `env` key.

### Authentication

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | API key for Claude SDK (sent as X-Api-Key header) |
| `ANTHROPIC_AUTH_TOKEN` | Custom Authorization header value (prefixed with "Bearer ") |
| `ANTHROPIC_CUSTOM_HEADERS` | Custom headers in "Name: Value" format |

### Model Configuration

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_MODEL` | Override default model |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Model for Haiku-class tasks |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Model for Sonnet-class tasks |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Model for Opus-class tasks |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Model for subagents |
| `MAX_THINKING_TOKENS` | Enable extended thinking with token budget |

### Bash Configuration

| Variable | Purpose |
|----------|---------|
| `BASH_DEFAULT_TIMEOUT_MS` | Default timeout for bash commands |
| `BASH_MAX_TIMEOUT_MS` | Maximum timeout model can set |
| `BASH_MAX_OUTPUT_LENGTH` | Max characters before middle-truncation |
| `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` | Return to original directory after each command |

### Feature Toggles

| Variable | Purpose |
|----------|---------|
| `DISABLE_AUTOUPDATER` | Disable automatic updates |
| `DISABLE_BUG_COMMAND` | Disable `/bug` command |
| `DISABLE_COST_WARNINGS` | Disable cost warning messages |
| `DISABLE_ERROR_REPORTING` | Opt out of Sentry error reporting |
| `DISABLE_TELEMETRY` | Opt out of Statsig telemetry |
| `DISABLE_NON_ESSENTIAL_MODEL_CALLS` | Disable flavor text model calls |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | Disable autoupdater, bug command, error reporting, telemetry |
| `CLAUDE_CODE_DISABLE_TERMINAL_TITLE` | Disable automatic terminal title updates |

### Prompt Caching

| Variable | Purpose |
|----------|---------|
| `DISABLE_PROMPT_CACHING` | Disable all prompt caching (precedence over per-model) |
| `DISABLE_PROMPT_CACHING_HAIKU` | Disable prompt caching for Haiku |
| `DISABLE_PROMPT_CACHING_SONNET` | Disable prompt caching for Sonnet |
| `DISABLE_PROMPT_CACHING_OPUS` | Disable prompt caching for Opus |

### MCP Configuration

| Variable | Purpose |
|----------|---------|
| `MCP_TIMEOUT` | MCP server startup timeout (milliseconds) |
| `MCP_TOOL_TIMEOUT` | MCP tool execution timeout (milliseconds) |
| `MAX_MCP_OUTPUT_TOKENS` | Maximum tokens in MCP tool responses (default: 25000) |

### Network Configuration

| Variable | Purpose |
|----------|---------|
| `HTTP_PROXY` | HTTP proxy server for network connections |
| `HTTPS_PROXY` | HTTPS proxy server for network connections |
| `NO_PROXY` | Domains/IPs to bypass proxy |

### Third-Party Providers

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_USE_BEDROCK` | Use Amazon Bedrock |
| `CLAUDE_CODE_USE_VERTEX` | Use Google Vertex AI |
| `CLAUDE_CODE_SKIP_BEDROCK_AUTH` | Skip AWS authentication |
| `CLAUDE_CODE_SKIP_VERTEX_AUTH` | Skip Google authentication |
| `AWS_BEARER_TOKEN_BEDROCK` | Bedrock API key |
| `VERTEX_REGION_CLAUDE_3_5_HAIKU` | Override region for Claude 3.5 Haiku (Vertex) |
| `VERTEX_REGION_CLAUDE_3_5_SONNET` | Override region for Claude 3.5 Sonnet (Vertex) |
| `VERTEX_REGION_CLAUDE_3_7_SONNET` | Override region for Claude 3.7 Sonnet (Vertex) |
| `VERTEX_REGION_CLAUDE_4_0_OPUS` | Override region for Claude 4.0 Opus (Vertex) |
| `VERTEX_REGION_CLAUDE_4_0_SONNET` | Override region for Claude 4.0 Sonnet (Vertex) |
| `VERTEX_REGION_CLAUDE_4_1_OPUS` | Override region for Claude 4.1 Opus (Vertex) |

### Authentication (mTLS)

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_CLIENT_CERT` | Path to client certificate file |
| `CLAUDE_CODE_CLIENT_KEY` | Path to client private key file |
| `CLAUDE_CODE_CLIENT_KEY_PASSPHRASE` | Passphrase for encrypted key (optional) |

### Other

| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Maximum output tokens for most requests |
| `CLAUDE_CODE_API_KEY_HELPER_TTL_MS` | Credential refresh interval (with apiKeyHelper) |
| `CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL` | Skip IDE extension auto-installation |
| `USE_BUILTIN_RIPGREP` | Use system rg instead of built-in (set to `0`) |
| `SLASH_COMMAND_TOOL_CHAR_BUDGET` | Max characters for slash command metadata (default: 15000) |

## Tools Available to Claude

Claude Code has access to these tools:

| Tool | Description | Permission Required |
|------|-------------|---------------------|
| **Bash** | Execute shell commands | Yes |
| **Edit** | Make targeted file edits | Yes |
| **Glob** | Find files by pattern | No |
| **Grep** | Search file contents | No |
| **NotebookEdit** | Modify Jupyter notebook cells | Yes |
| **NotebookRead** | Read Jupyter notebooks | No |
| **Read** | Read file contents | No |
| **SlashCommand** | Run custom slash command | Yes |
| **Task** | Run sub-agent for complex tasks | No |
| **TodoWrite** | Create and manage task lists | No |
| **WebFetch** | Fetch content from URL | Yes |
| **WebSearch** | Perform web searches | Yes |
| **Write** | Create or overwrite files | Yes |

**Configure tool permissions** with `/allowed-tools` or in permission settings.

## Excluding Sensitive Files

Prevent Claude Code from accessing sensitive files using `permissions.deny`:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(./config/credentials.json)",
      "Read(./build)"
    ]
  }
}
```

Files matching these patterns are completely invisible to Claude Code.

## Subagent Configuration

Custom AI subagents can be configured at user and project levels as Markdown files with YAML frontmatter:

- **User subagents**: `~/.claude/agents/` (available across all projects)
- **Project subagents**: `.claude/agents/` (project-specific, can be shared)

See [subagents documentation](/en/docs/claude-code/sub-agents) for details.

## Settings Precedence Summary

This hierarchy ensures enterprise security policies are always enforced while allowing teams and individuals to customize:

1. Enterprise managed policies (IT/DevOps deployed)
2. Command line arguments (temporary session overrides)
3. Local project settings (personal project preferences)
4. Shared project settings (team project settings)
5. User settings (personal global settings)

## Key Configuration System Points

- **Memory files (CLAUDE.md)**: Instructions and context loaded at startup
- **Settings files (JSON)**: Configure permissions, environment, tool behavior
- **Slash commands**: Custom commands invoked with `/command-name`
- **MCP servers**: Extend Claude Code with additional tools
- **Precedence**: Higher-level configs override lower-level ones
- **Inheritance**: Settings are merged with specific overriding broader

## Related Documentation

- **IAM and Permissions**: Learn about permission system and security
- **MCP Integration**: Connect to external tools and data sources
- **Subagents**: Create specialized AI assistants
- **Hooks**: Run custom commands before/after tool executions

---

**Last Updated:** 2025-10-21
**For More Details:** Run `/config` within Claude Code or see official documentation
