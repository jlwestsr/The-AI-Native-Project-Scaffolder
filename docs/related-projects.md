# Related projects

## neo-harness (agent runtime)

| | **nebulus-forge** (this repo) | **[neo-harness](https://github.com/westailabs/neo-harness)** |
|--|-------------------------------|--------------------------------------------------------------|
| **Job** | Project **scaffold**: docs, src/, AGENTS, CI, governance | Agent **runtime**: PLAN→ACT→REFLECT, Neo4j memory, policy, audit |
| **CLI** | `forge new`, `forge update`, `forge profiles` | `neo start`, `init-workspace`, `policy`, `audit` |
| **Creates** | Full tree: `docs/`, `workspace/scratchpad/`, hooks, tests, … | Thin embed: `jobs/`, `scripts/neo`, packs, `env.neo.example` |
| **Does not** | Run long agent loops or own Neo4j sessions | Generate full product skeletons |

### Compose them

```text
forge new ~/projects/app -p base|fullstack --neo auto
        │
        ├─► full project tree (this repo)
        └─► neo init-workspace (if neo installed)
                 │
                 ▼
           harness-ready repo → ./scripts/neo start …
```

```bash
# Scaffold only
forge new ~/projects/app -p base --neo off

# Scaffold + harness embed (default when neo is found)
forge new ~/projects/app -p fullstack --neo auto

# Require neo
export FORGE_NEO_CMD="$HOME/projects/neo-harness/.venv/bin/neo"
forge new ~/projects/app -p base --neo on
```

### neo-harness docs to read

| Link | Topic |
|------|--------|
| [neo-harness README](https://github.com/westailabs/neo-harness#readme) | Install, providers, CLI overview |
| [starting-a-workspace.md](https://github.com/westailabs/neo-harness/blob/master/docs/starting-a-workspace.md) | End-to-end embed (with or without Forge) |
| [init-workspace.md](https://github.com/westailabs/neo-harness/blob/master/docs/init-workspace.md) | What `neo init-workspace` creates |
| [policy.md](https://github.com/westailabs/neo-harness/blob/master/docs/policy.md) | report / propose / apply |
| [threat-model.md](https://github.com/westailabs/neo-harness/blob/master/docs/threat-model.md) | Operator vs model boundaries |

### Forge docs for neo users

| Doc | Topic |
|-----|--------|
| [creating-a-profile.md](./creating-a-profile.md) | Custom scaffold profiles |
| [profiles.md](./profiles.md) | Shipped `base` / `fullstack` |
| [reevaluation-2026-08.md](./reevaluation-2026-08.md) | Why the split exists |
