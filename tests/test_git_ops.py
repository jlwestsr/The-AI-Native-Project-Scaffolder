import os
import sys
import unittest
import subprocess
from unittest.mock import patch, call

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from project_generator import git_ops

class TestGitOps(unittest.TestCase):
    @patch('project_generator.git_ops.subprocess.run')
    def test_run_command_success(self, mock_run):
        """Test successful command execution."""
        git_ops.run_command("echo hello")
        mock_run.assert_called_with(
            "echo hello",
            check=True,
            shell=True,
            cwd=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
    @patch('project_generator.git_ops.subprocess.run')
    def test_run_command_failure(self, mock_run):
        """Test failed command execution."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr=b"Error")
        
        with self.assertRaises(SystemExit):
            git_ops.run_command("fail")

    @patch('project_generator.git_ops.run_command')
    def test_init_git(self, mock_run_cmd):
        """Test git initialization sequence."""
        git_ops.init_git("/tmp/test")
        
        expected_calls = [
            call("git init", cwd="/tmp/test"),
            call("git add .", cwd="/tmp/test"),
            call('git commit -m "Initial commit: Complete AI project scaffold"', cwd="/tmp/test"),
            call("git checkout -b develop", cwd="/tmp/test"),
            call("pip install pre-commit && pre-commit install", cwd="/tmp/test")
        ]
        mock_run_cmd.assert_has_calls(expected_calls)

if __name__ == '__main__':
    unittest.main()
