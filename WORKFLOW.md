# Project Workflow for The-AI-Native-Project-Scaffolder

## Branching Strategy

We follow a strict **Gitflow-lite** workflow.

### Permanent Branches (Remote)
- **`main`**: Production-ready code.
- **`develop`**: Integration branch for the next release. **All work merges here.**

### Temporary Branches (Local Only)
**CRITICAL**: These branches exist **ONLY** on your local machine. Do **NOT** push them to origin unless working on a long-lived collaborative feature.

- **`feat/name`**: New features.
- **`fix/description`**: Bug fixes.
- **`docs/description`**: Documentation updates.
- **`chore/description`**: Maintenance, config, refactoring.

## Workflow Steps

1.  **Start**: Checkout `develop` and pull latest.
    ```bash
    git checkout develop
    git pull origin develop
    ```
2.  **Branch**: Create a specific local branch.
    ```bash
    git checkout -b feat/my-new-feature
    ```
3.  **Work**: Implement changes using **Conventional Commits**.
    ```bash
    git commit -m "feat: add new feature"
    ```
4.  **Verify**: Run tests to ensure stability.
    ```bash
    ./scripts/run_tests.sh
    ```
5.  **Merge**: Switch back to `develop` and merge.
    ```bash
    git checkout develop
    git merge feat/my-new-feature
    ```
6.  **Push**: Push **ONLY** `develop`.
    ```bash
    git push origin develop
    ```
7.  **Cleanup**: Delete the local branch.
    ```bash
    git branch -d feat/my-new-feature
    ```
