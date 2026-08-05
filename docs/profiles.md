# Shipped profiles

Public OSS ships **three** project profiles for `forge new`:

| Name | Inherits | Adds |
|------|----------|------|
| **base** | — | src/tests/docs, AGENTS.md, Claude hooks/skills, CI, workspace/scratchpad, agents/ |
| **fullstack** | base | notebooks, data/, models, ansible/, Docker, mkdocs |
| **monorepo** | — (standalone) | products/services/hosts/lab control plane; LAYOUT; example-app; no root `src/<pkg>` |

Design notes: [monorepo-profile-scope.md](./monorepo-profile-scope.md).

```bash
forge profiles list
forge profiles show base
forge profiles show fullstack
forge profiles show monorepo
```

## Compose with neo-harness

Default neo pack: **`workspace`**.

```bash
forge new ~/projects/app -p base --neo auto --neo-pack workspace
forge new ~/projects/app -p fullstack --neo auto --neo-pack workspace
forge new ~/projects/eco -p monorepo --neo auto --neo-pack workspace
```

## Custom profiles

See **[creating-a-profile.md](./creating-a-profile.md)**.

## Ecosystem scaffolding (not a new-project profile)

`forge workspace` uses templates under `templates/workspace/` (multi-repo /
manifest style). That is separate from `forge new -p …`.
