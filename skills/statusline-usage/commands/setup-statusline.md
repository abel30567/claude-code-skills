---
name: setup-statusline
description: Install the status line script and configure the scheduler for automatic usage updates
allowed-tools: Bash(*), Read, Write, Edit
---

Set up the statusline usage display. Follow these steps:

1. Create cache directory:
```bash
mkdir -p ~/.claude-statusline-usage
```

2. Copy the scraper:
```bash
cp "${CLAUDE_PLUGIN_ROOT}/scripts/scrape-usage.py" ~/.claude-statusline-usage/
chmod +x ~/.claude-statusline-usage/scrape-usage.py
```

3. Copy the status line script:
```bash
cp "${CLAUDE_PLUGIN_ROOT}/scripts/statusline.sh" ~/.claude/statusline.sh
chmod +x ~/.claude/statusline.sh
```

4. Read the user's current `~/.claude/settings.json` and add or update the `statusLine` key:
```json
{
  "statusLine": {
    "script": "~/.claude/statusline.sh"
  }
}
```

5. Ask the user if they want to install the scheduler for automatic updates every 15 minutes.

If yes, run the appropriate scheduler installer:
- macOS: `${CLAUDE_PLUGIN_ROOT}/scheduler/install-scheduler.sh`
- Linux: `${CLAUDE_PLUGIN_ROOT}/scheduler/install-scheduler.sh`

6. Run an initial scrape:
```bash
python3 ~/.claude-statusline-usage/scrape-usage.py --quiet
```

7. Confirm everything is set up and tell the user to restart Claude Code to see the status line.
