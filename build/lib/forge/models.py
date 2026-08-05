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


# --- Workspace models ---


class BusinessConstraint(BaseModel):
    """A single business constraint entry."""
    constraint: str
    value: str


class HardwareTier(BaseModel):
    """A target hardware tier."""
    tier: int
    platform: str
    hardware: str
    use_case: str


class StrategicPriority(BaseModel):
    """A strategic priority with key result."""
    priority: int
    goal: str
    key_result: str


class TechStackEntry(BaseModel):
    """An approved technology in the stack."""
    layer: str
    technology: str
    locked: bool = True


class BusinessContext(BaseModel):
    """Full BUSINESS.md content model."""
    schema_version: str = "1.0"
    vision: str = ""
    constraints: list[BusinessConstraint] = Field(default_factory=list)
    hardware_tiers: list[HardwareTier] = Field(default_factory=list)
    priorities: list[StrategicPriority] = Field(default_factory=list)
    tech_stack: list[TechStackEntry] = Field(default_factory=list)
    governance_rules: list[str] = Field(default_factory=list)


class ProjectEntry(BaseModel):
    """A project registered in the ecosystem."""
    name: str
    role: str
    path: str
    remote: str
    depends_on: list[str] = Field(default_factory=list)


class ReleaseEntry(BaseModel):
    """Release status for a project."""
    project: str
    latest_release: str = "—"
    branch: str = "develop"
    tests: str = "—"


class TrackEntry(BaseModel):
    """An active work track."""
    track: str
    status: str = "In Progress"
    priority: int = 3
    link: str = ""


class CriticalPathEntry(BaseModel):
    """A critical path phase."""
    phase: str
    description: str
    status: str = "Pending"
    priority: int = 1


class OverlordManifest(BaseModel):
    """Full OVERLORD.md content model."""
    schema_version: str = "1.0"
    projects: list[ProjectEntry] = Field(default_factory=list)
    releases: list[ReleaseEntry] = Field(default_factory=list)
    tracks: list[TrackEntry] = Field(default_factory=list)
    critical_path: list[CriticalPathEntry] = Field(default_factory=list)


class WorkspaceConfig(BaseModel):
    """Top-level workspace configuration for scaffold + lock."""
    version: str = "1.0"
    workspace_name: str
    generated_at: str = ""
    business: BusinessContext = Field(default_factory=BusinessContext)
    manifest: OverlordManifest = Field(default_factory=OverlordManifest)
