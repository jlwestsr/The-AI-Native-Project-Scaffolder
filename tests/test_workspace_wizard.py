"""Tests for workspace wizard with mocked questionary."""
import pytest
from unittest.mock import patch, MagicMock

from forge.workspace_wizard import (
    run_workspace_wizard,
    _ask_workspace_name,
    _ask_vision,
    _ask_constraints,
    _ask_hardware_tiers,
    _ask_priorities,
    _ask_tech_stack,
    _ask_governance_rules,
    _ask_projects,
)


def _mock_ask(return_value):
    """Create a mock questionary return that has .ask() method."""
    mock = MagicMock()
    mock.ask.return_value = return_value
    return mock


class TestAskWorkspaceName:
    @patch("forge.workspace_wizard.questionary")
    def test_returns_name(self, mock_q):
        mock_q.text.return_value = _mock_ask("My Labs")
        result = _ask_workspace_name()
        assert result == "My Labs"

    @patch("forge.workspace_wizard.questionary")
    def test_cancelled_raises(self, mock_q):
        mock_q.text.return_value = _mock_ask(None)
        with pytest.raises(KeyboardInterrupt):
            _ask_workspace_name()


class TestAskVision:
    @patch("forge.workspace_wizard.questionary")
    def test_returns_vision(self, mock_q):
        mock_q.text.return_value = _mock_ask("Build AI")
        result = _ask_vision()
        assert result == "Build AI"


class TestAskConstraints:
    @patch("forge.workspace_wizard.questionary")
    def test_collects_constraints(self, mock_q):
        # First call: constraint name, second: value, third: empty to stop
        mock_q.text.side_effect = [
            _mock_ask("Privacy"),
            _mock_ask("Local-first"),
            _mock_ask(""),  # stop
        ]
        result = _ask_constraints()
        assert len(result) == 1
        assert result[0].constraint == "Privacy"
        assert result[0].value == "Local-first"

    @patch("forge.workspace_wizard.questionary")
    def test_empty_immediately(self, mock_q):
        mock_q.text.return_value = _mock_ask("")
        result = _ask_constraints()
        assert result == []


class TestAskHardwareTiers:
    @patch("forge.workspace_wizard.questionary")
    def test_collects_tier(self, mock_q):
        mock_q.text.side_effect = [
            _mock_ask("Edge"),
            _mock_ask("M4 Pro"),
            _mock_ask("Appliance"),
            _mock_ask(""),  # stop
        ]
        result = _ask_hardware_tiers()
        assert len(result) == 1
        assert result[0].tier == 1
        assert result[0].platform == "Edge"


class TestAskPriorities:
    @patch("forge.workspace_wizard.questionary")
    def test_collects_priority(self, mock_q):
        mock_q.text.side_effect = [
            _mock_ask("Ship v1"),
            _mock_ask("End-to-end running"),
            _mock_ask(""),  # stop
        ]
        result = _ask_priorities()
        assert len(result) == 1
        assert result[0].priority == 1


class TestAskTechStack:
    @patch("forge.workspace_wizard.questionary")
    def test_collects_entry(self, mock_q):
        mock_q.text.side_effect = [
            _mock_ask("Core"),
            _mock_ask("Python 3.10+"),
        ]
        mock_q.confirm.return_value = _mock_ask(True)
        # Next iteration: empty layer to stop
        mock_q.text.side_effect = [
            _mock_ask("Core"),
            _mock_ask("Python 3.10+"),
            _mock_ask(""),  # stop
        ]
        result = _ask_tech_stack()
        assert len(result) == 1
        assert result[0].locked is True


class TestAskGovernanceRules:
    @patch("forge.workspace_wizard.questionary")
    def test_collects_rules(self, mock_q):
        mock_q.text.side_effect = [
            _mock_ask("No cloud"),
            _mock_ask(""),  # stop
        ]
        result = _ask_governance_rules()
        assert result == ["No cloud"]


class TestAskProjects:
    @patch("forge.workspace_wizard.questionary")
    def test_collects_project(self, mock_q):
        # First project (no deps available)
        mock_q.text.side_effect = [
            _mock_ask("core"),       # name
            _mock_ask("core/"),      # path
            _mock_ask("org/core"),   # remote
            _mock_ask(""),           # stop
        ]
        mock_q.select.return_value = _mock_ask("shared-library")
        result = _ask_projects()
        assert len(result) == 1
        assert result[0].name == "core"
        assert result[0].role == "shared-library"


class TestRunWorkspaceWizard:
    @patch("forge.workspace_wizard._ask_projects")
    @patch("forge.workspace_wizard._ask_governance_rules")
    @patch("forge.workspace_wizard._ask_tech_stack")
    @patch("forge.workspace_wizard._ask_priorities")
    @patch("forge.workspace_wizard._ask_hardware_tiers")
    @patch("forge.workspace_wizard._ask_constraints")
    @patch("forge.workspace_wizard._ask_vision")
    @patch("forge.workspace_wizard._ask_workspace_name")
    def test_full_wizard(
        self, mock_name, mock_vision, mock_constraints,
        mock_tiers, mock_priorities, mock_stack,
        mock_rules, mock_projects,
    ):
        from forge.models import (
            BusinessConstraint,
            HardwareTier,
            ProjectEntry,
            StrategicPriority,
            TechStackEntry,
        )
        mock_name.return_value = "Test Labs"
        mock_vision.return_value = "Build AI"
        mock_constraints.return_value = [
            BusinessConstraint(constraint="X", value="Y"),
        ]
        mock_tiers.return_value = [
            HardwareTier(tier=1, platform="E", hardware="H", use_case="U"),
        ]
        mock_priorities.return_value = [
            StrategicPriority(priority=1, goal="G", key_result="K"),
        ]
        mock_stack.return_value = [
            TechStackEntry(layer="L", technology="T"),
        ]
        mock_rules.return_value = ["No cloud"]
        mock_projects.return_value = [
            ProjectEntry(
                name="core", role="lib", path="core/", remote="x/core",
            ),
        ]

        config = run_workspace_wizard()
        assert config.workspace_name == "Test Labs"
        assert config.business.vision == "Build AI"
        assert len(config.manifest.projects) == 1
