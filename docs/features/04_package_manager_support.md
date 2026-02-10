# Feature Title: Package Manager Support

## Overview
The current generator defaults to `requirements.txt` / `pip`. Modern Python workflows often prefer `poetry` or `uv` for better dependency resolution and project management. We want to support these tools out of the box.

## Requirements
List the specific requirements for this feature:
- [x] Add a `--manager` flag to the CLI (options: `pip`, `poetry`, `uv`).
- [x] If `poetry` is selected:
    - [x] Generate `pyproject.toml` with `[tool.poetry]` sections.
    - [x] Skip `requirements.txt`.
- [x] If `uv` is selected:
    - [x] Generate standard `pyproject.toml`.
    - [x] Skip `requirements.txt`.
- [x] Update `docker-compose.yml` and `Dockerfile` to respect the chosen manager (implied by skipping file, though Docker templates might need conditional logic - kept simple for now).

## Technical Implementation (v2)
- **Profile Variables**: Package manager selection is a profile variable (choice type in `profile.toml`).
- **Conditionals**: `structure.toml` conditionals control which files are generated (e.g., `requirements.txt` only when `use_pip == true`).
- **Templates**: Manager-specific templates in `profiles/*/templates/` (e.g., `pyproject.toml.j2` with conditional sections).
- **Pipeline**: Handled by `renderer.py` → `applier.py` — no special logic needed in the pipeline.

## Acceptance Criteria
How will we know this is working correctly?
- [x] `forge . --manager poetry` creates a valid `pyproject.toml` that `poetry install` accepts.
- [x] `forge . --manager uv` creates a structure compatible with `uv sync`.
- [x] Docker builds succeed for all choices.

## Feedback/Notes
Default to `pip` to maintain backward compatibility.
