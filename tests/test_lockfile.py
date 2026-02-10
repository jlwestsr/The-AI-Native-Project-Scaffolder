"""Tests for .forge.lock read/write/diff operations."""
import pytest

from forge.lockfile import write_lock, read_lock, diff_lock
from forge.models import (
    ForgeLock,
    ManagedFileEntry,
    RenderedFile,
    FileAction,
)


@pytest.fixture
def sample_lock():
    return ForgeLock(
        version="2.0.0",
        profile="fullstack",
        generated_at="2026-02-03T14:30:00Z",
        variables={"project_name": "test", "use_docker": True},
        managed={
            "README.md": ManagedFileEntry(template="README.md.j2", hash="abc123"),
            ".gitignore": ManagedFileEntry(template=".gitignore.j2", hash="def456"),
        },
    )


@pytest.fixture
def sample_rendered():
    return [
        RenderedFile(
            output_path="README.md",
            content="# Test",
            template_name="README.md.j2",
            content_hash="abc123",
        ),
        RenderedFile(
            output_path=".gitignore",
            content="__pycache__/",
            template_name=".gitignore.j2",
            content_hash="def456",
        ),
    ]


class TestWriteAndReadLock:
    def test_write_then_read(self, tmp_path, sample_lock):
        write_lock(sample_lock, tmp_path)
        loaded = read_lock(tmp_path)
        assert loaded is not None
        assert loaded.version == "2.0.0"
        assert loaded.profile == "fullstack"
        assert loaded.managed["README.md"].hash == "abc123"

    def test_read_missing_returns_none(self, tmp_path):
        result = read_lock(tmp_path)
        assert result is None

    def test_variables_preserved(self, tmp_path, sample_lock):
        write_lock(sample_lock, tmp_path)
        loaded = read_lock(tmp_path)
        assert loaded.variables["project_name"] == "test"
        assert loaded.variables["use_docker"] is True


class TestDiffLock:
    def test_detects_new_files(self, sample_lock, sample_rendered):
        new_file = RenderedFile(
            output_path="Dockerfile",
            content="FROM python:3.11",
            template_name="Dockerfile.j2",
            content_hash="new123",
        )
        actions = diff_lock(sample_lock, sample_rendered + [new_file])
        assert actions["Dockerfile"] == FileAction.CREATE

    def test_detects_updatable_files(self, sample_lock, sample_rendered):
        updated = RenderedFile(
            output_path="README.md",
            content="# Updated",
            template_name="README.md.j2",
            content_hash="new_hash",
        )
        rendered = [updated, sample_rendered[1]]
        actions = diff_lock(sample_lock, rendered, disk_hashes={"README.md": "abc123"})
        assert actions["README.md"] == FileAction.UPDATE

    def test_detects_user_modified_files(self, sample_lock, sample_rendered):
        updated = RenderedFile(
            output_path="README.md",
            content="# Updated",
            template_name="README.md.j2",
            content_hash="new_hash",
        )
        rendered = [updated, sample_rendered[1]]
        actions = diff_lock(
            sample_lock, rendered, disk_hashes={"README.md": "user_edited"}
        )
        assert actions["README.md"] == FileAction.SKIP_MODIFIED

    def test_detects_user_deleted_files(self, sample_lock):
        rendered = [
            RenderedFile(
                output_path="README.md",
                content="# Test",
                template_name="README.md.j2",
                content_hash="abc123",
            ),
        ]
        actions = diff_lock(
            sample_lock,
            rendered,
            disk_hashes={},
            existing_files=set(),
        )
        assert actions["README.md"] == FileAction.SKIP_DELETED

    def test_unchanged_files_not_in_actions(self, sample_lock, sample_rendered):
        actions = diff_lock(
            sample_lock,
            sample_rendered,
            disk_hashes={"README.md": "abc123", ".gitignore": "def456"},
        )
        assert "README.md" not in actions
        assert ".gitignore" not in actions
