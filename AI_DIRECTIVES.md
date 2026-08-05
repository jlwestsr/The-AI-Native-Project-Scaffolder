# AI Directives for Forge (The AI-Native Project Scaffolder)

These rules are critical for any AI agent "loading" this project. They encode the architectural standards, improved governance, and best practices for developing the Forge CLI.

## 1. Discovery-Driven Development
- **Ground Truth**: Before proposing any changes, you MUST check:
    -   `profiles/` for existing profile definitions, templates, and configs.
    -   `reference_shurtugal-lnx/`, `reference_gantry/`, etc., for the "Target State" of generated code.
- **Reference Awareness**: If the reference project implementation differs from our template, **the template is wrong**.
- **No Assumptions**: Do not implement features based on "general knowledge"; implement them based on the **Reference Projects**.

## 2. Profile-Driven Pipeline Architecture (v2)
Forge uses a **profile-driven pipeline** with clearly separated stages:
- **Data Models** (`models.py`):
    -   Pydantic models for profiles, rendered files, lock entries, and workspace config.
    -   Data structures only. **Minimize logic**.
- **Profile Loader** (`profile_loader.py`):
    -   Reads TOML configs (`profile.toml` + `structure.toml`) from `profiles/`.
    -   Resolves inheritance chains (child → parent → base).
    -   Returns `ResolvedProfile` with merged variables, files, directories, and conditionals.
- **Renderer** (`renderer.py`):
    -   Pure Jinja2 template rendering — **no I/O**.
    -   Returns `RenderedFile` objects in memory.
    -   Template lookup walks `template_dirs` child-first for inheritance.
- **Applier** (`applier.py`):
    -   Writes rendered files to disk with strategies: CREATE, UPDATE, FORCE.
    -   Respects lock file state for safe updates.
- **Pipeline** (`pipeline.py`):
    -   Orchestrates: load profile → merge inheritance → render → apply → write lock.
    -   **No Shadow Logic**: Do not hardcode file structures in the pipeline; read them from profiles.
- **Wizard** (`wizard.py` / `workspace_wizard.py`):
    -   Interactive prompts for profile variables and workspace configuration.
- **CLI** (`cli.py`):
    -   Typer entry point. Commands: `new`, `update`, `info`, `profiles`, `workspace`.
    -   **Current usage:** `forge new <path> -p base|fullstack|monorepo [--neo auto|on|off]`.
    -   Do **not** document legacy `forge .` or removed profiles (`openclaw-agent`,
        standalone `workspace` as a `forge new` profile).
    -   Post-hook: optional `neo init-workspace` via `--neo` / `FORGE_NEO_CMD` (`hooks.py`).
- **Defaults** (`defaults.py`):
    -   Fills missing wizard variables for `--no-interactive` runs.
- **Lock File** (`lockfile.py`):
    -   `.forge.lock` tracks managed files with content hashes for safe updates.
- **Ansible templates** (fullstack profile):
    -   Prefer Ansible-first, idempotent roles when generating host automation.

## 3. Testing & Quality Assurance
- **Venv**: Prefer project `.venv` (`source .venv/bin/activate` or `.venv/bin/python` / `.venv/bin/pytest`). Avoid system Python for installs.
- **Mandatory Unit Tests**: Changes to pipeline modules (`models`, `profile_loader`, `renderer`, `applier`, `pipeline`, `workspace`, `defaults`, `hooks`) need tests under `tests/`.
- **Pre-Commit Verification**: Run `./scripts/run_tests.sh` or `pytest -q` before marking work complete.
- **Public profiles**: Only `base`, `fullstack`, and `monorepo` ship for `forge new`.
- **Strict Linting**:
    -   **Python**: `flake8` (Zero errors).
    -   **Type Hints**: Mandatory for all new functions.

## 4. Development Workflow
- **Conventional Commits**: Use `feat:`, `fix:`, `docs:`, or `chore:` prefixes.
- **Git Tracking**:
    -   **NO DIRECT WORK ON MAIN/MASTER**.
    -   **Strict Local Branch Policy**: `feat`, `fix`, `docs`, and `chore` branches are **LOCAL ONLY**.
    -   Always merge `develop` into your feature branch before requesting a merge back.

## 5. Agentic Artifact Protocol
- **Task Tracking**: For complex tasks, maintain a `task.md` artifact to track progress.
- **Planning**: Before "Doing the Work" (Step 2 of Feature Workflow), create an `implementation_plan.md` for user approval.
- **Walkthrough**: Upon completion of significant features, create `walkthrough.md`.

## 6. Project Long-Term Memory
- **Mandate**: You are explicitly required to update `docs/AI_INSIGHTS.md` whenever you encounter a project-specific nuance, recurring pitfall, or architectural constraint.
- **Trigger**: If you find yourself thinking "I should remember this for next time" or "This was unexpected," you MUST document it in `docs/AI_INSIGHTS.md`.

