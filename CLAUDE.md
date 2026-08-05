# CLAUDE.md — Nebulus Forge

## Project overview

**Forge** is an AI-native **project scaffolder** (profile-driven pipeline).  
It is **not** an agent runtime — see [neo-harness](https://github.com/westailabs/neo-harness).

## Technical stack

- **Language:** Python 3.10+ (dev often 3.12)  
- **CLI:** Typer (`forge` entry point → `src/forge/cli.py`)  
- **Deps:** rich, questionary, jinja2, pydantic, platformdirs  

## Key directories

| Directory | Purpose |
|-----------|---------|
| `src/forge/` | CLI, pipeline, renderer, wizard, hooks (neo), workspace |
| `profiles/` | **base**, **fullstack**, **monorepo** (+ templates) |
| `templates/workspace/` | `forge workspace` templates (not a new-project profile) |
| `tests/` | Pytest |
| `docs/` | User docs — [docs/README.md](docs/README.md) |

## Architecture (v2)

Profile-driven: **load → merge inheritance → render Jinja2 → apply → `.forge.lock`**.  
Modules: `models`, `profile_loader`, `renderer`, `applier`, `pipeline`, `cli`, `wizard`, `defaults`, `hooks`, `workspace`, `lockfile`.

## Shipped profiles

| Profile | Shape |
|---------|--------|
| `base` | Single package `src/<slug>/` + governance + Claude hooks |
| `fullstack` | Inherits base + notebooks/data/ansible/docker |
| `monorepo` | Standalone control plane: products/services/hosts/lab (no root `src/<pkg>`) |

## Build & test

```bash
# Prefer project venv (.venv) or: .venv/bin/pytest
source .venv/bin/activate   # if present
./scripts/run_tests.sh      # or: pytest -q

# CLI (editable install or PATH)
forge profiles list
forge new /tmp/demo -p base --no-interactive --neo off
```

## Coding standards

- Type hints on public functions  
- Tests for pipeline/profile changes  
- Google-style docstrings  
- **No hardcoded file trees** in the pipeline — profiles own structure  

## Git workflow

- Gitflow-lite: `develop` integration, `main` releases  
- Feature branches: `feat/`, `fix/`, `docs/`, `chore/`  
- Conventional commits  

## Discovery

- Check `profiles/` before inventing new scaffold shapes  
- User docs: [docs/creating-a-profile.md](docs/creating-a-profile.md), [docs/related-projects.md](docs/related-projects.md)  
- Directives: [AI_DIRECTIVES.md](AI_DIRECTIVES.md) · [WORKFLOW.md](WORKFLOW.md) · [CONTEXT.md](CONTEXT.md)  
