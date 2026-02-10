"""Tests for applying rendered files to disk."""
import hashlib
import pytest

from forge.applier import apply_to_disk
from forge.models import (
    RenderedFile,
    ResolvedProfile,
    Strategy,
    ApplyResult,
    ForgeLock,
    ManagedFileEntry,
)


@pytest.fixture
def rendered_files():
    return [
        RenderedFile(
            output_path="README.md",
            content="# My Project",
            template_name="README.md.j2",
            content_hash="abc123",
        ),
        RenderedFile(
            output_path="src/myapp/__init__.py",
            content="",
            template_name="__init__.py.j2",
            content_hash="empty1",
        ),
    ]


@pytest.fixture
def profile():
    return ResolvedProfile(
        name="test",
        description="Test profile",
        directories=["src/myapp", "tests"],
        files={
            "README.md": "README.md.j2",
            "src/myapp/__init__.py": "__init__.py.j2",
        },
        template_dirs=[],
    )


class TestCreateStrategy:
    def test_creates_files(self, tmp_path, rendered_files, profile):
        result = apply_to_disk(rendered_files, profile, tmp_path, Strategy.CREATE)
        assert (tmp_path / "README.md").exists()
        assert (tmp_path / "README.md").read_text() == "# My Project"
        assert "README.md" in result.created

    def test_creates_directories(self, tmp_path, rendered_files, profile):
        apply_to_disk(rendered_files, profile, tmp_path, Strategy.CREATE)
        assert (tmp_path / "src" / "myapp").is_dir()
        assert (tmp_path / "tests").is_dir()

    def test_creates_nested_file_directories(self, tmp_path, rendered_files, profile):
        apply_to_disk(rendered_files, profile, tmp_path, Strategy.CREATE)
        assert (tmp_path / "src" / "myapp" / "__init__.py").exists()

    def test_errors_on_existing_files(self, tmp_path, rendered_files, profile):
        (tmp_path / "README.md").write_text("existing")
        with pytest.raises(FileExistsError):
            apply_to_disk(rendered_files, profile, tmp_path, Strategy.CREATE)


class TestForceStrategy:
    def test_overwrites_existing(self, tmp_path, rendered_files, profile):
        (tmp_path / "README.md").write_text("old content")
        result = apply_to_disk(rendered_files, profile, tmp_path, Strategy.FORCE)
        assert (tmp_path / "README.md").read_text() == "# My Project"
        assert "README.md" in result.created


class TestUpdateStrategy:
    def test_adds_new_files(self, tmp_path, rendered_files, profile):
        lock = ForgeLock(
            version="2.0.0",
            profile="test",
            generated_at="2026-01-01T00:00:00Z",
            managed={},
        )
        result = apply_to_disk(
            rendered_files, profile, tmp_path, Strategy.UPDATE, lock=lock
        )
        assert (tmp_path / "README.md").exists()
        assert "README.md" in result.created

    def test_updates_unmodified_files(self, tmp_path, profile):
        old_content = "# Old"
        old_hash = hashlib.sha256(old_content.encode()).hexdigest()[:16]
        (tmp_path / "README.md").write_text(old_content)

        lock = ForgeLock(
            version="2.0.0",
            profile="test",
            generated_at="2026-01-01T00:00:00Z",
            managed={
                "README.md": ManagedFileEntry(
                    template="README.md.j2", hash=old_hash
                )
            },
        )
        new_rendered = [
            RenderedFile(
                output_path="README.md",
                content="# New",
                template_name="README.md.j2",
                content_hash="new_hash",
            ),
        ]
        result = apply_to_disk(
            new_rendered, profile, tmp_path, Strategy.UPDATE, lock=lock
        )
        assert (tmp_path / "README.md").read_text() == "# New"
        assert "README.md" in result.updated

    def test_skips_user_modified_files(self, tmp_path, profile):
        (tmp_path / "README.md").write_text("# User edited this")

        lock = ForgeLock(
            version="2.0.0",
            profile="test",
            generated_at="2026-01-01T00:00:00Z",
            managed={
                "README.md": ManagedFileEntry(
                    template="README.md.j2", hash="original_hash"
                )
            },
        )
        new_rendered = [
            RenderedFile(
                output_path="README.md",
                content="# New from template",
                template_name="README.md.j2",
                content_hash="new_hash",
            ),
        ]
        result = apply_to_disk(
            new_rendered, profile, tmp_path, Strategy.UPDATE, lock=lock
        )
        assert (tmp_path / "README.md").read_text() == "# User edited this"
        assert "README.md" in result.skipped

    def test_requires_lock(self, tmp_path, rendered_files, profile):
        with pytest.raises(ValueError, match="lock"):
            apply_to_disk(
                rendered_files, profile, tmp_path, Strategy.UPDATE, lock=None
            )


class TestApplyResult:
    def test_result_counts(self, tmp_path, rendered_files, profile):
        result = apply_to_disk(rendered_files, profile, tmp_path, Strategy.CREATE)
        assert isinstance(result, ApplyResult)
        assert len(result.created) == 2
        assert len(result.skipped) == 0
