"""Tests for Jinja2 template rendering."""
import pytest
from pathlib import Path

from forge.renderer import render_templates
from forge.models import ResolvedProfile, RenderedFile


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
