"""Tests for Forge v2 Pydantic models."""
import pytest
from pathlib import Path
from pydantic import ValidationError

from forge.models import (
    VariableSpec,
    ProfileSpec,
    ResolvedProfile,
    RenderedFile,
    Strategy,
    ApplyResult,
    ManagedFileEntry,
    ForgeLock,
)


class TestVariableSpec:
    def test_string_variable(self):
        v = VariableSpec(prompt="Project name", type="string")
        assert v.prompt == "Project name"
        assert v.type == "string"
        assert v.default is None
        assert v.choices is None

    def test_choice_variable(self):
        v = VariableSpec(
            prompt="Package manager",
            type="choice",
            choices=["pip", "poetry", "uv"],
            default="pip",
        )
        assert v.choices == ["pip", "poetry", "uv"]
        assert v.default == "pip"

    def test_confirm_variable(self):
        v = VariableSpec(prompt="Include Docker?", type="confirm", default=True)
        assert v.type == "confirm"
        assert v.default is True

    def test_invalid_type_rejected(self):
        with pytest.raises(ValidationError):
            VariableSpec(prompt="Bad", type="banana")


class TestProfileSpec:
    def test_minimal_profile(self):
        p = ProfileSpec(
            name="test",
            description="A test profile",
            template_dir=Path("/tmp/templates"),
        )
        assert p.name == "test"
        assert p.inherits is None
        assert p.variables == {}
        assert p.directories == []
        assert p.files == {}

    def test_full_profile(self):
        p = ProfileSpec(
            name="fullstack",
            description="Full stack",
            inherits="base",
            variables={
                "project_name": VariableSpec(prompt="Name", type="string")
            },
            directories=["src", "tests"],
            files={"README.md": "README.md.j2"},
            conditionals={"Dockerfile": "use_docker"},
            template_dir=Path("/tmp/templates"),
        )
        assert p.inherits == "base"
        assert "project_name" in p.variables
        assert len(p.directories) == 2

    def test_missing_name_rejected(self):
        with pytest.raises(ValidationError):
            ProfileSpec(
                description="No name",
                template_dir=Path("/tmp"),
            )

    def test_missing_description_rejected(self):
        with pytest.raises(ValidationError):
            ProfileSpec(
                name="test",
                template_dir=Path("/tmp"),
            )


class TestResolvedProfile:
    def test_resolved_has_template_dirs_list(self):
        r = ResolvedProfile(
            name="fullstack",
            description="Full stack",
            template_dirs=[Path("/profiles/fullstack"), Path("/profiles/base")],
        )
        assert len(r.template_dirs) == 2


class TestRenderedFile:
    def test_rendered_file(self):
        rf = RenderedFile(
            output_path="README.md",
            content="# Hello",
            template_name="README.md.j2",
            content_hash="abc123",
        )
        assert rf.output_path == "README.md"
        assert rf.content_hash == "abc123"


class TestStrategy:
    def test_strategy_values(self):
        assert Strategy.CREATE == "create"
        assert Strategy.UPDATE == "update"
        assert Strategy.FORCE == "force"


class TestApplyResult:
    def test_empty_result(self):
        r = ApplyResult()
        assert r.created == []
        assert r.updated == []
        assert r.skipped == []
        assert r.warnings == []


class TestForgeLock:
    def test_lock_round_trip(self):
        lock = ForgeLock(
            version="2.0.0",
            profile="fullstack",
            generated_at="2026-02-03T14:30:00Z",
            variables={"project_name": "my-project", "use_docker": True},
            managed={
                "README.md": ManagedFileEntry(
                    template="README.md.j2", hash="abc123"
                )
            },
        )
        assert lock.profile == "fullstack"
        assert lock.managed["README.md"].hash == "abc123"
