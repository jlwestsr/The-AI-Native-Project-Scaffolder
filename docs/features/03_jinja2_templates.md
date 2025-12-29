# Feature Title: Variable Template System (Jinja2)

## Overview
Templates are currently stored as hardcoded Python strings in `assets/templates.py`. This is difficult to maintain, read, and extend. We want to move these to external template files and use a proper templating engine (Jinja2) to render them with dynamic variables.

## Requirements
List the specific requirements for this feature:
- [ ] Move large string constants to `src/project_generator/templates/*.j2` files.
- [ ] Integrate `jinja2` to render these files.
- [ ] Support dynamic variables: `{{ project_name }}`, `{{ author_name }}`, `{{ python_version }}`.
- [ ] Ensure the generator reads these files from the package resources (works when installed via `pip`).

## Technical Implementation (Optional)
If you have specific ideas about how this should be built, list them here:
- Proposed modules: `src/project_generator/engine.py` (rendering logic).
- Dependencies: `jinja2`.
- Data changes: New directory `src/project_generator/templates/`.

## Acceptance Criteria
How will we know this is working correctly?
- [ ] All generated files match the current output (regression test).
- [ ] Developers can edit a `.j2` file to update the scaffold without changing Python code.
- [ ] Unit tests verify variable substitution works correctly.

## Feedback/Notes
Ensure `MANIFEST.in` includes the non-Python template files so they are packaged correctly.
