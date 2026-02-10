# Feature Title: Modular Scaffolder Refactor

> **Historical Note (v1)**: This feature describes the original v1 modular refactor. The v1 architecture (`src/project_generator/`) was fully replaced by the v2 profile-driven pipeline (`src/forge/`) in February 2026. See `docs/AI_INSIGHTS.md` Section 4 for the v2 architecture.

## Overview
Transform the single-file `init_project.py` script into a modular Python application. This change improves maintainability, allows for easier extension of templates, and follows standard Python project structure conventions.

## Requirements
- [x] Extract project templates into a separate module.
- [x] Separate Git operations from core scaffolding logic.
- [x] Implement a CLI entry point.
- [x] Support passing a target directory as a command-line argument.
- [x] Configure `pyproject.toml` to support the tool as an installable package.
- [x] Remove legacy single-file script.

## Technical Implementation (v2)
- **Module Structure** (`src/forge/`):
    - `models.py`: Pydantic data models for profiles, rendered files, lock entries.
    - `profile_loader.py`: TOML profile loading and inheritance resolution.
    - `renderer.py`: Pure Jinja2 template rendering (no I/O).
    - `applier.py`: File writing to disk with strategies (CREATE/UPDATE/FORCE).
    - `lockfile.py`: `.forge.lock` management for safe updates.
    - `pipeline.py`: Orchestrates load → render → apply stages.
    - `wizard.py`: Interactive prompts for profile variables.
    - `workspace.py` / `workspace_wizard.py`: Ecosystem-level scaffolding.
    - `cli.py`: Typer-based CLI entry point.
- **Profiles** (`profiles/`): TOML-based profile definitions with Jinja2 templates.
- **CLI**: Typer app with commands: `new`, `update`, `info`, `profiles`, `workspace`.
- **Installation**: Defined `forge` script in `pyproject.toml` (`forge = "forge.cli:app"`).

## Acceptance Criteria
- [x] CLI can be executed via `forge new <target>`.
- [x] Scaffolding produces profile-driven output from TOML definitions.
- [x] Lock file (`.forge.lock`) prevents accidental overwrites during updates.
- [x] Interactive wizard collects profile variables.
- [x] New projects include AI collaboration files (`CLAUDE.md`, `AI_INSIGHTS.md`).

## Feedback/Notes
The v1 refactor served as a baseline. The v2 rewrite replaced the MVC pattern with a profile-driven pipeline for better extensibility — new profiles require zero Python code.
