"""Variable defaults for non-interactive forge new."""

from pathlib import Path

from forge.defaults import apply_variable_defaults


def test_defaults_fill_project_name_from_target(tmp_path: Path) -> None:
    profiles = Path(__file__).resolve().parents[1] / "profiles"
    target = tmp_path / "cool-app"
    target.mkdir()
    out = apply_variable_defaults("base", profiles, {}, target=target)
    assert out["project_name"] == "cool-app"
    assert out["project_slug"] == "cool_app"
    assert out["use_pip"] is True
    assert out["python_version"] == "3.12"


def test_defaults_respect_explicit_vars() -> None:
    profiles = Path(__file__).resolve().parents[1] / "profiles"
    out = apply_variable_defaults(
        "base",
        profiles,
        {"project_name": "X", "manager": "uv", "python_version": "3.11"},
        target=Path("/tmp/x"),
    )
    assert out["project_name"] == "X"
    assert out["use_pip"] is False
    assert out["python_version"] == "3.11"
