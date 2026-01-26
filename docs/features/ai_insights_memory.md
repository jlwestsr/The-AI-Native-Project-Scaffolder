# Feature Title: AI Project Memory (AI_INSIGHTS.md)

## Overview
This feature introduces a standardized `docs/AI_INSIGHTS.md` file to every project. This file serves as the project's "Long Term Memory," capturing architectural nuances, non-functional requirements (like model parameter thresholds), and "lessons learned" that are specific to the AI's interaction with the codebase.

The goal is to prevent future agents (or humans) from relearning known pitfalls (e.g., "This project requires a 30B model to avoid bureaucracy").

## Requirements
- [ ] **Standard File**: Every project must have `docs/AI_INSIGHTS.md` initialized.
- [ ] **Agent Mandate**: The system prompt or project context must explicitly encourage agents to read and *update* this file.
- [ ] **Structure**: The file should capture:
    -   **Date**: When the insight was learned.
    -   **Insight**: The core finding (e.g., "Small models struggle with negative constraints").
    -   **Action**: What changed in the project because of this (e.g., "Upgraded to 30B," "Added Telemetry").

## Technical Implementation (Optional)
- **Scaffolder Update**: Update the project creation logic (`src/...`) to generate `docs/AI_INSIGHTS.md` with an initial template.
- **Template Content**:
    ```markdown
    # AI Insights & Lessons Learned
    This document captures the nuances, architectural decisions, and "lessons learned" regarding the AI's behavior within this project.
    
    **Project Mandate**: Future AI agents working on this project are **explicitly encouraged** to recommend, document, or append new insights to this file.
    ```

## Acceptance Criteria
- [ ] `docs/AI_INSIGHTS.md` is present in newly scaffolded projects.
- [ ] The file contains the "Project Mandate" section.
- [ ] New agents can read this file to understand historical context without re-deriving it.

## Feedback/Notes
Inspired by work on `Mini-Nebulus` where we discovered massive autonomy differences between 7B and 30B models and needed a place to document that decision permanently.
