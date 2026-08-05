"""Monorepo profile loads and scaffolds expected buckets."""

from __future__ import annotations

from pathlib import Path

from forge.models import Strategy
from forge.pipeline import generate
from forge.profile_loader import list_profiles, resolve_profile


PROFILES = Path(__file__).resolve().parents[1] / "profiles"


def test_monorepo_listed() -> None:
    names = list_profiles(PROFILES)
    assert "monorepo" in names
    assert "base" in names
    assert "fullstack" in names


def test_monorepo_no_inherits() -> None:
    spec = resolve_profile("monorepo", PROFILES)
    assert spec.inherits is None


def test_monorepo_generate_shape(tmp_path: Path) -> None:
    target = tmp_path / "eco"
    target.mkdir()
    result = generate(
        "monorepo",
        target,
        {"project_name": "eco", "org_name": "Acme"},
        Strategy.CREATE,
        PROFILES,
        dry_run=False,
    )
    assert result.created
    assert (target / "LAYOUT.md").is_file()
    assert (target / "AGENTS.md").is_file()
    assert (target / "config" / "workspace-layout.yaml").is_file()
    assert (target / "products" / "example-app" / "README.md").is_file()
    assert (target / "services").is_dir()
    assert (target / "hosts").is_dir()
    assert (target / "lab").is_dir()
    assert (target / "workspace" / "scratchpad").is_dir()
    assert (target / "scripts" / "print_layout.py").is_file()
    assert not (target / "src").exists()
    # layout smoke
    import subprocess

    r = subprocess.run(
        ["python3", str(target / "scripts" / "print_layout.py")],
        cwd=target,
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    assert "products" in r.stdout
