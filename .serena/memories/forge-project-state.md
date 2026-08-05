# Forge Project State

## Last Updated: 2026-02-03

## Architecture
- **v2 is live**. The v1 code (`src/project_generator/`) has been fully removed — source files were deleted earlier, stale `__pycache__` and empty dirs cleaned up this session.
- v2 entry point: `src/forge/cli.py` (Typer-based)
- Profile-driven pipeline: `models.py`, `profile_loader.py`, `renderer.py`, `applier.py`, `lockfile.py`, `pipeline.py`, `cli.py`, `wizard.py`
- Profiles live in `profiles/` as TOML configs + Jinja2 templates
- 72 tests passing as of this session

## Branch & Git Setup
- **Default branch on GitHub**: `develop` (integration)
- **`main`**: stable releases only — no direct commits, only merges from `develop`
- **`master`**: deleted (both local and remote) this session
- Remote: `github.com:jlwestsr/The-AI-Native-Project-Scaffolder.git`
- Both `main` and `develop` are in sync at commit `890b076`

## Docs Updated This Session
All docs now reference v2 paths (`src/forge/`, `profiles/`) instead of v1 (`src/project_generator/`):
- `CLAUDE.md` — full rewrite for v2 architecture
- `CONTEXT.md` — persona responsibilities, project map, CLI reference
- `AI_DIRECTIVES.md` — discovery directive points to `profiles/`
- `GEMINI.md` — entry point updated
- `WORKFLOW.md` — discovery phase references `profiles/`
- `docs/AI_INSIGHTS.md` — v1 removal noted, config drift path updated
- `.gitignore` — removed stale v1 template exception
- `profiles/base/templates/GEMINI.md.j2` — fallback entry point fixed

## Key Decisions
- `egg-info` regenerates on `pip install -e` and is gitignored — expected in `src/`
- CHANGELOG.md, docs/features/*.md, docs/plans/*.md left as-is (historical records)
- Parent repo (`west_ai_labs/`) is local-only with no remote — don't try to push there

## What's Next
- Validate v2 output against reference projects
- Template porting may need Jinja2 variable name adjustments (v2 context vars differ slightly from v1)
- v1 entry point `forge = "project_generator.cli:main"` should be confirmed removed from `pyproject.toml`
