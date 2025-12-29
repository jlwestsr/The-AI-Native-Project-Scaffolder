import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Mock rich and questionary before importing wizard
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.panel'] = MagicMock()
sys.modules['questionary'] = MagicMock()

from project_generator import wizard

class TestWizard(unittest.TestCase):
    @patch('questionary.text')
    @patch('questionary.select')
    def test_run_wizard(self, mock_select, mock_text):
        """Test wizard collects inputs correctly."""
        # Setup mocks
        mock_text.return_value.ask.side_effect = ["MyProject", "Alice"] # Name, Author
        mock_select.return_value.ask.side_effect = [
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

    @patch('questionary.text')
    @patch('questionary.select')
    def test_run_wizard_defaults(self, mock_select, mock_text):
        """Test wizard handles defaults/empty input."""
        # Setup mocks: Return empty string for name to trigger default logic
        mock_text.return_value.ask.side_effect = ["", "User"] 
        mock_select.return_value.ask.side_effect = [
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

if __name__ == '__main__':
    unittest.main()
