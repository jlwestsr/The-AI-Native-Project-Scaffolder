"""Pydantic models for Forge v2 pipeline."""
from __future__ import annotations

import enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class VariableSpec(BaseModel):
    """Specification for a single profile variable."""
    prompt: str
    type: Literal["string", "choice", "confirm"]
    default: str | bool | None = None
    choices: list[str] | None = None


class ProfileSpec(BaseModel):
    """Raw profile loaded from a single profile.toml + structure.toml."""
    name: str
    description: str
    inherits: str | None = None
    variables: dict[str, VariableSpec] = Field(default_factory=dict)
    directories: list[str] = Field(default_factory=list)
    files: dict[str, str] = Field(default_factory=dict)
    conditionals: dict[str, str] = Field(default_factory=dict)
    template_dir: Path


class ResolvedProfile(BaseModel):
    """Profile after inheritance chain is fully merged."""
    name: str
    description: str
    variables: dict[str, VariableSpec] = Field(default_factory=dict)
    directories: list[str] = Field(default_factory=list)
    files: dict[str, str] = Field(default_factory=dict)
    conditionals: dict[str, str] = Field(default_factory=dict)
    template_dirs: list[Path] = Field(default_factory=list)


class RenderedFile(BaseModel):
    """A file that has been rendered in memory, ready to write."""
    output_path: str
    content: str
    template_name: str
    content_hash: str


class Strategy(str, enum.Enum):
    """File application strategy."""
    CREATE = "create"
    UPDATE = "update"
    FORCE = "force"


class FileAction(str, enum.Enum):
    """Action to take on a single file during apply."""
    CREATE = "create"
    UPDATE = "update"
    SKIP_MODIFIED = "skip_modified"
    SKIP_DELETED = "skip_deleted"
    WARN_DEPRECATED = "warn_deprecated"


class ApplyResult(BaseModel):
    """Result of applying rendered files to disk."""
    created: list[str] = Field(default_factory=list)
    updated: list[str] = Field(default_factory=list)
    skipped: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ManagedFileEntry(BaseModel):
    """A single entry in the lock file's managed files section."""
    template: str
    hash: str


class ForgeLock(BaseModel):
    """The .forge.lock file schema."""
    version: str
    profile: str
    generated_at: str
    variables: dict[str, str | bool] = Field(default_factory=dict)
    managed: dict[str, ManagedFileEntry] = Field(default_factory=dict)
