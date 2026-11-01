# Gate-OS AI Workspace

This directory documents the repository-shared Copilot workspace created for the Steel Gate overhaul.

## Layout

- `.github/copilot-instructions.md`: repository-wide mission and engineering rules.
- `.github/instructions/`: path-scoped instructions with narrow `applyTo` globs.
- `.github/agents/`: specialist charters, definitions of done, and handoffs.
- `.github/skills/`: reusable workflows with procedures and verification checklists.
- `.github/prompts/`: focused task entry points.
- `.vscode/mcp.json`: reviewed MCP connections; authentication is external and secrets are never committed.
- `.vscode/extensions.json` and `.vscode/settings.json`: team recommendations and safe defaults.
- `.devcontainer/`: unprivileged development container; ISO work is explicitly separate.

## Compatibility note

VS Code documentation currently distinguishes portable `mcpServers` from VS Code `servers`; this repository uses the VS Code format in `.vscode/mcp.json`. Workspace MCP configuration remains subject to VS Code version and harness support. External servers must be reviewed, authenticated through supported flows, and verified with a low-impact tool call before use. The Playwright entry is intentionally marked `latest` only as a development placeholder; pin the publisher-reviewed version before CI or release use.

Agent front matter is kept minimal (`name`, `description`, optional `model`) to remain compatible with current custom-agent discovery. If VS Code changes supported keys or locations, record the migration here and in the next checkpoint report.
