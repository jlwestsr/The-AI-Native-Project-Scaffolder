# Feature: Pre-commit hooks in scaffolds

## Overview

Generated projects include local quality gates so lint/format fails before push.

## Outcome (current)

- Template: `profiles/base/templates/.pre-commit-config.yaml.j2` (emitted for **base** and, by inheritance, **fullstack**).
- **monorepo** is standalone (does not inherit base) and does not ship this file.
- Post-scaffold: `forge new` attempts `pre-commit install` when available.
- Dev deps template may list `pre-commit` for the generated project.

## Acceptance (met)

- [x] New **base**/**fullstack** projects can include `.pre-commit-config.yaml`
- [x] Generator tests cover file creation paths

## Notes

Consider `ruff` in generated projects later; base still documents flake8/black-era hooks.
