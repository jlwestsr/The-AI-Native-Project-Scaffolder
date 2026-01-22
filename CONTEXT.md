# Project Context & Coding Standards

## 1. Project Overview
**Forge** is a production-grade project generator designed for modern AI engineering. It establishes an **AI Collaboration Framework** that ensures human-AI teams work within strict governance, shared context, and professional engineering standards.

## 2. 🚨 MANDATORY: AI Behavior & Rules
**CRITICAL**: Before proposing any changes or running commands, you MUST review and adhere to the rules defined in:
👉 **[.agent/rules/ai_behavior.md](.agent/rules/ai_behavior.md)**

Key constraints from these rules include:
*   **Agentic Artifacts**: Use `task.md` and `implementation_plan.md` for state tracking.
*   **Test-Driven**: `scripts/run_tests.sh` must pass before completion.
*   **Git-Ops**: Strict branching (Feature/Fix/Docs -> Develop -> Main).

## 3. 🤖 Recommended AI Personas
To effectively contribute to this project, adopt the following personas based on the task:

### 1. Scaffolding Architect (Primary)
*   **Focus**: System Design, Template Structure, Governance.
*   **Responsibilities**:
    *   Designing the folder structure in `src/project_generator/assets/configs.py`.
    *   Maintaining Jinja2 templates in `src/project_generator/assets/templates.py`.
    *   Ensuring generated projects comply with "AI-Native" standards.

### 2. Python Tool Developer
*   **Focus**: CLI Logic, File I/O, Testing.
*   **Responsibilities**:
    *   Implementing core logic in `engine.py` and `git_ops.py`.
    *   Writing `pytest` cases in `tests/`.
    *   Managing dependencies in `pyproject.toml`.

### 3. Release Manager
*   **Focus**: Documentation, CI/CD, Quality Assurance.
*   **Responsibilities**:
    *   Updating `README.md` and `docs/`.
    *   Verifying `scripts/run_tests.sh` passes.
    *   Managing versioning and releases.

## 4. 🗺️ Project Map
Quickly orient yourself by connecting directories to responsible personas:

| Directory/File | Primary Persona | Purpose |
| :--- | :--- | :--- |
| `src/project_generator/assets/` | **Architect** | Templates and directory configurations. |
| `src/project_generator/` | **Tool Dev** | Core application logic (CLI, Engine, Wizard). |
| `tests/` | **Tool Dev** | Unit tests for valid verification. |
| `scripts/` | **Release Mgr** | Test runners and utility scripts. |
| `.agent/rules/` | **All** | AI constraints and coding standards. |
| `docs/` | **Release Mgr** | Project documentation. |


## 5. 💻 CLI Reference

**Forge** is a command-line tool. The primary entry point is `forge` (or `python -m src.project_generator.cli`).

### Usage
```bash
forge [TARGET_DIR] [OPTIONS]
```

### Arguments
| Argument | Description |
| :--- | :--- |
| `TARGET_DIR` | Directory to initialize. Defaults to current directory (`.`). |

### Options
| Option | Short | Description |
| :--- | :--- | :--- |
| `--update` | `-u` | **Safe Update**: Adds missing files (e.g., `Dockerfile`, `rules/`) without overwriting existing content. |
| `--manager` | | Choose package manager: `pip` (default), `poetry`, or `uv`. |
| `--profile` | | Choose archetype: `fullstack` (default), `web`, or `system`. |
| `--config-list` | | Display global configuration settings. |
| `--config-set` | | Set global defaults (e.g., `--config-set author_name="Jane Doe"`). |

### Examples
```bash
# Interactive Wizard (Default)
forge

# Non-Interactive Customization
forge my-project --manager poetry --profile web

# Update Legacy Project
forge . --update --profile system
```

## 6. Coding Standards


1. **Unit Tests**: ALL changes must have accompanying unit tests in the `tests/` directory.
2. **Modular Code**: Do not put business logic in notebooks. Move logic to `src/` modules.
3. **Type Hinting**: Use Python type hints for all function definitions.
4. **Documentation**: All public functions must have docstrings (Google style).

## 7. Git Workflow

1. We use Git Flow.
2. Direct commits to `main` are forbidden. 
3. Work on feature branches off `develop`.
4. Ensure `git init` and `.gitignore` are respected.

## 8. File Structure

- `data/`: Contains raw and processed data. **Ignored by git**.
- `docs/`: Project documentation.
- `.agent/rules/`: AI compliance and behavior rules.
- `src/`: The core source code of the project.
- `tests/`: Unit tests mirroring the `src/` structure.


## Reference Directories (READ-ONLY)

The following directories are symbolic links to other projects for reference purposes only. **Do NOT modify content within these folders unless explicitly approved by the user.**

- `reference_gantry/`
- `reference_nebulus/`
- `reference_shurtugal-lnx/`