# Changelog

All notable changes to **Forge** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
