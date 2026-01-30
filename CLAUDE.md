# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin repository containing reusable "skills" that extend Claude's capabilities. Skills are installed via the plugin system and provide specialized tools, hooks, and knowledge.

## Architecture

### Skill Structure

Each skill is a self-contained plugin in `skills/<name>/`:
```
skills/<name>/
├── .claude-plugin/
│   └── plugin.json    # Skill's manifest (hooks, metadata)
├── SKILL.md           # YAML frontmatter + usage instructions for Claude
├── README.md          # User-facing documentation
├── commands/          # Slash commands (auto-discovered)
├── hooks/             # Shell scripts for lifecycle events
└── scripts/           # Utilities invoked by hooks or commands
```

### Plugin Distribution

The root `.claude-plugin/marketplace.json` is a catalog listing available skills. Each skill's `source` points to its directory, which contains its own `plugin.json`.

Users install individual skills:
```bash
/plugin marketplace add abel30567/claude-code-skills
/plugin install statusline-usage@abel30567-skills
```

Skills are independent - installing one does not install another's hooks or commands.

### Hook Execution

Hooks use `${CLAUDE_PLUGIN_ROOT}` which resolves to the skill's root directory:
```json
{
  "command": "${CLAUDE_PLUGIN_ROOT}/hooks/my-hook.sh"
}
```

## Creating New Skills

1. Create `skills/<name>/` with `.claude-plugin/plugin.json` and `SKILL.md`
2. Add slash commands in `commands/` directory
3. Add hooks to `plugin.json` and create `hooks/` directory as needed
4. Register in root `.claude-plugin/marketplace.json` under `plugins` array

## ABOUTME Convention

Code files use ABOUTME headers (first 2 lines) for semantic indexing:

```python
# ABOUTME: Brief description of what this file does.
# ABOUTME: Additional context about its purpose.
```
