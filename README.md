# ⚒️ Forge: The AI-Native Project Scaffolder

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![AI-Native](https://img.shields.io/badge/AI--Native-Collaboration-green.svg)](#ai-native-features)

**Forge** is a production-grade project generator designed specifically for modern AI engineering. It doesn't just create folders; it establishes an **AI Collaboration Framework** that ensures human-AI teams work within strict governance, shared context, and professional engineering standards.

---

## 🚀 Why Forge?

Traditional scaffolding tools (like Cookiecutter) focus on file organization. **Forge** focuses on **Agentic Governance**. It prepares your workspace to be understood and respected by AI tools (like Aider, Gemini Code Assist, or Cursor) the moment you run the first commit.

### Core Philosophy
- **AI-Native Context**: Every project ships with `CONTEXT.md` and `rules/ai_behavior.md` to ground your AI agent.
- **Strict Governance**: Prevent AI "shadow logic" and reinvention of existing utilities.
- **Production-Ready**: Enforces Type Hinting, Google-style docstrings, and 100% logic coverage in tests.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **Agentic Rules** | Dedicated `rules/ai_behavior.md` to define operational guardrails for AI agents. |
| **Universal Ansible** | Production-ready `ansible/` scaffold with `setup_workstation.yml` for instant environment bootstrapping. |
| **Strict Quality** | Enforced `pre-commit` hooks for `pytest`, `flake8`, `yamllint`, and `ansible-lint`. |
| **Aider Integration** | Pre-configured `.aider.conf.yml` forces auto-reading of context and rules. |
| **Git Flow Automation** | Initializes a repo with `main` and `develop` branches out of the box. |
| **Modular CI/CD** | Production-ready GitHub Actions for testing and linting. |
| **Feature Tracking** | Structured `docs/features/` system with a ready-to-use template. |
| **Standardized Layout** | Clean separation of `src/`, `data/`, `models/`, and `notebooks/`. |
| **MVC Architecture** | Web profile enforces `models/routers/services` pattern for clear separation of concerns. |

[View full Changelog](CHANGELOG.md)

---

## 🛠️ Installation

### Option 1: Global Installation (Recommended)
The easiest way to use Forge globally is with `pipx`. This installs Forge in an isolated environment and makes the `forge` command available everywhere.

```bash
# Install pipx if you haven't already
# brew install pipx (macOS) or sudo apt install pipx (Linux)
pipx ensurepath

# Install Forge directly from GitHub
pipx install git+https://github.com/jlwestsr/The-AI-Native-Project-Scaffolder.git
```

### Option 2: Local Development Installation
If you want to contribute to Forge or customize the templates locally:

1. Clone the repository:
   ```bash
   git clone https://github.com/jlwestsr/The-AI-Native-Project-Scaffolder.git
   cd forge-scaffolder
   ```

2. Create a virtual environment and install in editable mode:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

3. (Optional) Create a global alias for quick access:
   Add this to your `~/.zshrc` or `~/.bashrc`:
   ```bash
   alias forge="$(pwd)/.venv/bin/forge-project"
   ```

---

### Forge a New Project
Forge can be invoked as `forge-project` or via your `forge` alias (recommended).

```bash
# Forge in the current directory
forge .

# Forge in a specific target directory
forge ~/projects/my-new-ai-model
```

### Update an Existing Project
Enable the "Update" feature to add missing standard files (like `Dockerfile` or `rules/ai_behavior.md`) without overwriting your manual changes.

```bash
# Update existing project (safe, idempotent)
forge . --update
```

### How to use with AI Agents
1. **Define Features**: Use `docs/feature_template.md` to describe your feature.
2. **Review Rules**: Ensure `rules/ai_behavior.md` matches your team's specific requirements.
3. **Collaborate**: Launch Aider/Cursor. The pre-configured context will ensure the agent respects your architecture from the first prompt.

---

## 📁 The Forge Structure

When you forge a project, you get a battle-tested structure:

```text
.
├── CONTEXT.md             # High-level architecture & standards for AI
├── README.md              # Auto-generated project overview
├── data/                  # Git-ignored (raw/processed)
├── docs/
│   ├── feature_template.md # Standardized feature requirement format
│   └── features/          # Root for all feature documentation
├── models/                # Git-ignored model artifacts & checkpoints
├── notebooks/             # Research, discovery, and prototyping
├── rules/
│   └── ai_behavior.md     # MANDATORY rules for AI agent operation
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

## ❓ Troubleshooting

### Fix "Bad Interpreter" or Broken Environment
If you move or rename your project folder, the virtual environment paths will break, causing errors like `bad interpreter: .../old-path/.venv/bin/python: no such file or directory`.

**Solution:**
Recreate the virtual environment in the new location:

```bash
# Remove the old environment
rm -rf .venv

# Create a new one
python3 -m venv .venv
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
pip install -e .
```

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