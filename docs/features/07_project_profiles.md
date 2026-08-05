# Feature: Project profiles

## Overview

Profiles select scaffold shape at generation time via TOML + Jinja2, not
hardcoded Python trees.

## Outcome (current)

**Shipped `forge new` profiles:**

| Profile | Inherits | Shape |
|---------|----------|--------|
| `base` | — | Single package `src/<slug>/` + governance |
| `fullstack` | base | + notebooks, data, ansible, docker |
| `monorepo` | — | products/services/hosts/lab control plane |

```bash
forge profiles list
forge profiles show monorepo
forge new ~/projects/eco -p monorepo --no-interactive --neo auto --neo-pack workspace
forge new ~/projects/app -p base --no-interactive
forge new ~/projects/app -p fullstack --no-interactive
```

Implementation: `profiles/<name>/{profile.toml,structure.toml,templates/}`,
loaded by `profile_loader.py`, documented in [creating-a-profile.md](../creating-a-profile.md).

## Acceptance (met)

- [x] `-p` / `--profile` selects profile
- [x] Inheritance merges variables, files, directories
- [x] `forge profiles list` / `show`
- [x] Custom profiles supported under `profiles/` or `FORGE_PROFILES_DIR`
