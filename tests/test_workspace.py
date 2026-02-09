"""Tests for workspace scaffolding, rendering, parsing, and sync."""
import pytest
from pathlib import Path

from forge.models import (
    BusinessContext,
    BusinessConstraint,
    CriticalPathEntry,
    HardwareTier,
    OverlordManifest,
    ProjectEntry,
    ReleaseEntry,
    StrategicPriority,
    TechStackEntry,
    TrackEntry,
    WorkspaceConfig,
)
from forge.workspace import (
    SENTINEL_START,
    SENTINEL_END,
    build_dependency_ascii,
    parse_overlord_md,
    read_workspace_lock,
    render_business_md,
    render_overlord_md,
    render_workspace_claude_md,
    scaffold_workspace,
    sync_context,
    write_workspace_lock,
    _inject_section,
)


def _make_config(workspace_name: str = "Test Labs") -> WorkspaceConfig:
    """Build a representative WorkspaceConfig for testing."""
    return WorkspaceConfig(
        workspace_name=workspace_name,
        business=BusinessContext(
            vision="Build great AI",
            constraints=[
                BusinessConstraint(constraint="Privacy", value="Local-first"),
            ],
            hardware_tiers=[
                HardwareTier(
                    tier=1, platform="Edge",
                    hardware="M4 Pro", use_case="Appliance",
                ),
            ],
            priorities=[
                StrategicPriority(
                    priority=1, goal="Ship v1", key_result="Done",
                ),
            ],
            tech_stack=[
                TechStackEntry(layer="Core", technology="Python 3.10+"),
            ],
            governance_rules=["No cloud inference", "No new databases"],
        ),
        manifest=OverlordManifest(
            projects=[
                ProjectEntry(
                    name="core", role="shared-library",
                    path="core/", remote="org/core",
                ),
                ProjectEntry(
                    name="prime", role="platform-deployment",
                    path="prime/", remote="org/prime",
                    depends_on=["core"],
                ),
                ProjectEntry(
                    name="tools", role="tooling",
                    path="tools/", remote="org/tools",
                ),
            ],
            releases=[
                ReleaseEntry(project="core", latest_release="v0.1.0"),
                ReleaseEntry(project="prime"),
            ],
            tracks=[
                TrackEntry(track="Track A", status="In Progress", priority=1),
            ],
            critical_path=[
                CriticalPathEntry(phase="A", description="MCP Migration"),
            ],
        ),
    )


class TestRenderBusinessMd:
    def test_contains_vision(self):
        config = _make_config()
        result = render_business_md(config)
        assert "Build great AI" in result

    def test_contains_constraint_table(self):
        config = _make_config()
        result = render_business_md(config)
        assert "| Privacy | Local-first |" in result

    def test_contains_governance_rules(self):
        config = _make_config()
        result = render_business_md(config)
        assert "No cloud inference" in result

    def test_contains_tech_stack(self):
        config = _make_config()
        result = render_business_md(config)
        assert "Python 3.10+" in result


class TestRenderOverlordMd:
    def test_contains_projects_table(self):
        config = _make_config()
        result = render_overlord_md(config)
        assert "| core |" in result
        assert "| prime |" in result

    def test_contains_dependency_graph(self):
        config = _make_config()
        result = render_overlord_md(config)
        assert "core" in result
        assert "prime" in result

    def test_contains_releases(self):
        config = _make_config()
        result = render_overlord_md(config)
        assert "v0.1.0" in result


class TestRenderWorkspaceClaudeMd:
    def test_contains_workspace_name(self):
        config = _make_config()
        result = render_workspace_claude_md(config)
        assert "Test Labs" in result

    def test_contains_project_table(self):
        config = _make_config()
        result = render_workspace_claude_md(config)
        assert "core/" in result


class TestBuildDependencyAscii:
    def test_simple_tree(self):
        projects = [
            ProjectEntry(
                name="core", role="lib", path="core/", remote="x/core",
            ),
            ProjectEntry(
                name="prime", role="deploy", path="prime/", remote="x/prime",
                depends_on=["core"],
            ),
        ]
        result = build_dependency_ascii(projects)
        assert "core" in result
        assert "prime" in result

    def test_standalone_projects(self):
        projects = [
            ProjectEntry(
                name="tools", role="tooling", path="tools/", remote="x/tools",
            ),
        ]
        result = build_dependency_ascii(projects)
        assert "standalone" in result

    def test_mixed_tree_and_standalone(self):
        projects = [
            ProjectEntry(
                name="core", role="lib", path="core/", remote="x/core",
            ),
            ProjectEntry(
                name="prime", role="deploy", path="prime/", remote="x/prime",
                depends_on=["core"],
            ),
            ProjectEntry(
                name="tools", role="tooling", path="tools/", remote="x/tools",
            ),
        ]
        result = build_dependency_ascii(projects)
        assert "core" in result
        assert "prime" in result
        assert "standalone" in result


class TestScaffoldWorkspace:
    def test_creates_files(self, tmp_path):
        config = _make_config()
        result = scaffold_workspace(tmp_path, config)

        assert "BUSINESS.md" in result["created"]
        assert "OVERLORD.md" in result["created"]
        assert "CLAUDE.md" in result["created"]
        assert (tmp_path / "BUSINESS.md").exists()
        assert (tmp_path / "OVERLORD.md").exists()
        assert (tmp_path / "CLAUDE.md").exists()
        assert (tmp_path / "docs").is_dir()
        assert (tmp_path / "conductor" / "tracks").is_dir()

    def test_dry_run_writes_nothing(self, tmp_path):
        config = _make_config()
        result = scaffold_workspace(tmp_path, config, dry_run=True)

        assert "BUSINESS.md" in result["created"]
        assert not (tmp_path / "BUSINESS.md").exists()

    def test_skips_existing_files(self, tmp_path):
        (tmp_path / "BUSINESS.md").write_text("existing")
        config = _make_config()
        result = scaffold_workspace(tmp_path, config)

        assert "BUSINESS.md" in result["skipped"]
        assert (tmp_path / "BUSINESS.md").read_text() == "existing"

    def test_writes_lock(self, tmp_path):
        config = _make_config()
        scaffold_workspace(tmp_path, config)
        lock = read_workspace_lock(tmp_path)
        assert lock is not None
        assert lock.workspace_name == "Test Labs"


class TestLockIO:
    def test_round_trip(self, tmp_path):
        config = _make_config()
        config.generated_at = "2026-02-09T00:00:00Z"
        write_workspace_lock(tmp_path, config)
        loaded = read_workspace_lock(tmp_path)
        assert loaded is not None
        assert loaded.workspace_name == "Test Labs"
        assert len(loaded.manifest.projects) == 3
        assert loaded.business.vision == "Build great AI"

    def test_missing_lock_returns_none(self, tmp_path):
        assert read_workspace_lock(tmp_path) is None


class TestParseOverlordMd:
    def test_round_trip(self):
        config = _make_config()
        rendered = render_overlord_md(config)
        parsed = parse_overlord_md(rendered)

        assert len(parsed.projects) == 3
        assert parsed.projects[0].name == "core"
        assert parsed.projects[1].depends_on == ["core"]

    def test_parses_releases(self):
        config = _make_config()
        rendered = render_overlord_md(config)
        parsed = parse_overlord_md(rendered)

        assert len(parsed.releases) == 2
        assert parsed.releases[0].latest_release == "v0.1.0"

    def test_parses_tracks(self):
        config = _make_config()
        rendered = render_overlord_md(config)
        parsed = parse_overlord_md(rendered)

        assert len(parsed.tracks) == 1
        assert parsed.tracks[0].track == "Track A"

    def test_parses_critical_path(self):
        config = _make_config()
        rendered = render_overlord_md(config)
        parsed = parse_overlord_md(rendered)

        assert len(parsed.critical_path) == 1
        assert parsed.critical_path[0].phase == "A"

    def test_parses_real_overlord_md(self):
        """Parse the actual reference OVERLORD.md format."""
        content = """\
# OVERLORD.md — Ecosystem Manifest

## Projects

| Project | Role | Path | Remote | Depends On |
|---------|------|------|--------|------------|
| nebulus-core | shared-library | nebulus-core/ | jlwestsr/nebulus-core | — |
| nebulus-prime | platform-deployment | nebulus-prime/ | jlwestsr/nebulus-prime | nebulus-core |

## Release Status

| Project | Latest Release | Branch | Tests |
|---------|---------------|--------|-------|
| nebulus-core | v0.1.0 | develop | 372 |
"""
        parsed = parse_overlord_md(content)
        assert len(parsed.projects) == 2
        assert parsed.projects[0].name == "nebulus-core"
        assert parsed.projects[1].depends_on == ["nebulus-core"]
        assert len(parsed.releases) == 1


class TestInjectSection:
    def test_appends_when_no_sentinels(self):
        content = "# My File\n\nSome content"
        section = "## Injected"
        result = _inject_section(content, section)
        assert SENTINEL_START in result
        assert SENTINEL_END in result
        assert "## Injected" in result
        assert "Some content" in result

    def test_replaces_existing_sentinels(self):
        content = (
            "# My File\n\n"
            f"{SENTINEL_START}\nOLD CONTENT\n{SENTINEL_END}\n\n"
            "Footer"
        )
        result = _inject_section(content, "NEW CONTENT")
        assert "OLD CONTENT" not in result
        assert "NEW CONTENT" in result
        assert "Footer" in result

    def test_idempotent(self):
        content = "# My File"
        result1 = _inject_section(content, "SECTION")
        result2 = _inject_section(result1, "SECTION")
        assert result1 == result2


class TestSyncContext:
    def test_injects_into_existing_claude_md(self, tmp_path):
        # Set up workspace
        config = _make_config()
        scaffold_workspace(tmp_path, config)

        # Create a sub-project with CLAUDE.md
        core_dir = tmp_path / "core"
        core_dir.mkdir()
        (core_dir / "CLAUDE.md").write_text("# Core Project\n")

        result = sync_context(tmp_path)
        assert "core/CLAUDE.md" in result["updated"]

        updated = (core_dir / "CLAUDE.md").read_text()
        assert SENTINEL_START in updated
        assert "core" in updated

    def test_idempotent_sync(self, tmp_path):
        config = _make_config()
        scaffold_workspace(tmp_path, config)

        core_dir = tmp_path / "core"
        core_dir.mkdir()
        (core_dir / "CLAUDE.md").write_text("# Core Project\n")

        sync_context(tmp_path)
        content_after_first = (core_dir / "CLAUDE.md").read_text()

        result = sync_context(tmp_path)
        content_after_second = (core_dir / "CLAUDE.md").read_text()
        assert content_after_first == content_after_second
        # No updates on second run
        assert "core/CLAUDE.md" not in result["updated"]

    def test_preserves_user_content(self, tmp_path):
        config = _make_config()
        scaffold_workspace(tmp_path, config)

        core_dir = tmp_path / "core"
        core_dir.mkdir()
        (core_dir / "CLAUDE.md").write_text(
            "# Core Project\n\nUser content here\n"
        )

        sync_context(tmp_path)
        updated = (core_dir / "CLAUDE.md").read_text()
        assert "User content here" in updated

    def test_warns_missing_project_dir(self, tmp_path):
        config = _make_config()
        scaffold_workspace(tmp_path, config)

        result = sync_context(tmp_path)
        assert any("not found" in w for w in result["warnings"])

    def test_does_not_create_missing_claude_md(self, tmp_path):
        config = _make_config()
        scaffold_workspace(tmp_path, config)

        core_dir = tmp_path / "core"
        core_dir.mkdir()
        # No CLAUDE.md created here

        sync_context(tmp_path)
        assert not (core_dir / "CLAUDE.md").exists()

    def test_project_filter(self, tmp_path):
        config = _make_config()
        scaffold_workspace(tmp_path, config)

        core_dir = tmp_path / "core"
        core_dir.mkdir()
        (core_dir / "CLAUDE.md").write_text("# Core\n")

        prime_dir = tmp_path / "prime"
        prime_dir.mkdir()
        (prime_dir / "CLAUDE.md").write_text("# Prime\n")

        result = sync_context(tmp_path, project_filter="core")
        assert "core/CLAUDE.md" in result["updated"]
        assert "prime/CLAUDE.md" not in result["updated"]

    def test_dry_run_sync(self, tmp_path):
        config = _make_config()
        scaffold_workspace(tmp_path, config)

        core_dir = tmp_path / "core"
        core_dir.mkdir()
        (core_dir / "CLAUDE.md").write_text("# Core\n")

        result = sync_context(tmp_path, dry_run=True)
        assert "core/CLAUDE.md" in result["updated"]
        # File unchanged
        assert (core_dir / "CLAUDE.md").read_text() == "# Core\n"

    def test_syncs_gemini_md_too(self, tmp_path):
        config = _make_config()
        scaffold_workspace(tmp_path, config)

        core_dir = tmp_path / "core"
        core_dir.mkdir()
        (core_dir / "GEMINI.md").write_text("# Core Gemini\n")

        result = sync_context(tmp_path)
        assert "core/GEMINI.md" in result["updated"]
