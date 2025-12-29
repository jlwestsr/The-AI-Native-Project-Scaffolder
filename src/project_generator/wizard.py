"""Interactive wizard for project generation details."""
import os
import questionary
from rich.console import Console
from rich.panel import Panel

console = Console()

def run_wizard():
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
    # Try to Git config for default? simpler to just default to "User" for now
    # or use basic OS check
    author_name = questionary.text(
        "Author Name:",
        default="User"
    ).ask()
    
    # 3. License
    license_type = questionary.select(
        "License:",
        choices=[
            "MIT",
            "Apache-2.0",
            "Proprietary",
            "None"
        ]
    ).ask()
    
    # 4. Success
    console.print(f"[green]Configuration captured![/green]")
    console.print(f"Name: [bold]{project_name}[/bold]")
    console.print(f"Author: [bold]{author_name}[/bold]")
    console.print(f"License: [bold]{license_type}[/bold]")
    
    return {
        "__PROJECT_NAME__": project_name,
        "__AUTHOR_NAME__": author_name,
        "__LICENSE__": license_type
    }
