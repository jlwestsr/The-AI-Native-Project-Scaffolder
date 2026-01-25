import pytest
from unittest.mock import patch
from project_generator import engine


@pytest.fixture(autouse=True)
def mock_venv():
    with patch('project_generator.engine.setup_virtualenv') as mock:
        yield mock


def test_persona_logic_standard(tmp_path):
    """Verify standard persona uses default template."""
    target = tmp_path / "standard_project"
    target.mkdir()

    context = {
        "__PROJECT_NAME__": "test_standard",
        "__PROFILE__": "fullstack",
        "__AI_PERSONA__": "standard"
    }

    engine.create_structure(str(target), context=context)

    behavior_file = target / ".agent/rules/ai_behavior.md"
    assert behavior_file.exists()
    content = behavior_file.read_text()
    # Check for specific Fullstack text
    assert "Reference: Nebulus" in content
    assert "Strict Compliance" not in content


def test_persona_logic_architect(tmp_path):
    """Verify architect persona uses specific template."""
    target = tmp_path / "architect_project"
    target.mkdir()

    context = {
        "__PROJECT_NAME__": "test_architect",
        "__PROFILE__": "fullstack",
        "__AI_PERSONA__": "architect"
    }

    engine.create_structure(str(target), context=context)

    behavior_file = target / ".agent/rules/ai_behavior.md"
    assert behavior_file.exists()
    content = behavior_file.read_text()
    assert "Strict Compliance" in content
