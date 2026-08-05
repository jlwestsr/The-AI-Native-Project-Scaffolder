# Documentation review — 2026-08-05

## Purpose

Audit root and `docs/` against the live CLI and shipped profiles; remove or
quarantine stale guidance.

## Current product truth (at review)

| Item | Truth |
|------|--------|
| CLI | `forge new \| update \| info \| profiles \| workspace` |
| Create project | `forge new <path> -p …` (**not** `forge .`) |
| Profiles | `base`, `fullstack`, `monorepo` only |
| neo-harness | Optional post-hook `--neo auto\|on\|off`, pack default `workspace` |
| Install | Editable install or `FORGE_PROFILES_DIR` for profiles |
| Remote | Public GitHub `westailabs/nebulus-forge` |

## Stale items found and actions

| Location | Issue | Action |
|----------|--------|--------|
| CONTEXT.md | Old CLI; “only base/fullstack”; phantom `reference_*` as required | **Rewritten** |
| CLAUDE.md | `forge [TARGET]`; `venv/` only; missing monorepo/neo | **Rewritten** |
| GEMINI.md | “PROPRIETARY — LOCAL REMOTES ONLY”; incomplete CLI | **Rewritten** |
| AI_DIRECTIVES.md | No neo hook / profile list | **Updated** |
| docs/AI_INSIGHTS.md | `forge . --update` | **Updated** |
| docs/features/* | Historical `forge .`, old managers, wrong profiles | **Rewritten** to current CLI (base/fullstack/monorepo, `--var manager`, neo flags); zero stale strings |
| docs/plans/archive/* | v2 design history | Left as archive (intentional) |
| README.md | Tree only showed single-package | **Added monorepo tree** |
| WORKFLOW.md | “strictly MVC” for Forge itself | **Softened** |

## Canonical doc set (use these)

1. [README.md](../README.md)  
2. [docs/README.md](./README.md)  
3. [creating-a-profile.md](./creating-a-profile.md)  
4. [profiles.md](./profiles.md)  
5. [related-projects.md](./related-projects.md)  
6. [monorepo-profile-scope.md](./monorepo-profile-scope.md)  
7. [reevaluation-2026-08.md](./reevaluation-2026-08.md)  

## Residual

- Feature specs under `docs/features/` are short outcome notes aligned to the 2026-08 CLI; prefer README + `docs/profiles.md` for day-to-day use.  
- Tutorial example profile name `api-service` in creating-a-profile.md is intentional (custom profile demo, not shipped).  
- Root `AI_DIRECTIVES` may still mention optional reference trees if operators add them.  

