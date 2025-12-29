# Feature Title: Documentation Site Generator

## Overview
The `docs/` folder structure is excellent for version control, but less accessible for non-technical stakeholders. We want to auto-generate a static documentation site using `mkdocs` to make reading the documentation easier.

## Requirements
List the specific requirements for this feature:
- [ ] Generate `mkdocs.yml` in the project root.
- [ ] Configure `mkdocs-material` theme by default.
- [ ] Add a GitHub Action workflow `docs.yml` to deploy to GitHub Pages on push to `main`.
- [ ] Include `docs/features/*` in the navigation automatically.

## Technical Implementation (Optional)
If you have specific ideas about how this should be built, list them here:
- Proposed modules: `src/project_generator/assets/templates.py`.
- Dependencies: Add `mkdocs` and `mkdocs-material` to `requirements-dev.txt`.
- Data changes: None.

## Acceptance Criteria
How will we know this is working correctly?
- [ ] `mkdocs serve` runs without errors immediately after project generation.
- [ ] The site displays the `README.md` as the home page.
- [ ] Feature files are listed in the side navigation.

## Feedback/Notes
Keep it optional (`--with-docs-site`) to avoid bloat for small projects? Or enable by default for "Production Grade"? Let's verify size impact.
