# Feature: Interactive wizard

## Overview

`forge new` can collect profile variables interactively (questionary) when not
using `--no-interactive` and when `--var` is not fully supplied.

## Outcome (current)

| Piece | Location |
|-------|----------|
| Project wizard | `src/forge/wizard.py` |
| Defaults for non-interactive | `src/forge/defaults.py` |
| Workspace wizard | `src/forge/workspace_wizard.py` |

```bash
# Interactive (wizard)
forge new ~/projects/app -p fullstack

# Non-interactive
forge new ~/projects/app -p fullstack --no-interactive --var project_name=app
```

## Acceptance (met)

- [x] Wizard builds prompts from profile `VariableSpec`s
- [x] `--no-interactive` + defaults + `--var` works for scripting
