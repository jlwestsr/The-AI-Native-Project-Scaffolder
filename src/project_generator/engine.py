"""Core scaffolding engine."""
import os
import sys
from jinja2 import Environment, PackageLoader, select_autoescape
from .assets import configs

# Setup Jinja2 Environment
env = Environment(
    loader=PackageLoader("project_generator", "templates"),
    autoescape=select_autoescape()
)

# Raw content mappings for non-template files
RAW_CONTENT = {
    "requirements.txt": "numpy\npandas\nscikit-learn\n",
    "requirements-dev.txt": (
        "pytest\nblack\nflake8\npre-commit\naider-chat\nmkdocs-material\n"
    ),
    "tests/test_initial.py": """
def test_sanity():
    assert True
"""
}


def check_greenfield(path):
    """Ensures the directory is empty (ignoring the script itself)."""
    # Filter out common files like .git or this tool's files if they exist
    existing_items = [
        f for f in os.listdir(path) if f not in [".git", "init_project.py"]
    ]
    if existing_items:
        print(
            f"❌ Error: Directory '{path}' is not empty. "
            "Please run this in a greenfield folder."
        )
        print(f"   Found: {existing_items}")
        sys.exit(1)


def create_structure(base_path, update=False, context=None):
    """Creates folders and files.

    Args:
        base_path: The root directory for the project.
        update: If True, do not verify directory is empty and no overwrite.
        context: Dictionary of placeholders to replace in templates.
    """
    if context is None:
        context = {}

    # Get Profile Config
    profile_name = context.get("__PROFILE__", "fullstack")
    profile = configs.get_profile(profile_name)

    # Standardize context keys (remove dunders if present)
    jinja_context = {
        "project_name": context.get("__PROJECT_NAME__", "ai_project"),
        "author_name": context.get("__AUTHOR_NAME__", "User"),
        "license": context.get("__LICENSE__", "MIT"),
        "python_version": context.get("__PYTHON_VERSION__", "3.10"),
        "package_manager": context.get("__PACKAGE_MANAGER__", "pip"),
        "profile": profile_name,
    }

    print(f"...Scaffolding folder structure for profile: {profile_name}...")

    # Create Directories
    for folder in profile["structure"]:
        os.makedirs(os.path.join(base_path, folder), exist_ok=True)

    # Create Files
    for filename, template_name in profile["files"].items():
        # Package Manager Logic: Skip requirements.txt if not using pip
        if filename in ["requirements.txt", "requirements-dev.txt"] and jinja_context[
            "package_manager"
        ] != "pip":
            continue

        file_path = os.path.join(base_path, filename)
        # Ensure directory exists for nested files (like workflows)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if update and os.path.exists(file_path):
            print(f"   [SKIP] {filename} (Exists)")
            continue

        content = ""

        # Check if it's a raw content file
        if filename in RAW_CONTENT:
            content = RAW_CONTENT[filename]
        # Otherwise render from template
        elif template_name:
            try:
                template = env.get_template(template_name)
                content = template.render(**jinja_context)
            except Exception as e:
                print(f"Error rendering {template_name}: {e}")
                # Fallbck or re-raise?
                continue
        with open(file_path, 'w') as f:
            f.write(content.strip())
