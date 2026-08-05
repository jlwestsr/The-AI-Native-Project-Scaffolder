# Project Context & Coding Standards

## 1. Project Overview

**Forge** is a production-grade **project scaffolder** for AI engineering. It
generates opinionated project trees (profiles + Jinja2 templates). It is **not**
an agent runtime — use [neo-harness](https://github.com/westailabs/neo-harness)
for PLAN→ACT→REFLECT jobs.

## 2. Mandatory AI rules

Before proposing changes, follow **[AI_DIRECTIVES.md](AI_DIRECTIVES.md)**.

Key constraints:

- Prefer discovery from `profiles/` and tests over inventing structure
- Run tests before claiming done (`./scripts/run_tests.sh` or `pytest`)
- Gitflow-lite: feature branches → `develop` → `main`

## 3. Recommended AI personas

### Scaffolding Architect

- Profile TOML + Jinja2 under `profiles/`
- Keep public profiles OSS-safe (`base`, `fullstack`, `monorepo`)

### Python Tool Developer

- Logic in `src/forge/`
- Tests in `tests/`
- Dependencies in `pyproject.toml`

### Release / Docs

- `README.md`, `docs/`
- Cross-links to neo-harness stay accurate

## 4. Project map

| Path | Purpose |
|------|---------|
| `profiles/` | Shipped profiles: **base**, **fullstack**, **monorepo** |
| `templates/workspace/` | Templates for `forge workspace` (not a `forge new` profile) |
| `src/forge/` | CLI, pipeline, renderer, wizard, neo hook |
| `tests/` | Pytest suite |
| `docs/` | User + design docs — start at [docs/README.md](docs/README.md) |
| `scripts/` | Test runners / utilities |

## 5. CLI reference (current)

```bash
forge new <path> -p base|fullstack|monorepo [--no-interactive] [--var k=v] [--neo auto|on|off] [--neo-pack workspace]
forge update [path]
forge info [path]
forge profiles list
forge profiles show <name>
forge workspace init|sync|info
```

| Flag | Notes |
|------|--------|
| `-p / --profile` | Default `fullstack` |
| `--neo` | Post-hook: `neo init-workspace` if neo found (`auto` default) |
| `--neo-pack` | Default `workspace` |
| `--no-interactive` | Uses profile defaults + `--var` |

Install: **editable** recommended so profiles resolve:

```bash
pipx install --force --editable .
# or FORGE_PROFILES_DIR=/path/to/nebulus-forge/profiles
```

Docs: [creating-a-profile.md](docs/creating-a-profile.md) ·
[related-projects.md](docs/related-projects.md) ·
[monorepo-profile-scope.md](docs/monorepo-profile-scope.md)

## 6. Coding standards

1. Unit tests for pipeline/profile behavior changes  
2. Type hints on public functions  
3. Google-style docstrings  
4. **No shadow logic** — file trees live in profiles, not hardcoded in the pipeline  

## 7. Git workflow

1. Gitflow-lite (`develop` integration, `main` release)  
2. No direct commits to `main` without process  
3. Feature branches preferred  

## 8. Repo layout (this project)

- `src/forge/` — package source  
- `profiles/` — scaffold definitions  
- `tests/` — unit tests  
- `docs/` — documentation  
- `templates/workspace/` — `forge workspace` only  

Optional local `reference_*/` trees (if present) are read-only comparison targets; they are **not** required for Forge to run.
