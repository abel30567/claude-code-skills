---
name: statusline-usage
description: Check Claude API usage limits. Shows current session (5hr) and weekly usage percentages. Use when asking about rate limits, usage, or quota.
---

# Statusline Usage

Scrapes Claude CLI usage data via PTY automation and caches it for status line display.

## Usage

Run the scraper to get current usage:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/scrape-usage.py" --json
```

Parse the JSON output and display it to the user in a formatted way:

```
📊 Claude Usage Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session (5hr):  ██████████░░░░░░░░░░  45%
Weekly:         ████████░░░░░░░░░░░░  32%
```

If the scraper fails, inform the user they can run `/usage` directly in Claude Code.

## Commands

| Command | Description |
|---------|-------------|
| `/check-usage` | Check current usage limits on-demand |
| `/setup-statusline` | Install status line and scheduler |

## Status Line Format

When configured, the status line shows:

```
Ctx:45% | 5hr:30% | Wk:50% | $3.25
```

## Setup

Run `/setup-statusline` to install the status line script and configure the scheduler.
