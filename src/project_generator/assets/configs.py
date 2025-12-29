"""Configuration for the project generator."""
from . import templates

PROJECT_STRUCTURE = [
    "data/raw",
    "data/processed",
    "docs/features",
    "models",
    "notebooks",
    "src/data",
    "src/features",
    "src/models",
    "src/visualization",
    "tests",
    "rules",
    ".github/workflows"
]

FILES_TO_CREATE = {
    "README.md": "README.md.j2",
    "CONTEXT.md": "CONTEXT.md.j2",
    "rules/ai_behavior.md": "rules/ai_behavior.md.j2",
    "docs/feature_template.md": "docs/feature_template.md.j2",
    "docs/features/stub.txt": "",
    ".aider.conf.yml": ".aider.conf.yml.j2",
    ".pre-commit-config.yaml": ".pre-commit-config.yaml.j2",
    ".flake8": ".flake8.j2",
    "pyproject.toml": "pyproject.toml.j2",
    ".github/workflows/unittests.yml": ".github/workflows/unittests.yml.j2",
    "requirements.txt": "requirements.txt", # String content, not template
    "requirements-dev.txt": "requirements-dev.txt", # String content
    "src/__init__.py": "",
    "tests/__init__.py": "",
    "tests/test_initial.py": "tests/test_initial.py", # String content
    ".gitignore": ".gitignore.j2",
    "Dockerfile": "Dockerfile.j2",
    "docker-compose.yml": "docker-compose.yml.j2",
}
