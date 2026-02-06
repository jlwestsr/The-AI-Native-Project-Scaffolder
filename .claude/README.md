# Claude Code Configuration — nebulus-forge

**Project Type:** Python CLI Scaffolding Tool
**Template Engine:** Jinja2
**Configuration Date:** 2026-02-06

---

## Overview

Per-project Claude Code plugin configuration for Nebulus Forge, the AI-native project scaffolding CLI with profile-driven templates and governance rules.

## Enabled Plugins

### High Priority

- ✅ **Pyright LSP** — Type checking for CLI and template engine
- ✅ **Superpowers** — TDD for template generation logic

### Medium Priority

- ✅ **Serena** — Navigate templates and CLI structure
- ✅ **Context7** — Live docs for typer, jinja2, questionary, pydantic
- ✅ **PR Review Toolkit** — Code quality checks
- ✅ **Commit Commands** — Git workflow automation
- ✅ **Feature Dev** — Feature development workflows

### Low Priority

- ✅ **GitHub** — Minimal GitHub needs

## Disabled Plugins

- ❌ **TypeScript LSP** — No TypeScript
- ❌ **Playwright** — No UI
- ❌ **Supabase** — Not using Supabase
- ❌ **Ralph Loop** — No automation loops

## LSP Configuration

### Pyright

Configuration: `pyrightconfig.json` (project root)

**Settings:**

- Type checking: basic
- Python version: 3.10+
- Include: `src/`
- Exclude: `__pycache__`, `.pytest_cache`
- Virtual environment: `./venv`

## Architecture

Forge is a template-driven scaffolder:

- Profile-driven configuration
- Jinja2 template engine
- Interactive CLI with questionary
- Governance rule enforcement
- Plugin configuration templates (Claude Code, pre-commit, etc.)

## Testing

Run tests via pytest:

```bash
pytest tests/ -v
```

## Workflow

This project follows the develop→main git workflow:

1. Branch off `develop` for new work
2. Merge features back to `develop` with `--no-ff`
3. Release from `develop` to `main` with version tags

## Why These Plugins?

**Superpowers (High Priority)** — Template generation logic must be test-driven. Incorrect templates break downstream projects.

**Context7** — Jinja2 and typer evolve. Live docs ensure we use current best practices for CLI and templates.

**Serena** — Template structure can be complex. Semantic navigation helps manage multiple template types.

**GitHub (Low Priority)** — Forge is primarily a local tool. GitHub integration less critical than other projects.

## Template Integration

Forge now includes Claude Code plugin configuration templates:

```text
src/forge/templates/.claude/
├── python-library.config.json
├── python-cli.config.json
├── multi-agent-cli.config.json
├── scaffolding-tool.config.json
├── full-stack-web.config.json
└── ansible-infrastructure.config.json
```

When scaffolding a new project, forge will prompt for project type and install the appropriate plugin configuration.

## Maintenance

Update this configuration when:

- Adding new template types
- Performance issues (disable low-value plugins)
- New Claude Code plugins that benefit scaffolding tools

---

*Part of the West AI Labs plugin strategy. See `../docs/claude-code-plugin-strategy.md` for ecosystem-wide strategy.*
