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


def create_structure(base_path, update=False, context=None, force=False):
    """Creates folders and files.

    Args:
        base_path: The root directory for the project.
        update: If True, do not verify directory is empty and no overwrite.
        context: Dictionary of placeholders to replace in templates.
    """
    if context is None:
        context = {}

    # Get Profile Config
    import copy
    # Get Profile Config
    profile_name = context.get("__PROFILE__", "fullstack")
    profile = copy.deepcopy(configs.get_profile(profile_name))

    # AI Persona Logic
    persona = context.get("__AI_PERSONA__", "standard")

    # Map 'standard' to use the default template without suffix
    # For others, appending _{persona} to the template name
    behavior_file = ".agent/rules/ai_behavior.md"
    if persona != "standard" and behavior_file in profile["files"]:
        original_template = profile["files"][behavior_file]
        # Expecting: .agent/rules/ai_behavior_{profile}.md.j2
        # Target: .agent/rules/ai_behavior_{profile}_{persona}.md.j2
        if original_template.endswith(".md.j2"):
            prefix = original_template.replace(".md.j2", "")
            new_template = f"{prefix}_{persona}.md.j2"
            profile["files"][behavior_file] = new_template
            print(f"   ℹ️  AI Persona '{persona}' active. Using template: {new_template}")

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

        if update and not force and os.path.exists(file_path):
            print(f"   [SKIP] {filename} (Exists) - use --force to overwrite")
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

    print("   Upgrading pip...")
    try:
        subprocess.run(
            [pip_cmd, "install", "--upgrade", "pip"],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError:
        print("   ⚠️ Warning: Failed to upgrade pip.")

    # 2.5 Ensure build tools
    print("   Ensuring build tools (setuptools, wheel)...")
    try:
        subprocess.run(
            [pip_cmd, "install", "--upgrade", "setuptools", "wheel"],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError:
        print("   ⚠️ Warning: Failed to install build tools.")

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
