"""Workspace scaffolding and sync for ecosystem-level roots."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from forge.models import (
    BusinessContext,
    OverlordManifest,
    ProjectEntry,
    ReleaseEntry,
    TrackEntry,
    CriticalPathEntry,
    WorkspaceConfig,
)

LOCK_FILENAME = ".forge-workspace.lock"
SENTINEL_START = "<!-- forge:ecosystem-start -->"
SENTINEL_END = "<!-- forge:ecosystem-end -->"


def _get_template_env() -> Environment:
    """Create a Jinja2 environment for workspace templates."""
    template_dir = (
        Path(__file__).parent.parent.parent / "templates" / "workspace"
    )
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        keep_trailing_newline=True,
    )


# --- Lock I/O ---


def write_workspace_lock(target: Path, config: WorkspaceConfig) -> None:
    """Write workspace lock file as JSON.

    Args:
        target: Workspace root directory.
        config: Workspace configuration to persist.
    """
    lock_path = target / LOCK_FILENAME
    lock_path.write_text(
        config.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )


def read_workspace_lock(target: Path) -> WorkspaceConfig | None:
    """Read workspace lock file.

    Args:
        target: Workspace root directory.

    Returns:
        WorkspaceConfig if lock exists, None otherwise.
    """
    lock_path = target / LOCK_FILENAME
    if not lock_path.exists():
        return None
    data = json.loads(lock_path.read_text(encoding="utf-8"))
    return WorkspaceConfig(**data)


# --- Rendering ---


def render_business_md(config: WorkspaceConfig) -> str:
    """Render BUSINESS.md from workspace config.

    Args:
        config: Workspace configuration with business context.

    Returns:
        Rendered Markdown string.
    """
    env = _get_template_env()
    template = env.get_template("BUSINESS.md.j2")
    return template.render(
        workspace_name=config.workspace_name,
        business=config.business,
    )


def render_overlord_md(config: WorkspaceConfig) -> str:
    """Render OVERLORD.md from workspace config.

    Args:
        config: Workspace configuration with manifest.

    Returns:
        Rendered Markdown string.
    """
    env = _get_template_env()
    template = env.get_template("OVERLORD.md.j2")
    dep_graph = build_dependency_ascii(config.manifest.projects)
    return template.render(
        workspace_name=config.workspace_name,
        manifest=config.manifest,
        dependency_graph=dep_graph,
    )


def render_workspace_claude_md(config: WorkspaceConfig) -> str:
    """Render root CLAUDE.md from workspace config.

    Args:
        config: Workspace configuration.

    Returns:
        Rendered Markdown string.
    """
    env = _get_template_env()
    template = env.get_template("CLAUDE.md.j2")
    return template.render(
        workspace_name=config.workspace_name,
        manifest=config.manifest,
    )


# --- Dependency graph ---


def build_dependency_ascii(projects: list[ProjectEntry]) -> str:
    """Build an ASCII dependency tree from project entries.

    Args:
        projects: List of project entries with dependency info.

    Returns:
        ASCII representation of the dependency graph.
    """
    # Build adjacency: parent -> children (who depends on parent)
    children: dict[str, list[str]] = {}
    all_names = {p.name for p in projects}
    has_parent = set()

    for p in projects:
        for dep in p.depends_on:
            if dep in all_names:
                children.setdefault(dep, []).append(p.name)
                has_parent.add(p.name)

    # Roots = projects with no dependencies (or deps outside the set)
    roots = [p.name for p in projects if p.name not in has_parent]
    standalones = [r for r in roots if r not in children]
    tree_roots = [r for r in roots if r in children]

    lines: list[str] = []

    def _render_tree(name: str, prefix: str = "", is_last: bool = True) -> None:
        kids = children.get(name, [])
        for i, child in enumerate(kids):
            is_child_last = i == len(kids) - 1
            connector = "└── " if is_child_last else "├── "
            lines.append(f"{prefix}{connector}{child}")
            extension = "    " if is_child_last else "│   "
            _render_tree(child, prefix + extension, is_child_last)

    for root in tree_roots:
        lines.append(root)
        _render_tree(root)
        lines.append("")

    for standalone in standalones:
        lines.append(f"{standalone} (standalone)")

    return "\n".join(lines).rstrip()


# --- Scaffolding ---


def scaffold_workspace(
    target: Path,
    config: WorkspaceConfig,
    dry_run: bool = False,
) -> dict[str, list[str]]:
    """Scaffold a workspace root with governance files.

    Args:
        target: Directory to create the workspace in.
        config: Full workspace configuration.
        dry_run: If True, report actions without writing files.

    Returns:
        Dict with 'created' and 'skipped' file lists.
    """
    config.generated_at = datetime.now(timezone.utc).isoformat()

    dirs_to_create = [
        target / "docs",
        target / "conductor",
        target / "conductor" / "tracks",
    ]

    files_to_write = {
        "BUSINESS.md": render_business_md(config),
        "OVERLORD.md": render_overlord_md(config),
        "CLAUDE.md": render_workspace_claude_md(config),
    }

    result: dict[str, list[str]] = {"created": [], "skipped": []}

    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
        for d in dirs_to_create:
            d.mkdir(parents=True, exist_ok=True)

    for filename, content in files_to_write.items():
        filepath = target / filename
        if filepath.exists():
            result["skipped"].append(filename)
        else:
            if not dry_run:
                filepath.write_text(content, encoding="utf-8")
            result["created"].append(filename)

    # Write lock file
    if not dry_run:
        write_workspace_lock(target, config)
    result["created"].append(LOCK_FILENAME)

    return result


# --- Markdown parsing ---


def _parse_md_table(content: str, header_pattern: str) -> list[dict[str, str]]:
    """Extract rows from a Markdown table following a header pattern.

    Args:
        content: Full Markdown content.
        header_pattern: Regex pattern to match the table header row.

    Returns:
        List of dicts mapping column headers to cell values.
    """
    lines = content.split("\n")
    rows: list[dict[str, str]] = []
    headers: list[str] = []
    in_table = False

    for line in lines:
        stripped = line.strip()
        if not in_table:
            if re.match(header_pattern, stripped):
                # Parse header columns
                headers = [
                    h.strip() for h in stripped.strip("|").split("|")
                ]
                in_table = True
            continue

        # Skip separator line
        if re.match(r"^\|[-| ]+\|$", stripped):
            continue

        # Table row
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
        else:
            # End of table
            break

    return rows


def parse_overlord_md(content: str) -> OverlordManifest:
    """Parse OVERLORD.md content into an OverlordManifest.

    Args:
        content: Raw Markdown content of OVERLORD.md.

    Returns:
        Parsed OverlordManifest model.
    """
    # Parse projects table
    project_rows = _parse_md_table(
        content, r"^\|\s*Project\s*\|.*Role\s*\|"
    )
    projects = []
    for row in project_rows:
        deps_raw = row.get("Depends On", "—").strip()
        deps = (
            [d.strip() for d in deps_raw.split(",") if d.strip() and d.strip() != "—"]
            if deps_raw and deps_raw != "—"
            else []
        )
        projects.append(ProjectEntry(
            name=row.get("Project", ""),
            role=row.get("Role", ""),
            path=row.get("Path", ""),
            remote=row.get("Remote", ""),
            depends_on=deps,
        ))

    # Parse releases table
    release_rows = _parse_md_table(
        content, r"^\|\s*Project\s*\|.*Latest Release\s*\|"
    )
    releases = [
        ReleaseEntry(
            project=row.get("Project", ""),
            latest_release=row.get("Latest Release", "—"),
            branch=row.get("Branch", "develop"),
            tests=row.get("Tests", "—"),
        )
        for row in release_rows
    ]

    # Parse tracks table
    track_rows = _parse_md_table(
        content, r"^\|\s*Track\s*\|.*Status\s*\|"
    )
    tracks = [
        TrackEntry(
            track=row.get("Track", ""),
            status=row.get("Status", "In Progress"),
            priority=int(row.get("Priority", "3")),
            link=row.get("Link", ""),
        )
        for row in track_rows
    ]

    # Parse critical path table
    cp_rows = _parse_md_table(
        content, r"^\|\s*Phase\s*\|.*Description\s*\|"
    )
    critical_path = [
        CriticalPathEntry(
            phase=row.get("Phase", ""),
            description=row.get("Description", ""),
            status=row.get("Status", "Pending"),
            priority=int(row.get("Priority", "1")),
        )
        for row in cp_rows
    ]

    return OverlordManifest(
        projects=projects,
        releases=releases,
        tracks=tracks,
        critical_path=critical_path,
    )


# --- Sync ---


def _inject_section(content: str, section: str) -> str:
    """Insert or replace content between sentinel markers.

    Args:
        content: Existing file content.
        section: New content to place between sentinels.

    Returns:
        Updated content with section injected.
    """
    wrapped = f"{SENTINEL_START}\n{section}\n{SENTINEL_END}"

    if SENTINEL_START in content and SENTINEL_END in content:
        # Replace existing section
        pattern = re.compile(
            re.escape(SENTINEL_START) + r".*?" + re.escape(SENTINEL_END),
            re.DOTALL,
        )
        return pattern.sub(wrapped, content)

    # Append at end
    if content and not content.endswith("\n"):
        content += "\n"
    return content + "\n" + wrapped + "\n"


def _build_project_context(
    project: ProjectEntry,
    manifest: OverlordManifest,
    business: BusinessContext,
    workspace_name: str,
) -> str:
    """Build ecosystem context snippet for a single project.

    Args:
        project: The target project.
        manifest: Full ecosystem manifest.
        business: Business context for governance rules.
        workspace_name: Name of the workspace.

    Returns:
        Rendered Markdown snippet.
    """
    # Find reverse dependencies
    depended_on_by = [
        p.name for p in manifest.projects
        if project.name in p.depends_on
    ]

    # Build siblings list
    siblings = []
    for p in manifest.projects:
        if p.name == project.name:
            continue
        if project.name in p.depends_on:
            relationship = "depends on this"
        elif p.name in project.depends_on:
            relationship = "this depends on"
        else:
            relationship = "sibling"
        siblings.append({
            "name": p.name,
            "role": p.role,
            "relationship": relationship,
        })

    env = _get_template_env()
    template = env.get_template("ecosystem_context.md.j2")
    return template.render(
        workspace_name=workspace_name,
        project_name=project.name,
        project_role=project.role,
        depends_on=project.depends_on,
        depended_on_by=depended_on_by,
        siblings=siblings,
        governance_rules=business.governance_rules,
    )


def _parse_governance_rules(content: str) -> list[str]:
    """Extract governance rules from BUSINESS.md content."""
    rules: list[str] = []
    in_gov = False
    for line in content.split("\n"):
        if line.strip().startswith("## Governance Rules"):
            in_gov = True
            continue
        if in_gov:
            if line.strip().startswith("## "):
                break
            match = re.match(
                r"^\d+\.\s+\*\*(.+?)\*\*\s*—\s*(.+)$", line.strip()
            )
            if match:
                rules.append(f"**{match.group(1)}** — {match.group(2)}")
    return rules


def sync_context(
    target: Path,
    dry_run: bool = False,
    project_filter: str | None = None,
) -> dict[str, list[str]]:
    """Sync ecosystem context into sub-project CLAUDE.md and GEMINI.md files.

    Reads OVERLORD.md and BUSINESS.md from the workspace root, then injects
    a managed section into each sub-project's CLAUDE.md and GEMINI.md using
    sentinel comments.

    Args:
        target: Workspace root directory.
        dry_run: If True, report actions without writing.
        project_filter: If set, only sync this project name.

    Returns:
        Dict with 'updated' and 'warnings' lists.
    """
    result: dict[str, list[str]] = {"updated": [], "warnings": []}

    # Read OVERLORD.md
    overlord_path = target / "OVERLORD.md"
    if not overlord_path.exists():
        result["warnings"].append("OVERLORD.md not found in workspace root")
        return result
    manifest = parse_overlord_md(overlord_path.read_text(encoding="utf-8"))

    # Read BUSINESS.md for governance rules
    business_path = target / "BUSINESS.md"
    business = BusinessContext()
    if business_path.exists():
        biz_content = business_path.read_text(encoding="utf-8")
        business.governance_rules = _parse_governance_rules(biz_content)

    # Read workspace name from lock
    lock = read_workspace_lock(target)
    workspace_name = lock.workspace_name if lock else target.name

    # Sync each project
    for project in manifest.projects:
        if project_filter and project.name != project_filter:
            continue

        project_dir = target / project.path.rstrip("/")
        if not project_dir.is_dir():
            result["warnings"].append(
                f"Project directory not found: {project.path}"
            )
            continue

        context_snippet = _build_project_context(
            project, manifest, business, workspace_name,
        )

        for md_file in ["CLAUDE.md", "GEMINI.md"]:
            md_path = project_dir / md_file
            if not md_path.exists():
                # Don't create files that don't exist
                continue

            existing = md_path.read_text(encoding="utf-8")
            updated = _inject_section(existing, context_snippet)

            if updated != existing:
                if not dry_run:
                    md_path.write_text(updated, encoding="utf-8")
                result["updated"].append(f"{project.path}{md_file}")

    return result
