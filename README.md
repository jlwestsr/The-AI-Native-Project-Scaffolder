# ⚒️ Forge: The AI-Native Project Scaffolder

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![AI-Native](https://img.shields.io/badge/AI--Native-Collaboration-green.svg)](#ai-native-features)

**Forge** is a production-grade project generator designed specifically for modern AI engineering. It doesn't just create folders; it establishes an **AI Collaboration Framework** that ensures human-AI teams work within strict governance, shared context, and professional engineering standards.

---

## 🚀 Why Forge?

Traditional scaffolding tools (like Cookiecutter) focus on file organization. **Forge** focuses on **Agentic Governance**. It prepares your workspace to be understood and respected by AI tools (like Gemini Code Assist or Cursor) the moment you run the first commit.

### Core Philosophy
- **AI-Native Context**: Every project ships with `AI_DIRECTIVES.md`, `CLAUDE.md`, and `GEMINI.md` to ground your AI agent.
- **Strict Governance**: Prevent AI "shadow logic" and reinvention of existing utilities.
- **Production-Ready**: Enforces Type Hinting, Google-style docstrings, and 1000gic coverage in tests.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **Agentic Rules** | Dedicated `AI_DIRECTIVES.md` to define operational guardrails for AI agents. |
| **Universal Ansible** | Production-ready `ansible/` scaffold with `setup_workstation.yml` for instant environment bootstrapping. |
| **Strict Quality** | Enforced `pre-commit` hooks for `pytest`, `flake8`, `yamllint`, and `ansible-lint`. |
| **Git Flow Automation** | Initializes a repo with `main` and `develop` branches out of the box. |
| **Modular CI/CD** | Production-ready GitHub Actions for testing and linting. |
| **Feature Tracking** | Structured `docs/features/` system with a ready-to-use template. |
| **Standardized Layout** | Clean separation of `src/`, `data/`, `models/`, and `notebooks/`. |

[View full Changelog](CHANGELOG.md)

---

## 🛠️ Installation

### Option 1: Global Installation (Recommended)
The easiest way to use Forge globally is with `pipx`. This installs Forge in an isolated environment and makes the `forge` command available everywhere.

```bash
pipx install git+https://github.com/jlwestsr/nebulus-forge.git
```

### Option 2: Local Development Installation
If you want to contribute to Forge or customize the templates locally:

1. Clone the repository:
   ```bash
   git clone https://github.com/jlwestsr/nebulus-forge.git
   cd nebulus-forge
   ```

2. Create a virtual environment and install in editable mode:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

---

### Forge a New Project
Forge can be invoked as `forge` (via alias or pipx).

```bash
# Forge in the current directory
forge .

# Forge in a specific target directory
forge ~/projects/my-new-ai-model
```

### Update an Existing Project
Enable the "Update" feature to add missing standard files without overwriting your manual changes.

```bash
# Update existing project (safe, idempotent)
forge . --update --profile fullstack
```

---

## 📁 The Forge Structure

When you forge a project, you get a battle-tested structure:

```text
.
├── AI_DIRECTIVES.md       # Operational guardrails for AI
├── CLAUDE.md              # Persona & project instructions
├── GEMINI.md              # PM communication protocol
├── WORKFLOW.md            # Git & development process
├── data/                  # Git-ignored (raw/processed)
├── docs/
│   ├── feature_template.md # Standardized feature requirement format
│   └── features/          # Root for all feature documentation
├── src/                   # Production-grade Python modules
└── tests/                 # Unit & integration testing suite
```

---

## 📜 AI-Native Coding Standards

Forge projects enforce the following by default:
- **Type Hinting**: Mandatory for all function signatures.
- **Modular Logic**: Business logic lives in `src/`, never in notebooks.
- **Docstrings**: Google-style documentation for all public modules.
- **Automated Verification**: CI/CD pipeline integrated into every scaffold.

---

## 🤝 Contributing

We are building the future of AI-native engineering. If you have ideas for improving agentic governance or scaffolding templates, please:
1. Fork the repo.
2. Create a feature branch off `develop`.
3. Open a Pull Request.

---

## 📄 License

Iterate fast, governed safely. Forge is released under the [MIT License](LICENSE).

---
*Built with ❤️ by [JLWestSr](https://github.com/jlwestsr)*
