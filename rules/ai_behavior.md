# AI Agent Behavior & Operational Rules

This document outlines the specific operational standards and behavioral expectations for AI agents working on this project.

## 1. Operational Guardrails
- **Pre-Commit Verification**: Before marking any task as complete, the agent MUST run `pytest` and ensure all tests pass.
- **Linting Compliance**: All code must pass `flake8` checks. If new code introduces linting errors, the agent must fix them immediately.
- **No Shadow Logic**: Do not implement business logic that isn't requested in requirements. If a logic choice is ambiguous, use `notify_user` to clarify.

## 2. Research & Discovery
- **Codebase Awareness**: Before creating a new utility function or module, the agent MUST search `src/` to check for existing implementations.
- **Dependency Check**: Before adding new libraries to `requirements.txt`, the agent must verify if the functionality is already provided by existing dependencies (numpy, pandas, etc.).

## 3. Communication Standards
- **Task Transparency**: Use `TaskSummary` to explain the *why* behind technical decisions, not just the *what*.
- **Plan Approval**: For any change affecting more than 2 files or introducing new architecture, an `implementation_plan.md` must be created and approved via `notify_user`.

## 4. Coding Style (AI-Specific)
- **Type Hinting**: Mandatory for all new functions. Proactively add hints to existing code when modified.
- **Docstring Standard**: Use Google Style docstrings. Include "Args", "Returns", and "Raises" sections where applicable.
- **Refactoring**: When editing a file, small improvements to readability or standards (like removing unused imports) in that file are encouraged.

## 5. Tool Usage
- **Terminal Execution**: Use the terminal to verify file existence and state before making assumptions.
- **Browser Research**: Use the browser tool to look up documentation for specific library versions used in the project.