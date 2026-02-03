"""Tests for the Typer CLI."""
import pytest
from typer.testing import CliRunner
from pathlib import Path

from forge.cli import app


runner = CliRunner()


@pytest.fixture
def profiles_dir(tmp_path):
    """Create a minimal profile for CLI testing."""
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
''')

    (base / "templates" / "README.md.j2").write_text("# {{ project_name }}")
    return tmp_path / "profiles"


class TestNewCommand:
    def test_new_creates_project(self, tmp_path, profiles_dir, monkeypatch):
        target = tmp_path / "myproject"
        monkeypatch.setattr("forge.cli.get_profiles_dir", lambda: profiles_dir)

        result = runner.invoke(app, [
            "new", str(target),
            "--profile", "base",
            "--no-interactive",
            "--var", "project_name=myproject",
        ])

        assert result.exit_code == 0, result.output
        assert (target / "README.md").exists()

    def test_new_dry_run(self, tmp_path, profiles_dir, monkeypatch):
        target = tmp_path / "myproject"
        monkeypatch.setattr("forge.cli.get_profiles_dir", lambda: profiles_dir)

        result = runner.invoke(app, [
            "new", str(target),
            "--profile", "base",
            "--no-interactive",
            "--dry-run",
            "--var", "project_name=myproject",
        ])

        assert result.exit_code == 0, result.output
        assert not (target / "README.md").exists()

    def test_new_missing_profile_errors(self, tmp_path, profiles_dir, monkeypatch):
        target = tmp_path / "myproject"
        monkeypatch.setattr("forge.cli.get_profiles_dir", lambda: profiles_dir)

        result = runner.invoke(app, [
            "new", str(target),
            "--profile", "nonexistent",
            "--no-interactive",
            "--var", "project_name=test",
        ])

        assert result.exit_code != 0


class TestProfilesCommand:
    def test_profiles_list(self, profiles_dir, monkeypatch):
        monkeypatch.setattr("forge.cli.get_profiles_dir", lambda: profiles_dir)
        result = runner.invoke(app, ["profiles", "list"])
        assert result.exit_code == 0
        assert "base" in result.output
