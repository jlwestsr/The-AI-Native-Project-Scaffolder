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
    "README.md": templates.README_MD_CONTENT,
    "CONTEXT.md": templates.AIDER_CONTEXT,
    "rules/ai_behavior.md": templates.AI_BEHAVIOR_RULES,
    "docs/feature_template.md": templates.FEATURE_TEMPLATE,
    "docs/features/stub.txt": "",
    ".aider.conf.yml": templates.AIDER_CONFIG,
    ".pre-commit-config.yaml": templates.PRE_COMMIT_CONFIG,
    ".flake8": templates.FLAKE8_CONFIG,
    "pyproject.toml": templates.PYPROJECT_TOML,
    ".github/workflows/unittests.yml": templates.GITHUB_WORKFLOW,
    "requirements.txt": "numpy\npandas\nscikit-learn\n",
    "requirements-dev.txt": "pytest\nblack\nflake8\npre-commit\naider-chat\n",
    "src/__init__.py": "",
    "tests/__init__.py": "",
    "tests/test_initial.py": """
def test_sanity():
    assert True
""",
    "Dockerfile": templates.DOCKERFILE_CONTENT,
    "docker-compose.yml": templates.DOCKER_COMPOSE_CONTENT,
}
