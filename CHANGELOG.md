# Changelog

All notable changes to **Forge** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed
- Public `forge new` profiles: **`claude-governance`** (merged into `base`), **`openclaw-agent`**, **`workspace`**.
- Only **`base`** and **`fullstack`** remain as project profiles.

### Changed
- Claude hooks/skills/ADR/prompt templates now ship as part of **`base`**.
- `fullstack` inherits **`base`** directly.
- WAL ecosystem templates live under `templates/workspace/` for `forge workspace` only.

### Added
- **`monorepo` profile** — west_ai_labs-shaped control plane (LAYOUT, products/services/hosts/lab, example-app, generic AGENTS services stub); neo pack default remains `workspace`.
- **docs/creating-a-profile.md** — tutorial for authoring custom Forge profiles.
- **docs/README.md**, **docs/profiles.md** — documentation index and shipped-profile overview.
- **neo-harness post-hook**: `forge new --neo auto|on|off` runs `neo init-workspace` when neo is installed (`FORGE_NEO_CMD` / PATH / lab paths).
- **Variable defaults** for non-interactive runs (`apply_variable_defaults`: project_name from target, use_pip, project_slug, profile defaults).
- **Base layout refresh**: `AGENTS.md`, `workspace/scratchpad/`, `docs/ops/`, `agents/`.
- **docs/reevaluation-2026-08.md**: Forge vs neo roles and stale-template review.

### Changed
- Default Python version in base profile: **3.12**.
- README rewritten for `forge new` + neo composition (removed stale `forge .` examples).
- `FORGE_PROFILES_DIR` supported for profile discovery.

### Added (prior)
- **`claude-governance` profile**: New composable profile providing Claude Code enforcement layer — `.claude/hooks/` (guardrail-check + changelog-update), `.claude/skills/` (code-review, refactor, release), `docs/decisions/` (ADR template), `tools/prompts/` (versioned prompt library). All templates are Jinja2 with project_name interpolation.
- **Governance inheritance wired to all profiles**: `fullstack`, `openclaw-agent`, and `workspace` now inherit from `claude-governance` (which inherits `base`). Chain: `base` ← `claude-governance` ← `{fullstack|openclaw-agent|workspace}`. Every project stamped with these profiles gets the full governance layer automatically.
- **`workspace` profile.toml**: Added missing `profile.toml` to the `workspace` profile to formalize its inheritance chain.

### Changed
- **Universal Ansible Scaffolding**: All profiles (`fullstack`, `web`, `system`) now include a production-ready `ansible/` directory with `setup_workstation.yml`, `ansible.cfg`, and `inventory.ini`.
- **Strict Code Quality Enforcement**: Integrated `pre-commit` hooks for `pytest`, `flake8`, `yamllint`, and `ansible-lint`.
- **MVC Structure for Web Profile**: The `web` profile now enforces a strict Model-View-Controller (MVC) directory structure (`src/backend/app/{models,routers,services}`).
- **Yamllint Configuration**: Added `.yamllint` and `.yamllint.j2` with strict rules compatible with Ansible.

### Changed
- **Dependencies**: Cleaned up `requirements.txt` to remove unused data science libraries and updated `requirements-dev.txt` to include necessary linting tools.
- **Architecture (v2 Rewrite)**: Replaced v1 MVC architecture (`src/project_generator/`) with profile-driven pipeline in `src/forge/`. Core modules: `models.py`, `profile_loader.py`, `renderer.py`, `applier.py`, `lockfile.py`, `pipeline.py`, `cli.py`, `wizard.py`.
- **Template System**: Moved from hardcoded Python dicts to TOML-based profile definitions (`profiles/*/profile.toml` + `structure.toml`) with Jinja2 templates in `profiles/*/templates/`.
- **Workspace Scaffolding (v0.2.0)**: Added `forge workspace` subcommand group with `workspace.py`, `workspace_wizard.py`, and governance templates (`BUSINESS.md`, `OVERLORD.md`, `CLAUDE.md`).

### Fixed
- **Whitespace Issues**: Resolved persistent whitespace and newline errors in generated files and internal tests.
