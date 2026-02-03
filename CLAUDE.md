# CLAUDE.md - Project Context for Claude Code

## Project Overview
**Forge** is a production-grade AI Project Scaffolder CLI that generates opinionated project structures with built-in AI collaboration frameworks, governance, and professional engineering standards.

## Technical Stack
- **Language**: Python 3.10+
- **Project Type**: CLI Application (Profile-driven Pipeline Architecture)
- **Dependencies**: rich, questionary, jinja2, platformdirs, typer, pydantic
- **Entry Point**: `src/forge/cli.py`

## Key Directories
| Directory | Purpose |
|:---|:---|
| `src/forge/` | Core application logic (CLI, Pipeline, Renderer, Wizard) |
| `profiles/` | Profile definitions (TOML configs + Jinja2 templates) |
| `tests/` | Unit tests mirroring `src/` structure |
| `scripts/` | Test runners and utility scripts |
| `.agent/rules/` | AI constraints and coding standards |
| `docs/` | Project documentation |
| `reference_*/` | READ-ONLY symlinked reference projects |

## Architecture (v2 — Profile-driven Pipeline)
- **Models** (`models.py`): Pydantic data structures for profiles, rendered files, lock entries.
- **Profile Loader** (`profile_loader.py`): Reads TOML configs, resolves inheritance.
- **Renderer** (`renderer.py`): Jinja2 template rendering (pure, no I/O).
- **Applier** (`applier.py`): Writes rendered files to disk.
- **Pipeline** (`pipeline.py`): Orchestrates load → render → apply stages.
- **CLI** (`cli.py`): Typer-based entry point.
- **Wizard** (`wizard.py`): Interactive prompts for profile variables.

## Build & Test
```bash
# Activate venv first (mandatory — never use system Python)
source venv/bin/activate

# Run tests
./scripts/run_tests.sh

# Run CLI
forge [TARGET_DIR] [OPTIONS]
```

## Coding Standards
- **Type Hints**: Mandatory for all new functions.
- **Linting**: `flake8` with zero errors.
- **Unit Tests**: All changes must have accompanying tests in `tests/`.
- **Docstrings**: Google style for all public functions.
- **No Shadow Logic**: Do not hardcode file structures in the pipeline; read them from profiles.

## Git Workflow
- **Branching**: Gitflow-lite — `develop` (default branch, integration), `main` (stable releases only).
- **NO direct commits to `main` or `develop`** without verification.
- **Feature branches are LOCAL ONLY**: `feat/`, `fix/`, `docs/`, `chore/` — do not push unless collaborative.
- **Conventional Commits**: Use `feat:`, `fix:`, `docs:`, `chore:` prefixes.
- **Always merge `develop` into feature branch** before merging back.
- **Always run `./scripts/run_tests.sh`** before any commit.

## Discovery-Driven Development
- Check `profiles/` for existing templates/configs before proposing changes.
- Check `reference_*/` directories for the "Target State" of generated code.
- If the reference project differs from our template, **the template is wrong**.
- Do not implement features based on assumptions; implement based on **Reference Projects**.

## Reference Files
- **Directives**: [AI_DIRECTIVES.md](AI_DIRECTIVES.md)
- **Workflow**: [WORKFLOW.md](WORKFLOW.md)
- **Context**: [CONTEXT.md](CONTEXT.md)
- **AI Behavior Rules**: [.agent/rules/ai_behavior.md](.agent/rules/ai_behavior.md)
- **AI Insights / Long-Term Memory**: [docs/AI_INSIGHTS.md](docs/AI_INSIGHTS.md)
