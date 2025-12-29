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

## Technical Implementation (Optional)
If you have specific ideas about how this should be built, list them here:
- Proposed modules: `src/project_generator/engine.py`.
- Dependencies: None (the generator just writes files).
- Data changes: New templates for poetry/uv configurations.

## Acceptance Criteria
How will we know this is working correctly?
- [x] `forge . --manager poetry` creates a valid `pyproject.toml` that `poetry install` accepts.
- [x] `forge . --manager uv` creates a structure compatible with `uv sync`.
- [x] Docker builds succeed for all choices.

## Feedback/Notes
Default to `pip` to maintain backward compatibility.
