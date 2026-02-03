# CLAUDE.md - Project Context for Claude Code

## Project Overview
**Forge** is a production-grade AI Project Scaffolder CLI that generates opinionated project structures with built-in AI collaboration frameworks, governance, and professional engineering standards.

## Technical Stack
- **Language**: Python 3.10+
- **Project Type**: CLI Application (MVC Architecture)
- **Dependencies**: rich, questionary, jinja2, platformdirs
- **Entry Point**: `src/project_generator/cli.py`

## Key Directories
| Directory | Purpose |
|:---|:---|
| `src/project_generator/` | Core application logic (CLI, Engine, Wizard) |
| `src/project_generator/assets/` | Templates and directory configurations |
| `tests/` | Unit tests mirroring `src/` structure |
| `scripts/` | Test runners and utility scripts |
| `.agent/rules/` | AI constraints and coding standards |
| `docs/` | Project documentation |
| `reference_*/` | READ-ONLY symlinked reference projects |

## Architecture (MVC)
- **Model** (`configs.py`): Data structures defining project profiles and file mappings. Minimal logic.
- **View** (`templates/` & `wizard.py`): Jinja2 templates and interactive prompts. Minimal logic.
- **Controller** (`engine.py` & `cli.py`): Orchestration. No hardcoded file structures; read from the Model.

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
- **Unit Tests**: All changes to `engine.py` or `configs.py` must have accompanying tests in `tests/`.
- **Docstrings**: Google style for all public functions.
- **No Shadow Logic**: Do not hardcode file structures in the engine; read them from the Model.

## Git Workflow
- **Branching**: Gitflow-lite — `main` (production), `develop` (integration).
- **NO direct commits to `main` or `develop`** without verification.
- **Feature branches are LOCAL ONLY**: `feat/`, `fix/`, `docs/`, `chore/` — do not push unless collaborative.
- **Conventional Commits**: Use `feat:`, `fix:`, `docs:`, `chore:` prefixes.
- **Always merge `develop` into feature branch** before merging back.
- **Always run `./scripts/run_tests.sh`** before any commit.

## Discovery-Driven Development
- Check `src/project_generator/assets/` for existing templates/configs before proposing changes.
- Check `reference_*/` directories for the "Target State" of generated code.
- If the reference project differs from our template, **the template is wrong**.
- Do not implement features based on assumptions; implement based on **Reference Projects**.

## Reference Files
- **Directives**: [AI_DIRECTIVES.md](AI_DIRECTIVES.md)
- **Workflow**: [WORKFLOW.md](WORKFLOW.md)
- **Context**: [CONTEXT.md](CONTEXT.md)
- **AI Behavior Rules**: [.agent/rules/ai_behavior.md](.agent/rules/ai_behavior.md)
- **AI Insights / Long-Term Memory**: [docs/AI_INSIGHTS.md](docs/AI_INSIGHTS.md)
