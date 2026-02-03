"""Forge lock file (.forge.lock) operations."""
from __future__ import annotations

import sys
from pathlib import Path

import tomli_w

from forge.models import (
    ForgeLock,
    ManagedFileEntry,
    RenderedFile,
    FileAction,
)

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

LOCK_FILENAME = ".forge.lock"


def write_lock(lock: ForgeLock, target_dir: Path) -> None:
    """Write a ForgeLock to .forge.lock in the target directory.

    Args:
        lock: The lock data to write.
        target_dir: The project root directory.
    """
    lock_path = target_dir / LOCK_FILENAME

    data: dict = {
        "forge": {
            "version": lock.version,
            "profile": lock.profile,
            "generated_at": lock.generated_at,
        },
        "variables": dict(lock.variables),
        "files": {
            "managed": {
                path: {"template": entry.template, "hash": entry.hash}
                for path, entry in lock.managed.items()
            }
        },
    }

    with open(lock_path, "wb") as f:
        tomli_w.dump(data, f)


def read_lock(target_dir: Path) -> ForgeLock | None:
    """Read .forge.lock from the target directory.

    Args:
        target_dir: The project root directory.

    Returns:
        A ForgeLock if the file exists, None otherwise.
    """
    lock_path = target_dir / LOCK_FILENAME
    if not lock_path.exists():
        return None

    with open(lock_path, "rb") as f:
        data = tomllib.load(f)

    forge_section = data.get("forge", {})
    managed_raw = data.get("files", {}).get("managed", {})
    managed = {
        path: ManagedFileEntry(**entry) for path, entry in managed_raw.items()
    }

    return ForgeLock(
        version=forge_section["version"],
        profile=forge_section["profile"],
        generated_at=forge_section["generated_at"],
        variables=data.get("variables", {}),
        managed=managed,
    )


def diff_lock(
    old_lock: ForgeLock,
    new_rendered: list[RenderedFile],
    disk_hashes: dict[str, str] | None = None,
    existing_files: set[str] | None = None,
) -> dict[str, FileAction]:
    """Compare old lock state against newly rendered files.

    Args:
        old_lock: The existing lock from the project.
        new_rendered: Freshly rendered files from the pipeline.
        disk_hashes: Map of file path to current sha256 hash on disk.
            If None, assumes all lock hashes match disk.
        existing_files: Set of file paths that exist on disk.
            If None, derived from disk_hashes keys.

    Returns:
        Dict mapping file paths to the action that should be taken.
        Files that need no action are omitted.
    """
    if disk_hashes is None:
        disk_hashes = {path: entry.hash for path, entry in old_lock.managed.items()}

    if existing_files is None:
        existing_files = set(disk_hashes.keys())

    actions: dict[str, FileAction] = {}

    for rendered in new_rendered:
        path = rendered.output_path
        old_entry = old_lock.managed.get(path)

        if old_entry is None:
            actions[path] = FileAction.CREATE
        elif path not in existing_files:
            actions[path] = FileAction.SKIP_DELETED
        elif rendered.content_hash == old_entry.hash:
            continue
        else:
            disk_hash = disk_hashes.get(path)
            if disk_hash == old_entry.hash:
                actions[path] = FileAction.UPDATE
            else:
                actions[path] = FileAction.SKIP_MODIFIED

    return actions
