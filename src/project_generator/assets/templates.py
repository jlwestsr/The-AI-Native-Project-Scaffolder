"""Large string constants for project templates."""

AIDER_CONTEXT = """
# Project Context & Coding Standards

> **[IMPORTANCE: CRITICAL] AI AGENT DIRECTIVE**:
> You MUST read and adhere to [.agent/rules/ai_behavior.md](.agent/rules/ai_behavior.md) at the start of every session. It contains strict operational guardrails, "Ansible-First" policies, and Git branching rules that supersede general instructions.

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
- `data/`: Contains raw and processed data. **Ignored by git** to prevent leaking sensitive information.
- `docs/`: Project documentation, including feature specs (in `features/`) and architectural decisions.
- `models/`: Binary model files and weights. **Ignored by git**.
- `notebooks/`: Jupyter notebooks for experimentation and analysis. Logic MUST be moved to `src/` before production.
- `.agent/rules/`: AI compliance and behavior rules (e.g., `ai_behavior.md`).
- `src/`: The core source code of the project. Organized by feature or module.
- `tests/`: Unit tests mirroring the `src/` structure.
- `.github/`: CI/CD pipelines and GitHub Actions workflows.
"""

AI_BEHAVIOR_RULES = """
# AI Agent Behavior & Operational Rules

This document outlines the specific operational standards and behavioral expectations for AI agents working on this project.

## 1. Operational Guardrails
- **Pre-Commit Verification**: Before marking any task as complete, the agent MUST run `pytest` and ensure all tests pass.
- **Linting Compliance**: All code must pass `flake8` checks. If new code introduces linting errors, the agent must fix them immediately.
- **No Shadow Logic**: Do not implement business logic that isn't requested in requirements. If a logic choice is ambiguous, use `notify_user` to clarify.
- **Ansible-First**: Do not run manual `apt install`, `pip install`, or configuration edits unless experimenting. Once confirmed, IMMEDIATELY port the change to an Ansible role.

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

## 6. Testing & Quality Assurance
- **Mandatory Unit Tests**: All new Python scripts OR significant functional changes to existing ones MUST include unit tests (using `pytest`) in the `tests/` directory.
- **System Verification**: New Ulauncher extensions or major system configurations (desktop entries, services) MUST be added to the `ansible/verify.yml` playbook.
- **Test Runner**: Always run `./scripts/run_tests.sh` before finalizing work to ensure no regressions in linting, unit tests, or system state.
- **Ansible Lint**: While some pre-existing debt exists, all *new* Ansible code should aim for zero legacy warnings. Use specific tasks instead of generic `shell` where possible.

## 7. Development Workflow
- **Conventional Commits**: Use `feat:`, `fix:`, `docs:`, or `chore:` prefixes.
- **Python Environment (PEP 668)**: On Ubuntu 24.04, always use `--user --break-system-packages` for persistent system-level Python tool/dependency installation, OR use the project's `./venv/`.
- **Node.js**: Use `community.general.npm` with `global: true` for system-wide CLI tools. Ensure `nodejs` and `npm` are installed via `apt` in the `common` role first.
- **Verification**: After applying an Ansible role, run `ansible-playbook ansible/verify.yml` to ensure the system state matches the intended configuration.
- **Security**: Never commit `~/.ssh/` keys or personal tokens. If a script needs to check for them, it should do so without exposing contents.
- **Git Tracking & Branching**:
    - **NO DIRECT WORK ON MAIN/MASTER**. This branch is for production releases only.
    - **Chores**: Minor maintenance or documentation ("chore" work) may be done directly on the `develop` branch.
    - **Features/Bugs**: ALL other work (features, bug fixes, refactors) MUST be done on a new branch (e.g., `feat/...`, `fix/...`) created from `develop`.
    - Always merge `develop` into your feature branch before requesting a merge back.

## 8. Feature Implementation Workflow
When given a directive to work through a feature, follow these steps strictly:
0.  **Create Feature Document**: Create a new file in `docs/features/` using the content from `docs/feature_template.md`. This MUST be the first step to define the feature scope.
1.  **Create a Branch**: Create a new git branch to do the work (e.g., `git checkout -b feat/feature-name`).
2.  **Do the Work**: Implement the changes, following all coding standards and guardrails.
3.  **Test the Work**: Run standard tests (`pytest`, `flake8`) and add new tests as required. Ensure all pass.
4.  **Document the Work**: Update relevant documentation (README, feature docs, walkthrough).
5.  **Commit, Merge, and Push**:
    - Commit changes with conventional messages.
    - Switch to the main development branch (e.g., `develop`).
    - Merge the feature branch.
    - Push the updated branch to the remote.
"""

FEATURE_TEMPLATE = """
# Feature: [Feature Name]

## 1. Overview
**Branch**: `feat/[feature-name]`

Briefly describe the feature, the problem it solves, and why it is being built.

## 2. Requirements
List specific, testable requirements:
- [ ] Requirement 1
- [ ] Requirement 2

## 3. Technical Implementation
- **Modules**: List modified/created files (e.g., `src/module.py`).
- **Dependencies**: List new packages (e.g., `rich`).
- **Data**: Database changes or new assets.

## 4. Verification Plan
**Automated Tests**:
- [ ] Script/Test: `pytest tests/test_feature.py`
- [ ] Logic Verified: [Describe what is tested]

**Manual Verification**:
- [ ] Step 1: Run `forge --flag`
- [ ] Step 2: Verify output in `dist/`

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/...` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
"""

AIDER_CONFIG = """
# .aider.conf.yml
read:
  - .agent/rules/ai_behavior.md
  - CONTEXT.md

auto-commits: false  # We want manual control over commits to review them
dirty-commits: false # Ensure working directory is clean before coding
"""

PRE_COMMIT_CONFIG = """
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
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
name = "__PROJECT_NAME__"
version = "0.1.0"
description = "Production-grade AI Project"
authors = [{name = "__AUTHOR_NAME__", email = "labs@example.com"}]
requires-python = ">=3.10"
license = {text = "__LICENSE__"}

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
# __PROJECT_NAME__

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

DOCKERFILE_CONTENT = """
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the application (Default command, can be overridden)
# CMD ["python", "src/main.py"]
CMD ["/bin/bash"]
"""

DOCKER_COMPOSE_CONTENT = """
version: '3.8'

services:
  app:
    build: .
    volumes:
      - .:/app
    # command: python src/main.py
    command: tail -f /dev/null # Keep the container running for development
"""
