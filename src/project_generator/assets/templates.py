"""Large string constants for project templates."""

AIDER_CONTEXT = """
# Project Context & Coding Standards

## Project Overview
This is a production-grade AI engineering project. 

## Coding Standards
1. **Unit Tests**: ALL changes must have accompanying unit tests in the `tests/` directory.
2. **Modular Code**: Do not put business logic in notebooks. Move logic to `src/` modules.
3. **Type Hinting**: Use Python type hints for all function definitions.
4. **Documentation**: All public functions must have docstrings (Google style).

## Git Workflow
1. We use Git Flow.
2. Direct commits to `main` are forbidden. 
3. Work on feature branches off `develop`.
4. Ensure `git init` and `.gitignore` are respected.

## File Structure
- `data/` and `models/` are ignored by git.
- `src/` contains the source code.
- `tests/` mirrors the structure of `src/`.
"""

AI_BEHAVIOR_RULES = """
# AI Agent Behavior & Operational Rules

This document outlines the specific operational standards and behavioral expectations for AI agents working on this project.

## 1. Operational Guardrails
- **Pre-Commit Verification**: Before marking any task as complete, the agent MUST run `pytest` and ensure all tests pass.
- **Linting Compliance**: All code must pass `flake8` checks. If new code introduces linting errors, the agent must fix them immediately.
- **No Shadow Logic**: Do not implement business logic that isn't requested in requirements. If a logic choice is ambiguous, use `notify_user` to clarify.

## 2. Research & Discovery
- **Codebase Awareness**: Before creating a new utility function or module, the agent MUST search `src/` to check for existing implementations.
- **Dependency Check**: Before adding new libraries to `requirements.txt`, the agent must verify if the functionality is already provided by existing dependencies (numpy, pandas, etc.).

## 3. Communication Standards
- **Task Transparency**: Use `TaskSummary` to explain the *why* behind technical decisions, not just the *what*.
- **Plan Approval**: For any change affecting more than 2 files or introducing new architecture, an `implementation_plan.md` must be created and approved via `notify_user`.

## 4. Coding Style (AI-Specific)
- **Type Hinting**: Mandatory for all new functions. Proactively add hints to existing code when modified.
- **Docstring Standard**: Use Google Style docstrings. Include "Args", "Returns", and "Raises" sections where applicable.
- **Refactoring**: When editing a file, small improvements to readability or standards (like removing unused imports) in that file are encouraged.

## 5. Tool Usage
- **Terminal Execution**: Use the terminal to verify file existence and state before making assumptions.
- **Browser Research**: Use the browser tool to look up documentation for specific library versions used in the project.
"""

FEATURE_TEMPLATE = """
# Feature Title: [Enter Feature Name]

## Overview
Briefly describe what this feature is and why it's being built. What problem does it solve?

## Requirements
List the specific requirements for this feature:
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

## Technical Implementation (Optional)
If you have specific ideas about how this should be built, list them here:
- Proposed modules: `src/...`
- Dependencies: Any new libraries?
- Data changes: New data structures or files?

## Acceptance Criteria
How will we know this is working correctly?
- [ ] Criterion 1 (e.g., "Script runs without errors")
- [ ] Criterion 2 (e.g., "Output file is generated in `data/processed`")
- [ ] Criterion 3 (e.g., "Unit test coverage remains above 90%")

## Feedback/Notes
Any additional context or questions for the AI review?
"""

AIDER_CONFIG = """
# .aider.conf.yml
read:
  - rules/ai_behavior.md
  - CONTEXT.md

auto-commits: false  # We want manual control over commits to review them
dirty-commits: false # Ensure working directory is clean before coding
"""

FLAKE8_CONFIG = """
[flake8]
# 88 matches the Black line length standard
max-line-length = 88
extend-ignore = E203
exclude =
    .git,
    __pycache__,
    docs/source/conf.py,
    old,
    build,
    dist,
    .venv,
    venv,
    env,
    models,
    data
"""

PYPROJECT_TOML = """
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "ai_project"
version = "0.1.0"
description = "Production-grade AI Project"
authors = [{name = "JLWestSr", email = "labs@example.com"}]
requires-python = ">=3.10"

# --- Black Configuration ---
[tool.black]
line-length = 88
target-version = ['py310', 'py311']
include = '\\\\.pyi?$'
exclude = '''
/(
    \\\\.git
  | \\\\.hg
  | \\\\.mypy_cache
  | \\\\.tox
  | \\\\.venv
  | _build
  | buck-out
  | build
  | dist
  | models
  | data
)/
'''

# --- Pytest Configuration ---
[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q"
testpaths = [
    "tests",
]
pythonpath = [
    "src"
]
"""

GITHUB_WORKFLOW = """
name: CI/CD Pipeline

on:
  push:
    branches: [ "main", "develop" ]
  pull_request:
    branches: [ "main", "develop" ]

permissions:
  contents: read

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11"]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
        if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

    - name: Lint with flake8
      run: |
        flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 src tests --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

    - name: Test with pytest
      run: |
        export PYTHONPATH=src
        pytest tests/
"""

GITIGNORE_CONTENT = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
env/
venv/
.venv/
.env

# Jupyter Notebooks
.ipynb_checkpoints

# Project Data & Models (Never commit these!)
data/
models/
*.pkl
*.h5
*.pt
*.pth

# Aider / LLM tools
.aider*
!.aider.conf.yml
"""

README_MD_CONTENT = """
# AI Project

This project was forged using the **Forge AI-Native Scaffolder**.

## 🚀 Getting Started

Instructions to get the project up and running on your local machine.

### Prerequisites

List the software and tools required to run this project.

```bash
# Example
# pip install -r requirements.txt
```

### Installation

1.  Clone the repository.
2.  Install dependencies.

## Usage

Provide instructions and examples for using the project.

```bash
# Example usage command
```

## Features

-   Feature 1
-   Feature 2

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
"""
