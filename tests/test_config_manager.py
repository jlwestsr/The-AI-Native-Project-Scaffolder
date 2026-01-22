import unittest
from unittest.mock import patch, mock_open
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from project_generator import config_manager  # noqa: E402


class TestConfigManager(unittest.TestCase):
    @patch('project_generator.config_manager.get_config_path')
    @patch('project_generator.config_manager.tomli.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_setting(self, mock_file, mock_toml, mock_path):
        mock_path.return_value.exists.return_value = True
        mock_toml.return_value = {"author_name": "Test User"}

        val = config_manager.get_setting("author_name")
        assert val == "Test User"

    @patch('project_generator.config_manager.get_config_path')
    @patch('project_generator.config_manager.tomli_w.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_set_setting(self, mock_file, mock_dump, mock_path):
        mock_path.return_value.exists.return_value = False  # New file

        config_manager.set_setting("license", "MIT")

        # Verify dump was called with new config
        mock_dump.assert_called()
        args = mock_dump.call_args[0]
        assert args[0] == {"license": "MIT"}


if __name__ == '__main__':
    unittest.main()
