# Feature: Jinja2 template system

## Overview

Scaffold files are external `.j2` templates under each profile’s `templates/`,
rendered by `renderer.py` with child-first inheritance lookup.

## Outcome (current)

- Paths: `profiles/<name>/templates/**/*.j2`
- Shipped profiles: **base**, **fullstack**, **monorepo**
- Conditionals in `structure.toml` gate optional files (e.g. Docker when `use_docker`)
- Output paths may use `{{ project_slug }}` etc.

## Acceptance (met)

- [x] Edit templates without changing pipeline Python
- [x] Child profile can override parent template by same filename
- [x] Tests cover rendering and conditionals where applicable

## Notes

Editable install or `FORGE_PROFILES_DIR` is required so the `profiles/` tree is visible.
