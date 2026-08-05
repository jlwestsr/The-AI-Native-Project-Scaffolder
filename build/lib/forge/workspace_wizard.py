"""Interactive wizard for workspace configuration collection."""
from __future__ import annotations

import questionary
from rich.console import Console
from rich.panel import Panel

from forge.models import (
    BusinessConstraint,
    BusinessContext,
    HardwareTier,
    OverlordManifest,
    ProjectEntry,
    StrategicPriority,
    TechStackEntry,
    WorkspaceConfig,
)

console = Console()


def _ask_workspace_name() -> str:
    """Prompt for workspace name."""
    name = questionary.text(
        "Workspace name (e.g., 'West AI Labs'):",
    ).ask()
    if name is None:
        raise KeyboardInterrupt("Wizard cancelled by user")
    return name


def _ask_vision() -> str:
    """Prompt for business vision statement."""
    vision = questionary.text(
        "Business vision (one paragraph):",
    ).ask()
    if vision is None:
        raise KeyboardInterrupt("Wizard cancelled by user")
    return vision


def _ask_constraints() -> list[BusinessConstraint]:
    """Prompt for business constraints in a loop."""
    constraints: list[BusinessConstraint] = []
    console.print("\n[bold]Business Constraints[/bold] (enter empty constraint to stop)")

    while True:
        constraint = questionary.text("Constraint name:").ask()
        if constraint is None:
            raise KeyboardInterrupt("Wizard cancelled by user")
        if not constraint.strip():
            break
        value = questionary.text(f"Value for '{constraint}':").ask()
        if value is None:
            raise KeyboardInterrupt("Wizard cancelled by user")
        constraints.append(BusinessConstraint(constraint=constraint, value=value))

    return constraints


def _ask_hardware_tiers() -> list[HardwareTier]:
    """Prompt for hardware tiers in a loop."""
    tiers: list[HardwareTier] = []
    console.print("\n[bold]Hardware Tiers[/bold] (enter empty platform to stop)")
    tier_num = 1

    while True:
        platform = questionary.text(f"Tier {tier_num} platform:").ask()
        if platform is None:
            raise KeyboardInterrupt("Wizard cancelled by user")
        if not platform.strip():
            break
        hardware = questionary.text(f"Hardware for '{platform}':").ask()
        if hardware is None:
            raise KeyboardInterrupt("Wizard cancelled by user")
        use_case = questionary.text(f"Use case for '{platform}':").ask()
        if use_case is None:
            raise KeyboardInterrupt("Wizard cancelled by user")
        tiers.append(HardwareTier(
            tier=tier_num, platform=platform,
            hardware=hardware, use_case=use_case,
        ))
        tier_num += 1

    return tiers


def _ask_priorities() -> list[StrategicPriority]:
    """Prompt for strategic priorities in a loop."""
    priorities: list[StrategicPriority] = []
    console.print("\n[bold]Strategic Priorities[/bold] (enter empty goal to stop)")
    priority_num = 1

    while True:
        goal = questionary.text(f"Priority {priority_num} goal:").ask()
        if goal is None:
            raise KeyboardInterrupt("Wizard cancelled by user")
        if not goal.strip():
            break
        key_result = questionary.text(f"Key result for '{goal}':").ask()
        if key_result is None:
            raise KeyboardInterrupt("Wizard cancelled by user")
        priorities.append(StrategicPriority(
            priority=priority_num, goal=goal, key_result=key_result,
        ))
        priority_num += 1

    return priorities


def _ask_tech_stack() -> list[TechStackEntry]:
    """Prompt for tech stack entries in a loop."""
    stack: list[TechStackEntry] = []
    console.print("\n[bold]Tech Stack[/bold] (enter empty layer to stop)")

    while True:
        layer = questionary.text("Layer (e.g., 'Core language'):").ask()
        if layer is None:
            raise KeyboardInterrupt("Wizard cancelled by user")
        if not layer.strip():
            break
        technology = questionary.text(f"Technology for '{layer}':").ask()
        if technology is None:
            raise KeyboardInterrupt("Wizard cancelled by user")
        locked = questionary.confirm(f"Lock '{technology}'?", default=True).ask()
        if locked is None:
            raise KeyboardInterrupt("Wizard cancelled by user")
        stack.append(TechStackEntry(
            layer=layer, technology=technology, locked=locked,
        ))

    return stack


def _ask_governance_rules() -> list[str]:
    """Prompt for governance rules in a loop."""
    rules: list[str] = []
    console.print("\n[bold]Governance Rules[/bold] (enter empty rule to stop)")

    while True:
        rule = questionary.text("Rule:").ask()
        if rule is None:
            raise KeyboardInterrupt("Wizard cancelled by user")
        if not rule.strip():
            break
        rules.append(rule)

    return rules


def _ask_projects() -> list[ProjectEntry]:
    """Prompt for project entries with dependency selection."""
    projects: list[ProjectEntry] = []
    console.print("\n[bold]Projects[/bold] (enter empty name to stop)")

    while True:
        name = questionary.text("Project name:").ask()
        if name is None:
            raise KeyboardInterrupt("Wizard cancelled by user")
        if not name.strip():
            break

        role = questionary.select(
            f"Role for '{name}':",
            choices=[
                "shared-library",
                "platform-deployment",
                "application",
                "tooling",
                "provisioning",
            ],
        ).ask()
        if role is None:
            raise KeyboardInterrupt("Wizard cancelled by user")

        path = questionary.text(
            f"Path for '{name}':",
            default=f"{name}/",
        ).ask()
        if path is None:
            raise KeyboardInterrupt("Wizard cancelled by user")

        remote = questionary.text(f"Remote for '{name}':").ask()
        if remote is None:
            raise KeyboardInterrupt("Wizard cancelled by user")

        # Dependencies: multi-select from already-entered projects
        depends_on: list[str] = []
        if projects:
            existing_names = [p.name for p in projects]
            deps = questionary.checkbox(
                f"'{name}' depends on:",
                choices=existing_names,
            ).ask()
            if deps is None:
                raise KeyboardInterrupt("Wizard cancelled by user")
            depends_on = deps

        projects.append(ProjectEntry(
            name=name, role=role, path=path,
            remote=remote, depends_on=depends_on,
        ))

    return projects


def run_workspace_wizard() -> WorkspaceConfig:
    """Run the full interactive workspace wizard.

    Returns:
        A complete WorkspaceConfig from user input.
    """
    console.print(
        Panel(
            "[bold cyan]Forge Workspace Wizard[/bold cyan]",
            subtitle="Ecosystem scaffolding",
        )
    )

    workspace_name = _ask_workspace_name()
    vision = _ask_vision()
    constraints = _ask_constraints()
    hardware_tiers = _ask_hardware_tiers()
    priorities = _ask_priorities()
    tech_stack = _ask_tech_stack()
    governance_rules = _ask_governance_rules()
    projects = _ask_projects()

    business = BusinessContext(
        vision=vision,
        constraints=constraints,
        hardware_tiers=hardware_tiers,
        priorities=priorities,
        tech_stack=tech_stack,
        governance_rules=governance_rules,
    )

    manifest = OverlordManifest(projects=projects)

    return WorkspaceConfig(
        workspace_name=workspace_name,
        business=business,
        manifest=manifest,
    )
