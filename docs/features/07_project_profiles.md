# Feature Title: Project Type Profiles

## Overview
This feature introduces "Project Profiles" to Forge, allowing users to select the architecture of their new project at generation time. Instead of a single "one-size-fits-all" structure, users can choose between specialized setups.

## Requirements
- [x] Support multiple profiles with TOML-based definitions and inheritance.
- [x] Profiles defined as directories under `profiles/` with `profile.toml`, `structure.toml`, and `templates/`.
- [x] Profile inheritance: child profiles extend parent profiles (e.g., `fullstack` inherits `base`).
- [x] Update CLI to accept profile selection via `--profile` flag.
- [x] Update Interactive Wizard to prompt for profile variables.
- [x] Ensure specific templates utilize profile context variables.

## Technical Implementation (v2)
- **Profile Definitions**: Each profile is a directory under `profiles/` containing:
    - `profile.toml`: Variables, metadata, inheritance (`inherits = "base"`).
    - `structure.toml`: Directories, files, and conditionals.
    - `templates/`: Jinja2 `.j2` template files.
- **Profile Loader**: `src/forge/profile_loader.py` — loads TOML, resolves inheritance chains, merges variables/files/directories.
- **Listing**: `forge profiles list` shows all available profiles. `forge profiles show <name>` shows detail.
- **Wizard**: `src/forge/wizard.py` builds prompts from `VariableSpec` definitions in the resolved profile.
- **Inheritance**: Child templates override parent templates (child-first lookup in `template_dirs`).

## Acceptance Criteria
- [x] `forge new my-project --profile fullstack` creates a structure from the fullstack profile.
- [x] `forge new my-project --profile base` creates a minimal structure from the base profile.
- [x] `forge profiles list` shows available profiles with descriptions.
- [x] Profile inheritance correctly merges base → child variables, files, and directories.
- [x] Existing tests pass and new tests cover profile loading and inheritance.
