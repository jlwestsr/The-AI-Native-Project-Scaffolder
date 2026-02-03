"""Tests for the interactive wizard."""
import pytest
from pathlib import Path
from unittest.mock import patch

from forge.wizard import build_prompts
from forge.models import VariableSpec


class TestBuildPrompts:
    def test_string_produces_text_prompt(self):
        variables = {"name": VariableSpec(prompt="Your name", type="string")}
        prompts = build_prompts(variables)
        assert prompts[0]["type"] == "text"
        assert prompts[0]["name"] == "name"

    def test_choice_produces_select_prompt(self):
        variables = {
            "mgr": VariableSpec(
                prompt="Manager",
                type="choice",
                choices=["pip", "poetry"],
                default="pip",
            )
        }
        prompts = build_prompts(variables)
        assert prompts[0]["type"] == "select"
        assert prompts[0]["choices"] == ["pip", "poetry"]

    def test_confirm_produces_confirm_prompt(self):
        variables = {
            "docker": VariableSpec(
                prompt="Use Docker?", type="confirm", default=True
            )
        }
        prompts = build_prompts(variables)
        assert prompts[0]["type"] == "confirm"
        assert prompts[0]["default"] is True

    def test_default_preserved(self):
        variables = {
            "name": VariableSpec(
                prompt="Name", type="string", default="World"
            )
        }
        prompts = build_prompts(variables)
        assert prompts[0]["default"] == "World"
