"""Forge v2 CLI — Typer application."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from forge.models import Strategy
from forge.pipeline import generate
from forge.profile_loader import list_profiles, resolve_profile
from forge.lockfile import read_lock

app = typer.Typer(
    name="forge",
    help="Forge — AI Project Scaffolder",
    no_args_is_help=True,
)

profiles_app = typer.Typer(help="Manage profiles")
app.add_typer(profiles_app, name="profiles")

console = Console()


def get_profiles_dir() -> Path:
    """Return the path to the profiles directory.

    Looks for profiles/ relative to the package, falling back to CWD.
    """
    # Check relative to this file (installed package)
    pkg_profiles = Path(__file__).parent.parent.parent / "profiles"
    if pkg_profiles.is_dir():
        return pkg_profiles

    # Fallback: CWD
    cwd_profiles = Path.cwd() / "profiles"
    if cwd_profiles.is_dir():
        return cwd_profiles

    raise FileNotFoundError(
        "Cannot find profiles directory. "
        "Ensure Forge is installed correctly or run from the project root."
    )


def _parse_vars(var_list: list[str]) -> dict[str, str | bool]:
    """Parse --var key=value pairs into a dict."""
    variables: dict[str, str | bool] = {}
    for item in var_list:
        if "=" not in item:
            raise typer.BadParameter(f"Invalid variable format: {item}. Use key=value.")
        key, value = item.split("=", 1)
        # Convert boolean-like strings
        if value.lower() in ("true", "yes", "1"):
            variables[key] = True
        elif value.lower() in ("false", "no", "0"):
            variables[key] = False
        else:
            variables[key] = value
    return variables


@app.command()
def new(
    target: Path = typer.Argument(..., help="Directory to create the project in"),
    profile: str = typer.Option("fullstack", "--profile", "-p", help="Profile to use"),
    no_interactive: bool = typer.Option(False, "--no-interactive", help="Skip wizard"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would happen"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
    var: Optional[list[str]] = typer.Option(None, "--var", help="Variable as key=value"),
) -> None:
    """Create a new project from a profile."""
    profiles_dir = get_profiles_dir()
    variables = _parse_vars(var or [])

    strategy = Strategy.FORCE if force else Strategy.CREATE

    if not no_interactive and not variables:
        from forge.wizard import run_wizard
        variables = run_wizard(profile, profiles_dir)

    target.mkdir(parents=True, exist_ok=True)

    try:
        result = generate(
            profile_name=profile,
            target=target,
            variables=variables,
            strategy=strategy,
            profiles_dir=profiles_dir,
            dry_run=dry_run,
        )
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except FileExistsError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)

    if dry_run:
        console.print("[yellow]Dry run — no files written.[/yellow]")

    for path in result.created:
        console.print(f"  [green]CREATE[/green] {path}")
    for path in result.updated:
        console.print(f"  [blue]UPDATE[/blue] {path}")
    for path in result.skipped:
        console.print(f"  [yellow]SKIP[/yellow]   {path}")
    for warning in result.warnings:
        console.print(f"  [yellow]WARN[/yellow]   {warning}")

    console.print(f"\n[bold green]Done![/bold green] Project at {target}")


@app.command()
def update(
    target: Path = typer.Argument(".", help="Project directory to update"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite user changes"),
) -> None:
    """Update an existing Forge project with the latest templates."""
    profiles_dir = get_profiles_dir()
    target = target.resolve()

    lock = read_lock(target)
    if lock is None:
        console.print(
            "[red]Error:[/red] No .forge.lock found. "
            "This directory was not created by Forge, or the lock file was deleted."
        )
        raise typer.Exit(code=1)

    strategy = Strategy.FORCE if force else Strategy.UPDATE

    result = generate(
        profile_name=lock.profile,
        target=target,
        variables=dict(lock.variables),
        strategy=strategy,
        profiles_dir=profiles_dir,
    )

    for path in result.created:
        console.print(f"  [green]CREATE[/green] {path}")
    for path in result.updated:
        console.print(f"  [blue]UPDATE[/blue] {path}")
    for path in result.skipped:
        console.print(f"  [yellow]SKIP[/yellow]   {path}")
    for warning in result.warnings:
        console.print(f"  [yellow]WARN[/yellow]   {warning}")

    console.print(f"\n[bold green]Update complete![/bold green]")


@app.command()
def info(
    target: Path = typer.Argument(".", help="Project directory to inspect"),
) -> None:
    """Show info about a Forge-generated project."""
    target = target.resolve()
    lock = read_lock(target)

    if lock is None:
        console.print("[red]No .forge.lock found in this directory.[/red]")
        raise typer.Exit(code=1)

    console.print(f"[bold]Forge Project Info[/bold]")
    console.print(f"  Profile:    {lock.profile}")
    console.print(f"  Version:    {lock.version}")
    console.print(f"  Generated:  {lock.generated_at}")
    console.print(f"  Files:      {len(lock.managed)} managed")

    if lock.variables:
        console.print(f"\n[bold]Variables:[/bold]")
        for key, val in lock.variables.items():
            console.print(f"  {key} = {val}")


@profiles_app.command("list")
def profiles_list() -> None:
    """List available profiles."""
    profiles_dir = get_profiles_dir()
    names = list_profiles(profiles_dir)

    table = Table(title="Available Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Description")

    for name in names:
        try:
            spec = resolve_profile(name, profiles_dir)
            table.add_row(name, spec.description)
        except Exception:
            table.add_row(name, "[red]Error loading[/red]")

    console.print(table)


@profiles_app.command("show")
def profiles_show(
    name: str = typer.Argument(..., help="Profile name to inspect"),
) -> None:
    """Show details of a specific profile."""
    profiles_dir = get_profiles_dir()

    try:
        spec = resolve_profile(name, profiles_dir)
    except FileNotFoundError:
        console.print(f"[red]Profile '{name}' not found.[/red]")
        raise typer.Exit(code=1)

    console.print(f"[bold]{spec.name}[/bold] — {spec.description}")

    if spec.inherits:
        console.print(f"  Inherits: {spec.inherits}")

    if spec.variables:
        console.print(f"\n[bold]Variables:[/bold]")
        for key, var_spec in spec.variables.items():
            default = f" (default: {var_spec.default})" if var_spec.default is not None else ""
            console.print(f"  {key}: {var_spec.type}{default}")

    if spec.directories:
        console.print(f"\n[bold]Directories:[/bold]")
        for d in spec.directories:
            console.print(f"  {d}/")

    console.print(f"\n[bold]Files:[/bold] {len(spec.files)} templates")
