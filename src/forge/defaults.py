"""Variable defaults and derived flags for non-interactive / partial --var runs."""

from __future__ import annotations

from pathlib import Path

from forge.profile_loader import merge_inheritance, resolve_profile


def apply_variable_defaults(
    profile_name: str,
    profiles_dir: Path,
    variables: dict,
    *,
    target: Path | None = None,
) -> dict:
    """Fill missing variables from profile defaults and compute derived flags.

    Args:
        profile_name: Profile to load defaults from (with inheritance).
        profiles_dir: Profiles root.
        variables: User-supplied vars (mutated copy returned).
        target: Optional project path — used for default project_name.

    Returns:
        Complete variables dict suitable for Jinja rendering.
    """
    out = dict(variables)
    profile_spec = resolve_profile(profile_name, profiles_dir)
    resolved = merge_inheritance(profile_spec, profiles_dir)

    for name, spec in resolved.variables.items():
        if name not in out or out[name] in (None, ""):
            if spec.default is not None:
                out[name] = spec.default

    if not out.get("project_name"):
        if target is not None:
            out["project_name"] = target.resolve().name
        else:
            out["project_name"] = "project"

    if "project_slug" not in out or not out["project_slug"]:
        out["project_slug"] = (
            str(out["project_name"]).lower().replace("-", "_").replace(" ", "_")
        )

    # Conditionals used in structure.toml
    manager = str(out.get("manager") or "pip").lower()
    out["use_pip"] = manager == "pip"
    if "use_docker" not in out:
        # fullstack profile default is true; harmless for profiles without docker files
        out["use_docker"] = True

    # Optional author fallbacks
    out.setdefault("author_name", "")
    out.setdefault("author_email", "")
    out.setdefault("description", "")
    out.setdefault("python_version", "3.12")
    out.setdefault("license", "MIT")
    out.setdefault("persona", "standard")

    return out
