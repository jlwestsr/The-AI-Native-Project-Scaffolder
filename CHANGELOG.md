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
- **Engine Logic**: Refactored `src/project_generator/engine.py` to fix whitespace handling and improve generation reliability.
- **Template System**: Updated `src/project_generator/assets/configs.py` to support the new directory structures and universal Ansible inclusion.

### Fixed
- **Whitespace Issues**: Resolved persistent whitespace and newline errors in generated files and internal tests.
