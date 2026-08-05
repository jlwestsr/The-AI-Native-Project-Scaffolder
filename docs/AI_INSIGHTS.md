# Project AI Insights (Long-Term Memory)

## Purpose
This document serves as the **Long-Term Memory** for AI agents working on **Forge**. It captures project-specific behavioral nuances, recurring pitfalls, and architectural decisions that are not strictly "rules" (in `AI_DIRECTIVES.md`) but are critical for maintaining continuity.

## 1. Architectural Patterns
*   **Profile-Driven Pipeline (v2)**: The pipeline follows strict stage separation: `profile_loader.py` (load TOML) → `renderer.py` (pure Jinja2 rendering, no I/O) → `applier.py` (disk writes with strategies) → `lockfile.py` (state tracking). Do not leak file structure definitions into the pipeline; they belong in profile TOML files under `profiles/`.
*   **Reference-First**: We are a "Copy-Reference" generator. We do not invent structures; we replicate the structure of `reference_shurtugal-lnx` (or others).

## 2. Recurring Pitfalls
*   **Template Shadow Logic**: Avoid putting complex `{% if %}` logic in Jinja2 templates. Use profile conditionals in `structure.toml` to control which files are generated, and pass pre-computed variables to templates.
*   **Config Drift**: If you change a file in a reference project, you MUST update the corresponding template in `profiles/*/templates/` immediately.

## 3. Workflow Nuances
*   **Verification**: `pytest` is the baseline; also dry-run scaffolds with
    `forge new /tmp/probe -p base|fullstack|monorepo --no-interactive --dry-run --neo off`
    to catch template errors.
*   **CLI (2026-08)**: Use `forge new <path>`, not legacy `forge .`. Profiles for
    `forge new`: base, fullstack, monorepo only. neo-harness via `--neo auto|on|off`.
*   **Install**: Editable pipx/pip so `profiles/` resolve; or set `FORGE_PROFILES_DIR`.
*   **Dependencies**: When adding a dependency, check if it's needed for the *Generator* (add to `pyproject.toml`) or the *Generated Project* (add to `profiles/*/templates/`).

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
*   **v1 code has been removed** from `src/project_generator/`. All source and bytecode were deleted after v2 was validated.
*   **Template porting**: v1 templates were copied to `profiles/base/templates/` and `profiles/fullstack/templates/`. Some may need Jinja2 variable name adjustments as v2 context variables differ slightly from v1.
*   **Entry point**: v2 uses `forge = "forge.cli:app"` (Typer). v1 used `forge = "project_generator.cli:main"`. Both are in `pyproject.toml` — only one can be active.

## 5. v0.2.0 — Workspace Ecosystem Scaffolding (2026-02-09)

### What changed
Added `forge workspace` subcommand group for scaffolding ecosystem-level workspace roots and syncing governance context into sub-projects. New modules: `workspace.py`, `workspace_wizard.py`. New templates in `profiles/workspace/templates/`. 11 new Pydantic models added to `models.py`. 72 new tests (144 total).

### Architectural decisions
*   **Separate wizard**: `workspace_wizard.py` is separate from `wizard.py` because workspace data collection uses repeating groups (constraints, hardware tiers, projects) and inter-dependent fields (project dependencies reference previously entered projects). The existing wizard's flat variable-to-prompt pattern doesn't fit.
*   **Sentinel-based sync**: `sync_context()` uses `<!-- forge:ecosystem-start/end -->` comment markers to inject/replace a managed section in sub-project CLAUDE.md and GEMINI.md. This preserves user content outside the markers and is idempotent — running sync twice produces the same result.
*   **Sync does not create files**: If a sub-project has no CLAUDE.md, sync skips it. Sub-projects own their files; Forge only manages its section within them.
*   **JSON lock file**: `.forge-workspace.lock` uses JSON (Pydantic `model_dump_json`) instead of TOML like `.forge.lock`. The workspace config has nested lists of objects that map cleanly to JSON but awkwardly to TOML's array-of-tables syntax.
*   **Markdown table parser**: `parse_overlord_md()` uses regex-based table extraction rather than a Markdown AST library. The table format is constrained and predictable — a full parser would be overkill. Round-trip tested: render → parse → compare.
*   **ASCII dependency graph**: `build_dependency_ascii()` computes a tree from `ProjectEntry.depends_on` adjacency. Standalone projects (no deps, no dependents) are listed separately. The graph is embedded directly in OVERLORD.md.

### Lessons learned
*   **Typer sub-typers compose well**: Adding `workspace_app = typer.Typer()` and `app.add_typer(workspace_app, name="workspace")` gave us `forge workspace init/sync/info` with zero friction. The pattern scales to future subcommand groups.
*   **Templates should match reference files exactly**: The Jinja2 templates for BUSINESS.md and OVERLORD.md were written to reproduce the exact Markdown table format of the existing hand-written files in the ecosystem root. This ensures Overlord can parse either the hand-written or generated version.
*   **Testing sentinel injection thoroughly pays off**: The idempotency test (inject, then inject again, assert no change) caught an edge case with trailing newlines early.

### What to watch for
*   **Template drift**: If the ecosystem root's BUSINESS.md or OVERLORD.md format changes, the Jinja2 templates in `profiles/workspace/templates/` must be updated to match.
*   **Governance rule parsing**: `sync_context()` extracts governance rules from BUSINESS.md using a simple regex (`^\d+\.\s+\*\*(.+?)\*\*\s*—\s*(.+)$`). If the rule format changes, the regex must be updated.
*   **Lock file migration**: The workspace lock is v1.0 JSON. If the schema changes, a migration path will be needed.

## 6. GitHub Wiki v2 Update (2026-02-10)

### What changed
All 6 GitHub wiki pages updated to reflect v2 profile-driven pipeline architecture. Zero v1 references remain (`project_generator`, `configs.py`, `engine.py`, MVC pattern all removed). All 11 v2 modules documented across Architecture and Contributing pages.

### Pages updated
- **Home** — Updated feature list to highlight profile-driven pipeline, lock files, workspace management
- **Architecture** — Full rewrite: pipeline flow diagram, module table (all 11 modules), profile system, generated file layout, design principles
- **User Guide** — Rewritten with profiles, package managers, safe updates, workspace management, full CLI reference
- **Installation** — Updated repo URL to `nebulus-forge`, added pre-commit hooks step
- **Contributing** — References `src/forge/` modules and `profiles/` directory, updated standards
- **Troubleshooting** — Added lock file conflict resolution section

### Status
Complete. Wiki commit `b0b2b13` on the wiki repo. Source code docs were updated separately in commit `a20de54` on the main repo.

## 2026-03-29 — Bug: `--no-interactive` fails when required vars not passed via `--var`

**Reported by:** Moto during nebulus-conductor scaffold
**Severity:** Medium — silent failure, confusing error message

### What Happened
Running `forge new <target> --profile fullstack --no-interactive` without explicit `--var` flags throws:
```
UndefinedError: 'python_version' is undefined
```
The error occurs in `profiles/fullstack/templates/ansible/setup_workstation.yml.j2:36` where `{{ python_version.stdout }}` is used but `python_version` was never passed as a variable.

### Root Cause
`--no-interactive` skips the wizard but does NOT apply variable defaults from `profile.yml`. Required variables with no defaults (e.g. `project_name`) and variables used in templates (e.g. `python_version`) are left undefined. Jinja2 raises `UndefinedError` at render time.

### Workaround
Pass all required variables explicitly via `--var`:
```bash
forge new /path/to/project --profile fullstack --no-interactive \
  --var project_name="my-project" \
  --var python_version="3.11" \
  --var manager="pip" \
  --var license="MIT" \
  --var persona="architect" \
  --var use_docker=true
```

### Proper Fix (future)
`--no-interactive` should fall back to variable defaults defined in `profile.yml` when `--var` is not provided. No variables with defaults should be left undefined in non-interactive mode.

**File to fix:** `src/forge/pipeline.py` — variable resolution step before rendering.
