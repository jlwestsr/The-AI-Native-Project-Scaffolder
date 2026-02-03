"""Apply rendered files to disk with create/update/force strategies."""
from __future__ import annotations

import hashlib
from pathlib import Path

from jinja2 import Environment

from forge.models import (
    RenderedFile,
    ResolvedProfile,
    Strategy,
    ApplyResult,
    ForgeLock,
    FileAction,
)
from forge.lockfile import diff_lock


def _hash_file(path: Path) -> str:
    """Compute the same hash format used by RenderedFile."""
    content = path.read_text(encoding="utf-8")
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def apply_to_disk(
    rendered_files: list[RenderedFile],
    profile: ResolvedProfile,
    target: Path,
    strategy: Strategy,
    lock: ForgeLock | None = None,
    variables: dict | None = None,
) -> ApplyResult:
    """Write rendered files to the target directory.

    Args:
        rendered_files: Files rendered by the renderer.
        profile: The resolved profile (for directory creation).
        target: The project root directory.
        strategy: How to handle existing files.
        lock: Existing lock file (required for UPDATE strategy).
        variables: Template variables for rendering directory names.

    Returns:
        ApplyResult summarizing what happened.

    Raises:
        FileExistsError: If CREATE strategy and files already exist.
        ValueError: If UPDATE strategy but no lock provided.
    """
    result = ApplyResult()
    env = Environment()
    vars_ = variables or {}

    # Create profile directories (render Jinja2 variables in names)
    for directory in profile.directories:
        resolved_dir = env.from_string(directory).render(**vars_)
        (target / resolved_dir).mkdir(parents=True, exist_ok=True)

    if strategy == Strategy.UPDATE:
        if lock is None:
            raise ValueError(
                "Update strategy requires an existing .forge.lock file."
            )
        _apply_update(rendered_files, target, lock, result)
    elif strategy == Strategy.FORCE:
        _apply_create(rendered_files, target, result, force=True)
    else:
        _apply_create(rendered_files, target, result, force=False)

    return result


def _apply_create(
    rendered_files: list[RenderedFile],
    target: Path,
    result: ApplyResult,
    force: bool,
) -> None:
    """Apply files with create or force strategy."""
    for rendered in rendered_files:
        file_path = target / rendered.output_path

        if not force and file_path.exists():
            raise FileExistsError(
                f"File already exists: {file_path}. "
                "Use --force to overwrite."
            )

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(rendered.content, encoding="utf-8")
        result.created.append(rendered.output_path)


def _apply_update(
    rendered_files: list[RenderedFile],
    target: Path,
    lock: ForgeLock,
    result: ApplyResult,
) -> None:
    """Apply files with update strategy using lock file diffing."""
    disk_hashes: dict[str, str] = {}
    existing_files: set[str] = set()

    for rendered in rendered_files:
        file_path = target / rendered.output_path
        if file_path.exists():
            existing_files.add(rendered.output_path)
            disk_hashes[rendered.output_path] = _hash_file(file_path)

    actions = diff_lock(lock, rendered_files, disk_hashes, existing_files)
    rendered_map = {r.output_path: r for r in rendered_files}

    for path, action in actions.items():
        rendered = rendered_map[path]
        file_path = target / path

        if action == FileAction.CREATE:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(rendered.content, encoding="utf-8")
            result.created.append(path)

        elif action == FileAction.UPDATE:
            file_path.write_text(rendered.content, encoding="utf-8")
            result.updated.append(path)

        elif action == FileAction.SKIP_MODIFIED:
            result.skipped.append(path)
            result.warnings.append(
                f"Skipped {path} — modified by user"
            )

        elif action == FileAction.SKIP_DELETED:
            result.skipped.append(path)
