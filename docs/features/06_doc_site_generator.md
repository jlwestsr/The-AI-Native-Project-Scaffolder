# Feature Title: Documentation Site Generator

## Overview
The `docs/` folder structure is excellent for version control, but less accessible for non-technical stakeholders. We want to auto-generate a static documentation site using `mkdocs` to make reading the documentation easier.

## Requirements
List the specific requirements for this feature:
- [x] Generate `mkdocs.yml` in the project root.
- [x] Configure `mkdocs-material` theme by default.
- [x] Add a GitHub Action workflow `docs.yml` to deploy to GitHub Pages on push to `main`.
- [x] Include `docs/features/*` in the navigation automatically.

## Technical Implementation (v2)
- **Templates**: `mkdocs.yml.j2` and related templates in `profiles/base/templates/` or `profiles/fullstack/templates/`.
- **Conditionals**: Can be gated by a profile variable (e.g., `use_docs_site`) in `structure.toml`.
- **Pipeline**: Rendered and applied through the standard `renderer.py` → `applier.py` pipeline.
- **Dependencies**: `mkdocs` and `mkdocs-material` included in generated project's dev requirements template.

## Acceptance Criteria
How will we know this is working correctly?
- [x] `mkdocs serve` runs without errors immediately after project generation.
- [x] The site displays the `README.md` as the home page (via `docs/index.md` linking/referencing).
- [x] Feature files are listed in the side navigation.

## Feedback/Notes
Keep it optional (`--with-docs-site`) to avoid bloat for small projects? Or enable by default for "Production Grade"? Let's verify size impact.
