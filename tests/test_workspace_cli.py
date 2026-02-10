"""Tests for workspace CLI commands."""
import json
from typer.testing import CliRunner

from forge.cli import app
from forge.models import (
    BusinessContext,
    BusinessConstraint,
    OverlordManifest,
    ProjectEntry,
    WorkspaceConfig,
)

runner = CliRunner()


def _make_config_dict() -> dict:
    """Build a config dict for JSON file input."""
    config = WorkspaceConfig(
        workspace_name="CLI Test Labs",
        business=BusinessContext(
            vision="Test vision",
            constraints=[
                BusinessConstraint(constraint="X", value="Y"),
            ],
            governance_rules=["Rule 1"],
        ),
        manifest=OverlordManifest(
            projects=[
                ProjectEntry(
                    name="proj-a", role="library",
                    path="proj-a/", remote="org/proj-a",
                ),
            ],
        ),
    )
    return json.loads(config.model_dump_json())


class TestWorkspaceInit:
    def test_init_from_config_file(self, tmp_path):
        config_data = _make_config_dict()
        config_file = tmp_path / "ws-config.json"
        config_file.write_text(json.dumps(config_data))

        target = tmp_path / "workspace"
        result = runner.invoke(app, [
            "workspace", "init", str(target),
            "--no-interactive",
            "--config", str(config_file),
        ])

        assert result.exit_code == 0, result.output
        assert (target / "BUSINESS.md").exists()
        assert (target / "OVERLORD.md").exists()
        assert (target / "CLAUDE.md").exists()
        assert (target / ".forge-workspace.lock").exists()

    def test_init_dry_run(self, tmp_path):
        config_data = _make_config_dict()
        config_file = tmp_path / "ws-config.json"
        config_file.write_text(json.dumps(config_data))

        target = tmp_path / "workspace"
        result = runner.invoke(app, [
            "workspace", "init", str(target),
            "--no-interactive",
            "--config", str(config_file),
            "--dry-run",
        ])

        assert result.exit_code == 0, result.output
        assert "Dry run" in result.output
        assert not (target / "BUSINESS.md").exists()

    def test_init_no_interactive_without_config_errors(self, tmp_path):
        target = tmp_path / "workspace"
        result = runner.invoke(app, [
            "workspace", "init", str(target),
            "--no-interactive",
        ])
        assert result.exit_code != 0

    def test_init_rejects_existing_workspace(self, tmp_path):
        config_data = _make_config_dict()
        config_file = tmp_path / "ws-config.json"
        config_file.write_text(json.dumps(config_data))

        target = tmp_path / "workspace"
        # First init
        runner.invoke(app, [
            "workspace", "init", str(target),
            "--no-interactive",
            "--config", str(config_file),
        ])

        # Second init should fail
        result = runner.invoke(app, [
            "workspace", "init", str(target),
            "--no-interactive",
            "--config", str(config_file),
        ])
        assert result.exit_code != 0
        assert "already initialized" in result.output

    def test_init_force_overwrites(self, tmp_path):
        config_data = _make_config_dict()
        config_file = tmp_path / "ws-config.json"
        config_file.write_text(json.dumps(config_data))

        target = tmp_path / "workspace"
        # First init
        runner.invoke(app, [
            "workspace", "init", str(target),
            "--no-interactive",
            "--config", str(config_file),
        ])

        # Force reinit
        result = runner.invoke(app, [
            "workspace", "init", str(target),
            "--no-interactive",
            "--config", str(config_file),
            "--force",
        ])
        assert result.exit_code == 0, result.output


class TestWorkspaceSync:
    def test_sync_command(self, tmp_path):
        # Initialize workspace
        config_data = _make_config_dict()
        config_file = tmp_path / "ws-config.json"
        config_file.write_text(json.dumps(config_data))

        runner.invoke(app, [
            "workspace", "init", str(tmp_path),
            "--no-interactive",
            "--config", str(config_file),
        ])

        # Create sub-project with CLAUDE.md
        proj_dir = tmp_path / "proj-a"
        proj_dir.mkdir()
        (proj_dir / "CLAUDE.md").write_text("# Proj A\n")

        result = runner.invoke(app, [
            "workspace", "sync", str(tmp_path),
        ])

        assert result.exit_code == 0, result.output
        assert "SYNC" in result.output

    def test_sync_no_overlord_warns(self, tmp_path):
        result = runner.invoke(app, [
            "workspace", "sync", str(tmp_path),
        ])

        assert result.exit_code == 0, result.output
        assert "WARN" in result.output


class TestWorkspaceInfo:
    def test_info_shows_metadata(self, tmp_path):
        config_data = _make_config_dict()
        config_file = tmp_path / "ws-config.json"
        config_file.write_text(json.dumps(config_data))

        runner.invoke(app, [
            "workspace", "init", str(tmp_path),
            "--no-interactive",
            "--config", str(config_file),
        ])

        result = runner.invoke(app, [
            "workspace", "info", str(tmp_path),
        ])

        assert result.exit_code == 0, result.output
        assert "CLI Test Labs" in result.output
        assert "Projects:" in result.output

    def test_info_no_lock_errors(self, tmp_path):
        result = runner.invoke(app, [
            "workspace", "info", str(tmp_path),
        ])
        assert result.exit_code != 0
