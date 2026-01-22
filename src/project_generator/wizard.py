"""Interactive wizard for project generation details."""
import os
import questionary
from rich.console import Console
from rich.panel import Panel
from . import config_manager

console = Console()


def run_wizard(default_profile=None):
    """Runs the interactive wizard to gather project details."""
    console.print(Panel.fit("🧙 Forge Project Wizard", style="bold blue"))

    # Defaults
    default_name = os.path.basename(os.getcwd())

    # 1. Project Name
    project_name = questionary.text(
        "Project Name:",
        default=default_name
    ).ask()

    if not project_name:
        project_name = default_name

    # 2. Author Name
    default_author = config_manager.get_setting("author_name", "User")
    author_name = questionary.text(
        "Author Name:",
        default=default_author
    ).ask()

    # 3. Project Architecture (Profile)
    # If passed via CLI, use it as default.
    # Otherwise, prompt the user.
    from .assets import configs
    profiles = configs.list_profiles()

    profile_choices = []
    for p in profiles:
        desc = configs.get_profile(p).get("description", "")
        profile_choices.append(questionary.Choice(
            title=f"{p}: {desc}",
            value=p
        ))

    current_profile = default_profile if default_profile else "fullstack"
    current_desc = configs.get_profile(current_profile).get('description', '')

    profile_type = questionary.select(
        "Project Architecture:",
        choices=profile_choices,
        default=questionary.Choice(
            title=f"{current_profile}: {current_desc}",
            value=current_profile
        )
    ).ask()

    # 4. Python Version
    default_python = config_manager.get_setting("python_version", "3.10")
    python_version = questionary.select(
        "Python Version:",
        choices=["3.10", "3.11"],
        default=default_python
    ).ask()

    # 5. Package Manager
    default_manager = config_manager.get_setting("package_manager", "pip")
    package_manager = questionary.select(
        "Which package manager to use?",
        choices=["pip", "poetry", "uv"],
        default=default_manager
    ).ask()

    # 6. License
    default_license = config_manager.get_setting("license", "MIT")
    license_type = questionary.select(
        "Choose a License:",
        choices=[
            "MIT",
            "Apache 2.0",
            "Proprietary",
            "None"
        ],
        default=default_license
    ).ask()
    # 7. Success
    console.print("[green]Configuration captured![/green]")
    console.print(f"Name: [bold]{project_name}[/bold]")
    console.print(f"Profile: [bold]{profile_type}[/bold]")
    console.print(f"Author: [bold]{author_name}[/bold]")
    console.print(f"Package Manager: [bold]{package_manager}[/bold]")
    console.print(f"License: [bold]{license_type}[/bold]")

    return {
        "__PROJECT_NAME__": project_name,
        "__AUTHOR_NAME__": author_name,
        "__PYTHON_VERSION__": python_version,
        "__PACKAGE_MANAGER__": package_manager,
        "__LICENSE__": license_type,
        "__PROFILE__": profile_type
    }
