# Feature: Developer bootstrap

## Overview

Make the `forge` CLI available for local development of this repository.

## Outcome (current)

Recommended install (profiles resolve correctly):

```bash
cd /path/to/nebulus-forge
pipx install --force --editable .
# or
python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
```

Ensure `~/.local/bin` is on `PATH` for pipx.

Optional: `scripts/` may contain helpers; primary documented path is pipx/venv
editable install per [README.md](../../README.md).

## Acceptance

- [x] `forge --help` / `forge profiles list` work after editable install
- [x] Profiles load from repo `profiles/` tree
