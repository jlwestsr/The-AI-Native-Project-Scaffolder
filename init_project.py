import os
import sys
import subprocess

# --- Content Definitions ---

# 1. Aider Context ("The Brain")
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

# 2. Aider Config
AIDER_CONFIG = """
# Aider Configuration
auto-commits: false  # We want manual control over commits to review them
dirty-commits: false # Ensure working directory is clean before coding
"""

# 3. Flake8 Config (Linting)
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

# 4. Pyproject.toml (Black + Pytest Config)
PYPROJECT_TOML = """
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "ai_project"
version = "0.1.0"
description = "Production-grade AI Project"
authors = [{name = "Your Name", email = "you@example.com"}]
requires-python = ">=3.10"

# --- Black Configuration ---
[tool.black]
line-length = 88
target-version = ['py310', 'py311']
include = '\\.pyi?$'
exclude = '''
/(
    \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
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

# 5. GitHub Actions Workflow (CI/CD)
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

# 6. Gitignore
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

# 7. README.md (Initial Content)
README_MD_CONTENT = """
# AI Project

Project structure generated with industry best practices.

## Getting Started

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

# --- Configuration Mapping ---
PROJECT_STRUCTURE = [
    "data/raw",
    "data/processed",
    "docs",
    "models",
    "notebooks",
    "src/data",
    "src/features",
    "src/models",
    "src/visualization",
    "tests",
    ".github/workflows"
]

FILES_TO_CREATE = {
    "README.md": README_MD_CONTENT,
    "CONTEXT.md": AIDER_CONTEXT,
    ".aider.conf.yml": AIDER_CONFIG,
    ".flake8": FLAKE8_CONFIG,
    "pyproject.toml": PYPROJECT_TOML,
    ".github/workflows/unittests.yml": GITHUB_WORKFLOW,
    "requirements.txt": "numpy\npandas\nscikit-learn\n",
    "requirements-dev.txt": "pytest\nblack\nflake8\naider-chat\n",
    "src/__init__.py": "",
    "tests/__init__.py": "",
    "tests/test_initial.py": """
def test_sanity():
    assert True
""",
}

def run_command(command, cwd=None):
    """Runs a shell command and handles errors."""
    try:
        subprocess.run(
            command, 
            check=True, 
            shell=True, 
            cwd=cwd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        print(f"✔ Executed: {command}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing: {command}")
        print(e.stderr.decode())
        sys.exit(1)

def check_greenfield(path):
    """Ensures the directory is empty (ignoring the script itself)."""
    existing_items = [f for f in os.listdir(path) if f != "init_project.py"]
    if existing_items:
        print(f"❌ Error: Directory '{path}' is not empty. Please run this in a greenfield folder.")
        print(f"   Found: {existing_items}")
        sys.exit(1)

def create_structure(base_path):
    """Creates folders and files."""
    print("...Scaffolding folder structure...")
    
    # Create Directories
    for folder in PROJECT_STRUCTURE:
        os.makedirs(os.path.join(base_path, folder), exist_ok=True)
    
    # Create Files
    for filename, content in FILES_TO_CREATE.items():
        file_path = os.path.join(base_path, filename)
        # Ensure directory exists for nested files (like workflows)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(content.strip())
            
    # Create .gitignore specifically
    with open(os.path.join(base_path, ".gitignore"), 'w') as f:
        f.write(GITIGNORE_CONTENT.strip())

def init_git(base_path):
    """Initializes Git, commits baseline, and creates develop branch."""
    print("...Initializing Git and Branching Strategy...")
    
    # 1. Init
    run_command("git init", cwd=base_path)
    
    # 2. Add files
    run_command("git add .", cwd=base_path)
    
    # 3. Commit to Main
    run_command('git commit -m "Initial commit: Complete AI project scaffold"', cwd=base_path)
    
    # 4. Create and Switch to Develop branch
    run_command("git checkout -b develop", cwd=base_path)

def main():
    current_dir = os.getcwd()
    
    print(f"Starting AI Project Initialization in: {current_dir}")
    
    # 1. Safety Check
    check_greenfield(current_dir)
    
    # 2. Build Structure
    create_structure(current_dir)
    
    # 3. Git Operations
    init_git(current_dir)
    
    print("\n✅ Success! Project is ready.")
    print("   - You are currently on the 'develop' branch.")
    print("   - CI/CD is configured in .github/workflows/unittests.yml")
    print("   - Linter/Formatter configs are set (.flake8, pyproject.toml)")
    print("   - Aider context is ready in CONTEXT.md")

if __name__ == "__main__":
    main()