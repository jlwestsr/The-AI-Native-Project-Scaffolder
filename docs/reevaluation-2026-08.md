# Forge re-evaluation (2026-08)

**Context:** Forge had been unused for months; neo-harness owns bounded agent
jobs and thin workspace embed. This note records what is stale, what we keep,
and how the tools compose.

## Roles (locked)

| Tool | Responsibility |
|------|----------------|
| **Forge** | Full project / ecosystem **scaffold** (docs, governance, layout, CI) |
| **neo-harness** | **Runtime** for PLAN→ACT→REFLECT + thin `init-workspace` embed |

Pipeline:

```text
forge new ~/projects/app -p fullstack [--neo auto]
        │
        ▼
  project tree (docs, src, AGENTS, workspace/, …)
        │
        └─ post-hook (if neo installed) → neo init-workspace
                 │
                 ▼
           agents/workspace, jobs/, scripts/neo, env.neo.example
```

## Template / layout findings

| Area | Status | Action |
|------|--------|--------|
| `base` governance files (CLAUDE, GEMINI, AI_DIRECTIVES) | Still useful | Keep; add **AGENTS.md** |
| `docs/` + `docs/features/` | Still useful | Keep; add **docs/ops/** |
| Missing disposable surface | Stale vs monorepo practice | Add **workspace/scratchpad/** |
| ML dirs on every fullstack project | Often unused | Keep on `fullstack` only; document lean profiles later |
| `openclaw-agent` | Lab / OpenClaw-specific | **Removed** from public profiles |
| `workspace` profile (OVERLORD, BUSINESS) | WAL-specific | **Removed** as `forge new` profile; `forge workspace` uses `templates/workspace/` |
| `claude-governance` standalone | Mid-layer only | **Merged into `base`** |
| README `forge .` | Stale | Document **`forge new`** |
| Non-interactive missing defaults | Bug | **apply_variable_defaults** |
| Profiles not in wheel | Packaging gap | Editable install + `FORGE_PROFILES_DIR` |

### Public profile set (2026-08)

**`base`** and **`fullstack`** only (`fullstack` inherits `base`).

## Directory model (target)

**Always (base):**

```text
src/<slug>/  tests/  docs/{features,ops}/  scripts/
workspace/scratchpad/  agents/
AGENTS.md  CLAUDE.md  GEMINI.md  AI_DIRECTIVES.md  WORKFLOW.md  CONTEXT.md
.github/workflows/  .pre-commit-config.yaml  …
```

**Optional (fullstack / etc.):** notebooks, models, data/, ansible/, docker.

**From neo (post-hook, if present):** `jobs/`, `scripts/neo`, `env.neo.example`,
`requirements-neo.txt`, pack under `agents/<pack>/`.

## neo hook

- CLI: `--neo auto|on|off` (default **auto**)
- Resolves `neo` via PATH, `FORGE_NEO_CMD`, or lab paths
- Calls `neo init-workspace --pack workspace`
- Does **not** reimplement neo; skip with message if missing

## Follow-ups (not this change)

- Lean `app` profile without ML dirs
- Ship profiles inside the package wheel for non-editable pipx
- Archive or rewrite OVERLORD-centric workspace profile for public consumers
