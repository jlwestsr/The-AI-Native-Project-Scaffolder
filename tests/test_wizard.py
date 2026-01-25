import unittest
from unittest.mock import patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from project_generator import wizard  # noqa: E402


class TestWizard(unittest.TestCase):
    @patch('project_generator.wizard.config_manager.get_setting')
    @patch('project_generator.wizard.questionary.text')
    @patch('project_generator.wizard.questionary.select')
    @patch('project_generator.wizard.Console')
    def test_run_wizard(self, mock_console, mock_select, mock_text, mock_config):
        """Test wizard collects inputs correctly."""
        # Setup mocks
        mock_config.return_value = "DefaultVal"
        mock_text.return_value.ask.side_effect = ["MyProject", "Alice"]
        mock_select.return_value.ask.side_effect = [
            "fullstack",  # Profile
            "standard",   # Persona
            "3.10",    # Python
            "poetry",  # Package Manager
            "MIT"      # License
        ]

        # Run
        context = wizard.run_wizard()

        # Verify
        assert context["__PROJECT_NAME__"] == "MyProject"
        assert context["__AUTHOR_NAME__"] == "Alice"
        assert context["__PYTHON_VERSION__"] == "3.10"
        assert context["__PACKAGE_MANAGER__"] == "poetry"
        assert context["__LICENSE__"] == "MIT"
        assert context["__PROFILE__"] == "fullstack"

    @patch('project_generator.wizard.config_manager.get_setting')
    @patch('project_generator.wizard.questionary.text')
    @patch('project_generator.wizard.questionary.select')
    @patch('project_generator.wizard.Console')
    def test_run_wizard_defaults(self, mock_console, mock_select, mock_text, mock_cfg):
        """Test wizard handles defaults/empty input."""
        mock_cfg.return_value = "DefaultVal"
        # Setup mocks: Return empty string for name to trigger default logic
        mock_text.return_value.ask.side_effect = ["", "User"]
        mock_select.return_value.ask.side_effect = [
            "fullstack",  # Profile
            "standard",   # Persona
            "3.10",  # Python Version
            "pip",   # Package Manager
            "MIT"    # License
        ]

        # Run
        with patch('os.path.basename', return_value="cwd_name"):
            context = wizard.run_wizard()

        # Verify
        assert context["__PROJECT_NAME__"] == "cwd_name"
        assert context["__AUTHOR_NAME__"] == "User"
        assert context["__PYTHON_VERSION__"] == "3.10"
        assert context["__PACKAGE_MANAGER__"] == "pip"
        assert context["__LICENSE__"] == "MIT"
        assert context["__PROFILE__"] == "fullstack"


if __name__ == '__main__':
    unittest.main()
