# Claude Code Skills

A collection of Claude Code skills by abel30567.

## Installation

```bash
# Add the marketplace
/plugin marketplace add abel30567/claude-code-skills

# Install a specific skill
/plugin install statusline-usage@abel30567-skills
```

## Available Skills

### statusline-usage

Display Claude API usage limits in your Claude Code status line. Shows session (5hr) and weekly usage percentages alongside context window usage and session cost.

```
Ctx:45% | 5hr:30% | Wk:50% | $3.25
```

**How it works:**

1. A Python scraper queries Claude CLI via PTY automation
2. Results are cached and refreshed every 15 minutes via scheduler
3. The status line script reads the cache and formats it for display

**Commands:**
- `/check-usage` - Check usage on-demand
- `/setup-statusline` - Install status line and scheduler

[Full documentation](skills/statusline-usage/README.md)

## License

MIT
