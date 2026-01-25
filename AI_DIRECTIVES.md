# AI Directives for The-AI-Native-Project-Scaffolder

1. **Commit Messages**: Use Conventional Commits.
2. **Branching**: All work happens on `develop`. `main` is for stable releases.
3. **Coding Style**: Python 3.10+ with Type Hinting.
4. **Testing**: `pytest` for unit tests.
5. **Linting**: `flake8` is enforced via pre-commit.

# Architecture Standards

We adhere to a modular **CLI Tool** structure.

## Directory Structure
- **src/project_generator/**: Core application logic.
  - **cli.py**: Command-line entry point.
  - **engine.py**: Scaffolding engine.
  - **templates/**: Jinja2 templates used for generation.
- **tests/**: Unit and integration tests.

## Coding Standards
- **Type Hints**: Mandatory for all function signatures.
- **Configuration**: Managed via `pyproject.toml` and environment variables.

## Source Control Standards
- **Strict Branching**: Always create a specific branch (`feat/`, `fix/`, `docs/`, `chore/`) for your work.
- **Commit Messages**: Strictly follow [Conventional Commits](https://www.conventionalcommits.org/).
