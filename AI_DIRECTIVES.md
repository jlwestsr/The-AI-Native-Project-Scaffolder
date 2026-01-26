# AI Directives for Forge (The AI-Native Project Scaffolder)

These rules are critical for any AI agent "loading" this project. They encode the architectural standards, improved governance, and best practices for developing the Forge CLI.

## 1. Discovery-Driven Development
- **Ground Truth**: Before proposing any changes, you MUST check:
    -   `src/project_generator/assets/` for existing templates/configs.
    -   `reference_shurtugal-lnx/`, `reference_gantry/`, etc., for the "Target State" of generated code.
- **Reference Awareness**: If the reference project implementation differs from our template, **the template is wrong**.
- **No Assumptions**: Do not implement features based on "general knowledge"; implement them based on the **Reference Projects**.

## 2. Scaffolding MVC Architecture
We follow a strict **Model-View-Controller** pattern for the CLI:
- **Model (`configs.py`)**:
    -   Holds the "Truth" of what a project looks like (Profiles, File Mappings).
    -   Data structures only. **Minimize logic**.
- **View (`templates/` & `wizard.py`)**:
    -   `wizard.py`: Handles interaction/prompts.
    -   `templates/`: Jinja2 templates. Keep logic minimal.
    -   **Ansible Templates**:
        -   Adhere to **Ansible-First** principles.
        -   `become: true` where needed.
        -   Idempotency checks/guards.
        -   Strict YAML formatting.
- **Controller (`engine.py` & `cli.py`)**:
    -   Orchestrates the flow.
    -   **No Shadow Logic**: Do not hardcode file structures in the engine; read them from the Model.

## 3. Testing & Quality Assurance
- **The VENV Mandate**: You generally CANNOT run `pip install` or `python` commands using the system interpreter. You **MUST** assume the virtual environment is active (`source venv/bin/activate`) or explicitly call `./venv/bin/python`.
- **Mandatory Unit Tests**: ALL changes to `engine.py` or `configs.py` must be verified in `tests/`.
- **Pre-Commit Verification**: Run `./scripts/run_tests.sh` before marking any task as complete.
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

