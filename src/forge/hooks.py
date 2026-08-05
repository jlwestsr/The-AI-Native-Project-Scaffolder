"""Optional post-scaffold hooks (neo-harness embed, etc.)."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from rich.console import Console

console = Console()

# Lab-friendly search paths when `neo` is not on PATH
_LAB_NEO_CANDIDATES = (
    Path.home() / "projects" / "neo-harness" / ".venv" / "bin" / "neo",
    Path.home() / "projects" / "west_ai_labs" / ".venv-neo" / "bin" / "neo",
)


def resolve_neo_command() -> list[str] | None:
    """Locate a neo CLI for init-workspace.

    Order:
      1. FORGE_NEO_CMD (shell-like string or absolute path)
      2. ``neo`` on PATH
      3. Known lab editable installs

    Returns:
        argv prefix (e.g. [\"neo\"] or [\"/path/to/neo\"]) or None.
    """
    env_cmd = os.environ.get("FORGE_NEO_CMD", "").strip()
    if env_cmd:
        # Allow either a single path or "uv run neo"-style
        parts = env_cmd.split()
        return parts

    which = shutil.which("neo")
    if which:
        return [which]

    for candidate in _LAB_NEO_CANDIDATES:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return [str(candidate)]

    return None


def run_neo_init_workspace(
    target: Path,
    *,
    pack: str = "workspace",
    force: bool = False,
) -> bool:
    """Run ``neo init-workspace`` on target if neo is available.

    Args:
        target: Project root.
        pack: neo agent pack id.
        force: Pass --force to overwrite neo embed files.

    Returns:
        True if neo ran successfully, False if skipped or failed.
    """
    neo_cmd = resolve_neo_command()
    if neo_cmd is None:
        console.print(
            "  [dim]neo-harness not found — skip init-workspace. "
            "Install neo or set FORGE_NEO_CMD, then: "
            f"neo init-workspace {target} --pack {pack}[/dim]"
        )
        return False

    argv = [
        *neo_cmd,
        "init-workspace",
        str(target),
        "--pack",
        pack,
    ]
    if force:
        argv.append("--force")
    # forge already git-inits; neo requires git unless --force-no-git
    if not (target / ".git").exists():
        argv.append("--force-no-git")

    console.print(
        f"  [dim]Running neo-harness embed: {' '.join(argv)}[/dim]"
    )
    try:
        proc = subprocess.run(
            argv,
            cwd=str(target),
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        console.print(f"  [yellow]⚠️  neo init-workspace failed to start: {exc}[/yellow]")
        return False

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        console.print(
            f"  [yellow]⚠️  neo init-workspace exited {proc.returncode}"
            f"{': ' + err[:200] if err else ''}[/yellow]"
        )
        return False

    console.print("  [green]✅ neo-harness workspace embed complete[/green]")
    return True
