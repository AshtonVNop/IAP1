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

## Walking skeleton and CI prompt and diff

### Prompt used

> Implement and verify one thin end-to-end slice of the existing college student planner without changing its in-memory storage decision. Add a real CLI integration test that submits tasks, exercises the planner, and verifies chronological output. Configure GitHub Actions to run the test suite and document this work in the prompt-and-diff log.

### Diff summary

- Added [test_app.py](../../test_app.py), which starts the actual CLI as a subprocess, submits two tasks in reverse deadline order, and verifies the displayed planner sorts them chronologically.
- Added [ci.yml](../../.github/workflows/ci.yml), which installs pytest and runs the complete suite on pushes, pull requests, and manual dispatches.
- Added [walking-skeleton.svg](../evidence/walking-skeleton.svg), a terminal-style rendering of the successful real CLI output; the environment has no capturable display for a desktop screenshot.
- Kept the existing in-memory `Planner` collection as the storage layer, consistent with [ADR-001](../adr/ADR-001-in-memory-planner-state.md); no canned data or alternate persistence was introduced.


## M7 behaviour-preserving refactor prompt and diff

### Prompt used

> Improve the internal structure of your app without changing what it does, and prove that is what happened. Identify something in your codebase that is genuinely worse than it should be. Name the smell. Refactor it. Run the same tests before and after. They must pass both times, unchanged. Write a short note: what was wrong, what you did, and what is now easier. Evidence: before-and-after diff, test output from before and after, the written note, prompt-and-diff log.

### What the AI did with the prompt

1. Read all source, test, and docs files, and committed the untouched project as a git baseline (`fbf7efb`).
2. Named the smell: `read_task()` in `app.py` mixed responsibilities and hard-wired console I/O. It did prompting, quit detection, parsing, the domain call, and printing, then returned a boolean continue-flag (a CQS violation), leaving no seam for testing.
3. Ran `python -m pytest -v` **before** changing any code and recorded the test-file SHA-256 checksums.
4. Refactored `app.py` only. `planner.py` and both test files are unchanged.
5. Re-ran the identical command **after**, confirmed the checksums match, and confirmed `git diff` on the test files is empty.
6. Ran an extra 13-scenario before/after stdout comparison, plus a deliberate one-character change to show the comparison can catch a difference.

### Diff summary

- `app.py`: replaced `read_task` and `display_tasks` with `prompt_for_task`, `submit_task`, `format_task`, `render_planner`, and `run_session`; injected `read`/`write` (defaulting to `input`/`print`); added a `QUIT_COMMAND` constant; reduced `main()` to one call. Full diff: [refactor.diff](../refactor/refactor.diff).
- Added evidence under [docs/refactor/](../refactor/): `test-output-before.txt`, `test-output-after.txt`, `cli-equivalence-check.txt`, `compare_cli.py`, and [refactor-note.md](../refactor/refactor-note.md).
- No change to user-visible behaviour: same prompts, messages, ordering, exit codes.

### What I checked / kept from the AI output

- The AI first suggested an alternative: moving title validation into `Task.__post_init__`. It was rejected because `Task("  ", ...)` currently succeeds, so that change would alter behaviour rather than restructure code.
- Tests that use the new seams were deliberately left for a later milestone so the test set stays identical across the before and after runs.


## Web interface prompt and diff

### Prompt used

> Do you think you could make run as a website instead?

### Diff summary

- Added [web.py](../../web.py): a local website built on the standard library's `http.server` (no new dependencies). It holds one in-memory `Planner` (consistent with [ADR-001](../adr/ADR-001-in-memory-planner-state.md)) and adds tasks through `app.submit_task`, the function extracted in the M7 refactor. Validation and error messages therefore match the CLI exactly. The browser's `2026-09-12T15:00` value is converted to the CLI's `YYYY-MM-DD HH:MM` format before parsing.
- The page lists tasks earliest first, grouped by day, marks the next upcoming task and overdue tasks, escapes titles to prevent HTML injection, and redirects after a successful add so a refresh does not add a task twice.
- Added [test_web.py](../../test_web.py) with 5 tests: form-to-CLI path, blank-title rejection, HTML escaping, and two end-to-end tests against a real server on a free port.
- `app.py`, `planner.py`, and the existing tests are unchanged; the CLI still works as before.
