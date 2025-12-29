import os
import shutil
import tempfile
import sys
import unittest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from project_generator import engine
from project_generator.assets import configs

class TestPreCommit(unittest.TestCase):
    def test_config_creation(self):
        """Test .pre-commit-config.yaml creation."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            engine.create_structure(tmpdirname)
            
            config_path = os.path.join(tmpdirname, ".pre-commit-config.yaml")
            assert os.path.exists(config_path)
            
            with open(config_path, "r") as f:
                content = f.read()
                assert "repos:" in content
                assert "https://github.com/pre-commit/pre-commit-hooks" in content
                assert "https://github.com/psf/black" in content

    def test_requirements(self):
        """Test pre-commit is in requirements-dev.txt."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            engine.create_structure(tmpdirname)
            
            req_path = os.path.join(tmpdirname, "requirements-dev.txt")
            with open(req_path, "r") as f:
                content = f.read()
                assert "pre-commit" in content

if __name__ == '__main__':
    unittest.main()
