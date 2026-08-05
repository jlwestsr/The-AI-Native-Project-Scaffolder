# Session notes: Forge re-eval, profile trim, monorepo, neo hook

**Date:** 2026-08-05  
**Repo:** nebulus-forge  
**Branch (work):** `feat/reeval-neo-hook`

## Decisions

1. **Forge vs neo-harness roles**
   - Forge = full project **scaffold** (docs, layout, governance).
   - neo-harness = agent **runtime** + thin `init-workspace` embed.
   - Compose: `forge new … --neo auto|on|off` → optional `neo init-workspace`.

2. **Public profiles trimmed to product surface**
   - **Ship:** `base`, `fullstack`, **`monorepo`**.
   - **Removed as `forge new` profiles:** `claude-governance` (merged into base), `openclaw-agent`, `workspace` (WAL/Overlord).
   - WAL ecosystem templates for `forge workspace` live under `templates/workspace/` (not a new-project profile).

3. **`monorepo` profile (implemented)** — modeled on `west_ai_labs`:
   - Buckets: `products/`, `services/`, `hosts/`, `lab/`, `docs/`, `workspace/`, `agents/`, `config/`, `scripts/`, `tests/`, `jobs/`.
   - **No** single-package root `src/<slug>/` (standalone; does not inherit `base`).
   - **example-app** stub under `products/example-app/`.
   - Default neo pack: **`workspace`**.
   - AGENTS: **generic** shared graph/RAG stub (probe before assert health).
   - `LAYOUT.md` + `config/workspace-layout.yaml` + `scripts/print_layout.py`.

4. **Install** — editable `pipx install -e` so `profiles/` resolve; `FORGE_PROFILES_DIR` supported.

5. **Docs**
   - Profile tutorial: `docs/creating-a-profile.md`
   - Cross-ref neo: `docs/related-projects.md`
   - Monorepo scope: `docs/monorepo-profile-scope.md` (status: implemented)

## How to check neo after `forge new --neo auto`

```bash
cd <project>
ls scripts/neo env.neo.example jobs/ agents/workspace/
./scripts/neo version providers policy agents
# .env must match running Neo4j host port + password
./scripts/neo init-db
./scripts/neo start --task-file jobs/smoke-mock.md --agent workspace -p mock
```

## Hand walkthrough (reference)

```bash
export PATH="$HOME/.local/bin:$PATH"
forge new ~/projects/forge-handtest -p base --no-interactive --neo auto
# or monorepo:
forge new ~/projects/eco-demo -p monorepo --no-interactive --neo auto --neo-pack workspace
```

## Related (neo-harness)

https://github.com/westailabs/neo-harness/blob/master/docs/related-projects.md  
https://github.com/westailabs/neo-harness/blob/master/docs/troubleshooting.md  
