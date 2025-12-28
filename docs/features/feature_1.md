# Feature Title: Modular Scaffolder Refactor

## Overview
Transform the single-file `init_project.py` script into a modular Python application. This change improves maintainability, allows for easier extension of templates, and follows standard Python project structure conventions.

## Requirements
- [x] Extract project templates into a separate module.
- [x] Separate Git operations from core scaffolding logic.
- [x] Implement a CLI entry point using `argparse`.
- [x] Support passing a target directory as a command-line argument.
- [x] Configure `pyproject.toml` to support the tool as an installable package.
- [x] Remove legacy single-file script.

## Technical Implementation
- **Module Structure**: 
    - `src/project_generator/assets/`: Templates and configurations.
    - `src/project_generator/engine.py`: Directory and file creation logic.
    - `src/project_generator/git_ops.py`: Git commands and shell utilities.
    - `src/project_generator/cli.py`: CLI orchestration.
- **CLI**: Added argument parsing for `target_dir` with a default of the current working directory.
- **Installation**: Defined `forge-project` script in `pyproject.toml`.

## Acceptance Criteria
- [x] Script can be executed via `python -m project_generator.cli`.
- [x] Scaffolding produces identical results to the legacy script.
- [x] Target directory check (greenfield) still prevents accidental overwrites.
- [x] Git initialization correctly sets up `develop` branch.
- [x] New project includes `rules/ai_behavior.md` and `.aider.conf.yml` with auto-read settings.

## Feedback/Notes
This refactor serves as a baseline for future features like "Interactive Configuration" or "Custom Template Selection".
