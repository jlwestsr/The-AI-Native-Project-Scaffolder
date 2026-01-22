"""Interactive wizard for project generation details."""
import os
import questionary
from rich.console import Console
from rich.panel import Panel
from . import config_manager


class Wizard:
    """Handles interactive user prompts for project configuration."""
    def __init__(self, console=None):
        self.console = console or Console()
        self.defaults = {}

    def fetch_defaults(self):
        """Loads default settings from config manager."""
        self.defaults = {
            "author": config_manager.get_setting("author_name", "User"),
            "python": config_manager.get_setting("python_version", "3.10"),
            "manager": config_manager.get_setting("package_manager", "pip"),
            "license": config_manager.get_setting("license", "MIT")
        }

    def ask_project_name(self, current_name):
        """Prompts for project name."""
        name = questionary.text(
            "Project Name:",
            default=current_name
        ).ask()
        return name if name else current_name

    def ask_author(self):
        """Prompts for author name."""
        return questionary.text(
            "Author Name:",
            default=self.defaults["author"]
        ).ask()

    def ask_profile(self, default_profile=None):
        """Prompts for project profile."""
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

        return questionary.select(
            "Project Architecture:",
            choices=profile_choices,
            default=questionary.Choice(
                title=f"{current_profile}: {current_desc}",
                value=current_profile
            )
        ).ask()

    def run(self, default_profile=None):
        """Main entry point for the wizard."""
        self.console.print(Panel.fit("🧙 Forge Project Wizard", style="bold blue"))
        self.fetch_defaults()

        # 1. Project Name
        default_name = os.path.basename(os.getcwd())
        project_name = self.ask_project_name(default_name)

        # 2. Author
        author_name = self.ask_author()

        # 3. Profile
        profile_type = self.ask_profile(default_profile)

        # 4. Tech Stack (Simplified for now, assuming standard defaults per profile)
        # But we still let user choose Python/Manager/License universally
        python_version = questionary.select(
            "Python Version:",
            choices=["3.10", "3.11"],
            default=self.defaults["python"]
        ).ask()

        package_manager = questionary.select(
            "Which package manager to use?",
            choices=["pip", "poetry", "uv"],
            default=self.defaults["manager"]
        ).ask()

        license_type = questionary.select(
            "Choose a License:",
            choices=["MIT", "Apache 2.0", "Proprietary", "None"],
            default=self.defaults["license"]
        ).ask()

        # Summary
        self.console.print("[green]Configuration captured![/green]")
        self.console.print(f"Name: [bold]{project_name}[/bold]")
        self.console.print(f"Profile: [bold]{profile_type}[/bold]")

        return {
            "__PROJECT_NAME__": project_name,
            "__AUTHOR_NAME__": author_name,
            "__PYTHON_VERSION__": python_version,
            "__PACKAGE_MANAGER__": package_manager,
            "__LICENSE__": license_type,
            "__PROFILE__": profile_type
        }


def run_wizard(default_profile=None):
    """Legacy entry point wrapper."""
    wizard = Wizard()
    return wizard.run(default_profile)
