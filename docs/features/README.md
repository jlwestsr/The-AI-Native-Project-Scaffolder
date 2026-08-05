# Feature notes (historical)

Short records of past feature work. Prefer live docs for CLI/profile truth:

| Topic | Doc |
|-------|-----|
| Install & CLI | [../../README.md](../../README.md) |
| Docs index | [../README.md](../README.md) |
| Custom profiles | [../creating-a-profile.md](../creating-a-profile.md) |
| Shipped profiles | [../profiles.md](../profiles.md) |
| Forge vs neo | [../related-projects.md](../related-projects.md) |
| Monorepo profile | [../monorepo-profile-scope.md](../monorepo-profile-scope.md) |

## Shipped today

| Item | Value |
|------|--------|
| Profiles | **base**, **fullstack**, **monorepo** |
| CLI | `forge new <path> -p <profile> [--neo auto\|on\|off] [--neo-pack workspace]` |
| Ecosystem | `forge workspace` (separate from `forge new` profiles) |

Do not document retired one-shot generators or removed profile names as current.

## Index

| File | Topic |
|------|--------|
| [00_modular_scaffolder_refactor.md](./00_modular_scaffolder_refactor.md) | v2 pipeline (`src/forge/`) |
| [01_pre_commit_hooks.md](./01_pre_commit_hooks.md) | pre-commit in base/fullstack |
| [02_interactive_mode.md](./02_interactive_mode.md) | wizard / `--no-interactive` |
| [03_jinja2_templates.md](./03_jinja2_templates.md) | profile templates |
| [04_package_manager_support.md](./04_package_manager_support.md) | `manager` var (not `--manager`) |
| [05_global_configuration.md](./05_global_configuration.md) | defaults + `--var` |
| [06_doc_site_generator.md](./06_doc_site_generator.md) | mkdocs on fullstack |
| [07_project_profiles.md](./07_project_profiles.md) | base / fullstack / monorepo |
| [ai_insights_memory.md](./ai_insights_memory.md) | AI_INSIGHTS template |
| [bootstrap_script.md](./bootstrap_script.md) | editable / pipx install |
