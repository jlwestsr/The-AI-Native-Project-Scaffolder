# Feature: Documentation site (mkdocs)

## Overview

**fullstack** scaffolds can include MkDocs config for a static docs site.

## Outcome (current)

- Templates live under the **fullstack** profile (e.g. `mkdocs.yml.j2`).
- Base/monorepo focus on vault-style `docs/` trees without requiring MkDocs.
- CI templates may include docs workflows where the profile ships them.

```bash
forge new ~/projects/app -p fullstack --no-interactive --var project_name=app
# then in the generated project, if mkdocs is present:
# pip install mkdocs mkdocs-material && mkdocs serve
```

## Acceptance (met)

- [x] fullstack can emit mkdocs-related files via profile templates
- [x] base/monorepo remain usable without a docs site toolchain
