# Feature Title: Project Type Profiles

## Overview
This feature introduces "Project Profiles" to Forge, allowing users to select the architecture of their new project at generation time. Instead of a single "one-size-fits-all" structure, users can choose between specialized setups.

## Requirements
- [ ] Support 3 distinct profiles:
    1. **Full Stack (Default)**: Based on `reference_nebulus`. General purpose AI system.
    2. **Web Application**: Based on `reference_gantry`. Python backend + HTML/JS frontend.
    3. **System Administration**: Based on `reference_shurtugal-lnx`. Ansible + IaC focused.
- [ ] Update CLI to accept profile selection via arguments (e.g., `--profile web`).
- [ ] Update Interactive Wizard to prompt for profile selection.
- [ ] Refactor `assets/configs.py` to support modular/swappable configurations.
- [ ] Ensure specific templates (like `README.md`) utilize the profile context.

## Technical Implementation
- **Refactor Configs**: Change `assets/configs.py` to export a dictionary of profiles or a `get_config(profile_name)` function.
- **Engine Logic**: Update `engine.create_structure` to accept a profile name and load the corresponding file list.
- **Wizard**: Add a selection step for "Project Type".
- **Templates**: Ensure templates are generic enough or have conditionals to handle profile differences (e.g., `cookiecutter`-like behavior).

## Acceptance Criteria
- [ ] `forge --profile web my-web-app` creates a structure matching `reference_gantry`.
- [ ] `forge --profile system my-infra` creates a structure matching `reference_shurtugal-lnx`.
- [ ] `forge` (wizard) asks "What type of project?" and generates accordingly.
- [ ] Existing tests pass and new tests cover profile generation.
