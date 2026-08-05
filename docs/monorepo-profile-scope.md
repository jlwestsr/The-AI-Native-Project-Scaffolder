# Scope: Forge `monorepo` profile

**Status:** Implemented (v1)  
**Model:** `~/projects/west_ai_labs` layout (control-plane monorepo)  
**Date:** 2026-08-05  
**Decisions:** example product stub **yes**; neo pack **`workspace`**; shared services language **generic stub** in AGENTS.md.

## 1. Why a third profile?

| Profile | Shape | Use when |
|---------|--------|----------|
| **base** | Single Python package under `src/<slug>/` | Libraries, CLIs, small apps |
| **fullstack** | base + ML/data/ansible/docker extras | Data/ML product in one package tree |
| **monorepo** (proposed) | Multi-bucket root, **no** single `src/<slug>` app | Ecosystem / platform control plane like west_ai_labs |

west_ai_labs is **not** a single-package repo. Scaffolding it with `base` creates the wrong spine (`src/forge_handtest/`). Operators need buckets: products, services, hosts, lab, docs, workspace.

## 2. Goals

1. `forge new ~/projects/my-ecosystem -p monorepo` produces a **thin-root monorepo** AI agents can navigate.
2. Encode **where things live** (`LAYOUT.md` + `config/workspace-layout.yaml`) so agents don’t invent top-level dirs.
3. Ship **governance stubs** (AGENTS, CLAUDE, WORKFLOW, BUSINESS) without WAL proprietary content.
4. Compose cleanly with **neo-harness** (`--neo auto`, pack default e.g. `platform` or `workspace`).
5. Stay **OSS-safe** — no Overlord, no personal hostnames, no private product names required.

## 3. Non-goals (v1)

| Out of scope | Why |
|--------------|-----|
| Nested git product clones | Operator adds real products later |
| Full session-init CLI / shared-rag wiring | Org-specific; optional later profile or scripts |
| Ansible golden images | Live under `hosts/<name>/` when needed |
| Copy of west_ai_labs docs vault | Too large; scaffold empty taxonomy + README only |
| Replacing `forge workspace` | Multi-repo ecosystem lock stays separate |

## 4. Inheritance decision

**Do not inherit `base` as-is.**  
`base` always unions `src/{{ project_slug }}` and package-centric files. That fights monorepo shape.

| Option | Pros | Cons |
|--------|------|------|
| **A. Standalone monorepo** (no inherits) | Clean tree | Duplicate governance templates |
| **B. Split `base` → `governance` + `python-pkg`** | DRY long-term | Larger refactor |
| **C. Inherit base + empty product dirs** | Fast | Wrong `src/` at root forever |

**Recommendation for v1:** **Option A** — standalone profile with its own templates (copy/adapt from base governance files).  
**v2:** extract shared governance into a non-listed `governance` parent (optional).

## 5. Target tree (v1 scaffold)

Generic names; `{{ monorepo_name }}` / `{{ project_name }}` for titles.

```text
{{ monorepo_name }}/
├── LAYOUT.md                 # orientation (first file AI should read)
├── README.md
├── AGENTS.md                 # AI bootstrap + monorepo rules
├── CLAUDE.md                 # coding + git + IaC policy stubs
├── GEMINI.md                 # optional short PM notes
├── BUSINESS.md               # tech stack / constraints stubs
├── WORKFLOW.md               # Gitflow-lite
├── .gitignore
├── .github/workflows/        # lightweight CI (hygiene / layout check)
│
├── config/
│   └── workspace-layout.yaml # bucket registry (SoT for paths)
│
├── products/                 # SHIPS — product code
│   └── .gitkeep + README.md
├── services/                 # SHIPS — platform services
│   └── .gitkeep + README.md
├── hosts/                    # IaC (appliance / workstation)
│   └── .gitkeep + README.md
├── lab/                      # NOT product — experiments, forks
│   └── README.md
│
├── docs/
│   ├── README.md             # vault map
│   ├── architecture/
│   ├── decisions/            # ADR template
│   ├── ops/
│   ├── product/
│   └── research/
│
├── workspace/
│   └── scratchpad/           # disposable only
│
├── agents/
│   └── README.md             # free-form role profiles live here
│
├── scripts/
│   ├── print_layout.py       # minimal: print buckets from yaml
│   └── README.md
│
├── tests/                    # monorepo-level tests (layout smoke)
│   └── test_layout.py
│
└── jobs/                     # neo task briefs (if neo hook)
    └── (from neo init-workspace)
```

**Explicitly absent at root (vs base):**  
`src/<package>/`, `requirements.txt` as primary app deps, notebooks/, models/, data/.

## 6. Files to generate (content principles)

| File | Content intent |
|------|----------------|
| `LAYOUT.md` | 30-second map + “where do I put X?” table (generic buckets) |
| `config/workspace-layout.yaml` | `buckets:` map + empty `trees: {}` or example entries |
| `AGENTS.md` | Open order: LAYOUT → AGENTS → CLAUDE; no invent top-level dirs; neo section |
| `CLAUDE.md` | Gitflow-lite, conventional commits, IaC via hosts/, graph-first *stub* (optional) |
| `BUSINESS.md` | Placeholder vision/constraints table |
| `WORKFLOW.md` | develop/main, local feature branches |
| `docs/**/README.md` | One-liners for each vault area |
| `scripts/print_layout.py` | Read yaml, print buckets (stdlib only) |
| `tests/test_layout.py` | Assert required top-level dirs exist |

Keep templates **generic** (`Your Org`, `products/`, not `nebulus-gantry`).

## 7. Variables (`profile.toml`)

| Variable | Type | Default | Purpose |
|----------|------|---------|---------|
| `project_name` / monorepo title | string | target dir name | Titles in docs |
| `org_name` | string | `"My Org"` | AGENTS/CLAUDE branding |
| `include_hosts_bucket` | confirm | true | Optionally omit `hosts/` |
| `include_lab_bucket` | confirm | true | Optionally omit `lab/` |
| `default_integration_branch` | choice | `develop` | WORKFLOW.md |
| `python_version` | choice | `3.12` | Tooling notes only |

Derived: `project_slug` for any nested example paths.

## 8. neo-harness composition

| Setting | Recommendation |
|---------|----------------|
| Default `--neo-pack` when profile is monorepo | `platform` if we add a monorepo-oriented pack name, else `workspace` |
| `NEO_PROVIDER_CWD` | Monorepo root |
| Session-init | **Not** scaffolded in v1 (org-specific); document as optional follow-on |

Post-hook already runs `neo init-workspace`. Monorepo profile should document:

```bash
forge new ~/projects/eco -p monorepo --neo auto --neo-pack workspace
```

Optional later: monorepo-specific neo pack template under `agents/platform/` in the profile (or rely on neo’s pack only).

## 9. Comparison to west_ai_labs (mapping)

| west_ai_labs | monorepo profile v1 |
|--------------|---------------------|
| `LAYOUT.md` | Yes (generic) |
| `config/workspace-layout.yaml` | Yes (minimal) |
| `products/`, `services/`, `hosts/`, `lab/` | Yes (empty + README) |
| `docs/` vault | Taxonomy stubs, not full vault |
| `agents/*-agent/` roles | `agents/README` only |
| `scripts/session_cli`, path_registry | **Out** of v1 (or stub print_layout only) |
| `services/shared-rag` real code | **Out** — empty services/ |
| Product boundary doc | Link pattern in LAYOUT only |
| Obsidian | **Out** |

## 10. Implementation plan (when approved)

| Step | Work |
|------|------|
| 1 | Add `profiles/monorepo/{profile.toml,structure.toml,templates/…}` |
| 2 | Templates for LAYOUT, AGENTS, CLAUDE, WORKFLOW, BUSINESS, config yaml, READMEs |
| 3 | `scripts/print_layout.py.j2` + `tests/test_layout.py.j2` |
| 4 | Update `docs/profiles.md`, `creating-a-profile.md` chain diagram, README |
| 5 | pytest: profile loads, dry-run creates expected dirs, no `src/` package root |
| 6 | Manual: `forge new /tmp/eco -p monorepo --no-interactive --neo off` |

**Estimate:** ~0.5–1 day for v1 skeleton + tests.

## 11. Open questions

1. **Default profile for `forge new`?** Keep `fullstack` or switch monorepo users to explicit `-p monorepo` only (recommended: keep fullstack default).  
2. **Nested product stubs?** e.g. `products/example-app/README.md` — helpful or noise?  
3. **Include CODEX.md / multi-worker matrix?** WAL-specific; optional variable.  
4. **Graph/RAG stubs in AGENTS?** Generic “validate shared services if configured” vs omit.  

## 12. Success criteria

- [x] `forge profiles list` shows `base`, `fullstack`, `monorepo`  
- [x] Generated tree has products/services/hosts/lab/docs/workspace/agents/config/scripts  
- [x] **No** root `src/<slug>` application package  
- [x] LAYOUT + workspace-layout.yaml present and consistent  
- [x] `python3 scripts/print_layout.py` runs without deps  
- [x] example-app stub under products/  
- [x] AGENTS generic shared-services stub  
- [ ] `forge new … --neo auto` verified in CI/manual  
- [x] Docs updated (profiles.md, this scope)

## 13. Related

- Reference layout: `west_ai_labs/LAYOUT.md`, `config/workspace-layout.yaml`  
- [creating-a-profile.md](./creating-a-profile.md)  
- [related-projects.md](./related-projects.md)  
- [neo-harness starting-a-workspace](https://github.com/westailabs/neo-harness/blob/master/docs/starting-a-workspace.md)  
