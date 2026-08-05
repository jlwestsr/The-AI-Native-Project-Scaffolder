# Feature: Modular scaffolder (v1 → v2)

> Historical. Current architecture is the v2 profile-driven pipeline under `src/forge/`.

## Overview

Replaced a single-file generator with a modular package and installable CLI
entry point `forge` (`forge = "forge.cli:app"` in `pyproject.toml`).

## Outcome (current)

| Module | Role |
|--------|------|
| `models.py` | Pydantic models |
| `profile_loader.py` | TOML profiles + inheritance |
| `renderer.py` | Jinja2 render (no I/O) |
| `applier.py` | Write files (CREATE / UPDATE / FORCE) |
| `pipeline.py` | Orchestration |
| `cli.py` | Typer: `new`, `update`, `info`, `profiles`, `workspace` |
| `wizard.py` / `defaults.py` / `hooks.py` | Interactive vars, defaults, neo post-hook |

## Acceptance (met)

- [x] `forge new <target> -p base|fullstack|monorepo`
- [x] Profile-driven output from TOML + templates
- [x] `.forge.lock` for safe updates via `forge update`
