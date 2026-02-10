"""Tests for profile loading from TOML files."""
import pytest

from forge.profile_loader import resolve_profile, list_profiles, merge_inheritance
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


class TestMergeInheritance:
    @pytest.fixture
    def two_level_profiles(self, tmp_path):
        """Create base + fullstack profiles for inheritance testing."""
        base = tmp_path / "base"
        base.mkdir()
        (base / "templates").mkdir()
        (base / "profile.toml").write_text('''
[profile]
name = "base"
description = "Base"

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

[conditionals]
"requirements.txt" = "use_pip"
''')

        child = tmp_path / "fullstack"
        child.mkdir()
        (child / "templates").mkdir()
        (child / "profile.toml").write_text('''
[profile]
name = "fullstack"
inherits = "base"
description = "Fullstack"

[variables]
[variables.use_docker]
prompt = "Docker?"
type = "confirm"
default = true
''')
        (child / "structure.toml").write_text('''
[directories]
root = ["notebooks", "models"]

[files]
"Dockerfile" = "Dockerfile.j2"

[conditionals]
"Dockerfile" = "use_docker"
''')

        return tmp_path

    def test_merges_variables(self, two_level_profiles):
        spec = resolve_profile("fullstack", two_level_profiles)
        resolved = merge_inheritance(spec, two_level_profiles)
        assert "project_name" in resolved.variables  # from base
        assert "use_docker" in resolved.variables     # from child

    def test_unions_directories(self, two_level_profiles):
        spec = resolve_profile("fullstack", two_level_profiles)
        resolved = merge_inheritance(spec, two_level_profiles)
        assert "src" in resolved.directories       # from base
        assert "notebooks" in resolved.directories  # from child

    def test_child_files_override_parent(self, two_level_profiles):
        spec = resolve_profile("fullstack", two_level_profiles)
        resolved = merge_inheritance(spec, two_level_profiles)
        assert "README.md" in resolved.files    # from base
        assert "Dockerfile" in resolved.files   # from child

    def test_merges_conditionals(self, two_level_profiles):
        spec = resolve_profile("fullstack", two_level_profiles)
        resolved = merge_inheritance(spec, two_level_profiles)
        assert "requirements.txt" in resolved.conditionals  # from base
        assert "Dockerfile" in resolved.conditionals         # from child

    def test_template_dirs_child_first(self, two_level_profiles):
        spec = resolve_profile("fullstack", two_level_profiles)
        resolved = merge_inheritance(spec, two_level_profiles)
        assert resolved.template_dirs[0].parent.name == "fullstack"
        assert resolved.template_dirs[1].parent.name == "base"

    def test_resolved_uses_child_name(self, two_level_profiles):
        spec = resolve_profile("fullstack", two_level_profiles)
        resolved = merge_inheritance(spec, two_level_profiles)
        assert resolved.name == "fullstack"

    def test_circular_inheritance_raises(self, tmp_path):
        a = tmp_path / "a"
        a.mkdir()
        (a / "templates").mkdir()
        (a / "profile.toml").write_text('''
[profile]
name = "a"
inherits = "b"
description = "A"
''')
        (a / "structure.toml").write_text("")

        b = tmp_path / "b"
        b.mkdir()
        (b / "templates").mkdir()
        (b / "profile.toml").write_text('''
[profile]
name = "b"
inherits = "a"
description = "B"
''')
        (b / "structure.toml").write_text("")

        spec = resolve_profile("a", tmp_path)
        with pytest.raises(ValueError, match="Circular"):
            merge_inheritance(spec, tmp_path)

    def test_base_profile_no_inheritance(self, profiles_dir):
        spec = resolve_profile("base", profiles_dir)
        resolved = merge_inheritance(spec, profiles_dir)
        assert resolved.name == "base"
        assert len(resolved.template_dirs) == 1
