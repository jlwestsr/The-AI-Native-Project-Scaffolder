"""Tests for profile loading from TOML files."""
import pytest
from pathlib import Path

from forge.profile_loader import resolve_profile, list_profiles
from forge.models import ProfileSpec


@pytest.fixture
def profiles_dir(tmp_path):
    """Create a minimal profile directory structure for testing."""
    base = tmp_path / "base"
    base.mkdir()
    (base / "templates").mkdir()

    (base / "profile.toml").write_text('''
[profile]
name = "base"
description = "Test base profile"

[variables]
[variables.project_name]
prompt = "Project name"
type = "string"

[variables.manager]
prompt = "Package manager"
type = "choice"
choices = ["pip", "poetry", "uv"]
default = "pip"
''')

    (base / "structure.toml").write_text('''
[directories]
root = ["src", "tests", "docs"]

[files]
"README.md" = "README.md.j2"
".gitignore" = ".gitignore.j2"
"pyproject.toml" = "pyproject.toml.j2"

[conditionals]
"requirements.txt" = "use_pip"
''')

    return tmp_path


class TestResolveProfile:
    def test_loads_valid_profile(self, profiles_dir):
        profile = resolve_profile("base", profiles_dir)
        assert isinstance(profile, ProfileSpec)
        assert profile.name == "base"
        assert profile.description == "Test base profile"

    def test_loads_variables(self, profiles_dir):
        profile = resolve_profile("base", profiles_dir)
        assert "project_name" in profile.variables
        assert profile.variables["project_name"].type == "string"
        assert "manager" in profile.variables
        assert profile.variables["manager"].choices == ["pip", "poetry", "uv"]

    def test_loads_directories(self, profiles_dir):
        profile = resolve_profile("base", profiles_dir)
        assert profile.directories == ["src", "tests", "docs"]

    def test_loads_files(self, profiles_dir):
        profile = resolve_profile("base", profiles_dir)
        assert profile.files["README.md"] == "README.md.j2"
        assert len(profile.files) == 3

    def test_loads_conditionals(self, profiles_dir):
        profile = resolve_profile("base", profiles_dir)
        assert profile.conditionals["requirements.txt"] == "use_pip"

    def test_template_dir_set(self, profiles_dir):
        profile = resolve_profile("base", profiles_dir)
        assert profile.template_dir == profiles_dir / "base" / "templates"

    def test_nonexistent_profile_raises(self, profiles_dir):
        with pytest.raises(FileNotFoundError):
            resolve_profile("nonexistent", profiles_dir)

    def test_missing_profile_toml_raises(self, tmp_path):
        (tmp_path / "bad").mkdir()
        with pytest.raises(FileNotFoundError):
            resolve_profile("bad", tmp_path)


class TestListProfiles:
    def test_lists_available_profiles(self, profiles_dir):
        profiles = list_profiles(profiles_dir)
        assert "base" in profiles

    def test_ignores_non_profile_dirs(self, profiles_dir):
        (profiles_dir / "not_a_profile").mkdir()
        profiles = list_profiles(profiles_dir)
        assert "not_a_profile" not in profiles
