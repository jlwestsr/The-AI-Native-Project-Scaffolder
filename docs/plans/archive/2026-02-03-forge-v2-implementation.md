# Forge v2 Rewrite — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rewrite Forge as a profile-driven project lifecycle manager with TOML profiles, lock file tracking, pipeline engine, and Typer CLI.

**Architecture:** Six-stage pipeline (resolve → merge → render → apply → lock) with profiles defined as TOML + Jinja2 directories. Pydantic models at every boundary. Typer for the CLI.

**Tech Stack:** Python 3.10+, Typer, Pydantic v2, Jinja2, questionary, tomli/tomli-w, platformdirs, rich

**Worktree:** `.worktrees/v2-rewrite` on branch `feat/v2-rewrite`

**Working directory for all commands:** `/home/jlwestsr/projects/west_ai_labs/forge/.worktrees/v2-rewrite`

---

## Task 1: Project Skeleton

**Files:**
- Create: `src/forge/__init__.py`
- Create: `src/forge/models.py`
- Modify: `pyproject.toml`
- Create: `tests/__init__.py`
- Create: `tests/test_models.py`

**Step 1: Clean the v1 source tree**

Remove v1 application code from the worktree. Keep docs, templates (for reference), and scripts.

```bash
cd /home/jlwestsr/projects/west_ai_labs/forge/.worktrees/v2-rewrite
rm -rf src/project_generator src/data src/features src/models src/visualization
rm -rf tests/test_engine.py tests/test_wizard.py tests/test_cli.py tests/test_git_ops.py tests/test_config_manager.py tests/test_pre_commit.py tests/test_update.py tests/test_persona.py tests/test_initial.py
rm -f src/__init__.py
mkdir -p src/forge
touch src/forge/__init__.py
touch tests/__init__.py
```

**Step 2: Update pyproject.toml**

Replace the existing pyproject.toml with v2 dependencies and entry point:

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "forge-scaffolder"
version = "2.0.0"
description = "Production-grade AI Project Scaffolder"
requires-python = ">=3.10"
dependencies = [
    "typer[all]>=0.9.0",
    "pydantic>=2.0.0",
    "jinja2>=3.1.0",
    "questionary>=2.0.0",
    "platformdirs>=3.0.0",
    "tomli>=2.0.0;python_version<'3.11'",
    "tomli-w>=1.0.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-tmp-files>=0.0.2",
]

[project.scripts]
forge = "forge.cli:app"

[tool.setuptools.packages.find]
where = ["src"]

[tool.black]
line-length = 88
target-version = ["py310", "py311", "py312"]

[tool.pytest.ini_options]
minversion = "6.0"
testpaths = ["tests"]
pythonpath = ["src"]

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503"]
```

**Step 3: Write models.py**

```python
"""Pydantic models for Forge v2 pipeline."""
from __future__ import annotations

import enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class VariableSpec(BaseModel):
    """Specification for a single profile variable."""
    prompt: str
    type: Literal["string", "choice", "confirm"]
    default: str | bool | None = None
    choices: list[str] | None = None


class ProfileSpec(BaseModel):
    """Raw profile loaded from a single profile.toml + structure.toml."""
    name: str
    description: str
    inherits: str | None = None
    variables: dict[str, VariableSpec] = Field(default_factory=dict)
    directories: list[str] = Field(default_factory=list)
    files: dict[str, str] = Field(default_factory=dict)
    conditionals: dict[str, str] = Field(default_factory=dict)
    template_dir: Path


class ResolvedProfile(BaseModel):
    """Profile after inheritance chain is fully merged."""
    name: str
    description: str
    variables: dict[str, VariableSpec] = Field(default_factory=dict)
    directories: list[str] = Field(default_factory=list)
    files: dict[str, str] = Field(default_factory=dict)
    conditionals: dict[str, str] = Field(default_factory=dict)
    template_dirs: list[Path] = Field(default_factory=list)


class RenderedFile(BaseModel):
    """A file that has been rendered in memory, ready to write."""
    output_path: str
    content: str
    template_name: str
    content_hash: str


class Strategy(str, enum.Enum):
    """File application strategy."""
    CREATE = "create"
    UPDATE = "update"
    FORCE = "force"


class FileAction(str, enum.Enum):
    """Action to take on a single file during apply."""
    CREATE = "create"
    UPDATE = "update"
    SKIP_MODIFIED = "skip_modified"
    SKIP_DELETED = "skip_deleted"
    WARN_DEPRECATED = "warn_deprecated"


class ApplyResult(BaseModel):
    """Result of applying rendered files to disk."""
    created: list[str] = Field(default_factory=list)
    updated: list[str] = Field(default_factory=list)
    skipped: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ManagedFileEntry(BaseModel):
    """A single entry in the lock file's managed files section."""
    template: str
    hash: str


class ForgeLock(BaseModel):
    """The .forge.lock file schema."""
    version: str
    profile: str
    generated_at: str
    variables: dict[str, str | bool] = Field(default_factory=dict)
    managed: dict[str, ManagedFileEntry] = Field(default_factory=dict)
```

**Step 4: Write the failing test**

Create `tests/test_models.py`:

```python
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
```

**Step 5: Run test to verify it fails**

```bash
cd /home/jlwestsr/projects/west_ai_labs/forge/.worktrees/v2-rewrite
pip install -e ".[dev]" 2>/dev/null
pytest tests/test_models.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'forge'` or similar until models.py is in place.

**Step 6: Place models.py and run tests**

```bash
pytest tests/test_models.py -v
```

Expected: All 12 tests PASS.

**Step 7: Commit**

```bash
git add -A
git commit -m "feat(v2): project skeleton with Pydantic models

Set up v2 project structure with Typer, Pydantic, Jinja2 dependencies.
Define all pipeline data models: VariableSpec, ProfileSpec,
ResolvedProfile, RenderedFile, Strategy, ApplyResult, ForgeLock."
```

---

## Task 2: Profile Loader (Single Profile, No Inheritance)

**Files:**
- Create: `profiles/base/profile.toml`
- Create: `profiles/base/structure.toml`
- Create: `src/forge/profile_loader.py`
- Create: `tests/test_profile_loader.py`

**Step 1: Create the base profile TOML files**

Create `profiles/base/profile.toml`:

```toml
[profile]
name = "base"
description = "Common foundation for all Forge projects"

[variables]
[variables.project_name]
prompt = "Project name"
type = "string"

[variables.author_name]
prompt = "Author name"
type = "string"
default = ""

[variables.author_email]
prompt = "Author email"
type = "string"
default = ""

[variables.description]
prompt = "Project description"
type = "string"
default = ""

[variables.python_version]
prompt = "Minimum Python version"
type = "choice"
choices = ["3.10", "3.11", "3.12"]
default = "3.10"

[variables.manager]
prompt = "Package manager"
type = "choice"
choices = ["pip", "poetry", "uv"]
default = "pip"

[variables.license]
prompt = "License"
type = "choice"
choices = ["MIT", "Apache 2.0", "Proprietary", "None"]
default = "MIT"
```

Create `profiles/base/structure.toml`:

```toml
[directories]
root = [
    "src/{{ project_slug }}",
    "tests",
    "docs",
    "docs/features",
    "scripts",
    ".agent/rules",
    ".github/workflows",
]

[files]
"README.md" = "README.md.j2"
"CONTEXT.md" = "CONTEXT.md.j2"
"AI_DIRECTIVES.md" = "AI_DIRECTIVES.md.j2"
"WORKFLOW.md" = "WORKFLOW.md.j2"
"GEMINI.md" = "GEMINI.md.j2"
".gitignore" = ".gitignore.j2"
".flake8" = ".flake8.j2"
".yamllint" = ".yamllint.j2"
".pre-commit-config.yaml" = ".pre-commit-config.yaml.j2"
"docs/index.md" = "docs/index.md.j2"
"docs/feature_template.md" = "docs/feature_template.md.j2"
"docs/AI_INSIGHTS.md" = "docs/AI_INSIGHTS.md.j2"
".github/workflows/docs.yml" = ".github/workflows/docs.yml.j2"
"pyproject.toml" = "pyproject.toml.j2"
"requirements.txt" = "requirements.txt.j2"
"requirements-dev.txt" = "requirements-dev.txt.j2"
"src/{{ project_slug }}/__init__.py" = "__init__.py.j2"
"tests/__init__.py" = "__init__.py.j2"
"tests/test_initial.py" = "tests/test_initial.py.j2"
".agent/rules/ai_behavior.md" = ".agent/rules/ai_behavior.md.j2"
".github/workflows/unittests.yml" = ".github/workflows/unittests.yml.j2"

[conditionals]
"requirements.txt" = "use_pip"
"requirements-dev.txt" = "use_pip"
```

Create `profiles/base/templates/` — initially empty, will be populated in Task 10.

```bash
mkdir -p profiles/base/templates
```

**Step 2: Write the failing test**

Create `tests/test_profile_loader.py`:

```python
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
        # Create a directory without profile.toml
        (profiles_dir / "not_a_profile").mkdir()
        profiles = list_profiles(profiles_dir)
        assert "not_a_profile" not in profiles
```

**Step 3: Run test to verify it fails**

```bash
pytest tests/test_profile_loader.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'forge.profile_loader'`

**Step 4: Write profile_loader.py**

Create `src/forge/profile_loader.py`:

```python
"""Load and validate profiles from TOML files."""
from __future__ import annotations

import sys
from pathlib import Path

from forge.models import ProfileSpec, VariableSpec

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def resolve_profile(name: str, profiles_dir: Path) -> ProfileSpec:
    """Load a single profile from its TOML files.

    Args:
        name: Profile directory name (e.g., "base", "fullstack").
        profiles_dir: Root directory containing all profile directories.

    Returns:
        A validated ProfileSpec.

    Raises:
        FileNotFoundError: If the profile directory or required files are missing.
    """
    profile_path = profiles_dir / name
    if not profile_path.is_dir():
        raise FileNotFoundError(f"Profile directory not found: {profile_path}")

    profile_toml = profile_path / "profile.toml"
    if not profile_toml.exists():
        raise FileNotFoundError(f"profile.toml not found in: {profile_path}")

    structure_toml = profile_path / "structure.toml"

    # Load profile.toml
    with open(profile_toml, "rb") as f:
        profile_data = tomllib.load(f)

    # Load structure.toml (optional — a profile may only have profile.toml)
    structure_data: dict = {}
    if structure_toml.exists():
        with open(structure_toml, "rb") as f:
            structure_data = tomllib.load(f)

    # Parse variables
    raw_variables = profile_data.get("variables", {})
    variables = {
        key: VariableSpec(**val) for key, val in raw_variables.items()
    }

    # Build ProfileSpec
    profile_section = profile_data.get("profile", {})
    return ProfileSpec(
        name=profile_section["name"],
        description=profile_section["description"],
        inherits=profile_section.get("inherits"),
        variables=variables,
        directories=structure_data.get("directories", {}).get("root", []),
        files=structure_data.get("files", {}),
        conditionals=structure_data.get("conditionals", {}),
        template_dir=profile_path / "templates",
    )


def list_profiles(profiles_dir: Path) -> list[str]:
    """List all valid profile names in the profiles directory.

    A valid profile is a subdirectory containing a profile.toml file.

    Args:
        profiles_dir: Root directory containing all profile directories.

    Returns:
        Sorted list of profile names.
    """
    profiles = []
    for entry in sorted(profiles_dir.iterdir()):
        if entry.is_dir() and (entry / "profile.toml").exists():
            profiles.append(entry.name)
    return profiles
```

**Step 5: Run tests**

```bash
pytest tests/test_profile_loader.py -v
```

Expected: All 9 tests PASS.

**Step 6: Commit**

```bash
git add -A
git commit -m "feat(v2): profile loader with TOML parsing

Add profile_loader.py that reads profile.toml and structure.toml
into validated ProfileSpec models. Create base profile TOML files.
Supports listing available profiles and error handling for missing
profiles."
```

---

## Task 3: Renderer

**Files:**
- Create: `src/forge/renderer.py`
- Create: `tests/test_renderer.py`

**Step 1: Write the failing test**

Create `tests/test_renderer.py`:

```python
"""Tests for Jinja2 template rendering."""
import pytest
from pathlib import Path

from forge.renderer import render_templates
from forge.models import ResolvedProfile, VariableSpec, RenderedFile


@pytest.fixture
def base_templates(tmp_path):
    """Create a base templates directory with sample templates."""
    tpl_dir = tmp_path / "base_templates"
    tpl_dir.mkdir()
    (tpl_dir / "README.md.j2").write_text("# {{ project_name }}\n\n{{ description }}")
    (tpl_dir / ".gitignore.j2").write_text("__pycache__/\n*.pyc")
    (tpl_dir / "__init__.py.j2").write_text("")
    return tpl_dir


@pytest.fixture
def child_templates(tmp_path):
    """Create a child templates directory that overrides README."""
    tpl_dir = tmp_path / "child_templates"
    tpl_dir.mkdir()
    (tpl_dir / "README.md.j2").write_text(
        "# {{ project_name }} (Fullstack)\n\n{{ description }}"
    )
    (tpl_dir / "Dockerfile.j2").write_text("FROM python:{{ python_version }}")
    return tpl_dir


@pytest.fixture
def base_profile(base_templates):
    return ResolvedProfile(
        name="base",
        description="Base profile",
        variables={},
        directories=["src", "tests"],
        files={
            "README.md": "README.md.j2",
            ".gitignore": ".gitignore.j2",
        },
        conditionals={},
        template_dirs=[base_templates],
    )


@pytest.fixture
def child_profile(child_templates, base_templates):
    return ResolvedProfile(
        name="fullstack",
        description="Fullstack profile",
        variables={},
        directories=["src", "tests", "notebooks"],
        files={
            "README.md": "README.md.j2",
            ".gitignore": ".gitignore.j2",
            "Dockerfile": "Dockerfile.j2",
        },
        conditionals={"Dockerfile": "use_docker"},
        template_dirs=[child_templates, base_templates],
    )


class TestRenderTemplates:
    def test_renders_simple_template(self, base_profile):
        variables = {"project_name": "my-project", "description": "A test project"}
        rendered = render_templates(base_profile, variables)
        readme = next(r for r in rendered if r.output_path == "README.md")
        assert "# my-project" in readme.content
        assert "A test project" in readme.content

    def test_returns_rendered_file_objects(self, base_profile):
        variables = {"project_name": "test", "description": ""}
        rendered = render_templates(base_profile, variables)
        assert all(isinstance(r, RenderedFile) for r in rendered)
        assert len(rendered) == 2

    def test_content_hash_is_deterministic(self, base_profile):
        variables = {"project_name": "test", "description": ""}
        rendered1 = render_templates(base_profile, variables)
        rendered2 = render_templates(base_profile, variables)
        hash1 = {r.output_path: r.content_hash for r in rendered1}
        hash2 = {r.output_path: r.content_hash for r in rendered2}
        assert hash1 == hash2

    def test_child_template_overrides_parent(self, child_profile):
        variables = {
            "project_name": "test",
            "description": "",
            "python_version": "3.11",
            "use_docker": True,
        }
        rendered = render_templates(child_profile, variables)
        readme = next(r for r in rendered if r.output_path == "README.md")
        assert "(Fullstack)" in readme.content

    def test_falls_back_to_parent_template(self, child_profile):
        variables = {
            "project_name": "test",
            "description": "",
            "python_version": "3.11",
            "use_docker": True,
        }
        rendered = render_templates(child_profile, variables)
        gitignore = next(r for r in rendered if r.output_path == ".gitignore")
        assert "__pycache__/" in gitignore.content

    def test_missing_template_raises(self):
        profile = ResolvedProfile(
            name="bad",
            description="Bad",
            files={"README.md": "nonexistent.j2"},
            template_dirs=[Path("/tmp/empty")],
        )
        with pytest.raises(FileNotFoundError):
            render_templates(profile, {})

    def test_conditional_excludes_file_when_falsy(self, child_profile):
        variables = {
            "project_name": "test",
            "description": "",
            "python_version": "3.11",
            "use_docker": False,
        }
        rendered = render_templates(child_profile, variables)
        paths = [r.output_path for r in rendered]
        assert "Dockerfile" not in paths

    def test_conditional_includes_file_when_truthy(self, child_profile):
        variables = {
            "project_name": "test",
            "description": "",
            "python_version": "3.11",
            "use_docker": True,
        }
        rendered = render_templates(child_profile, variables)
        paths = [r.output_path for r in rendered]
        assert "Dockerfile" in paths

    def test_jinja_variables_in_output_paths(self, base_templates):
        profile = ResolvedProfile(
            name="test",
            description="Test",
            files={"src/{{ project_slug }}/__init__.py": "__init__.py.j2"},
            template_dirs=[base_templates],
        )
        variables = {"project_slug": "my_project"}
        rendered = render_templates(profile, variables)
        assert rendered[0].output_path == "src/my_project/__init__.py"

    def test_template_name_preserved(self, base_profile):
        variables = {"project_name": "test", "description": ""}
        rendered = render_templates(base_profile, variables)
        readme = next(r for r in rendered if r.output_path == "README.md")
        assert readme.template_name == "README.md.j2"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_renderer.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'forge.renderer'`

**Step 3: Write renderer.py**

Create `src/forge/renderer.py`:

```python
"""Jinja2 template rendering for Forge profiles."""
from __future__ import annotations

import hashlib
from pathlib import Path

from jinja2 import Environment, BaseLoader, TemplateNotFound

from forge.models import ResolvedProfile, RenderedFile


class ProfileTemplateLoader(BaseLoader):
    """Jinja2 loader that searches template_dirs in order (child first)."""

    def __init__(self, template_dirs: list[Path]) -> None:
        self.template_dirs = template_dirs

    def get_source(
        self, environment: Environment, template: str
    ) -> tuple[str, str, callable]:
        for tpl_dir in self.template_dirs:
            path = tpl_dir / template
            if path.is_file():
                source = path.read_text(encoding="utf-8")
                return source, str(path), lambda: path.stat().st_mtime
        raise TemplateNotFound(template)


def render_templates(
    profile: ResolvedProfile, variables: dict
) -> list[RenderedFile]:
    """Render all templates in a profile to in-memory RenderedFile objects.

    Args:
        profile: A fully resolved profile (inheritance already merged).
        variables: User-provided template variables.

    Returns:
        List of RenderedFile objects, one per file in the profile.

    Raises:
        FileNotFoundError: If a template cannot be found in any template dir.
    """
    env = Environment(
        loader=ProfileTemplateLoader(profile.template_dirs),
        keep_trailing_newline=True,
    )

    rendered: list[RenderedFile] = []

    for output_path, template_name in profile.files.items():
        # Check conditionals — skip if the controlling variable is falsy
        condition_var = profile.conditionals.get(output_path)
        if condition_var is not None and not variables.get(condition_var):
            continue

        # Render output path (may contain Jinja2 variables like {{ project_slug }})
        resolved_output_path = env.from_string(output_path).render(**variables)

        # Render template content
        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise FileNotFoundError(
                f"Template '{template_name}' not found in: "
                f"{[str(d) for d in profile.template_dirs]}"
            )

        content = template.render(**variables)
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

        rendered.append(
            RenderedFile(
                output_path=resolved_output_path,
                content=content,
                template_name=template_name,
                content_hash=content_hash,
            )
        )

    return rendered
```

**Step 4: Run tests**

```bash
pytest tests/test_renderer.py -v
```

Expected: All 10 tests PASS.

**Step 5: Commit**

```bash
git add -A
git commit -m "feat(v2): Jinja2 renderer with template fallback and conditionals

Renderer resolves templates through ordered template_dirs (child first,
parent fallback). Supports conditional file inclusion based on variables
and Jinja2 expressions in output paths. Content hashing for lock file."
```

---

## Task 4: Lock File

**Files:**
- Create: `src/forge/lockfile.py`
- Create: `tests/test_lockfile.py`

**Step 1: Write the failing test**

Create `tests/test_lockfile.py`:

```python
"""Tests for .forge.lock read/write/diff operations."""
import pytest
from pathlib import Path

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
        # Change the rendered hash but keep lock hash matching "disk"
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
        # Disk hash differs from lock hash = user modified
        actions = diff_lock(
            sample_lock, rendered, disk_hashes={"README.md": "user_edited"}
        )
        assert actions["README.md"] == FileAction.SKIP_MODIFIED

    def test_detects_user_deleted_files(self, sample_lock):
        # Rendered still has README.md but it's missing from disk
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
        # README.md is in lock and rendered but not on disk — user deleted it
        assert actions["README.md"] == FileAction.SKIP_DELETED

    def test_unchanged_files_not_in_actions(self, sample_lock, sample_rendered):
        actions = diff_lock(
            sample_lock,
            sample_rendered,
            disk_hashes={"README.md": "abc123", ".gitignore": "def456"},
        )
        # Hashes match lock and rendered — no action needed
        assert "README.md" not in actions
        assert ".gitignore" not in actions
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_lockfile.py -v
```

Expected: FAIL

**Step 3: Write lockfile.py**

Create `src/forge/lockfile.py`:

```python
"""Forge lock file (.forge.lock) operations."""
from __future__ import annotations

import sys
from pathlib import Path

import tomli_w

from forge.models import (
    ForgeLock,
    ManagedFileEntry,
    RenderedFile,
    FileAction,
)

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

LOCK_FILENAME = ".forge.lock"


def write_lock(lock: ForgeLock, target_dir: Path) -> None:
    """Write a ForgeLock to .forge.lock in the target directory.

    Args:
        lock: The lock data to write.
        target_dir: The project root directory.
    """
    lock_path = target_dir / LOCK_FILENAME

    # Build TOML-compatible dict
    data: dict = {
        "forge": {
            "version": lock.version,
            "profile": lock.profile,
            "generated_at": lock.generated_at,
        },
        "variables": dict(lock.variables),
        "files": {
            "managed": {
                path: {"template": entry.template, "hash": entry.hash}
                for path, entry in lock.managed.items()
            }
        },
    }

    with open(lock_path, "wb") as f:
        tomli_w.dump(data, f)


def read_lock(target_dir: Path) -> ForgeLock | None:
    """Read .forge.lock from the target directory.

    Args:
        target_dir: The project root directory.

    Returns:
        A ForgeLock if the file exists, None otherwise.
    """
    lock_path = target_dir / LOCK_FILENAME
    if not lock_path.exists():
        return None

    with open(lock_path, "rb") as f:
        data = tomllib.load(f)

    forge_section = data.get("forge", {})
    managed_raw = data.get("files", {}).get("managed", {})
    managed = {
        path: ManagedFileEntry(**entry) for path, entry in managed_raw.items()
    }

    return ForgeLock(
        version=forge_section["version"],
        profile=forge_section["profile"],
        generated_at=forge_section["generated_at"],
        variables=data.get("variables", {}),
        managed=managed,
    )


def diff_lock(
    old_lock: ForgeLock,
    new_rendered: list[RenderedFile],
    disk_hashes: dict[str, str] | None = None,
    existing_files: set[str] | None = None,
) -> dict[str, FileAction]:
    """Compare old lock state against newly rendered files.

    Args:
        old_lock: The existing lock from the project.
        new_rendered: Freshly rendered files from the pipeline.
        disk_hashes: Map of file path to current sha256 hash on disk.
            If None, assumes all lock hashes match disk (first update).
        existing_files: Set of file paths that exist on disk.
            If None, derived from disk_hashes keys.

    Returns:
        Dict mapping file paths to the action that should be taken.
        Files that need no action are omitted.
    """
    if disk_hashes is None:
        disk_hashes = {path: entry.hash for path, entry in old_lock.managed.items()}

    if existing_files is None:
        existing_files = set(disk_hashes.keys())

    actions: dict[str, FileAction] = {}

    for rendered in new_rendered:
        path = rendered.output_path
        old_entry = old_lock.managed.get(path)

        if old_entry is None:
            # New file not in old lock
            actions[path] = FileAction.CREATE
        elif path not in existing_files:
            # File was in lock but user deleted it from disk
            actions[path] = FileAction.SKIP_DELETED
        elif rendered.content_hash == old_entry.hash:
            # Template hasn't changed — nothing to do
            continue
        else:
            # Template changed. Check if user modified the file.
            disk_hash = disk_hashes.get(path)
            if disk_hash == old_entry.hash:
                # Disk matches old lock — user hasn't touched it, safe to update
                actions[path] = FileAction.UPDATE
            else:
                # Disk differs from lock — user customized it, skip
                actions[path] = FileAction.SKIP_MODIFIED

    return actions
```

**Step 4: Run tests**

```bash
pytest tests/test_lockfile.py -v
```

Expected: All 7 tests PASS.

**Step 5: Commit**

```bash
git add -A
git commit -m "feat(v2): lock file read/write/diff for smart updates

Implements .forge.lock in TOML format. write_lock/read_lock for
persistence, diff_lock for computing file actions (create, update,
skip_modified, skip_deleted) by comparing lock hashes to disk state."
```

---

## Task 5: Applier

**Files:**
- Create: `src/forge/applier.py`
- Create: `tests/test_applier.py`

**Step 1: Write the failing test**

Create `tests/test_applier.py`:

```python
"""Tests for applying rendered files to disk."""
import hashlib
import pytest
from pathlib import Path

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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_applier.py -v
```

Expected: FAIL

**Step 3: Write applier.py**

Create `src/forge/applier.py`:

```python
"""Apply rendered files to disk with create/update/force strategies."""
from __future__ import annotations

import hashlib
from pathlib import Path

from forge.models import (
    RenderedFile,
    ResolvedProfile,
    Strategy,
    ApplyResult,
    ForgeLock,
    FileAction,
)
from forge.lockfile import diff_lock


def _hash_file(path: Path) -> str:
    """Compute the same hash format used by RenderedFile."""
    content = path.read_text(encoding="utf-8")
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def apply_to_disk(
    rendered_files: list[RenderedFile],
    profile: ResolvedProfile,
    target: Path,
    strategy: Strategy,
    lock: ForgeLock | None = None,
) -> ApplyResult:
    """Write rendered files to the target directory.

    Args:
        rendered_files: Files rendered by the renderer.
        profile: The resolved profile (for directory creation).
        target: The project root directory.
        strategy: How to handle existing files.
        lock: Existing lock file (required for UPDATE strategy).

    Returns:
        ApplyResult summarizing what happened.

    Raises:
        FileExistsError: If CREATE strategy and files already exist.
        ValueError: If UPDATE strategy but no lock provided.
    """
    result = ApplyResult()

    # Create profile directories
    for directory in profile.directories:
        (target / directory).mkdir(parents=True, exist_ok=True)

    if strategy == Strategy.UPDATE:
        if lock is None:
            raise ValueError(
                "Update strategy requires an existing .forge.lock file."
            )
        _apply_update(rendered_files, target, lock, result)
    elif strategy == Strategy.FORCE:
        _apply_create(rendered_files, target, result, force=True)
    else:
        _apply_create(rendered_files, target, result, force=False)

    return result


def _apply_create(
    rendered_files: list[RenderedFile],
    target: Path,
    result: ApplyResult,
    force: bool,
) -> None:
    """Apply files with create or force strategy."""
    for rendered in rendered_files:
        file_path = target / rendered.output_path

        if not force and file_path.exists():
            raise FileExistsError(
                f"File already exists: {file_path}. "
                "Use --force to overwrite."
            )

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(rendered.content, encoding="utf-8")
        result.created.append(rendered.output_path)


def _apply_update(
    rendered_files: list[RenderedFile],
    target: Path,
    lock: ForgeLock,
    result: ApplyResult,
) -> None:
    """Apply files with update strategy using lock file diffing."""
    # Build disk state
    disk_hashes: dict[str, str] = {}
    existing_files: set[str] = set()

    for rendered in rendered_files:
        file_path = target / rendered.output_path
        if file_path.exists():
            existing_files.add(rendered.output_path)
            disk_hashes[rendered.output_path] = _hash_file(file_path)

    actions = diff_lock(lock, rendered_files, disk_hashes, existing_files)
    rendered_map = {r.output_path: r for r in rendered_files}

    for path, action in actions.items():
        rendered = rendered_map[path]
        file_path = target / path

        if action == FileAction.CREATE:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(rendered.content, encoding="utf-8")
            result.created.append(path)

        elif action == FileAction.UPDATE:
            file_path.write_text(rendered.content, encoding="utf-8")
            result.updated.append(path)

        elif action == FileAction.SKIP_MODIFIED:
            result.skipped.append(path)
            result.warnings.append(
                f"Skipped {path} — modified by user"
            )

        elif action == FileAction.SKIP_DELETED:
            result.skipped.append(path)
```

**Step 4: Run tests**

```bash
pytest tests/test_applier.py -v
```

Expected: All 8 tests PASS.

**Step 5: Commit**

```bash
git add -A
git commit -m "feat(v2): file applier with create/update/force strategies

Applies rendered files to disk. CREATE writes all files (errors on
conflict). FORCE overwrites. UPDATE uses lock file diff to add new
files, update unmodified files, and skip user-customized files."
```

---

## Task 6: Pipeline

**Files:**
- Create: `src/forge/pipeline.py`
- Create: `tests/test_pipeline.py`

**Step 1: Write the failing test**

Create `tests/test_pipeline.py`:

```python
"""Integration tests for the full Forge pipeline."""
import pytest
from pathlib import Path

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
        (profiles_dir / "base" / "templates" / "CHANGELOG.md.j2").write_text(
            "# Changelog"
        )

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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_pipeline.py -v
```

Expected: FAIL

**Step 3: Write pipeline.py**

Create `src/forge/pipeline.py`:

```python
"""Forge v2 pipeline — the core orchestration."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from forge.models import (
    Strategy,
    ApplyResult,
    ForgeLock,
    ManagedFileEntry,
    ResolvedProfile,
)
from forge.profile_loader import resolve_profile, merge_inheritance
from forge.renderer import render_templates
from forge.applier import apply_to_disk
from forge.lockfile import write_lock, read_lock


def generate(
    profile_name: str,
    target: Path,
    variables: dict,
    strategy: Strategy,
    profiles_dir: Path,
    dry_run: bool = False,
) -> ApplyResult:
    """Run the full Forge pipeline: resolve → merge → render → apply → lock.

    Args:
        profile_name: Name of the profile to generate from.
        target: Target directory for the generated project.
        variables: User-provided template variables.
        strategy: How to handle file creation (create/update/force).
        profiles_dir: Root directory containing profile directories.
        dry_run: If True, render but don't write to disk.

    Returns:
        ApplyResult summarizing what was created/updated/skipped.
    """
    # Step 1-2: Resolve profile and merge inheritance
    profile_spec = resolve_profile(profile_name, profiles_dir)
    resolved = merge_inheritance(profile_spec, profiles_dir)

    # Step 3: Render templates
    rendered = render_templates(resolved, variables)

    if dry_run:
        # Return what would happen without writing
        return ApplyResult(created=[r.output_path for r in rendered])

    # Step 4: Apply to disk
    lock = read_lock(target) if strategy == Strategy.UPDATE else None
    result = apply_to_disk(rendered, resolved, target, strategy, lock=lock)

    # Step 5: Write lock file
    now = datetime.now(timezone.utc).isoformat()
    new_lock = ForgeLock(
        version="2.0.0",
        profile=resolved.name,
        generated_at=now,
        variables={k: v for k, v in variables.items() if isinstance(v, (str, bool))},
        managed={
            r.output_path: ManagedFileEntry(
                template=r.template_name, hash=r.content_hash
            )
            for r in rendered
        },
    )
    write_lock(new_lock, target)

    return result
```

**Step 4: Add merge_inheritance to profile_loader.py**

This function was referenced in the pipeline but not yet implemented. Add it to `src/forge/profile_loader.py`:

```python
def merge_inheritance(
    profile: ProfileSpec, profiles_dir: Path
) -> ResolvedProfile:
    """Resolve the inheritance chain and merge into a single ResolvedProfile.

    Args:
        profile: The starting profile (may have an `inherits` field).
        profiles_dir: Root directory containing all profile directories.

    Returns:
        A fully merged ResolvedProfile with no inheritance references.

    Raises:
        ValueError: If circular inheritance is detected.
    """
    # Collect the inheritance chain (child first)
    chain: list[ProfileSpec] = [profile]
    seen: set[str] = {profile.name}

    current = profile
    while current.inherits:
        if current.inherits in seen:
            raise ValueError(
                f"Circular inheritance detected: "
                f"{current.name} -> {current.inherits}"
            )
        seen.add(current.inherits)
        parent = resolve_profile(current.inherits, profiles_dir)
        chain.append(parent)
        current = parent

    # Merge from base (last) to child (first)
    chain.reverse()  # now [base, ..., child]

    merged_variables: dict = {}
    merged_directories: list[str] = []
    merged_files: dict[str, str] = {}
    merged_conditionals: dict[str, str] = {}
    template_dirs: list[Path] = []

    for spec in chain:
        merged_variables.update(spec.variables)
        # Union directories (preserving order, no duplicates)
        for d in spec.directories:
            if d not in merged_directories:
                merged_directories.append(d)
        merged_files.update(spec.files)
        merged_conditionals.update(spec.conditionals)

    # Template dirs: child first for lookup priority
    for spec in reversed(chain):
        template_dirs.append(spec.template_dir)

    child = chain[-1]  # The originally requested profile
    return ResolvedProfile(
        name=child.name,
        description=child.description,
        variables=merged_variables,
        directories=merged_directories,
        files=merged_files,
        conditionals=merged_conditionals,
        template_dirs=template_dirs,
    )
```

**Step 5: Run tests**

```bash
pytest tests/test_pipeline.py tests/test_profile_loader.py tests/test_renderer.py tests/test_lockfile.py tests/test_applier.py tests/test_models.py -v
```

Expected: All tests PASS.

**Step 6: Commit**

```bash
git add -A
git commit -m "feat(v2): pipeline orchestration with merge_inheritance

Core pipeline function that runs resolve → merge → render → apply → lock.
Adds merge_inheritance to profile_loader for walking the inherits chain.
Supports dry_run mode. Integration tests cover full generate and update."
```

---

## Task 7: Typer CLI

**Files:**
- Create: `src/forge/cli.py`
- Create: `tests/test_cli.py`

**Step 1: Write the failing test**

Create `tests/test_cli.py`:

```python
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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_cli.py -v
```

Expected: FAIL

**Step 3: Write cli.py**

Create `src/forge/cli.py`:

```python
"""Forge v2 CLI — Typer application."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from forge.models import Strategy
from forge.pipeline import generate
from forge.profile_loader import list_profiles, resolve_profile
from forge.lockfile import read_lock

app = typer.Typer(
    name="forge",
    help="Forge — AI Project Scaffolder",
    no_args_is_help=True,
)

profiles_app = typer.Typer(help="Manage profiles")
app.add_typer(profiles_app, name="profiles")

console = Console()


def get_profiles_dir() -> Path:
    """Return the path to the profiles directory.

    Looks for profiles/ relative to the package, falling back to CWD.
    """
    # Check relative to this file (installed package)
    pkg_profiles = Path(__file__).parent.parent.parent / "profiles"
    if pkg_profiles.is_dir():
        return pkg_profiles

    # Fallback: CWD
    cwd_profiles = Path.cwd() / "profiles"
    if cwd_profiles.is_dir():
        return cwd_profiles

    raise FileNotFoundError(
        "Cannot find profiles directory. "
        "Ensure Forge is installed correctly or run from the project root."
    )


def _parse_vars(var_list: list[str]) -> dict[str, str | bool]:
    """Parse --var key=value pairs into a dict."""
    variables: dict[str, str | bool] = {}
    for item in var_list:
        if "=" not in item:
            raise typer.BadParameter(f"Invalid variable format: {item}. Use key=value.")
        key, value = item.split("=", 1)
        # Convert boolean-like strings
        if value.lower() in ("true", "yes", "1"):
            variables[key] = True
        elif value.lower() in ("false", "no", "0"):
            variables[key] = False
        else:
            variables[key] = value
    return variables


@app.command()
def new(
    target: Path = typer.Argument(..., help="Directory to create the project in"),
    profile: str = typer.Option("fullstack", "--profile", "-p", help="Profile to use"),
    no_interactive: bool = typer.Option(False, "--no-interactive", help="Skip wizard"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would happen"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
    var: Optional[list[str]] = typer.Option(None, "--var", help="Variable as key=value"),
) -> None:
    """Create a new project from a profile."""
    profiles_dir = get_profiles_dir()
    variables = _parse_vars(var or [])

    strategy = Strategy.FORCE if force else Strategy.CREATE

    if not no_interactive and not variables:
        from forge.wizard import run_wizard
        variables = run_wizard(profile, profiles_dir)

    target.mkdir(parents=True, exist_ok=True)

    try:
        result = generate(
            profile_name=profile,
            target=target,
            variables=variables,
            strategy=strategy,
            profiles_dir=profiles_dir,
            dry_run=dry_run,
        )
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except FileExistsError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)

    if dry_run:
        console.print("[yellow]Dry run — no files written.[/yellow]")

    for path in result.created:
        console.print(f"  [green]CREATE[/green] {path}")
    for path in result.updated:
        console.print(f"  [blue]UPDATE[/blue] {path}")
    for path in result.skipped:
        console.print(f"  [yellow]SKIP[/yellow]   {path}")
    for warning in result.warnings:
        console.print(f"  [yellow]WARN[/yellow]   {warning}")

    console.print(f"\n[bold green]Done![/bold green] Project at {target}")


@app.command()
def update(
    target: Path = typer.Argument(".", help="Project directory to update"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite user changes"),
) -> None:
    """Update an existing Forge project with the latest templates."""
    profiles_dir = get_profiles_dir()
    target = target.resolve()

    lock = read_lock(target)
    if lock is None:
        console.print(
            "[red]Error:[/red] No .forge.lock found. "
            "This directory was not created by Forge, or the lock file was deleted."
        )
        raise typer.Exit(code=1)

    strategy = Strategy.FORCE if force else Strategy.UPDATE

    result = generate(
        profile_name=lock.profile,
        target=target,
        variables=dict(lock.variables),
        strategy=strategy,
        profiles_dir=profiles_dir,
    )

    for path in result.created:
        console.print(f"  [green]CREATE[/green] {path}")
    for path in result.updated:
        console.print(f"  [blue]UPDATE[/blue] {path}")
    for path in result.skipped:
        console.print(f"  [yellow]SKIP[/yellow]   {path}")
    for warning in result.warnings:
        console.print(f"  [yellow]WARN[/yellow]   {warning}")

    console.print(f"\n[bold green]Update complete![/bold green]")


@app.command()
def info(
    target: Path = typer.Argument(".", help="Project directory to inspect"),
) -> None:
    """Show info about a Forge-generated project."""
    target = target.resolve()
    lock = read_lock(target)

    if lock is None:
        console.print("[red]No .forge.lock found in this directory.[/red]")
        raise typer.Exit(code=1)

    console.print(f"[bold]Forge Project Info[/bold]")
    console.print(f"  Profile:    {lock.profile}")
    console.print(f"  Version:    {lock.version}")
    console.print(f"  Generated:  {lock.generated_at}")
    console.print(f"  Files:      {len(lock.managed)} managed")

    if lock.variables:
        console.print(f"\n[bold]Variables:[/bold]")
        for key, val in lock.variables.items():
            console.print(f"  {key} = {val}")


@profiles_app.command("list")
def profiles_list() -> None:
    """List available profiles."""
    profiles_dir = get_profiles_dir()
    names = list_profiles(profiles_dir)

    table = Table(title="Available Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Description")

    for name in names:
        try:
            spec = resolve_profile(name, profiles_dir)
            table.add_row(name, spec.description)
        except Exception:
            table.add_row(name, "[red]Error loading[/red]")

    console.print(table)


@profiles_app.command("show")
def profiles_show(
    name: str = typer.Argument(..., help="Profile name to inspect"),
) -> None:
    """Show details of a specific profile."""
    profiles_dir = get_profiles_dir()

    try:
        spec = resolve_profile(name, profiles_dir)
    except FileNotFoundError:
        console.print(f"[red]Profile '{name}' not found.[/red]")
        raise typer.Exit(code=1)

    console.print(f"[bold]{spec.name}[/bold] — {spec.description}")

    if spec.inherits:
        console.print(f"  Inherits: {spec.inherits}")

    if spec.variables:
        console.print(f"\n[bold]Variables:[/bold]")
        for key, var in spec.variables.items():
            default = f" (default: {var.default})" if var.default is not None else ""
            console.print(f"  {key}: {var.type}{default}")

    if spec.directories:
        console.print(f"\n[bold]Directories:[/bold]")
        for d in spec.directories:
            console.print(f"  {d}/")

    console.print(f"\n[bold]Files:[/bold] {len(spec.files)} templates")
```

**Step 4: Run tests**

```bash
pytest tests/test_cli.py -v
```

Expected: All 4 tests PASS.

**Step 5: Commit**

```bash
git add -A
git commit -m "feat(v2): Typer CLI with new, update, info, and profiles commands

Typer app with subcommands: new (generate project), update (smart
update from lock), info (show project metadata), profiles list/show.
Supports --dry-run, --force, --var, --no-interactive flags."
```

---

## Task 8: Wizard

**Files:**
- Create: `src/forge/wizard.py`
- Create: `tests/test_wizard.py`

**Step 1: Write the failing test**

Create `tests/test_wizard.py`:

```python
"""Tests for the interactive wizard."""
import pytest
from pathlib import Path
from unittest.mock import patch

from forge.wizard import run_wizard, build_prompts
from forge.models import VariableSpec, ResolvedProfile


@pytest.fixture
def profiles_dir(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    (base / "templates").mkdir()
    (base / "profile.toml").write_text('''
[profile]
name = "base"
description = "Test"

[variables]
[variables.project_name]
prompt = "Project name"
type = "string"

[variables.manager]
prompt = "Package manager"
type = "choice"
choices = ["pip", "poetry", "uv"]
default = "pip"

[variables.use_docker]
prompt = "Include Docker?"
type = "confirm"
default = true
''')
    (base / "structure.toml").write_text('''
[directories]
root = []

[files]
''')
    return tmp_path


class TestBuildPrompts:
    def test_string_produces_text_prompt(self):
        variables = {"name": VariableSpec(prompt="Your name", type="string")}
        prompts = build_prompts(variables)
        assert prompts[0]["type"] == "text"
        assert prompts[0]["name"] == "name"

    def test_choice_produces_select_prompt(self):
        variables = {
            "mgr": VariableSpec(
                prompt="Manager",
                type="choice",
                choices=["pip", "poetry"],
                default="pip",
            )
        }
        prompts = build_prompts(variables)
        assert prompts[0]["type"] == "select"
        assert prompts[0]["choices"] == ["pip", "poetry"]

    def test_confirm_produces_confirm_prompt(self):
        variables = {
            "docker": VariableSpec(
                prompt="Use Docker?", type="confirm", default=True
            )
        }
        prompts = build_prompts(variables)
        assert prompts[0]["type"] == "confirm"
        assert prompts[0]["default"] is True

    def test_default_preserved(self):
        variables = {
            "name": VariableSpec(
                prompt="Name", type="string", default="World"
            )
        }
        prompts = build_prompts(variables)
        assert prompts[0]["default"] == "World"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_wizard.py -v
```

Expected: FAIL

**Step 3: Write wizard.py**

Create `src/forge/wizard.py`:

```python
"""Interactive wizard that generates prompts from profile variables."""
from __future__ import annotations

from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel

from forge.models import VariableSpec
from forge.profile_loader import resolve_profile, merge_inheritance

console = Console()


def build_prompts(variables: dict[str, VariableSpec]) -> list[dict]:
    """Convert profile variable specs into questionary prompt configs.

    Args:
        variables: Profile variables from the resolved profile.

    Returns:
        List of prompt config dicts for questionary.
    """
    prompts: list[dict] = []

    for name, spec in variables.items():
        prompt: dict = {"name": name, "message": spec.prompt}

        if spec.type == "string":
            prompt["type"] = "text"
            if spec.default is not None:
                prompt["default"] = str(spec.default)
        elif spec.type == "choice":
            prompt["type"] = "select"
            prompt["choices"] = spec.choices or []
            if spec.default is not None:
                prompt["default"] = spec.default
        elif spec.type == "confirm":
            prompt["type"] = "confirm"
            prompt["default"] = spec.default if spec.default is not None else False

        prompts.append(prompt)

    return prompts


def _ask_prompt(prompt: dict) -> str | bool:
    """Ask a single prompt using questionary."""
    if prompt["type"] == "text":
        return questionary.text(
            prompt["message"],
            default=prompt.get("default", ""),
        ).ask()
    elif prompt["type"] == "select":
        return questionary.select(
            prompt["message"],
            choices=prompt["choices"],
            default=prompt.get("default"),
        ).ask()
    elif prompt["type"] == "confirm":
        return questionary.confirm(
            prompt["message"],
            default=prompt.get("default", False),
        ).ask()
    return ""


def run_wizard(
    profile_name: str,
    profiles_dir: Path,
) -> dict[str, str | bool]:
    """Run the interactive wizard for a given profile.

    Reads the profile's variable definitions and prompts the user
    for each value.

    Args:
        profile_name: Name of the profile to generate prompts for.
        profiles_dir: Root profiles directory.

    Returns:
        Dict of variable name → user-provided value.
    """
    console.print(
        Panel(
            "[bold cyan]Forge Project Wizard[/bold cyan]",
            subtitle=f"Profile: {profile_name}",
        )
    )

    profile_spec = resolve_profile(profile_name, profiles_dir)
    resolved = merge_inheritance(profile_spec, profiles_dir)
    prompts = build_prompts(resolved.variables)

    variables: dict[str, str | bool] = {}
    for prompt in prompts:
        answer = _ask_prompt(prompt)
        if answer is None:
            raise KeyboardInterrupt("Wizard cancelled by user")
        variables[prompt["name"]] = answer

    return variables
```

**Step 4: Run tests**

```bash
pytest tests/test_wizard.py -v
```

Expected: All 4 tests PASS.

**Step 5: Commit**

```bash
git add -A
git commit -m "feat(v2): interactive wizard auto-generated from profile variables

Wizard reads variable specs from resolved profile and generates
questionary prompts (text/select/confirm). No wizard code changes
needed when adding profile variables — prompts are data-driven."
```

---

## Task 9: Inheritance (Fullstack Profile)

**Files:**
- Create: `profiles/fullstack/profile.toml`
- Create: `profiles/fullstack/structure.toml`
- Create: `profiles/fullstack/templates/` (empty initially)
- Modify: `tests/test_profile_loader.py` (add inheritance tests)

**Step 1: Create fullstack profile TOML**

Create `profiles/fullstack/profile.toml`:

```toml
[profile]
name = "fullstack"
inherits = "base"
description = "Full-stack AI system with notebooks, models, and Ansible"

[variables]
[variables.persona]
prompt = "AI persona"
type = "choice"
choices = ["standard", "architect", "developer"]
default = "standard"

[variables.use_docker]
prompt = "Include Docker support?"
type = "confirm"
default = true
```

Create `profiles/fullstack/structure.toml`:

```toml
[directories]
root = [
    "notebooks",
    "models",
    "data/raw",
    "data/processed",
    "ansible/roles",
    "ansible/group_vars",
    "ansible/host_vars",
    "src/data",
    "src/features",
    "src/models",
    "src/visualization",
]

[files]
"Dockerfile" = "Dockerfile.j2"
"docker-compose.yml" = "docker-compose.yml.j2"
"mkdocs.yml" = "mkdocs.yml.j2"
"ansible/ansible.cfg" = "ansible/ansible.cfg.j2"
"ansible/inventory.ini" = "ansible/inventory.ini.j2"
"ansible/setup_workstation.yml" = "ansible/setup_workstation.yml.j2"

[conditionals]
"Dockerfile" = "use_docker"
"docker-compose.yml" = "use_docker"
```

```bash
mkdir -p profiles/fullstack/templates
```

**Step 2: Write inheritance tests**

Add to `tests/test_profile_loader.py`:

```python
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
        from forge.profile_loader import resolve_profile, merge_inheritance
        spec = resolve_profile("fullstack", two_level_profiles)
        resolved = merge_inheritance(spec, two_level_profiles)
        assert "project_name" in resolved.variables  # from base
        assert "use_docker" in resolved.variables     # from child

    def test_unions_directories(self, two_level_profiles):
        from forge.profile_loader import resolve_profile, merge_inheritance
        spec = resolve_profile("fullstack", two_level_profiles)
        resolved = merge_inheritance(spec, two_level_profiles)
        assert "src" in resolved.directories       # from base
        assert "notebooks" in resolved.directories  # from child

    def test_child_files_override_parent(self, two_level_profiles):
        from forge.profile_loader import resolve_profile, merge_inheritance
        spec = resolve_profile("fullstack", two_level_profiles)
        resolved = merge_inheritance(spec, two_level_profiles)
        assert "README.md" in resolved.files    # from base
        assert "Dockerfile" in resolved.files   # from child

    def test_merges_conditionals(self, two_level_profiles):
        from forge.profile_loader import resolve_profile, merge_inheritance
        spec = resolve_profile("fullstack", two_level_profiles)
        resolved = merge_inheritance(spec, two_level_profiles)
        assert "requirements.txt" in resolved.conditionals  # from base
        assert "Dockerfile" in resolved.conditionals         # from child

    def test_template_dirs_child_first(self, two_level_profiles):
        from forge.profile_loader import resolve_profile, merge_inheritance
        spec = resolve_profile("fullstack", two_level_profiles)
        resolved = merge_inheritance(spec, two_level_profiles)
        assert resolved.template_dirs[0].parent.name == "fullstack"
        assert resolved.template_dirs[1].parent.name == "base"

    def test_resolved_uses_child_name(self, two_level_profiles):
        from forge.profile_loader import resolve_profile, merge_inheritance
        spec = resolve_profile("fullstack", two_level_profiles)
        resolved = merge_inheritance(spec, two_level_profiles)
        assert resolved.name == "fullstack"

    def test_circular_inheritance_raises(self, tmp_path):
        from forge.profile_loader import resolve_profile, merge_inheritance

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
        from forge.profile_loader import resolve_profile, merge_inheritance
        spec = resolve_profile("base", profiles_dir)
        resolved = merge_inheritance(spec, profiles_dir)
        assert resolved.name == "base"
        assert len(resolved.template_dirs) == 1
```

**Step 3: Run tests**

```bash
pytest tests/test_profile_loader.py -v
```

Expected: All tests PASS (original 9 + new 8 = 17).

**Step 4: Commit**

```bash
git add -A
git commit -m "feat(v2): fullstack profile with inheritance from base

Add fullstack profile TOML that inherits base, adding notebooks,
models, data, ansible directories and Docker/MkDocs files with
conditionals. Full inheritance test coverage including circular
detection."
```

---

## Task 10: Port Templates and Polish

**Files:**
- Copy: v1 Jinja2 templates into `profiles/base/templates/` and `profiles/fullstack/templates/`
- Create: `profiles/base/templates/__init__.py.j2` (empty file template)
- Modify: `CLAUDE.md`
- Modify: `README.md`

**Step 1: Copy v1 templates to base profile**

The v1 templates live in the main repo at `src/project_generator/templates/`. Copy the common ones to `profiles/base/templates/` in the worktree:

```bash
cd /home/jlwestsr/projects/west_ai_labs/forge/.worktrees/v2-rewrite

# Base templates (governance, config, shared)
cp ../src/project_generator/templates/README.md.j2 profiles/base/templates/
cp ../src/project_generator/templates/CONTEXT.md.j2 profiles/base/templates/
cp ../src/project_generator/templates/AI_DIRECTIVES.md.j2 profiles/base/templates/
cp ../src/project_generator/templates/WORKFLOW.md.j2 profiles/base/templates/
cp ../src/project_generator/templates/GEMINI.md.j2 profiles/base/templates/
cp ../src/project_generator/templates/.gitignore.j2 profiles/base/templates/
cp ../src/project_generator/templates/.flake8.j2 profiles/base/templates/
cp ../src/project_generator/templates/.yamllint.j2 profiles/base/templates/
cp ../src/project_generator/templates/.pre-commit-config.yaml.j2 profiles/base/templates/
cp ../src/project_generator/templates/pyproject.toml.j2 profiles/base/templates/
cp ../src/project_generator/templates/requirements.txt.j2 profiles/base/templates/
cp ../src/project_generator/templates/requirements-dev.txt.j2 profiles/base/templates/

# Nested templates
mkdir -p profiles/base/templates/docs
mkdir -p profiles/base/templates/.github/workflows
mkdir -p profiles/base/templates/.agent/rules
mkdir -p profiles/base/templates/tests

cp ../src/project_generator/templates/docs/index.md.j2 profiles/base/templates/docs/
cp ../src/project_generator/templates/docs/feature_template.md.j2 profiles/base/templates/docs/
cp ../src/project_generator/templates/docs/AI_INSIGHTS.md.j2 profiles/base/templates/docs/
cp ../src/project_generator/templates/.github/workflows/docs.yml.j2 profiles/base/templates/.github/workflows/
cp ../src/project_generator/templates/.github/workflows/unittests.yml.j2 profiles/base/templates/.github/workflows/
cp ../src/project_generator/templates/.agent/rules/ai_behavior.md.j2 profiles/base/templates/.agent/rules/
cp ../src/project_generator/templates/tests/test_initial.py.j2 profiles/base/templates/tests/

# Empty __init__.py template
echo "" > profiles/base/templates/__init__.py.j2
```

**Step 2: Copy fullstack-specific templates**

```bash
mkdir -p profiles/fullstack/templates/ansible
cp ../src/project_generator/templates/Dockerfile.j2 profiles/fullstack/templates/
cp ../src/project_generator/templates/docker-compose.yml.j2 profiles/fullstack/templates/
cp ../src/project_generator/templates/mkdocs.yml.j2 profiles/fullstack/templates/
cp ../src/project_generator/templates/ansible/ansible.cfg.j2 profiles/fullstack/templates/ansible/
cp ../src/project_generator/templates/ansible/inventory.ini.j2 profiles/fullstack/templates/ansible/
cp ../src/project_generator/templates/ansible/setup_workstation.yml.j2 profiles/fullstack/templates/ansible/
```

**Step 3: Run full test suite**

```bash
pytest tests/ -v
```

Expected: All tests PASS.

**Step 4: Update CLAUDE.md for v2**

Update CLAUDE.md to reflect the v2 architecture (profiles directory, new module names, Typer CLI commands, etc.)

**Step 5: Commit**

```bash
git add -A
git commit -m "feat(v2): port v1 templates and update documentation

Copy all 33 Jinja2 templates from v1 into profile directories.
Base profile gets shared templates, fullstack gets Docker/Ansible.
Update CLAUDE.md to reflect v2 architecture."
```

**Step 6: Run full validation**

```bash
pytest tests/ -v --tb=short
flake8 src/forge/ tests/
```

Expected: All tests PASS, flake8 clean.

**Step 7: Final commit if any fixes needed**

```bash
git add -A
git commit -m "chore(v2): lint fixes and test polish"
```

---

## Summary

| Task | What it builds | Tests |
|:---|:---|:---|
| 1 | Project skeleton + Pydantic models | 12 |
| 2 | Profile loader (TOML → ProfileSpec) | 9 |
| 3 | Renderer (Jinja2 + conditionals + fallback) | 10 |
| 4 | Lock file (read/write/diff) | 7 |
| 5 | Applier (create/update/force) | 8 |
| 6 | Pipeline orchestration + merge_inheritance | 5 |
| 7 | Typer CLI | 4 |
| 8 | Interactive wizard | 4 |
| 9 | Fullstack profile + inheritance tests | 8 |
| 10 | Port templates + polish | — |
| **Total** | | **~67** |
