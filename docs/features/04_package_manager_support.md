# Feature Title: Package Manager Support

## Overview
The current generator defaults to `requirements.txt` / `pip`. Modern Python workflows often prefer `poetry` or `uv` for better dependency resolution and project management. We want to support these tools out of the box.

## Requirements
List the specific requirements for this feature:
- [ ] Add a `--manager` flag to the CLI (options: `pip`, `poetry`, `uv`).
- [ ] If `poetry` is selected:
    - Generate `pyproject.toml` with `[tool.poetry]` sections.
    - Skip `requirements.txt`.
- [ ] If `uv` is selected:
    - Generate standard `pyproject.toml`.
    - Skip `requirements.txt`.
- [ ] Update `docker-compose.yml` and `Dockerfile` to respect the chosen manager.

## Technical Implementation (Optional)
If you have specific ideas about how this should be built, list them here:
- Proposed modules: `src/project_generator/engine.py`.
- Dependencies: None (the generator just writes files).
- Data changes: New templates for poetry/uv configurations.

## Acceptance Criteria
How will we know this is working correctly?
- [ ] `forge . --manager poetry` creates a valid `pyproject.toml` that `poetry install` accepts.
- [ ] `forge . --manager uv` creates a structure compatible with `uv sync`.
- [ ] Docker builds succeed for all choices.

## Feedback/Notes
Default to `pip` to maintain backward compatibility.
