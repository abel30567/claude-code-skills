---
name: check-usage
description: Check current Claude API session and weekly usage limits
allowed-tools: Bash(python3*)
---

Run the usage scraper and display results:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/scrape-usage.py" --force
```

Display the output to the user. If it fails, suggest running `/usage` directly.
