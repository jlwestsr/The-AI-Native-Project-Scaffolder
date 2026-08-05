# Feature: Defaults and configuration

## Overview

Users should not re-type the same author/license defaults every run.

## Outcome (current)

| Mechanism | Role |
|-----------|------|
| Profile `default` in `profile.toml` | Wizard + non-interactive defaults |
| `src/forge/defaults.py` | Fills missing vars (`project_name` from target dir, `use_pip`, slug, …) |
| CLI `--var key=value` | Highest precedence for a run |
| `FORGE_PROFILES_DIR` / `FORGE_NEO_CMD` | Env overrides for profiles path and neo binary |

```bash
forge new ~/projects/app -p base --no-interactive --var author_name="Jane Doe"
```

## Acceptance (met)

- [x] Non-interactive runs succeed with target-dir project name when unset
- [x] Explicit `--var` overrides defaults

## Notes

A dedicated `forge config` subcommand is **not** the current primary UX; prefer
profile defaults and `--var`. Historical designs mentioned `~/.config/forge/` —
treat as optional future work unless reintroduced with tests.
