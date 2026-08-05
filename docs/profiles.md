# Shipped profiles

Public OSS ships **two** project profiles for `forge new`:

| Name | Inherits | Adds |
|------|----------|------|
| **base** | — | src/tests/docs, AGENTS.md, Claude hooks/skills, CI, workspace/scratchpad, agents/ |
| **fullstack** | base | notebooks, data/, models, ansible/, Docker, mkdocs |

```bash
forge profiles list
forge profiles show base
forge profiles show fullstack
```

## Compose with neo-harness

```bash
forge new ~/projects/app -p base --neo auto
# or
forge new ~/projects/app -p fullstack --neo on --neo-pack workspace
```

## Custom profiles

See **[creating-a-profile.md](./creating-a-profile.md)**.

## Ecosystem scaffolding (not a new-project profile)

`forge workspace` uses templates under `templates/workspace/` (multi-repo /
manifest style). That is separate from `forge new -p …`.
