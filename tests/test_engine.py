import os
import tempfile
import sys
import unittest
from unittest.mock import patch

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from project_generator import engine  # noqa: E402


class TestEngine(unittest.TestCase):
    def setUp(self):
        # Patch setup_virtualenv to prevent actual venv creation
        self.venv_patcher = patch("project_generator.engine.setup_virtualenv")
        self.mock_setup_venv = self.venv_patcher.start()

    def tearDown(self):
        self.venv_patcher.stop()

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
        """Test creates folders and files (Default: Fullstack)."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Create structure
            engine.create_structure(tmpdirname)
            # Verify venv setup was called
            self.mock_setup_venv.assert_called_with(tmpdirname, "pip")

            # Check files exist
            dockerfile_path = os.path.join(tmpdirname, "Dockerfile")
            compose_path = os.path.join(tmpdirname, "docker-compose.yml")

            assert os.path.exists(dockerfile_path)
            assert os.path.exists(compose_path)
            assert os.path.exists(os.path.join(tmpdirname, "mkdocs.yml"))
            assert os.path.exists(os.path.join(tmpdirname, "docs/index.md"))
            assert os.path.exists(
                os.path.join(tmpdirname, ".github/workflows/docs.yml")
            )
            assert os.path.exists(
                os.path.join(tmpdirname, ".agent/rules/ai_behavior.md")
            )
            # Verify Ansible Common
            assert os.path.exists(os.path.join(tmpdirname, "ansible/setup_workstation.yml"))

    def test_create_structure_profiles(self):
        """Test generating different profiles."""
        # 1. Web Profile
        with tempfile.TemporaryDirectory() as web_dir:
            context = {"__PROFILE__": "web"}
            engine.create_structure(web_dir, context=context)
            self.mock_setup_venv.assert_called_with(web_dir, "pip")

            # Check for Gantry-like structure
            assert os.path.exists(os.path.join(web_dir, "src/backend/app/models"))
            assert os.path.exists(os.path.join(web_dir, "src/backend/app/routers"))
            assert os.path.exists(os.path.join(web_dir, "src/backend/app/services"))
            assert os.path.exists(os.path.join(web_dir, "src/backend/core"))
            assert os.path.exists(os.path.join(web_dir, "src/frontend/static"))
            # Should NOT have src/models from fullstack
            assert not os.path.exists(os.path.join(web_dir, "src/models"))

            # Check AI Rules content
            rules_path = os.path.join(web_dir, ".agent/rules/ai_behavior.md")
            with open(rules_path, "r") as f:
                content = f.read()
                assert "Reference: Gantry" in content
                assert "Gantry Architect" in content

            # Verify Ansible exists here too
            assert os.path.exists(os.path.join(web_dir, "ansible/roles"))

        # 2. System Profile
        with tempfile.TemporaryDirectory() as sys_dir:
            context = {"__PROFILE__": "system"}
            engine.create_structure(sys_dir, context=context)

            # Check for Shurtugal-like structure
            assert os.path.exists(os.path.join(sys_dir, "ansible/roles"))
            assert os.path.exists(os.path.join(sys_dir, "scripts/bootstrap.sh"))
            # Should NOT have web backend
            assert not os.path.exists(os.path.join(sys_dir, "src/backend"))

            # Check for Flake8 (via COMMON_FILES)
            assert os.path.exists(os.path.join(sys_dir, ".flake8"))

            # Check AI Rules content
            rules_path = os.path.join(sys_dir, ".agent/rules/ai_behavior.md")
            with open(rules_path, "r") as f:
                content = f.read()
                assert "Reference: Shurtugal-LNX" in content
                assert "Ansible-First" in content

        # 3. MVC Profile
        with tempfile.TemporaryDirectory() as mvc_dir:
            context = {"__PROFILE__": "mvc"}
            engine.create_structure(mvc_dir, context=context)

            # Check for MVC structure
            assert os.path.exists(os.path.join(mvc_dir, "src/app/controllers"))
            assert os.path.exists(os.path.join(mvc_dir, "src/app/models"))
            assert os.path.exists(os.path.join(mvc_dir, "src/app/views"))
            assert os.path.exists(os.path.join(mvc_dir, "src/app/main.py"))

            # Should have tests structure
            assert os.path.exists(os.path.join(mvc_dir, "tests/controllers"))
            assert os.path.exists(os.path.join(mvc_dir, "tests/models"))

            # Verify Ansible exists
            assert os.path.exists(os.path.join(mvc_dir, "ansible/roles"))

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
                assert "name = \"MyAIProject\"" in content
                assert (
                    "authors = [{name = \"Alice\", email = \"labs@example.com\"}]"
                    in content
                )
                assert "license = {text = \"MIT\"}" in content

    def test_create_structure_poetry(self):
        """Test poetry validation (requirements.txt skipped)."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            context = {
                "__PROJECT_NAME__": "PoetryProject",
                "__PACKAGE_MANAGER__": "poetry"
            }
            engine.create_structure(tmpdirname, context=context)

            # venv should NOT be called for poetry
            self.mock_setup_venv.assert_called_with(tmpdirname, "poetry")

            # requirements.txt should NOT exist
            assert not os.path.exists(os.path.join(tmpdirname, "requirements.txt"))

            # pyproject.toml should contain poetry section
            with open(os.path.join(tmpdirname, "pyproject.toml"), "r") as f:
                content = f.read()
                assert "[tool.poetry]" in content


if __name__ == "__main__":
    unittest.main()
