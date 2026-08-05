"""Forge v2 pipeline — the core orchestration."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from forge.defaults import apply_variable_defaults
from forge.models import (
    Strategy,
    ApplyResult,
    ForgeLock,
    ManagedFileEntry,
)
from forge.profile_loader import resolve_profile, merge_inheritance
from forge.renderer import render_templates
from forge.applier import apply_to_disk
from forge.lockfile import write_lock, read_lock


def generate(
    profile_name: str,
    target: Path,
    variables: dict,
    strategy: Strategy,
    profiles_dir: Path,
    dry_run: bool = False,
) -> ApplyResult:
    """Run the full Forge pipeline: resolve -> merge -> render -> apply -> lock.

    Args:
        profile_name: Name of the profile to generate from.
        target: Target directory for the generated project.
        variables: User-provided template variables.
        strategy: How to handle file creation (create/update/force).
        profiles_dir: Root directory containing profile directories.
        dry_run: If True, render but don't write to disk.

    Returns:
        ApplyResult summarizing what was created/updated/skipped.
    """
    # Step 1-2: Resolve profile and merge inheritance
    profile_spec = resolve_profile(profile_name, profiles_dir)
    resolved = merge_inheritance(profile_spec, profiles_dir)

    # Defaults + derived flags (use_pip, project_slug, …)
    variables = apply_variable_defaults(
        profile_name, profiles_dir, variables, target=target
    )

    # Step 3: Render templates
    rendered = render_templates(resolved, variables)

    if dry_run:
        return ApplyResult(created=[r.output_path for r in rendered])

    # Step 4: Apply to disk
    lock = read_lock(target) if strategy == Strategy.UPDATE else None
    result = apply_to_disk(rendered, resolved, target, strategy, lock=lock, variables=variables)

    # Step 5: Write lock file
    now = datetime.now(timezone.utc).isoformat()
    new_lock = ForgeLock(
        version="2.0.0",
        profile=resolved.name,
        generated_at=now,
        variables={k: v for k, v in variables.items() if isinstance(v, (str, bool))},
        managed={
            r.output_path: ManagedFileEntry(
                template=r.template_name, hash=r.content_hash
            )
            for r in rendered
        },
    )
    write_lock(new_lock, target)

    return result
