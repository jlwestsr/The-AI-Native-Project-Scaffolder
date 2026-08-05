"""neo-harness post-hook resolution."""

from pathlib import Path
from unittest.mock import patch

from forge.hooks import resolve_neo_command, run_neo_init_workspace


def test_resolve_neo_from_env(monkeypatch, tmp_path: Path) -> None:
    fake = tmp_path / "neo"
    fake.write_text("#!/bin/sh\n", encoding="utf-8")
    fake.chmod(0o755)
    monkeypatch.setenv("FORGE_NEO_CMD", str(fake))
    assert resolve_neo_command() == [str(fake)]


def test_run_neo_init_skips_when_missing(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("FORGE_NEO_CMD", raising=False)
    with patch("forge.hooks.resolve_neo_command", return_value=None):
        assert run_neo_init_workspace(tmp_path) is False


def test_run_neo_init_invokes_cmd(monkeypatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))

        class R:
            returncode = 0
            stdout = ""
            stderr = ""

        return R()

    monkeypatch.setattr(
        "forge.hooks.resolve_neo_command",
        lambda: ["/bin/neo"],
    )
    monkeypatch.setattr("forge.hooks.subprocess.run", fake_run)
    assert run_neo_init_workspace(tmp_path, pack="workspace") is True
    assert calls
    assert calls[0][:3] == ["/bin/neo", "init-workspace", str(tmp_path)]
