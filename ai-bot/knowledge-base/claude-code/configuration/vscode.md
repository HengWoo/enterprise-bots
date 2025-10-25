# Visual Studio Code Integration

> Use Claude Code with VS Code through native extension or CLI integration

## VS Code Extension (Beta)

The VS Code extension provides a native graphical interface integrated directly into your IDE, making Claude Code accessible for users who prefer a visual interface.

### Features

- **Native IDE experience**: Dedicated sidebar panel accessed via Spark icon
- **Plan mode with editing**: Review and edit Claude's plans before accepting
- **Auto-accept edits mode**: Automatically apply Claude's changes
- **File management**: @-mention files or attach via system file picker
- **MCP server usage**: Use MCP servers configured through CLI
- **Conversation history**: Easy access to past conversations
- **Multiple sessions**: Run multiple Claude Code sessions simultaneously
- **Keyboard shortcuts**: Most CLI shortcuts supported
- **Slash commands**: Access CLI slash commands directly

### Requirements

- VS Code 1.98.0 or higher

### Installation

Install from [VS Code Extension Marketplace](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code)

### Updating

1. Open command palette: `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Search for "Claude Code: Update"
3. Select the command to update

### How to Use

1. Click Spark icon in sidebar to open Claude Code panel
2. Prompt Claude as you would in terminal
3. Watch Claude analyze code and suggest changes
4. Review and accept edits directly

**Tip:** Drag sidebar wider to see inline diffs, then click to expand for full details.

### Using Third-Party Providers

The extension supports Bedrock and Vertex AI. When configured, no login prompt appears.

**Configuration Steps:**

1. Open VS Code settings
2. Search for "Claude Code: Environment Variables"
3. Add required environment variables

**Required Environment Variables:**

| Variable | Description | Required For | Example |
|----------|-------------|--------------|---------|
| `CLAUDE_CODE_USE_BEDROCK` | Enable Bedrock | Bedrock | `"1"` or `"true"` |
| `CLAUDE_CODE_USE_VERTEX` | Enable Vertex AI | Vertex AI | `"1"` or `"true"` |
| `ANTHROPIC_API_KEY` | API key | Both | `"your-api-key"` |
| `AWS_REGION` | AWS region | Bedrock | `"us-east-2"` |
| `AWS_PROFILE` | AWS profile | Bedrock | `"your-profile"` |
| `CLOUD_ML_REGION` | Vertex region | Vertex AI | `"global"` or `"us-east5"` |
| `ANTHROPIC_VERTEX_PROJECT_ID` | GCP project ID | Vertex AI | `"your-project-id"` |
| `ANTHROPIC_MODEL` | Override primary model | Optional | `"us.anthropic.claude-3-7-sonnet-20250219-v1:0"` |
| `ANTHROPIC_SMALL_FAST_MODEL` | Override small/fast model | Optional | `"us.anthropic.claude-3-5-haiku-20241022-v1:0"` |

**See Also:**
- [Claude Code on Amazon Bedrock](/en/docs/claude-code/amazon-bedrock)
- [Claude Code on Google Vertex AI](/en/docs/claude-code/google-vertex-ai)

### Not Yet Implemented

Features not yet available in VS Code extension:

- **Full MCP server configuration**: Configure via CLI first, then extension uses them
- **Subagents configuration**: Configure via CLI to use in VS Code
- **Checkpoints**: Save/restore conversation state at specific points
- **Advanced shortcuts**:
  - `#` shortcut to add to memory
  - `!` shortcut to run bash commands directly
- **Tab completion**: File path completion with tab key

We're working on adding these features in future updates.

## Security Considerations

When Claude Code runs in VS Code with auto-edit permissions, it may modify IDE config files that can auto-execute.

**Risk**: May increase risk of running in auto-edit mode and allow bypassing permission prompts for bash execution.

**Recommendations:**
- Enable [VS Code Restricted Mode](https://code.visualstudio.com/docs/editor/workspace-trust#_restricted-mode) for untrusted workspaces
- Use manual approval mode for edits
- Ensure Claude is only used with trusted prompts

## Legacy CLI Integration

The legacy integration allows Claude Code running in terminal to interact with your IDE.

**Features:**
- **Selection context sharing**: Current selection/tab automatically shared
- **Diff viewing**: View diffs in IDE instead of terminal
- **File reference shortcuts**: `Cmd+Option+K` (Mac) or `Alt+Ctrl+K` (Windows/Linux) to insert file references like @File#L1-99
- **Automatic diagnostic sharing**: Lint and syntax errors

**Setup:**

1. **Auto-install**: Run `claude` from VS Code's integrated terminal - all features activate automatically

2. **External terminal**: Use `/ide` command to connect Claude Code to VS Code instance

3. **Configuration**: Run `claude`, enter `/config`, set diff tool to `auto` for automatic IDE detection

**Compatibility:**
- Visual Studio Code
- Cursor
- Windsurf
- VSCodium

## Troubleshooting

### Extension Not Installing

- Ensure VS Code 1.85.0 or later
- Check VS Code has permission to install extensions
- Try installing directly from marketplace website

### Legacy Integration Not Working

**Issue:** Integration not activating

**Solutions:**

1. Ensure running Claude Code from VS Code's integrated terminal

2. Ensure IDE CLI command is installed:
   - **VS Code**: `code` command
   - **Cursor**: `cursor` command
   - **Windsurf**: `windsurf` command
   - **VSCodium**: `codium` command

3. If command isn't installed:
   - Open command palette: `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Search for "Shell Command: Install 'code' command in PATH"
   - Run command (replace 'code' with your IDE's command)

**For additional help:** See [troubleshooting guide](/en/docs/claude-code/troubleshooting)

## Quick Reference

**VS Code Extension:**
- **Install**: VS Code Extension Marketplace
- **Activate**: Click Spark icon in sidebar
- **Update**: Command palette → "Claude Code: Update"

**Legacy CLI Integration:**
- **Activate**: Run `claude` from VS Code integrated terminal
- **Connect external terminal**: Use `/ide` command
- **Configure**: `/config` → set diff tool to `auto`

---

**Last Updated:** 2025-10-21
**Extension Version:** Beta
**Compatibility:** VS Code 1.98.0+ (and variants: Cursor, Windsurf, VSCodium)
