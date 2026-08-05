# Feature: Package manager selection

## Overview

Generated **base**/**fullstack** projects can prefer pip, poetry, or uv via the
`manager` profile variable (wizard or `--var manager=…`).

## Outcome (current)

Not a top-level CLI flag. Use profile variables:

```bash
forge new ~/projects/app -p base --no-interactive \
  --var project_name=app \
  --var manager=uv
```

| `manager` | Effect (via defaults + conditionals) |
|-----------|--------------------------------------|
| `pip` | `use_pip=true` → `requirements.txt` / `requirements-dev.txt` rendered |
| `poetry` / `uv` | `use_pip=false` → requirements files skipped; `pyproject.toml` still generated |

## Acceptance (met)

- [x] Variable-driven generation (no hard-coded manager in pipeline)
- [x] Conditionals in `structure.toml` control requirements files

## Notes

Default remains `pip` for broad compatibility.
