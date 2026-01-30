# Feature: Bootstrap Script

## 1. Overview
**Branch**: `feat/bootstrap-script`

A self-contained `scripts/bootstrap.sh` script to set up the Forge development environment on macOS and Linux. It ensures `forge` is accessible in the system PATH and manages the Python environment.

## 2. Requirements
- [ ] **Cross-Platform**: Run on macOS and Linux (Ubuntu/Debian).
- [ ] **Environment**: Create a Python 3 `venv` in the project root.
- [ ] **Dependencies**: Install `requirements.txt` and `requirements-dev.txt`.
- [ ] **Installation**: Install the package in editable mode (`pip install -e .`).
- [ ] **Path Registration**: Symlink or place the `forge` executable in the OS PATH (e.g., `~/.local/bin` or `/usr/local/bin`).
- [ ] **Naming**: Rename/Alias the CLI entry point to `forge` (currently `forge-project`).

## 3. Technical Implementation
- **Script**: `scripts/bootstrap.sh`
- **Configuration**: Update `pyproject.toml` to define `forge` script entry point.
- **Logic**:
    1. Check Python version.
    2. Create `venv`.
    3. Install deps.
    4. Install `forge` (editable).
    5. Symlink to `~/.local/bin` (creating if missing) or `/usr/local/bin` (prompting for sudo if needed).

## 4. Verification Plan
**Automated Tests**:
- [ ] Script runs without error on the user's machine.
- [ ] `forge --version` / `forge --help` works from a new terminal session (or after source).

**Manual Verification**:
- [ ] Run `./scripts/bootstrap.sh`.
- [ ] Check `which forge`.
