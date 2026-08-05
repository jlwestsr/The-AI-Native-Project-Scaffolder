# Forge documentation

**Forge** scaffolds full AI-native project trees. It is not an agent runtime
(use [neo-harness](https://github.com/westailabs/neo-harness) for bounded jobs).

| Document | Audience |
|----------|----------|
| [../README.md](../README.md) | Install, `forge new`, neo hook |
| [**related-projects.md**](./related-projects.md) | **neo-harness** (runtime) vs Forge (scaffold) |
| [creating-a-profile.md](./creating-a-profile.md) | **Tutorial: write your own profile** |
| [profiles.md](./profiles.md) | Shipped `base` / `fullstack` |
| [**monorepo-profile-scope.md**](./monorepo-profile-scope.md) | **Proposed** third profile (west_ai_labs-shaped) |
| [reevaluation-2026-08.md](./reevaluation-2026-08.md) | Layout decisions, Forge vs neo |
| [features/](./features/) | Historical feature notes (may be stale) |
| [plans/archive/](./plans/archive/) | v2 design archive |

### neo-harness (runtime)

| Link | Topic |
|------|--------|
| [neo-harness README](https://github.com/westailabs/neo-harness#readme) | Install, providers, CLI |
| [starting-a-workspace](https://github.com/westailabs/neo-harness/blob/master/docs/starting-a-workspace.md) | Embed harness (with or without Forge) |
| [init-workspace](https://github.com/westailabs/neo-harness/blob/master/docs/init-workspace.md) | What the neo post-hook creates |

## Shipped profiles

| Profile | Role |
|---------|------|
| `base` | Foundation project (src, tests, docs, AGENTS, Claude hooks, CI) |
| `fullstack` | Extends `base` with notebooks, data/, Ansible, Docker |

## Quick commands

```bash
forge profiles list
forge profiles show base
forge new ~/projects/my-app -p base --no-interactive
forge new ~/projects/my-app -p fullstack --neo auto
```
