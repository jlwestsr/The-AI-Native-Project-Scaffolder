"""Load and validate profiles from TOML files."""
from __future__ import annotations

import sys
from pathlib import Path

from forge.models import ProfileSpec, ResolvedProfile, VariableSpec

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def resolve_profile(name: str, profiles_dir: Path) -> ProfileSpec:
    """Load a single profile from its TOML files.

    Args:
        name: Profile directory name (e.g., "base", "fullstack").
        profiles_dir: Root directory containing all profile directories.

    Returns:
        A validated ProfileSpec.

    Raises:
        FileNotFoundError: If the profile directory or required files are missing.
    """
    profile_path = profiles_dir / name
    if not profile_path.is_dir():
        raise FileNotFoundError(f"Profile directory not found: {profile_path}")

    profile_toml = profile_path / "profile.toml"
    if not profile_toml.exists():
        raise FileNotFoundError(f"profile.toml not found in: {profile_path}")

    structure_toml = profile_path / "structure.toml"

    # Load profile.toml
    with open(profile_toml, "rb") as f:
        profile_data = tomllib.load(f)

    # Load structure.toml (optional)
    structure_data: dict = {}
    if structure_toml.exists():
        with open(structure_toml, "rb") as f:
            structure_data = tomllib.load(f)

    # Parse variables
    raw_variables = profile_data.get("variables", {})
    variables = {
        key: VariableSpec(**val) for key, val in raw_variables.items()
    }

    # Build ProfileSpec
    profile_section = profile_data.get("profile", {})
    return ProfileSpec(
        name=profile_section["name"],
        description=profile_section["description"],
        inherits=profile_section.get("inherits"),
        variables=variables,
        directories=structure_data.get("directories", {}).get("root", []),
        files=structure_data.get("files", {}),
        conditionals=structure_data.get("conditionals", {}),
        template_dir=profile_path / "templates",
    )


def list_profiles(profiles_dir: Path) -> list[str]:
    """List all valid profile names in the profiles directory.

    A valid profile is a subdirectory containing a profile.toml file.

    Args:
        profiles_dir: Root directory containing all profile directories.

    Returns:
        Sorted list of profile names.
    """
    profiles = []
    for entry in sorted(profiles_dir.iterdir()):
        if entry.is_dir() and (entry / "profile.toml").exists():
            profiles.append(entry.name)
    return profiles


def merge_inheritance(
    profile: ProfileSpec, profiles_dir: Path
) -> ResolvedProfile:
    """Resolve the inheritance chain and merge into a single ResolvedProfile.

    Args:
        profile: The starting profile (may have an `inherits` field).
        profiles_dir: Root directory containing all profile directories.

    Returns:
        A fully merged ResolvedProfile with no inheritance references.

    Raises:
        ValueError: If circular inheritance is detected.
    """
    # Collect the inheritance chain (child first)
    chain: list[ProfileSpec] = [profile]
    seen: set[str] = {profile.name}

    current = profile
    while current.inherits:
        if current.inherits in seen:
            raise ValueError(
                f"Circular inheritance detected: "
                f"{current.name} -> {current.inherits}"
            )
        seen.add(current.inherits)
        parent = resolve_profile(current.inherits, profiles_dir)
        chain.append(parent)
        current = parent

    # Merge from base (last) to child (first)
    chain.reverse()  # now [base, ..., child]

    merged_variables: dict = {}
    merged_directories: list[str] = []
    merged_files: dict[str, str] = {}
    merged_conditionals: dict[str, str] = {}
    template_dirs: list[Path] = []

    for spec in chain:
        merged_variables.update(spec.variables)
        # Union directories (preserving order, no duplicates)
        for d in spec.directories:
            if d not in merged_directories:
                merged_directories.append(d)
        merged_files.update(spec.files)
        merged_conditionals.update(spec.conditionals)

    # Template dirs: child first for lookup priority
    for spec in reversed(chain):
        template_dirs.append(spec.template_dir)

    child = chain[-1]  # The originally requested profile
    return ResolvedProfile(
        name=child.name,
        description=child.description,
        variables=merged_variables,
        directories=merged_directories,
        files=merged_files,
        conditionals=merged_conditionals,
        template_dirs=template_dirs,
    )
