import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from project_generator import cli  # noqa: E402


class TestCLI(unittest.TestCase):
    @patch('project_generator.cli.engine')
    @patch('project_generator.cli.git_ops')
    @patch('project_generator.cli.os')
    def test_main_success(self, mock_os, mock_git, mock_engine):
        """Test the main execution flow."""
        # Setup mocks
        mock_os.getcwd.return_value = "/tmp/test"
        mock_os.path.abspath.return_value = "/tmp/test"
        # Ensure git init check passes
        mock_os.path.exists.return_value = False

        # Call main with no args (uses default)
        with patch(
            'argparse.ArgumentParser.parse_args',
            return_value=MagicMock(
                target_dir="/tmp/test",
                update=False,
                manager=None,
                config_list=False,
                config_set=None
            )
        ):
            cli.main()

        # Verify calls
        mock_os.makedirs.assert_called_with("/tmp/test", exist_ok=True)
        mock_engine.check_greenfield.assert_called_with("/tmp/test")
        mock_engine.create_structure.assert_called_with(
            "/tmp/test",
            update=False,
            context={}
        )
        mock_git.init_git.assert_called_with("/tmp/test")


if __name__ == '__main__':
    unittest.main()
