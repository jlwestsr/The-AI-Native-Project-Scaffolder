# Feature Title: Interactive CLI Mode

## Overview
The current CLI uses command-line arguments, which are fast but rigid. To improve the User Experience (UX) and capture richer user intent (like author name, license preference, etc.), we want to add an Interactive Mode that prompts the user for input if no arguments are provided.

## Requirements
List the specific requirements for this feature:
- [x] Detect if the program is running in an interactive terminal.
- [x] If no arguments are provided, launch an interactive wizard.
- [x] Prompt for: Project Name, Author Name, Python Version (3.10/3.11), and License (MIT/Apache/Proprietary).
- [x] Support a `--non-interactive` flag to force default behavior (for scripts).

## Technical Implementation (Optional)
If you have specific ideas about how this should be built, list them here:
- Proposed modules: `src/project_generator/cli.py`.
- Dependencies: `rich` and `questionary` for beautiful prompts.
- Data changes: None.

## Acceptance Criteria
How will we know this is working correctly?
- [x] Running `forge` without args launches the wizard.
- [x] Users can select options via arrow keys (for License/Python version).
- [x] The generated `pyproject.toml` and `README.md` reflect the user's inputs.

## Feedback/Notes
Default to current behavior if `sys.stdin` is not a TTY.
