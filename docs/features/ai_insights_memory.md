# Feature: AI_INSIGHTS long-term memory file

## Overview

Scaffolds include `docs/AI_INSIGHTS.md` (or monorepo-equivalent durable notes)
so agents record project-specific lessons.

## Outcome (current)

- **base** / **fullstack**: template under `profiles/base/templates/docs/AI_INSIGHTS.md.j2`
- **monorepo**: durable notes live under `docs/` taxonomy; operators may add
  `docs/AI_INSIGHTS.md` manually or extend the profile later
- Agent docs encourage reading and updating insights files when present

## Acceptance (met)

- [x] base/fullstack generate an insights file path for agents
- [x] Mandate language points agents at long-term memory, not only chat context
