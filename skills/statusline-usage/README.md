# statusline-usage

Display Claude API usage limits (session 5hr and weekly percentages) in your Claude Code status line.

## What it shows

```
Ctx:45% | 5hr:30% | Wk:50% | $3.25
```

- **Ctx** - Context window usage (from Claude Code)
- **5hr** - Rolling 5-hour session limit
- **Wk** - Weekly quota across all models
- **$** - Session cost

## Installation

```bash
/plugin marketplace add abel30567/claude-code-skills
/plugin install statusline-usage@abel30567-skills
```

Then run `/setup-statusline` to configure the status line and scheduler.

## Commands

| Command | Description |
|---------|-------------|
| `/check-usage` | Check current usage limits on-demand |
| `/setup-statusline` | Install status line script and scheduler |

## How it works

1. A Python scraper spawns Claude CLI in a PTY, sends `/usage`, and parses the output
2. Results are cached to `~/.claude-statusline-usage/cache.json`
3. A scheduler (LaunchAgent/cron) refreshes the cache every 15 minutes
4. The status line script reads the cache and formats it for display

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `CLAUDE_USAGE_CACHE_DIR` | `~/.claude-statusline-usage` | Cache directory |
| `CLAUDE_USAGE_CACHE_TTL` | `14400` (4 hours) | Cache validity in seconds |

## Platform Support

| Platform | Scraper | Scheduler |
|----------|---------|-----------|
| macOS | PTY automation | LaunchAgent |
| Linux | PTY automation | cron |
| Windows | Manual only | Task Scheduler (reminder) |

## Troubleshooting

- **No 5hr/Wk data**: Run `python3 ~/.claude-statusline-usage/scrape-usage.py --force`
- **Debug logs**: `cat ~/.claude-statusline-usage/debug.log`
- **Scheduler status (macOS)**: `launchctl list | grep claude`
- **Scheduler status (Linux)**: `crontab -l | grep scrape`
