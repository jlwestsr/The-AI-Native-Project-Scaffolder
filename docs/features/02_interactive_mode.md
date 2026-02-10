# Feature Title: Interactive CLI Mode

## Overview
The current CLI uses command-line arguments, which are fast but rigid. To improve the User Experience (UX) and capture richer user intent (like author name, license preference, etc.), we want to add an Interactive Mode that prompts the user for input if no arguments are provided.

## Requirements
List the specific requirements for this feature:
- [x] Detect if the program is running in an interactive terminal.
- [x] If no arguments are provided, launch an interactive wizard.
- [x] Prompt for: Project Name, Author Name, Python Version (3.10/3.11), and License (MIT/Apache/Proprietary).
- [x] Support a `--non-interactive` flag to force default behavior (for scripts).

## Technical Implementation (v2)
- **Wizard**: `src/forge/wizard.py` — builds prompts from profile variable specs (`VariableSpec` in `models.py`).
- **Workspace Wizard**: `src/forge/workspace_wizard.py` — interactive wizard for ecosystem-level configuration.
- **CLI Integration**: `src/forge/cli.py` — runs wizard when no `--var` flags and not `--no-interactive`.
- **Dependencies**: `rich` and `questionary` for beautiful prompts.

## Acceptance Criteria
How will we know this is working correctly?
- [x] Running `forge` without args launches the wizard.
- [x] Users can select options via arrow keys (for License/Python version).
- [x] The generated `pyproject.toml` and `README.md` reflect the user's inputs.

## Feedback/Notes
Default to current behavior if `sys.stdin` is not a TTY.
