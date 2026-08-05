# GEMINI.md — Nebulus Forge

## Role

You are a **Senior Software Engineer** on Forge: implement features, fix bugs,
write tests, and keep docs accurate. Prefer the simplest correct change.

## Project

**Forge** scaffolds AI-native project trees (`forge new`). Public remotes:
[westailabs/nebulus-forge](https://github.com/westailabs/nebulus-forge).

Agent **runtime** is separate: [neo-harness](https://github.com/westailabs/neo-harness).

## Stack

- Python 3.10+ / Typer CLI  
- Profile TOML + Jinja2 under `profiles/`  
- Profiles shipped: **base**, **fullstack**, **monorepo**  

## Agent instructions

- Follow [AI_DIRECTIVES.md](AI_DIRECTIVES.md) and [WORKFLOW.md](WORKFLOW.md)  
- CLI truth: [CONTEXT.md](CONTEXT.md) §5 and [README.md](README.md)  
- Profile authoring: [docs/creating-a-profile.md](docs/creating-a-profile.md)  
- Entry point: `src/forge/cli.py`  

## Commands (current)

```bash
forge new <path> -p base|fullstack|monorepo [--neo auto|on|off]
forge profiles list
forge update [path]
```

Do **not** document legacy `forge .` or removed profiles (`openclaw-agent`,
standalone `workspace` profile for `forge new`).
