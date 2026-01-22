import os
import sys
import subprocess
from jinja2 import Environment, PackageLoader, select_autoescape
from .assets import configs

# Setup Jinja2 Environment
env = Environment(
    loader=PackageLoader("project_generator", "templates"),
    autoescape=select_autoescape()
)


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

        # Use Jinja2 template if defined
        if template_name:
            try:
                template = env.get_template(template_name)
                content = template.render(**jinja_context)
            except Exception as e:
                print(f"Error rendering {template_name}: {e}")
                continue

        with open(file_path, 'w') as f:
            f.write(content.strip())

    # Setup Virtualenv (if using pip)
    setup_virtualenv(base_path, jinja_context["package_manager"])


def setup_virtualenv(base_path, package_manager):
    """Sets up a virtual environment and installs dependencies."""
    if package_manager != "pip":
        return

    print("\n📦 Setting up virtual environment (venv)...")
    venv_path = os.path.join(base_path, "venv")

    # 1. Create venv
    try:
        subprocess.run(
            ["python3", "-m", "venv", venv_path],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating venv: {e}")
        return

    # Pip path
    pip_cmd = os.path.join(venv_path, "bin", "pip")

    # 2. Upgrade pip
    print("   Upgrading pip...")
    try:
        subprocess.run(
            [pip_cmd, "install", "--upgrade", "pip"],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError:
        print("   ⚠️ Warning: Failed to upgrade pip.")

    # 3. Install requirements
    for req_file in ["requirements.txt", "requirements-dev.txt"]:
        req_path = os.path.join(base_path, req_file)
        if os.path.exists(req_path):
            print(f"   Installing {req_file}...")
            proc = subprocess.run(
                [pip_cmd, "install", "-r", req_path],
                capture_output=True,
                text=True
            )
            if proc.returncode != 0:
                print(f"   ⚠️ Warning: Failed to install {req_file}.")
                print(f"   Output: {proc.stderr}")
