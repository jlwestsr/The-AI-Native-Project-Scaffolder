import os
import shutil
import tempfile
import sys
import unittest
from unittest.mock import patch

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from project_generator import engine
from project_generator.assets import templates

class TestEngine(unittest.TestCase):
    def test_check_greenfield_valid(self):
        """Test greenfield check passes on empty dir."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Should not raise
            engine.check_greenfield(tmpdirname)
            
    def test_check_greenfield_valid_with_git(self):
        """Test greenfield check ignores .git."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            os.makedirs(os.path.join(tmpdirname, ".git"))
            # Should not raise
            engine.check_greenfield(tmpdirname)

    def test_check_greenfield_invalid(self):
        """Test greenfield check fails on non-empty dir."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(os.path.join(tmpdirname, "random.txt"), "w") as f:
                f.write("data")
            
            with self.assertRaises(SystemExit):
                engine.check_greenfield(tmpdirname)

    def test_create_structure(self):
        """Test creates folders and files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Create structure
            engine.create_structure(tmpdirname)
            
            # Check files exist
            dockerfile_path = os.path.join(tmpdirname, "Dockerfile")
            compose_path = os.path.join(tmpdirname, "docker-compose.yml")
            
            assert os.path.exists(dockerfile_path)
            assert os.path.exists(compose_path)
            
            # Check content
            with open(dockerfile_path, 'r') as f:
                content = f.read()
                assert content.strip() == templates.DOCKERFILE_CONTENT.strip()
                
            with open(compose_path, 'r') as f:
                content = f.read()
                assert content.strip() == templates.DOCKER_COMPOSE_CONTENT.strip()

    def test_create_structure_with_context(self):
        """Test file creation with context replacement (Jinja2)."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            context = {
                "__PROJECT_NAME__": "MyAIProject",
                "__AUTHOR_NAME__": "Alice",
                "__LICENSE__": "MIT"
            }
            engine.create_structure(tmpdirname, context=context)
            
            # Check README
            readme_path = os.path.join(tmpdirname, "README.md")
            with open(readme_path, "r") as f:
                content = f.read()
                assert "# MyAIProject" in content
                
            # Check pyproject.toml
            toml_path = os.path.join(tmpdirname, "pyproject.toml")
            with open(toml_path, "r") as f:
                content = f.read()
                assert 'name = "MyAIProject"' in content
                assert 'authors = [{name = "Alice", email = "labs@example.com"}]' in content
                assert 'license = {text = "MIT"}' in content

if __name__ == '__main__':
    unittest.main()
