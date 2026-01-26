# Project AI Insights (Long-Term Memory)

## Purpose
This document serves as the **Long-Term Memory** for AI agents working on **Forge**. It captures project-specific behavioral nuances, recurring pitfalls, and architectural decisions that are not strictly "rules" (in `AI_DIRECTIVES.md`) but are critical for maintaining continuity.

## 1. Architectural Patterns
*   **Scaffolding MVC**: The separation of `configs.py` (Model) from `wizard.py` (View) and `engine.py` (Controller) is absolute. Do not leak directory structure definitions into the engine logic.
*   **Reference-First**: We are a "Copy-Reference" generator. We do not invent structures; we replicate the structure of `reference_shurtugal-lnx` (or others).

## 2. Recurring Pitfalls
*   **Template Shadow Logic**: Avoid putting complex `{% if %}` logic in Jinja2 templates. Pre-calculate boolean flags in `engine.py` and pass them as context.
*   **Config Drift**: If you change a file in a reference project, you MUST update the corresponding template in `src/project_generator/assets/templates/` immediately.

## 3. Workflow Nuances
*   **Verification**: `pytest` is the baseline, but manual inspection of generated output (using `forge . --update --dry-run` or similar) is often necessary to catch template errors.
*   **Dependencies**: When adding a dependency, check if it's needed for the *Generator* (add to `pyproject.toml`) or the *Generated Project* (add to `configs.py` templates).
