"""Configuration for the project generator."""

# Common files shared across all profiles
COMMON_FILES = {
    "WORKFLOW.md": "WORKFLOW.md.j2",
    "GEMINI.md": "GEMINI.md.j2",
    "AI_DIRECTIVES.md": "AI_DIRECTIVES.md.j2",
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
    ".yamllint": ".yamllint.j2",
    "ansible/ansible.cfg": "ansible/ansible.cfg.j2",
    "ansible/inventory.ini": "ansible/inventory.ini.j2",
    "ansible/setup_workstation.yml": "ansible/setup_workstation.yml.j2",
    "docs/AI_INSIGHTS.md": "docs/AI_INSIGHTS.md.j2",
}

# AI Personas (Behavior Profiles)
AI_PERSONAS = {
    "standard": "Standard (Adheres to profile defaults)",
    "architect": "Architect (Strict planning & governance)",
    "developer": "Developer (Focused on implementation)",
}

# Profile Definitions
PROFILES = {
    "fullstack": {
        "description": "General purpose AI system (Reference: Nebulus)",
        "structure": [
            "ansible/roles",
            "ansible/group_vars",
            "ansible/host_vars",
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
            "tests",
            ".github/workflows"
        ],
        "files": {
            **COMMON_FILES,
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
            "ansible/roles",
            "ansible/group_vars",
            "ansible/host_vars",
            "docs/features",
            "src/backend/app/models",
            "src/backend/app/routers",
            "src/backend/app/services",
            "src/backend/core",
            "src/frontend/static/css",
            "src/frontend/static/js",
            "src/frontend/templates",
            "tests",
            "tests/backend/routers",
            "tests/backend/services",
            "tests",
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
            "ansible/group_vars",
            "ansible/host_vars",
            "docs/features",
            "scripts",
            "tests",
            "tests",
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
    },
    "mvc": {
        "description": "Python MVC Architecture (Reference: Desktop/CLI App)",
        "structure": [
            "ansible/roles",
            "ansible/group_vars",
            "ansible/host_vars",
            "docs/features",
            "src/app/controllers",
            "src/app/models",
            "src/app/views",
            "tests/controllers",
            "tests/models",
            "tests/views",
            "tests",
            ".github/workflows"
        ],
        "files": {
            **COMMON_FILES,
            ".agent/rules/ai_behavior.md": ".agent/rules/ai_behavior_system.md.j2",
            "pyproject.toml": "pyproject.toml.j2",
            ".github/workflows/unittests.yml": ".github/workflows/unittests.yml.j2",
            "requirements.txt": "requirements.txt.j2",
            "requirements-dev.txt": "requirements-dev.txt.j2",
            "src/__init__.py": "",
            "src/app/__init__.py": "",
            "src/app/main.py": "",
            "tests/__init__.py": "",
            "tests/test_initial.py": "tests/test_initial.py.j2",
            "Dockerfile": "Dockerfile.j2",
            "docker-compose.yml": "docker-compose.yml.j2",
            "mkdocs.yml": "mkdocs.yml.j2",
        }
    }
}


def get_profile(name="fullstack"):
    """Returns the configuration for a specific profile."""
    return PROFILES.get(name, PROFILES["fullstack"])


def list_profiles():
    """Returns a list of available profile names."""
    return list(PROFILES.keys())
