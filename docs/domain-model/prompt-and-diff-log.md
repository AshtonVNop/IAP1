# Prompt-and-Diff Log

## Source requirements

The workspace contains no separate M2 requirements document. The prompt was based on the concept brief in the README: a simple college-student planner lets a user add objectives with due dates and automatically organizes them chronologically. The app code and tests were consulted afterward to critique behavior details, not to expand the stated requirements.

## Prompt used for the first draft

> Draft a domain model for the college student planner described in the project requirements. Include likely entities, important attributes, and relationships. Show it as a Mermaid class diagram and briefly explain the model.

The complete first response, including its diagram, is preserved unedited in [ai-first-draft.md](ai-first-draft.md).

## Prompt used for the corrected model and critique

> Compare the saved first draft against the README concept brief and the current implementation. Keep only entities and relationships supported by the app's scope. Identify what the first draft got right, over-modelled, guessed without evidence, and under-modelled. Produce a concise Mermaid class diagram for the corrected model.

## Model diff

| First draft | Corrected model | Reason |
| --- | --- | --- |
| `User`, `Role`, `Permission` | Removed | No accounts, access control, or role behavior in requirements or implementation. |
| `Category`, `AuditLog`, `Settings` | Removed | No categories, audit trail, or preferences are requested or implemented. |
| `Planner` and `Task` | Kept | Directly represented in the code; planner holds the task collection. |
| IDs, description, status, priority, timestamps, category, preferences | Removed | No supported behavior or persistence needs these attributes. |
| Task title and due date/time | Kept as `title` and `due_at` | These are the objective and deadline described in the brief and used by the program. |
| Generic planner contains task relationship | Made explicit as in-memory directed association | Captures the actual collection without suggesting persistence or user ownership. |
| No ordering or validation rules | Added chronological ordering and title constraint | These define implemented behavior: sorted by `due_at`; blank titles are rejected after trimming. |
| No equal-deadline rule | Added stable addition-order note | Confirmed by the ordering implementation and test. |

## ADR-001 prompt and diff

### Prompt used

> Write one architecture decision record for one real decision actually made in this app. Ground the decision in the current implementation and project scope. Include context, the decision, alternatives considered, and consequences, including what the decision makes harder. Save it as `docs/adr/ADR-001-in-memory-planner-state.md`.

### Diff summary

- Added [ADR-001](../adr/ADR-001-in-memory-planner-state.md), recording the existing choice to keep planner tasks in memory for the current single-session CLI scope.
- Considered JSON-file and SQLite persistence as alternatives, and documented the cost of lost tasks at process exit and the work a later persistence requirement would introduce.
- No application code or behavior was changed.
