"""Configuration for the project generator."""

# Common files shared across all profiles
COMMON_FILES = {
    "README.md": "README.md.j2",
    "CONTEXT.md": "CONTEXT.md.j2",
    "docs/feature_template.md": "docs/feature_template.md.j2",
    "docs/features/stub.txt": "",
    ".aider.conf.yml": ".aider.conf.yml.j2",
    ".pre-commit-config.yaml": ".pre-commit-config.yaml.j2",
    ".gitignore": ".gitignore.j2",
    "docs/index.md": "docs/index.md.j2",
    ".github/workflows/docs.yml": ".github/workflows/docs.yml.j2",
    ".flake8": ".flake8.j2",
}

# Profile Definitions
PROFILES = {
    "fullstack": {
        "description": "General purpose AI system (Reference: Nebulus)",
        "structure": [
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
            ".agent/rules",
            ".github/workflows"
        ],
        "files": {
            **COMMON_FILES,
            ".agent/rules/ai_behavior.md": ".agent/rules/ai_behavior_fullstack.md.j2",
            "pyproject.toml": "pyproject.toml.j2",
            ".github/workflows/unittests.yml": ".github/workflows/unittests.yml.j2",
            "requirements.txt": "requirements.txt.j2",
            "requirements-dev.txt": "requirements-dev.txt.j2",
            "src/__init__.py": "",
            "tests/__init__.py": "",
            "tests/test_initial.py": "tests/test_initial.py.j2",
            "Dockerfile": "Dockerfile.j2",
            "docker-compose.yml": "docker-compose.yml.j2",
            "mkdocs.yml": "mkdocs.yml.j2",
        }
    },
    "web": {
        "description": "Python Backend + HTML/JS Frontend (Reference: Gantry)",
        "structure": [
            "docs/features",
            "src/backend",
            "src/frontend/static/css",
            "src/frontend/static/js",
            "src/frontend/templates",
            "tests",
            ".agent/rules",
            ".github/workflows"
        ],
        "files": {
            **COMMON_FILES,
            ".agent/rules/ai_behavior.md": ".agent/rules/ai_behavior_web.md.j2",
            "pyproject.toml": "pyproject.toml.j2",
            ".github/workflows/unittests.yml": ".github/workflows/unittests.yml.j2",
            "requirements.txt": "requirements.txt.j2",
            "requirements-dev.txt": "requirements-dev.txt.j2",
            "src/__init__.py": "",
            "tests/__init__.py": "",
            "tests/test_initial.py": "tests/test_initial.py.j2",
            "Dockerfile": "Dockerfile.j2",
            "docker-compose.yml": "docker-compose.yml.j2",
            "mkdocs.yml": "mkdocs.yml.j2",
        }
    },
    "system": {
        "description": "Ansible Automation & IaC (Reference: Shurtugal-LNX)",
        "structure": [
            "ansible/roles/common",
            "ansible/roles/desktop",
            "docs/features",
            "scripts",
            "tests",
            ".agent/rules",
            ".github/workflows"
        ],
        "files": {
            **COMMON_FILES,
            ".agent/rules/ai_behavior.md": ".agent/rules/ai_behavior_system.md.j2",
            "ansible/site.yml": "",
            "ansible/verify.yml": "",
            "scripts/bootstrap.sh": "",
            "scripts/run_tests.sh": "",
            ".github/workflows/unittests.yml": ".github/workflows/unittests.yml.j2",
            "tests/test_initial.py": "tests/test_initial.py.j2",
        }
    }
}


def get_profile(name="fullstack"):
    """Returns the configuration for a specific profile."""
    return PROFILES.get(name, PROFILES["fullstack"])


def list_profiles():
    """Returns a list of available profile names."""
    return list(PROFILES.keys())
