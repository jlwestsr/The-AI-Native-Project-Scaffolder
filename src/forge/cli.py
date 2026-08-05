"""Forge v2 CLI — Typer application."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from forge.hooks import resolve_neo_command, run_neo_init_workspace
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

workspace_app = typer.Typer(help="Workspace ecosystem scaffolding")
app.add_typer(workspace_app, name="workspace")

console = Console()


def get_profiles_dir() -> Path:
    """Return the path to the profiles directory.

    Order:
      1. ``FORGE_PROFILES_DIR`` env
      2. Repo root ``profiles/`` (editable install: …/nebulus-forge/profiles)
      3. CWD ``profiles/``
    """
    env = os.environ.get("FORGE_PROFILES_DIR", "").strip()
    if env:
        env_path = Path(env).expanduser().resolve()
        if env_path.is_dir():
            return env_path

    # Editable: src/forge/cli.py → parents[2] = repo root
    repo_profiles = Path(__file__).resolve().parent.parent.parent / "profiles"
    if repo_profiles.is_dir():
        return repo_profiles

    cwd_profiles = Path.cwd() / "profiles"
    if cwd_profiles.is_dir():
        return cwd_profiles

    raise FileNotFoundError(
        "Cannot find profiles directory. "
        "Use an editable install (pipx install -e /path/to/nebulus-forge) "
        "or set FORGE_PROFILES_DIR to the profiles/ folder."
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


def _post_scaffold(
    target: Path,
    *,
    neo_mode: str = "auto",
    neo_pack: str = "workspace",
) -> None:
    """Run post-scaffold steps: git init, hooks, optional neo-harness embed.

    Args:
        target: Project root.
        neo_mode: ``auto`` (run if neo found), ``on`` (require neo), ``off``.
        neo_pack: Pack id passed to ``neo init-workspace --pack``.
    """
    # git init (idempotent — safe if already a repo)
    git_dir = target / ".git"
    if not git_dir.exists():
        console.print("  [dim]Initializing git repository...[/dim]")
        subprocess.run(["git", "init", str(target)], check=True, capture_output=True)

    # Make install-hooks.sh executable
    hooks_script = target / "scripts" / "install-hooks.sh"
    if hooks_script.exists():
        hooks_script.chmod(0o755)

    # Install pre-commit hooks if config exists and pre-commit is available
    precommit_config = target / ".pre-commit-config.yaml"
    if precommit_config.exists():
        # Look for pre-commit in venv first, then system
        venv_precommit = target / "venv" / "bin" / "pre-commit"
        precommit_bin = str(venv_precommit) if venv_precommit.exists() else "pre-commit"

        try:
            console.print("  [dim]Installing pre-commit hooks...[/dim]")
            subprocess.run(
                [precommit_bin, "install"],
                cwd=str(target),
                check=True,
                capture_output=True,
            )
            console.print("  [green]✅ pre-commit hooks installed[/green]")
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print(
                "  [yellow]⚠️  pre-commit not available — "
                "run scripts/install-hooks.sh after setting up venv[/yellow]"
            )

    # Optional neo-harness thin embed (not a second full scaffold)
    mode = (neo_mode or "auto").lower()
    if mode in ("off", "false", "0", "no"):
        console.print("  [dim]neo-harness embed skipped (--neo off)[/dim]")
        return
    if mode in ("on", "true", "1", "yes", "force"):
        if resolve_neo_command() is None:
            console.print(
                "  [red]neo required (--neo on) but not found. "
                "Install neo-harness or set FORGE_NEO_CMD.[/red]"
            )
            raise typer.Exit(code=1)
        run_neo_init_workspace(target, pack=neo_pack, force=True)
        return
    # auto
    run_neo_init_workspace(target, pack=neo_pack, force=False)


@app.command()
def new(
    target: Path = typer.Argument(..., help="Directory to create the project in"),
    profile: str = typer.Option("fullstack", "--profile", "-p", help="Profile to use"),
    no_interactive: bool = typer.Option(False, "--no-interactive", help="Skip wizard"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would happen"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
    var: Optional[list[str]] = typer.Option(None, "--var", help="Variable as key=value"),
    neo: str = typer.Option(
        "auto",
        "--neo",
        help="After scaffold: auto|on|off — run neo init-workspace if neo-harness is installed",
    ),
    neo_pack: str = typer.Option(
        "workspace",
        "--neo-pack",
        help="Agent pack id for neo init-workspace",
    ),
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

    if not dry_run:
        console.print("\n[dim]Running post-scaffold steps...[/dim]")
        _post_scaffold(
            target.resolve(),
            neo_mode=neo,
            neo_pack=neo_pack,
        )

    console.print(f"\n[bold green]Done![/bold green] Project at {target}")
    if not dry_run and neo.lower() != "off":
        console.print(
            "[dim]Next: cd into the project, copy env.neo.example → .env if present, "
            "then ./scripts/neo start … or see neo-harness docs/starting-a-workspace.md[/dim]"
        )

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

    console.print("\n[bold green]Update complete![/bold green]")


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

    console.print("[bold]Forge Project Info[/bold]")
    console.print(f"  Profile:    {lock.profile}")
    console.print(f"  Version:    {lock.version}")
    console.print(f"  Generated:  {lock.generated_at}")
    console.print(f"  Files:      {len(lock.managed)} managed")

    if lock.variables:
        console.print("\n[bold]Variables:[/bold]")
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
        console.print("\n[bold]Variables:[/bold]")
        for key, var_spec in spec.variables.items():
            default = f" (default: {var_spec.default})" if var_spec.default is not None else ""
            console.print(f"  {key}: {var_spec.type}{default}")

    if spec.directories:
        console.print("\n[bold]Directories:[/bold]")
        for d in spec.directories:
            console.print(f"  {d}/")

    console.print(f"\n[bold]Files:[/bold] {len(spec.files)} templates")


# --- Workspace commands ---


@workspace_app.command("init")
def workspace_init(
    target: Path = typer.Argument(..., help="Directory to create workspace in"),
    no_interactive: bool = typer.Option(
        False, "--no-interactive", help="Skip wizard"
    ),
    config_file: Optional[Path] = typer.Option(
        None, "--config", help="JSON config file instead of wizard"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would happen"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing files"
    ),
) -> None:
    """Initialize a new workspace with governance files."""
    from forge.workspace import scaffold_workspace, read_workspace_lock
    from forge.models import WorkspaceConfig

    if config_file:
        import json
        data = json.loads(config_file.read_text(encoding="utf-8"))
        ws_config = WorkspaceConfig(**data)
    elif no_interactive:
        console.print(
            "[red]Error:[/red] --no-interactive requires --config FILE"
        )
        raise typer.Exit(code=1)
    else:
        from forge.workspace_wizard import run_workspace_wizard
        ws_config = run_workspace_wizard()

    if not force:
        existing = read_workspace_lock(target)
        if existing is not None:
            console.print(
                "[red]Error:[/red] Workspace already initialized. "
                "Use --force to overwrite."
            )
            raise typer.Exit(code=1)

    result = scaffold_workspace(target, ws_config, dry_run=dry_run)

    if dry_run:
        console.print("[yellow]Dry run — no files written.[/yellow]")

    for path in result["created"]:
        console.print(f"  [green]CREATE[/green] {path}")
    for path in result["skipped"]:
        console.print(f"  [yellow]SKIP[/yellow]   {path}")

    console.print(
        f"\n[bold green]Workspace initialized![/bold green] "
        f"{ws_config.workspace_name} at {target}"
    )


@workspace_app.command("sync")
def workspace_sync(
    target: Path = typer.Argument(".", help="Workspace root directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would happen"),
    project: Optional[str] = typer.Option(
        None, "--project", help="Sync only this project"
    ),
) -> None:
    """Sync ecosystem context into sub-project CLAUDE.md/GEMINI.md files."""
    from forge.workspace import sync_context

    target = target.resolve()
    result = sync_context(target, dry_run=dry_run, project_filter=project)

    if dry_run:
        console.print("[yellow]Dry run — no files written.[/yellow]")

    for path in result["updated"]:
        console.print(f"  [blue]SYNC[/blue]   {path}")
    for warning in result["warnings"]:
        console.print(f"  [yellow]WARN[/yellow]   {warning}")

    if not result["updated"] and not result["warnings"]:
        console.print("  [dim]Everything up to date.[/dim]")

    console.print("\n[bold green]Sync complete![/bold green]")


@workspace_app.command("info")
def workspace_info(
    target: Path = typer.Argument(".", help="Workspace root directory"),
) -> None:
    """Show info about an initialized workspace."""
    from forge.workspace import read_workspace_lock

    target = target.resolve()
    lock = read_workspace_lock(target)

    if lock is None:
        console.print(
            "[red]No .forge-workspace.lock found in this directory.[/red]"
        )
        raise typer.Exit(code=1)

    console.print("[bold]Forge Workspace Info[/bold]")
    console.print(f"  Name:       {lock.workspace_name}")
    console.print(f"  Version:    {lock.version}")
    console.print(f"  Generated:  {lock.generated_at}")
    console.print(f"  Projects:   {len(lock.manifest.projects)}")
