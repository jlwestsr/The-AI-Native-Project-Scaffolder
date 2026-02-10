"""Integration tests for the full Forge pipeline."""
import pytest

from forge.pipeline import generate
from forge.models import Strategy, ApplyResult
from forge.lockfile import read_lock


@pytest.fixture
def profiles_dir(tmp_path):
    """Create base profile with real templates."""
    base = tmp_path / "profiles" / "base"
    base.mkdir(parents=True)
    (base / "templates").mkdir()

    (base / "profile.toml").write_text('''
[profile]
name = "base"
description = "Test base"

[variables]
[variables.project_name]
prompt = "Project name"
type = "string"
''')

    (base / "structure.toml").write_text('''
[directories]
root = ["src", "tests"]

[files]
"README.md" = "README.md.j2"
".gitignore" = ".gitignore.j2"
''')

    (base / "templates" / "README.md.j2").write_text("# {{ project_name }}")
    (base / "templates" / ".gitignore.j2").write_text("__pycache__/")

    return tmp_path / "profiles"


class TestGenerate:
    def test_full_generate(self, tmp_path, profiles_dir):
        target = tmp_path / "output"
        target.mkdir()

        result = generate(
            profile_name="base",
            target=target,
            variables={"project_name": "my-test"},
            strategy=Strategy.CREATE,
            profiles_dir=profiles_dir,
        )

        assert isinstance(result, ApplyResult)
        assert (target / "README.md").exists()
        assert "# my-test" in (target / "README.md").read_text()
        assert (target / ".gitignore").exists()
        assert (target / "src").is_dir()
        assert (target / "tests").is_dir()

    def test_lock_file_created(self, tmp_path, profiles_dir):
        target = tmp_path / "output"
        target.mkdir()

        generate(
            profile_name="base",
            target=target,
            variables={"project_name": "test"},
            strategy=Strategy.CREATE,
            profiles_dir=profiles_dir,
        )

        lock = read_lock(target)
        assert lock is not None
        assert lock.profile == "base"
        assert lock.managed["README.md"].template == "README.md.j2"

    def test_generate_then_update_adds_new_file(self, tmp_path, profiles_dir):
        target = tmp_path / "output"
        target.mkdir()

        # First generate
        generate(
            profile_name="base",
            target=target,
            variables={"project_name": "test"},
            strategy=Strategy.CREATE,
            profiles_dir=profiles_dir,
        )

        # Add a new file to the profile
        (profiles_dir / "base" / "structure.toml").write_text('''
[directories]
root = ["src", "tests"]

[files]
"README.md" = "README.md.j2"
".gitignore" = ".gitignore.j2"
"CHANGELOG.md" = "README.md.j2"
''')

        # Update
        result = generate(
            profile_name="base",
            target=target,
            variables={"project_name": "test"},
            strategy=Strategy.UPDATE,
            profiles_dir=profiles_dir,
        )
        assert "CHANGELOG.md" in result.created

    def test_update_preserves_user_changes(self, tmp_path, profiles_dir):
        target = tmp_path / "output"
        target.mkdir()

        generate(
            profile_name="base",
            target=target,
            variables={"project_name": "test"},
            strategy=Strategy.CREATE,
            profiles_dir=profiles_dir,
        )

        # User edits README
        (target / "README.md").write_text("# My Custom README")

        # Update with different template content
        result = generate(
            profile_name="base",
            target=target,
            variables={"project_name": "test-v2"},
            strategy=Strategy.UPDATE,
            profiles_dir=profiles_dir,
        )

        assert "README.md" in result.skipped
        assert (target / "README.md").read_text() == "# My Custom README"

    def test_dry_run(self, tmp_path, profiles_dir):
        target = tmp_path / "output"
        target.mkdir()

        result = generate(
            profile_name="base",
            target=target,
            variables={"project_name": "test"},
            strategy=Strategy.CREATE,
            profiles_dir=profiles_dir,
            dry_run=True,
        )

        assert len(result.created) > 0
        assert not (target / "README.md").exists()
