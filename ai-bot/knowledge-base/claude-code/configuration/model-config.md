# Model Configuration

> Learn about Claude Code model configuration, aliases, and selection

## Available Models

You can configure Claude Code with:
- A **model alias** (recommended)
- A full **[model name](/en/docs/about-claude/models/overview#model-names)**
- For Bedrock, an ARN

### Model Aliases

Convenient shortcuts for model selection without remembering exact version numbers:

| Alias | Behavior |
|-------|----------|
| **`default`** | Recommended model based on your account type |
| **`sonnet`** | Latest Sonnet model (currently Sonnet 4.5) for daily coding |
| **`opus`** | Opus model (currently Opus 4.1) for complex reasoning |
| **`haiku`** | Fast and efficient Haiku for simple tasks |
| **`sonnet[1m]`** | Sonnet with 1 million token context window for long sessions |
| **`opusplan`** | Uses `opus` in plan mode, switches to `sonnet` for execution |

### Setting Your Model

**Priority order (highest to lowest):**

1. **During session**: Use `/model <alias|name>` to switch mid-session
2. **At startup**: Launch with `claude --model <alias|name>`
3. **Environment variable**: Set `ANTHROPIC_MODEL=<alias|name>`
4. **Settings file**: Configure in `settings.json` using `model` field

**Examples:**

```bash
# Start with Opus
claude --model opus

# Switch to Sonnet during session
/model sonnet
```

**Settings file example:**
```json
{
  "permissions": { ... },
  "model": "opus"
}
```

## Special Model Behavior

### `default` Model Setting

Behavior depends on your account type.

**For certain Max users:** Claude Code automatically falls back to Sonnet if you hit usage threshold with Opus.

### `opusplan` Model Setting

Automated hybrid approach:

- **In plan mode**: Uses `opus` for complex reasoning and architecture decisions
- **In execution mode**: Automatically switches to `sonnet` for code generation

**Benefit:** Opus's superior reasoning for planning + Sonnet's efficiency for execution.

### Extended Context with [1m]

For Console/API users, add `[1m]` suffix to full model names for 1 million token context window.

```bash
# Example with extended context
/model anthropic.claude-sonnet-4-5-20250929-v1:0[1m]
```

**Note:** Extended context models have different pricing. See [long context pricing](/en/docs/about-claude/pricing#long-context-pricing).

## Checking Current Model

View your current model via:

1. **Status line** (if configured)
2. **`/status` command** (also displays account information)

## Environment Variables for Model Control

These environment variables must use full **model names**:

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Model for `opus` alias, or `opusplan` in Plan Mode |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Model for `sonnet` alias, or `opusplan` in execution |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Model for `haiku` alias, or background functionality |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Model for subagents |

**Note:** `ANTHROPIC_SMALL_FAST_MODEL` is deprecated in favor of `ANTHROPIC_DEFAULT_HAIKU_MODEL`.

## Prompt Caching Configuration

Claude Code automatically uses [prompt caching](/en/docs/build-with-claude/prompt-caching) to optimize performance and reduce costs.

**Control prompt caching:**

| Variable | Description |
|----------|-------------|
| `DISABLE_PROMPT_CACHING` | Disable for all models (takes precedence) |
| `DISABLE_PROMPT_CACHING_HAIKU` | Disable for Haiku only |
| `DISABLE_PROMPT_CACHING_SONNET` | Disable for Sonnet only |
| `DISABLE_PROMPT_CACHING_OPUS` | Disable for Opus only |

**Usage:**
```bash
# Disable all prompt caching
export DISABLE_PROMPT_CACHING=1
claude

# Disable only for Sonnet
export DISABLE_PROMPT_CACHING_SONNET=1
claude
```

**Use Cases for Disabling:**
- Debugging specific models
- Working with cloud providers with different caching implementations
- Cost control in specific scenarios
- Testing without cache benefits

## Model Selection Guide

### When to Use Each Model

**Sonnet (Default for Most Tasks)**
- ✅ Daily coding tasks
- ✅ Code refactoring
- ✅ Bug fixes
- ✅ Documentation
- ✅ Test writing
- ✅ General development

**Opus (Complex Reasoning)**
- ✅ Architectural decisions
- ✅ Complex algorithm design
- ✅ System design
- ✅ Performance optimization strategies
- ✅ Security analysis
- ✅ Planning phase of large features

**Haiku (Fast & Simple)**
- ✅ Simple queries
- ✅ Code formatting
- ✅ Quick fixes
- ✅ File operations
- ✅ Background tasks
- ✅ Simple refactoring

**Opusplan (Hybrid Approach)**
- ✅ Large features requiring planning
- ✅ Multi-step implementations
- ✅ Complex refactoring projects
- ✅ System-wide changes
- **Benefit:** Smart switching between Opus (planning) and Sonnet (execution)

**Sonnet[1m] (Extended Context)**
- ✅ Very large codebases
- ✅ Long conversation sessions
- ✅ Working with extensive documentation
- ✅ Analyzing large files
- **Note:** Different pricing applies

## Model Switching Strategies

### During Development

**Start with appropriate model:**
```bash
# For new feature with planning
claude --model opusplan

# For quick fixes
claude --model sonnet

# For simple tasks
claude --model haiku
```

**Switch mid-session as needed:**
```
# Upgrade to Opus for complex decision
> /model opus
> How should I architect the caching layer?

# Switch back to Sonnet for implementation
> /model sonnet
> Implement the caching layer based on that design
```

### For Different Project Types

**Large-scale systems:**
- Start: `opusplan` or `opus`
- Reason: Need strong architectural thinking

**Microservices / Small projects:**
- Start: `sonnet`
- Reason: Balance of capability and speed

**Scripts / Utilities:**
- Start: `haiku` or `sonnet`
- Reason: Straightforward implementation

**Legacy codebases:**
- Start: `sonnet[1m]` if very large
- Reason: Need extended context for understanding

## Cost Optimization

**Strategies:**

1. **Use appropriate model tier:**
   - Don't use Opus for simple tasks
   - Haiku for quick operations
   - Sonnet for most work

2. **Leverage prompt caching:**
   - Enabled by default
   - Reduces repeated context costs
   - Especially beneficial for long sessions

3. **Use opusplan for hybrid approach:**
   - Opus where it matters (planning)
   - Sonnet for implementation (lower cost)

4. **Monitor usage with `/status`:**
   - Check current model
   - Verify account type
   - Understand usage patterns

## Troubleshooting

**Issue:** Model not switching
**Solution:** Check `/status` to verify current model, use `/model <alias>` to switch

**Issue:** Unexpected model behavior
**Solution:** Verify model setting with `/status`, check environment variables

**Issue:** High costs
**Solution:** Review model usage, consider using Haiku or Sonnet instead of Opus, leverage prompt caching

**Issue:** Need more context
**Solution:** Use `sonnet[1m]` for extended context (API users only)

**Issue:** Slow responses
**Solution:** Switch to Haiku for simple tasks, check network connection

## Quick Reference

**Check current model:**
```
> /status
```

**Switch models:**
```
> /model sonnet
> /model opus
> /model haiku
> /model opusplan
```

**Set default model:**
```bash
# Via environment variable
export ANTHROPIC_MODEL=opus
claude

# Via settings file
{
  "model": "opus"
}
```

**Disable prompt caching:**
```bash
export DISABLE_PROMPT_CACHING=1
```

---

**Last Updated:** 2025-10-21
**Current Models:** Sonnet 4.5, Opus 4.1, Haiku (latest)
**For Pricing:** See [Claude pricing documentation](/en/docs/about-claude/pricing)
