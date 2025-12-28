# New Project Generator: AI Engineering Edition

A specialized scaffolding tool designed to initialize production-grade AI engineering projects with industry-standard structure, governance, and development workflows.

## 🚀 Overview

This tool automates the creation of a modular, testable, and documented project environment specifically tailored for AI/ML development and AI-agent collaboration. It enforces strict coding standards, Git Flow branching, and integrates AI-specific operational rules.

## ✨ Key Features

- **Automated Scaffolding**: Generates a comprehensive folder structure (`data/`, `src/`, `tests/`, `docs/`, `notebooks/`).
- **AI Behavior Guardrails**: Includes a `rules/ai_behavior.md` file to govern how AI agents (like Aider or Gemini) should operate within the codebase.
- **Git Flow Ready**: Automatically initializes a Git repository with `main` and `develop` branches.
- **CI/CD Integration**: Pre-configured GitHub Actions for automated unit testing (`pytest`) and linting (`flake8`).
- **Standardized Documentation**: Includes feature templates and a requirements tracking system in `docs/features/`.
- **Developer Experience**: Pre-configured `.gitignore`, `pyproject.toml` (for Black & Pytest), and `.flake8` settings.

## 🛠️ Getting Started

### Prerequisites

- Python 3.10+
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/west_ai_labs/new-project-generator.git
   cd new-project-generator
   ```

2. Standard installation (pip):
   ```bash
   pip install -e .
   ```
   *Note: Using a virtual environment is highly recommended.*

### Usage

1. Create a new directory for your output project:
   ```bash
   mkdir my-new-ai-project
   cd my-new-ai-project
   ```

2. Run the generator using the `forge-project` command:
   ```bash
   forge-project .
   ```

Alternatively, you can run it without installation:
```bash
python -m project_generator.cli .
```

## 📁 Generated Project Structure

```text
.
├── CONTEXT.md             # Project-wide context for AI agents
├── README.md              # Project overview and getting started
├── data/                  # Raw and processed data (Git ignored)
├── docs/
│   ├── feature_template.md # Template for describing new features
│   └── features/          # Tracked feature documentation
├── models/                # Trained model artifacts (Git ignored)
├── notebooks/             # Experimental research and discovery
├── rules/
│   └── ai_behavior.md     # Governance for AI agent contributions
├── src/                   # Production source code
└── tests/                 # Unit and integration tests
├── .aider.conf.yml        # Pre-configured Aider behavior
```

## 📜 Coding Standards (Enforced)

The generated project expects:
- **Type Hinting**: Mandatory for all function definitions.
- **Unit Testing**: 100% logic coverage in the `tests/` directory.
- **Modular Code**: Business logic resides in `src/`, not notebooks.
- **Documentation**: Google-style docstrings for all public modules.

## 🏗️ Development of the Generator

To work on the generator itself:

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Linux/macOS
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Run the generator in development mode:
   ```bash
   pip install -e .
   ```

## 🤝 Contributing

Contributions to the generator are welcome! Please follow the Git Flow workflow and ensure any new scaffolding features are accompanied by updates to the `src/project_generator/assets/` modules and this README.

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.