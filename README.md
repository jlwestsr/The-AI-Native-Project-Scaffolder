# Forge — AI-native project scaffolder

**Forge** generates a full project skeleton (governance docs, layout, CI hooks)
for human–AI teams. It is **not** an agent runtime.

For bounded PLAN→ACT→REFLECT jobs and a thin harness embed, use
**[neo-harness](https://github.com/westailabs/neo-harness)** (`neo init-workspace`).

```text
forge new   →  project tree (docs, src, AGENTS, workspace/, …)
     └─(optional)→  neo init-workspace  →  jobs/, scripts/neo, packs
```

---

## Install (recommended for development)

Profiles live in this repo and are **not** fully packaged in the wheel. Prefer
an **editable** install:

```bash
git clone https://github.com/westailabs/nebulus-forge.git
cd nebulus-forge
pipx install --force --editable .
# ensure ~/.local/bin is on PATH
forge profiles list
```

Or:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

Optional: `export FORGE_PROFILES_DIR=/path/to/nebulus-forge/profiles`

---

## Quick start

```bash
# Interactive (wizard fills variables)
forge new ~/projects/my-app --profile fullstack

# Non-interactive (defaults applied for missing vars)
forge new ~/projects/my-app -p fullstack --no-interactive \
  --var project_name=my-app

# Skip neo-harness embed
forge new ~/projects/my-app -p fullstack --neo off

# Require neo embed (fails if neo not installed)
forge new ~/projects/my-app -p fullstack --neo on
```

After scaffold, if neo ran: copy `env.neo.example` → `.env`, set Neo4j password,
then `./scripts/neo start --task-file jobs/smoke-mock.md -p mock`.

---

## Commands

| Command | Purpose |
|---------|---------|
| `forge new <path>` | Create project from profile |
| `forge update [path]` | Refresh managed files from lock |
| `forge info` | Project / lock info |
| `forge profiles list` | List profiles |
| `forge workspace …` | Ecosystem workspace helpers |

### `forge new` options

| Option | Default | Meaning |
|--------|---------|---------|
| `-p / --profile` | `fullstack` | Profile name |
| `--no-interactive` | off | Use defaults + `--var` only |
| `--var key=value` | — | Template variables |
| `--neo` | `auto` | `auto` / `on` / `off` — post-hook neo init-workspace |
| `--neo-pack` | `workspace` | Pack id for neo |
| `--force` | off | Overwrite files |
| `--dry-run` | off | Render only |

---

## Profiles

| Profile | Role |
|---------|------|
| `base` | Foundation: src/tests/docs, AGENTS.md, governance, CI |
| `claude-governance` | Claude hooks/skills layer (inherited) |
| `fullstack` | base + notebooks/data/ansible/docker extras |
| `openclaw-agent` | Agent identity / OpenClaw-oriented layout |
| `workspace` | West AI Labs ecosystem workspace files |

See [docs/reevaluation-2026-08.md](docs/reevaluation-2026-08.md) for layout rationale.

---

## What a forged tree looks like (base + typical)

```text
my-app/
├── AGENTS.md, CLAUDE.md, GEMINI.md, AI_DIRECTIVES.md, WORKFLOW.md, CONTEXT.md
├── src/<slug>/
├── tests/
├── docs/features/  docs/ops/
├── workspace/scratchpad/
├── agents/                 # free-form / neo packs
├── scripts/
├── .github/workflows/
└── … pre-commit, pyproject, etc.

# If neo hook ran:
├── jobs/smoke-mock.md
├── scripts/neo
├── env.neo.example
└── agents/workspace/       # neo pack
```

---

## neo-harness integration

| Env | Purpose |
|-----|---------|
| `FORGE_NEO_CMD` | Override neo binary (e.g. `/path/to/.venv/bin/neo`) |
| `FORGE_PROFILES_DIR` | Override profiles root |

Lab paths are also probed: `~/projects/neo-harness/.venv/bin/neo`,
`~/projects/west_ai_labs/.venv-neo/bin/neo`.

---

## License

MIT — see [LICENSE](LICENSE).
