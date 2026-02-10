# Feature Title: Pre-commit Hook Integration

## Overview
Currently, linting and code quality checks are performed in the CI/CD pipeline. This feedback loop is too slow. "AI Native" governance implies stopping bad code *before* it enters the repository. This requirement is to integrate `pre-commit` hooks into the project scaffold to strictly enforce standards locally.

## Requirements
List the specific requirements for this feature:
- [x] Generate a `.pre-commit-config.yaml` file by default in new projects.
- [x] Include standard hooks: `black` (formatter), `flake8` (linter), and `check-yaml`.
- [x] Automatically install the hooks (run `pre-commit install`) during the `git init` phase of the generator.
- [x] Ensure the hooks respect the project's configuration (e.g., line lengths).

## Technical Implementation (v2)
- **Template**: `.pre-commit-config.yaml.j2` in `profiles/base/templates/` (inherited by all profiles).
- **Rendering**: Handled by `renderer.py` → `applier.py` pipeline.
- **Dependencies**: `pre-commit` included in generated project's `requirements-dev.txt` template.

## Acceptance Criteria
How will we know this is working correctly?
- [x] New project contains `.pre-commit-config.yaml`.
- [x] `git commit` fails if code is poorly formatted, and passes after `black` fixes it.
- [x] Updates to the generator include verification tests for this file creation.

## Feedback/Notes
Consider using `ruff` in the future for faster linting, but stick to `flake8`/`black` for now to match current standards.
