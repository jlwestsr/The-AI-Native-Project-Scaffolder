"""Interactive wizard that generates prompts from profile variables."""
from __future__ import annotations

from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel

from forge.models import VariableSpec
from forge.profile_loader import resolve_profile, merge_inheritance

console = Console()


def build_prompts(variables: dict[str, VariableSpec]) -> list[dict]:
    """Convert profile variable specs into questionary prompt configs.

    Args:
        variables: Profile variables from the resolved profile.

    Returns:
        List of prompt config dicts for questionary.
    """
    prompts: list[dict] = []

    for name, spec in variables.items():
        prompt: dict = {"name": name, "message": spec.prompt}

        if spec.type == "string":
            prompt["type"] = "text"
            if spec.default is not None:
                prompt["default"] = str(spec.default)
        elif spec.type == "choice":
            prompt["type"] = "select"
            prompt["choices"] = spec.choices or []
            if spec.default is not None:
                prompt["default"] = spec.default
        elif spec.type == "confirm":
            prompt["type"] = "confirm"
            prompt["default"] = spec.default if spec.default is not None else False

        prompts.append(prompt)

    return prompts


def _ask_prompt(prompt: dict) -> str | bool:
    """Ask a single prompt using questionary."""
    if prompt["type"] == "text":
        return questionary.text(
            prompt["message"],
            default=prompt.get("default", ""),
        ).ask()
    elif prompt["type"] == "select":
        return questionary.select(
            prompt["message"],
            choices=prompt["choices"],
            default=prompt.get("default"),
        ).ask()
    elif prompt["type"] == "confirm":
        return questionary.confirm(
            prompt["message"],
            default=prompt.get("default", False),
        ).ask()
    return ""


def run_wizard(
    profile_name: str,
    profiles_dir: Path,
) -> dict[str, str | bool]:
    """Run the interactive wizard for a given profile.

    Reads the profile's variable definitions and prompts the user
    for each value.

    Args:
        profile_name: Name of the profile to generate prompts for.
        profiles_dir: Root profiles directory.

    Returns:
        Dict of variable name -> user-provided value.
    """
    console.print(
        Panel(
            "[bold cyan]Forge Project Wizard[/bold cyan]",
            subtitle=f"Profile: {profile_name}",
        )
    )

    profile_spec = resolve_profile(profile_name, profiles_dir)
    resolved = merge_inheritance(profile_spec, profiles_dir)
    prompts = build_prompts(resolved.variables)

    variables: dict[str, str | bool] = {}
    for prompt in prompts:
        answer = _ask_prompt(prompt)
        if answer is None:
            raise KeyboardInterrupt("Wizard cancelled by user")
        variables[prompt["name"]] = answer

    return variables
