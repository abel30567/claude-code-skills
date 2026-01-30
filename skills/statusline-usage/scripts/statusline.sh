#!/bin/bash
# ABOUTME: Status line script that reads cached usage data and formats it for Claude Code.
# ABOUTME: Shows context%, session 5hr%, weekly%, and session cost in the status bar.

# Configure in ~/.claude/settings.json:
#   "statusLine": { "script": "~/.claude/statusline.sh" }
#
# Environment variables:
#   CLAUDE_USAGE_CACHE_DIR - Cache directory (default: ~/.claude-statusline-usage)
#   CLAUDE_USAGE_CACHE_TTL - Cache TTL in seconds (default: 14400 = 4 hours)

set -e

INPUT=$(cat)

CACHE_DIR="${CLAUDE_USAGE_CACHE_DIR:-$HOME/.claude-statusline-usage}"
CACHE_FILE="$CACHE_DIR/cache.json"
CACHE_TTL="${CLAUDE_USAGE_CACHE_TTL:-14400}"

CONTEXT=$(echo "$INPUT" | jq -r '.context_window.used_percentage // 0' 2>/dev/null | cut -d'.' -f1)
COST=$(echo "$INPUT" | jq -r '.cost.total_cost_usd // 0' 2>/dev/null)

SESSION_USED=""
WEEKLY_USED=""

if [ -f "$CACHE_FILE" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        CACHE_MTIME=$(stat -f %m "$CACHE_FILE" 2>/dev/null || echo 0)
    else
        CACHE_MTIME=$(stat -c %Y "$CACHE_FILE" 2>/dev/null || echo 0)
    fi
    CACHE_AGE=$(( $(date +%s) - CACHE_MTIME ))

    if [ "$CACHE_AGE" -lt "$CACHE_TTL" ]; then
        SESSION_USED=$(jq -r '.session.used // empty' "$CACHE_FILE" 2>/dev/null)
        WEEKLY_USED=$(jq -r '.weekly.used // empty' "$CACHE_FILE" 2>/dev/null)
    fi
fi

OUT="Ctx:${CONTEXT}%"

if [ -n "$SESSION_USED" ]; then
    OUT="$OUT | 5hr:${SESSION_USED}%"
fi

if [ -n "$WEEKLY_USED" ]; then
    OUT="$OUT | Wk:${WEEKLY_USED}%"
fi

if [ "$COST" != "0" ] && [ "$COST" != "null" ] && [ -n "$COST" ]; then
    COST_FMT=$(printf "%.2f" "$COST")
    OUT="$OUT | \$$COST_FMT"
fi

echo "$OUT"
