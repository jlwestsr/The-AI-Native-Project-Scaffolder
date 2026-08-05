# Forge documentation

**Forge** scaffolds full AI-native project trees. It is not an agent runtime
(use [neo-harness](https://github.com/westailabs/neo-harness) for bounded jobs).

| Document | Audience |
|----------|----------|
| [../README.md](../README.md) | Install, `forge new`, neo hook |
| [creating-a-profile.md](./creating-a-profile.md) | **Tutorial: write your own profile** |
| [reevaluation-2026-08.md](./reevaluation-2026-08.md) | Layout decisions, Forge vs neo |
| [features/](./features/) | Historical feature notes (may be stale) |
| [plans/archive/](./plans/archive/) | v2 design archive |

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
