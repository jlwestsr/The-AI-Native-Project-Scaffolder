"""Tests for workspace Pydantic models."""
import pytest
from pydantic import ValidationError

from forge.models import (
    BusinessConstraint,
    BusinessContext,
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


class TestBusinessConstraint:
    def test_construction(self):
        c = BusinessConstraint(constraint="Privacy", value="Local-first")
        assert c.constraint == "Privacy"
        assert c.value == "Local-first"

    def test_missing_field_rejected(self):
        with pytest.raises(ValidationError):
            BusinessConstraint(constraint="Privacy")


class TestHardwareTier:
    def test_construction(self):
        h = HardwareTier(
            tier=1, platform="Edge", hardware="M4 Pro", use_case="Appliance"
        )
        assert h.tier == 1
        assert h.platform == "Edge"

    def test_missing_field_rejected(self):
        with pytest.raises(ValidationError):
            HardwareTier(tier=1, platform="Edge")


class TestStrategicPriority:
    def test_construction(self):
        p = StrategicPriority(priority=1, goal="Ship v1", key_result="Done")
        assert p.priority == 1
        assert p.goal == "Ship v1"


class TestTechStackEntry:
    def test_construction_with_default_locked(self):
        t = TechStackEntry(layer="Core", technology="Python 3.10+")
        assert t.locked is True

    def test_explicit_unlocked(self):
        t = TechStackEntry(layer="CSS", technology="Tailwind", locked=False)
        assert t.locked is False


class TestBusinessContext:
    def test_defaults(self):
        b = BusinessContext()
        assert b.schema_version == "1.0"
        assert b.vision == ""
        assert b.constraints == []
        assert b.governance_rules == []

    def test_full_construction(self):
        b = BusinessContext(
            vision="Build AI",
            constraints=[BusinessConstraint(constraint="X", value="Y")],
            governance_rules=["No cloud"],
        )
        assert b.vision == "Build AI"
        assert len(b.constraints) == 1
        assert len(b.governance_rules) == 1


class TestProjectEntry:
    def test_construction(self):
        p = ProjectEntry(
            name="core", role="shared-library", path="core/", remote="org/core"
        )
        assert p.depends_on == []

    def test_with_dependencies(self):
        p = ProjectEntry(
            name="prime", role="deployment", path="prime/",
            remote="org/prime", depends_on=["core"],
        )
        assert p.depends_on == ["core"]


class TestReleaseEntry:
    def test_defaults(self):
        r = ReleaseEntry(project="core")
        assert r.latest_release == "—"
        assert r.branch == "develop"
        assert r.tests == "—"


class TestTrackEntry:
    def test_defaults(self):
        t = TrackEntry(track="My Track")
        assert t.status == "In Progress"
        assert t.priority == 3


class TestCriticalPathEntry:
    def test_defaults(self):
        c = CriticalPathEntry(phase="A", description="Do thing")
        assert c.status == "Pending"
        assert c.priority == 1


class TestOverlordManifest:
    def test_defaults(self):
        m = OverlordManifest()
        assert m.projects == []
        assert m.releases == []
        assert m.tracks == []
        assert m.critical_path == []

    def test_full_construction(self):
        m = OverlordManifest(
            projects=[
                ProjectEntry(
                    name="core", role="lib", path="core/", remote="x/core"
                )
            ],
            releases=[ReleaseEntry(project="core", latest_release="v1.0")],
            tracks=[TrackEntry(track="T1")],
            critical_path=[CriticalPathEntry(phase="A", description="D")],
        )
        assert len(m.projects) == 1
        assert m.releases[0].latest_release == "v1.0"


class TestWorkspaceConfig:
    def test_minimal(self):
        w = WorkspaceConfig(workspace_name="Test Labs")
        assert w.workspace_name == "Test Labs"
        assert w.version == "1.0"
        assert w.generated_at == ""

    def test_serialization_round_trip(self):
        w = WorkspaceConfig(
            workspace_name="Test Labs",
            generated_at="2026-02-09T00:00:00Z",
            business=BusinessContext(vision="Build"),
            manifest=OverlordManifest(
                projects=[
                    ProjectEntry(
                        name="a", role="lib", path="a/", remote="x/a"
                    )
                ]
            ),
        )
        json_str = w.model_dump_json()
        w2 = WorkspaceConfig.model_validate_json(json_str)
        assert w2.workspace_name == "Test Labs"
        assert len(w2.manifest.projects) == 1
        assert w2.business.vision == "Build"
