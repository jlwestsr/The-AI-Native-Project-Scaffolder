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

## 4. v2 Rewrite — Architectural Decisions (2026-02-03)

### What changed
v1's MVC architecture (`configs.py` / `engine.py` / `wizard.py`) was replaced with a **profile-driven pipeline** architecture. Key modules: `models.py`, `profile_loader.py`, `renderer.py`, `applier.py`, `lockfile.py`, `pipeline.py`, `cli.py`, `wizard.py`.

### Lessons learned
*   **Profiles as data, not code**: Moving from 375-line Python dicts (`configs.py`) to TOML files (`profile.toml` + `structure.toml`) per profile makes adding new profiles a zero-Python task. This was the single biggest architectural win.
*   **Pipeline stages must be pure functions**: `render_templates()` returns `RenderedFile` objects in memory — no disk I/O. `apply_to_disk()` handles all writing. This separation makes every stage independently testable.
*   **Lock file hashing**: SHA-256 truncated to 16 hex chars is sufficient for content-change detection in `.forge.lock`. Full SHA would be overkill for this use case.
*   **Profile inheritance is shallow merge**: Child overrides parent for variables/files/conditionals; directories are unioned. Template lookup walks `template_dirs` child-first. Circular inheritance is detected eagerly.
*   **Typer + Pydantic + Jinja2 is a strong stack**: Typer handles CLI, Pydantic validates at boundaries, Jinja2 renders. Each library stays in its lane — no overlap.
*   **Worktree isolation works well**: Using `.worktrees/` for the rewrite kept `develop` clean throughout the multi-commit implementation.

### What to watch for
*   **v1 code still exists** in `src/project_generator/`. It will need to be removed or deprecated once v2 is validated against reference projects.
*   **Template porting**: v1 templates were copied to `profiles/base/templates/` and `profiles/fullstack/templates/`. Some may need Jinja2 variable name adjustments as v2 context variables differ slightly from v1.
*   **Entry point**: v2 uses `forge = "forge.cli:app"` (Typer). v1 used `forge = "project_generator.cli:main"`. Both are in `pyproject.toml` — only one can be active.
