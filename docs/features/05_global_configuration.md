# Feature Title: Global Configuration

## Overview
Users verify their `author` and `email` information frequently. They shouldn't have to provide this every time they generate a project. The tool should respect a global configuration file in the user's home directory.

## Requirements
List the specific requirements for this feature:
- [ ] Look for checking `~/.config/forge/config.toml` (or `~/.forgeconfig`).
- [ ] Read default values for: `author_name`, `author_email`, `license`, `python_version`.
- [ ] Override global defaults with CLI arguments if provided.
- [ ] Add a `forge config` command to easily set these values.

## Technical Implementation (Optional)
If you have specific ideas about how this should be built, list them here:
- Proposed modules: `src/project_generator/config_manager.py`.
- Dependencies: `tomli` (for read) / `tomli_w` (for write).
- Data changes: None.

## Acceptance Criteria
How will we know this is working correctly?
- [ ] Use defaults from config file if no args provided.
- [ ] `forge config --set author="Jane Doe"` updates the file.
- [ ] Tests verify precedence: CLI Args > Global Config > Hardcoded Defaults.

## Feedback/Notes
Use `platformdirs` to determine the correct config path for the OS.
