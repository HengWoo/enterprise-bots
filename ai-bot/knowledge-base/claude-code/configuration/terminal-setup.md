# Terminal Setup and Optimization

> Optimize your terminal for the best Claude Code experience

## Themes and Appearance

Claude Code cannot control your terminal theme - that's handled by your terminal application.

**Match theme to terminal:** Use `/config` command within Claude Code anytime

**Custom status line:** Configure a [custom status line](/en/docs/claude-code/statusline) to display contextual information (model, working directory, git branch) at the bottom of your terminal.

## Line Breaks

### Three Options for Entering Line Breaks

**1. Quick Escape**
Type `\` followed by Enter to create a newline

**2. Shift+Enter (VS Code or iTerm2)**
Run `/terminal-setup` within Claude Code to automatically configure Shift+Enter

**3. Option+Enter (Terminal.app, iTerm2, VS Code)**

**For macOS Terminal.app:**
1. Open Settings → Profiles → Keyboard
2. Check "Use Option as Meta Key"

**For iTerm2 and VS Code terminal:**
1. Open Settings → Profiles → Keys
2. Under General, set Left/Right Option key to "Esc+"

## Notification Setup

Never miss when Claude completes a task with proper notification configuration.

### iTerm 2 System Notifications

**Setup for iTerm 2 alerts:**

1. Open iTerm 2 Preferences
2. Navigate to Profiles → Terminal
3. Enable "Silence bell"
4. Set Filter Alerts → "Send escape sequence-generated alerts"
5. Set your preferred notification delay

**Note:** These notifications are specific to iTerm 2 and not available in default macOS Terminal.

### Custom Notification Hooks

For advanced notification handling, create [notification hooks](/en/docs/claude-code/hooks#notification) to run your own logic.

## Handling Large Inputs

When working with extensive code or long instructions:

**❌ Avoid:** Direct pasting of very long content
- Claude Code may struggle with lengthy pasted content
- Particularly problematic in VS Code terminal

**✅ Use:** File-based workflows
1. Write content to a file
2. Ask Claude to read the file

Example:
```
> Read the content from long-instructions.txt and implement the changes
```

**Limitation:** VS Code terminal is particularly prone to truncating long pastes

## Vim Mode

Claude Code supports a subset of Vim keybindings.

**Enable Vim Mode:**
- Command: `/vim`
- Configure: `/config`

**Supported Vim Features:**

**Mode Switching:**
- `Esc` - Switch to NORMAL mode
- `i` / `I` - Insert mode
- `a` / `A` - Append mode
- `o` / `O` - Open new line mode

**Navigation:**
- `h` / `j` / `k` / `l` - Left/down/up/right
- `w` / `e` / `b` - Word forward/end/back
- `0` / `$` / `^` - Line start/end/first non-blank
- `gg` / `G` - File start/end

**Editing:**
- `x` - Delete character
- `dw` / `de` / `db` / `dd` / `D` - Delete word/to end/to beginning/line/to end of line
- `cw` / `ce` / `cb` / `cc` / `C` - Change word/to end/to beginning/line/to end of line
- `.` - Repeat last edit

**Not Supported:**
- Visual mode
- Macros
- Complex motion commands
- Register operations
- Most advanced Vim features

## Terminal-Specific Tips

### VS Code Integrated Terminal

**Advantages:**
- Legacy CLI integration auto-installs
- Automatic context sharing
- IDE diff viewing
- Diagnostic sharing

**Limitations:**
- May truncate long pastes
- Limited notification support

**Best Practices:**
- Use file-based workflows for large inputs
- Enable Restricted Mode for untrusted workspaces
- Use `/ide` command if integration doesn't auto-activate

### External Terminal (iTerm2, Terminal.app, etc.)

**Advantages:**
- Better handling of large pastes
- Native notification support (iTerm2)
- More customization options

**Connection to IDE:**
- Use `/ide` command to connect to VS Code instance
- Requires IDE CLI command installed (`code`, `cursor`, etc.)

**Best Practices:**
- Configure notification settings
- Set up Option/Shift+Enter for line breaks
- Use `/terminal-setup` for quick configuration

### Windows Terminal / PowerShell

**Line Break Support:**
- `\` + Enter works
- Configure Shift+Enter if desired

**Best Practices:**
- Native Windows requires `cmd /c` wrapper for MCP npx commands
- WSL recommended for better compatibility
- Use PowerShell 7+ for best experience

## Quick Setup Checklist

**Essential Configuration:**
- [ ] Match Claude Code theme to terminal theme (`/config`)
- [ ] Set up line break method (Shift+Enter or Option+Enter)
- [ ] Configure notifications (if using iTerm2)
- [ ] Test large input handling (use file-based workflow)

**Optional Enhancements:**
- [ ] Enable Vim mode (`/vim`) if preferred
- [ ] Configure custom status line
- [ ] Set up notification hooks
- [ ] Configure IDE integration (if using VS Code)

## Troubleshooting

**Issue:** Line breaks not working
**Solution:** Run `/terminal-setup` or manually configure Option as Meta key

**Issue:** Large pastes get truncated
**Solution:** Save content to file, ask Claude to read it

**Issue:** No notifications when task completes
**Solution:** Configure iTerm2 notification settings or create custom notification hooks

**Issue:** Vim mode not behaving as expected
**Solution:** Remember only subset is supported - check supported commands list

**Issue:** VS Code integration not working
**Solution:** Ensure running `claude` from VS Code integrated terminal, or use `/ide` command

## Related Documentation

- **Hooks Guide**: Custom commands for notifications and automation
- **Status Line**: Customize bottom-of-screen context display
- **VS Code Integration**: IDE-specific setup and features

---

**Last Updated:** 2025-10-21
**Supported Terminals:** macOS Terminal.app, iTerm2, VS Code integrated terminal, Windows Terminal, PowerShell
