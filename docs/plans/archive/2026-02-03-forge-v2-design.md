# Forge v2 — Design Document

**Date**: 2026-02-03
**Branch**: `feat/v2-rewrite`
**Status**: Approved

---

## 1. Scope and Goals

### What we're building

A rewrite of Forge as a profile-driven project lifecycle manager. The core loop is: **generate → track → update**.

### What's in scope for v2.0

- Pipeline engine (resolve → merge → render → apply → lock)
- Profile-as-data format (TOML + Jinja2 directories)
- Profile inheritance (`base` → `fullstack`)
- `.forge.lock` for tracking generated state
- Smart `--update` using lock file diffing (add / safe-update / skip / warn)
- `--dry-run` mode
- Typer CLI
- Interactive wizard (carry forward from v1, adapted to Typer)
- Test suite covering each pipeline stage independently

### What's explicitly out of scope for v2.0

- Remote profile sources (`gh:user/repo/profile`) — local paths only for now
- Profile registry or discovery
- Migration tooling from v1-generated projects
- Web/system/mvc profiles — added after fullstack proves the architecture
- Plugin system

### Success criteria

- `forge new my-project` generates a fullstack project identical in quality to v1 output
- `forge update my-project` uses the lock file to intelligently add/update/skip
- Every pipeline stage is independently testable with no filesystem side effects (except `apply_to_disk`)
- A new profile can be created by copying a directory and editing TOML — no Python required

---

## 2. Project Structure

```
forge/
├── pyproject.toml
├── README.md
├── CLAUDE.md
├── profiles/                     # Profile data (not Python code)
│   ├── base/
│   │   ├── profile.toml          # name, description, variables
│   │   ├── structure.toml        # directories + file mappings
│   │   └── templates/
│   │       ├── README.md.j2
│   │       ├── .gitignore.j2
│   │       ├── pyproject.toml.j2
│   │       ├── AI_DIRECTIVES.md.j2
│   │       ├── CONTEXT.md.j2
│   │       ├── WORKFLOW.md.j2
│   │       ├── GEMINI.md.j2
│   │       ├── .flake8.j2
│   │       ├── .pre-commit-config.yaml.j2
│   │       └── ...              # shared governance/config templates
│   └── fullstack/
│       ├── profile.toml          # inherits = "base"
│       ├── structure.toml        # adds notebooks/, models/, ansible/
│       └── templates/
│           ├── Dockerfile.j2
│           ├── docker-compose.yml.j2
│           └── ...              # fullstack-specific templates only
├── src/
│   └── forge/
│       ├── __init__.py
│       ├── cli.py                # Typer app, thin — just gathers input
│       ├── wizard.py             # Interactive prompts (questionary)
│       ├── pipeline.py           # The six-step pipeline
│       ├── models.py             # Pydantic models (ProfileSpec, ResolvedProfile, etc.)
│       ├── profile_loader.py     # Reads TOML, resolves inheritance
│       ├── renderer.py           # Jinja2 rendering logic
│       ├── applier.py            # Writes to disk (create/update/force)
│       ├── lockfile.py           # .forge.lock read/write/diff
│       └── git_ops.py            # Git init + initial commit
├── tests/
│   ├── test_pipeline.py          # Integration: full pipeline
│   ├── test_profile_loader.py    # Unit: TOML parsing, inheritance
│   ├── test_renderer.py          # Unit: Jinja2 rendering
│   ├── test_applier.py           # Unit: file writing strategies
│   ├── test_lockfile.py          # Unit: lock file operations
│   ├── test_cli.py               # CLI argument handling
│   └── test_wizard.py            # Interactive prompts
└── scripts/
    └── run_tests.sh
```

Key differences from v1:

- **`profiles/` is a top-level directory**, not Python code inside `src/`
- **`src/forge/`** not `src/project_generator/` — shorter, matches the CLI name
- **Each module has a single responsibility** — no 375-line constants files
- **`models.py` uses Pydantic** — validates profile data at load time, not at runtime failures
- **Tests mirror the pipeline** — one test file per stage

---

## 3. Data Formats

### profile.toml

The identity card for a profile. Base profile:

```toml
[profile]
name = "base"
description = "Common foundation for all Forge projects"

[variables]
project_name = { prompt = "Project name", type = "string" }
author_name = { prompt = "Author name", type = "string", default = "" }
author_email = { prompt = "Author email", type = "string", default = "" }
description = { prompt = "Project description", type = "string", default = "" }
python_version = { prompt = "Minimum Python version", type = "choice", choices = ["3.10", "3.11", "3.12"], default = "3.10" }
manager = { prompt = "Package manager", type = "choice", choices = ["pip", "poetry", "uv"], default = "pip" }
```

Fullstack profile inherits and extends:

```toml
[profile]
name = "fullstack"
inherits = "base"
description = "Full-stack AI system with notebooks, models, and Ansible"

[variables]
persona = { prompt = "AI persona", type = "choice", choices = ["standard", "architect", "developer"], default = "standard" }
use_docker = { prompt = "Include Docker support?", type = "confirm", default = true }
```

The wizard auto-generates prompts from this. No Python code needed to add a new variable.

### structure.toml

Declares what gets created. Base:

```toml
[directories]
root = [
    "src/{{ project_slug }}",
    "tests",
    "docs",
    "scripts",
    ".agent/rules",
]

[files]
"README.md" = "README.md.j2"
".gitignore" = ".gitignore.j2"
"pyproject.toml" = "pyproject.toml.j2"
"AI_DIRECTIVES.md" = "AI_DIRECTIVES.md.j2"
"CONTEXT.md" = "CONTEXT.md.j2"
"WORKFLOW.md" = "WORKFLOW.md.j2"
"GEMINI.md" = "GEMINI.md.j2"
".flake8" = ".flake8.j2"
".yamllint" = ".yamllint.j2"
".pre-commit-config.yaml" = ".pre-commit-config.yaml.j2"
"requirements.txt" = "requirements.txt.j2"
"requirements-dev.txt" = "requirements-dev.txt.j2"
"src/{{ project_slug }}/__init__.py" = "__init__.py.j2"
"tests/__init__.py" = "__init__.py.j2"
```

Fullstack only declares what it adds:

```toml
[directories]
root = [
    "notebooks",
    "models",
    "data",
    "ansible",
]

[files]
"Dockerfile" = "Dockerfile.j2"
"docker-compose.yml" = "docker-compose.yml.j2"
"ansible/site.yml" = "ansible/site.yml.j2"
"mkdocs.yml" = "mkdocs.yml.j2"

[conditionals]
"Dockerfile" = "use_docker"
"docker-compose.yml" = "use_docker"
```

The `[conditionals]` section keeps conditional logic declarative. If `use_docker` is false, those files are not rendered.

### .forge.lock

Written into the generated project:

```toml
[forge]
version = "2.0.0"
profile = "fullstack"
generated_at = "2026-02-03T14:30:00Z"

[variables]
project_name = "my-project"
manager = "poetry"
persona = "architect"
use_docker = true

[files.managed]
"README.md" = { template = "README.md.j2", hash = "a1b2c3d4" }
"pyproject.toml" = { template = "pyproject.toml.j2", hash = "e5f6a7b8" }
".gitignore" = { template = ".gitignore.j2", hash = "c9d0e1f2" }
```

### Update algorithm

| Lock hash vs disk | Action |
|:---|:---|
| Matches disk | File unmodified by user. Safe to overwrite with new version. |
| Differs from disk | User customized this file. **Skip**, warn in output. |
| File missing from lock, exists on disk | New in profile. **Add** it. |
| File in lock, missing from disk | User deleted it intentionally. **Skip**. |

---

## 4. Pipeline Implementation

### models.py — Data types

```python
class VariableSpec(BaseModel):
    prompt: str
    type: Literal["string", "choice", "confirm"]
    default: str | bool | None = None
    choices: list[str] | None = None

class ProfileSpec(BaseModel):
    name: str
    description: str
    inherits: str | None = None
    variables: dict[str, VariableSpec]
    directories: list[str]
    files: dict[str, str]           # output_path → template_name
    conditionals: dict[str, str]    # output_path → variable_name
    template_dir: Path

class ResolvedProfile(BaseModel):
    name: str
    description: str
    variables: dict[str, VariableSpec]
    directories: list[str]
    files: dict[str, str]
    conditionals: dict[str, str]
    template_dirs: list[Path]       # ordered: [profile, base] for fallback

class RenderedFile(BaseModel):
    output_path: str
    content: str
    template_name: str
    content_hash: str

class ApplyResult(BaseModel):
    created: list[str]
    updated: list[str]
    skipped: list[str]
    warnings: list[str]
```

### profile_loader.py — Steps 1 and 2

```
resolve_profile(name, profiles_dir) → ProfileSpec
merge_inheritance(profile, profiles_dir) → ResolvedProfile
```

Resolution reads `profile.toml` and `structure.toml`, validates into `ProfileSpec`. Inheritance walks the chain, merging:

- **Variables**: child overrides parent
- **Directories**: union of both lists
- **Files**: child overrides parent
- **Conditionals**: child overrides parent
- **Template dirs**: ordered list, child first

Circular inheritance detected and raises immediately.

### renderer.py — Step 3

```
render_templates(profile, variables) → list[RenderedFile]
```

No side effects. Takes resolved profile and user variables, renders every Jinja2 template in memory, returns `RenderedFile` objects with content hashes.

Conditionals evaluated here — falsy variables cause the file to be excluded entirely.

Template lookup walks `template_dirs` in order. First match wins.

### applier.py — Step 4

```
apply_to_disk(files, target, strategy, lock=None) → ApplyResult
```

Three strategies:

- **`create`** — fresh project, write everything
- **`update`** — requires `.forge.lock`, uses hash comparison
- **`force`** — write everything regardless

### lockfile.py — Step 5

```
write_lock(result, profile, variables, target) → None
read_lock(target) → ForgeLock | None
diff_lock(old_lock, new_files) → list[FileAction]
```

`diff_lock` compares old lock against newly rendered files and returns actions. The applier executes them.

### pipeline.py — Orchestration

```python
def generate(profile_name, target, variables, strategy, profiles_dir):
    profile = resolve_profile(profile_name, profiles_dir)
    resolved = merge_inheritance(profile, profiles_dir)
    rendered = render_templates(resolved, variables)

    lock = read_lock(target) if strategy == Strategy.UPDATE else None
    result = apply_to_disk(rendered, target, strategy, lock)
    write_lock(result, resolved, variables, target)

    return result
```

---

## 5. CLI Design

```
forge new <target> [--profile] [--manager] [--no-interactive] [--dry-run]
forge update <target> [--force]
forge info <target>            # reads .forge.lock
forge profiles list            # shows available profiles
forge profiles show <name>     # shows profile details
```

`new` and `update` are explicit subcommands. `--dry-run` runs the full pipeline through rendering but prints what would happen instead of writing.

The wizard activates by default on `forge new` (unless `--no-interactive`). It reads variables from the resolved profile and generates prompts automatically.

---

## 6. Testing Strategy

### test_profile_loader.py

- Loads valid profile into ProfileSpec
- Rejects missing required fields
- Rejects invalid variable types
- Merges single-level inheritance
- Child variables override parent
- Child files override parent
- Directories are unioned
- Template dirs ordered [child, parent]
- Detects circular inheritance
- Handles base profile (no parent)

### test_renderer.py

- Renders simple template with variables
- Template lookup: child dir before parent
- Missing template in child falls back to parent
- Missing template in both raises error
- Conditionals: file excluded when variable falsy
- Conditionals: file included when variable truthy
- Jinja2 variables in output paths
- Content hash deterministic for same input

### test_applier.py

- Create: writes all files and directories
- Create: errors on existing conflicting files
- Create + force: overwrites existing
- Update: adds new files not in lock
- Update: updates unmodified files (hash matches)
- Update: skips user-modified files (hash differs)
- Update: skips user-deleted files
- Update: warns about deprecated files
- Directories with Jinja2 variables created correctly

### test_lockfile.py

- Write then read: data matches
- Read missing lock returns None
- diff_lock: detects new files to add
- diff_lock: detects updatable files
- diff_lock: detects user-modified files to skip
- diff_lock: detects removed files to warn

### test_pipeline.py

- Full generate: expected directory structure
- Full generate: .forge.lock exists and valid
- Generate then update: new files added
- Generate then update: user changes preserved
- Dry run: renders but writes nothing

### test_cli.py

- `forge new` with flags
- `forge new` with wizard (mocked)
- `forge update` with lock file
- `forge update` without lock file (error)
- `forge info` shows profile and variables
- `forge profiles list` shows profiles
- `--dry-run` produces output, no files

### test_wizard.py

- Generates prompts from profile variables
- String → text prompt
- Choice → select prompt
- Confirm → yes/no prompt
- Defaults respected when skipped

---

## 7. Build Sequence

### Phase 1 — Foundation

**Step 1: Project skeleton + models**
- Create branch `feat/v2-rewrite`
- Set up `pyproject.toml` with Typer, Pydantic, Jinja2, questionary
- Write `models.py` with all Pydantic models
- Tests for model validation

**Step 2: Profile loader**
- Create `profiles/base/` with `profile.toml`, `structure.toml`, and templates
- Write `profile_loader.py` — TOML parsing into ProfileSpec
- Tests for loading and validation
- No inheritance yet

**Step 3: Renderer**
- Write `renderer.py` — Jinja2 rendering, template lookup, conditionals, hashing
- Tests for rendering
- At this point: load a profile and render in memory

**Step 4: Applier + lock file**
- Write `applier.py` — create strategy only
- Write `lockfile.py` — write and read
- Tests for both
- At this point: `forge new` works end to end

### Phase 2 — Full Pipeline

**Step 5: Pipeline + CLI**
- Write `pipeline.py` — orchestration function
- Write `cli.py` — Typer app with `new` command, `--dry-run`, `--no-interactive`
- Integration and CLI tests
- **Milestone: `forge new my-project --profile fullstack` works**

**Step 6: Wizard**
- Write `wizard.py` — auto-generate prompts from profile variables
- Wire into CLI
- Tests for wizard

**Step 7: Inheritance**
- Create `profiles/fullstack/` inheriting from base
- Add inheritance merging to profile_loader.py
- Update tests
- **Milestone: two-layer profiles work**

### Phase 3 — Update Lifecycle

**Step 8: Smart update**
- Add update strategy to applier.py
- Add `diff_lock` to lockfile.py
- Add `forge update` command
- Update-specific tests
- **Milestone: `forge update` works with lock file diffing**

**Step 9: Info and profile commands**
- Add `forge info` and `forge profiles list/show`
- Wire git_ops.py for optional git init

**Step 10: Polish**
- Carry over v1 templates to profile directories
- Verify generated output matches v1 quality
- Update CLAUDE.md, README, docs
- **Milestone: v2 feature-complete, matches v1 output**
