"""Load and validate profiles from TOML files."""
from __future__ import annotations

import sys
from pathlib import Path

from forge.models import ProfileSpec, VariableSpec

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
