# Feature Title: Variable Template System (Jinja2)

## Overview
Templates are stored as external Jinja2 `.j2` files within profile directories. The v2 architecture uses a profile-driven template system with inheritance, enabling child profiles to override parent templates.

## Requirements
- [x] Templates live in `profiles/*/templates/*.j2` (per-profile, with inheritance).
- [x] Integrate `jinja2` to render these files via `renderer.py`.
- [x] Support dynamic variables: `{{ project_name }}`, `{{ author_name }}`, `{{ python_version }}`.
- [x] Custom template loader (`ProfileTemplateLoader`) searches child → parent template directories.

## Technical Implementation (v2)
- **Renderer**: `src/forge/renderer.py` — pure in-memory rendering, returns `RenderedFile` objects (no I/O).
- **Template Loader**: `ProfileTemplateLoader` in `renderer.py` — searches `template_dirs` in child-first order.
- **Profiles**: Templates organized under `profiles/base/templates/`, `profiles/fullstack/templates/`, etc.
- **Conditionals**: Files can be conditionally generated based on profile variable values (defined in `structure.toml`).
- **Dependencies**: `jinja2`.

## Acceptance Criteria
How will we know this is working correctly?
- [x] All generated files match the current output (regression test).
- [x] Developers can edit a `.j2` file to update the scaffold without changing Python code.
- [x] Unit tests verify variable substitution works correctly.

## Feedback/Notes
Ensure `MANIFEST.in` includes the non-Python template files so they are packaged correctly.
