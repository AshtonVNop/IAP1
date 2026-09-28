# ADR-001: Keep Planner State In Memory

- Status: Accepted
- Date: 2026-09-28

## Context

The app is a small, single-user command-line planner. Its stated job is to accept objectives with due dates and display them in chronological order. The current `Planner` owns a Python list of `Task` objects; tasks exist only for the lifetime of that planner instance. The CLI creates one planner when it starts and displays its tasks when the user quits.

Durable storage was a plausible alternative: it would let a student resume a planner after closing the program. It would also expand this app beyond the brief's single-session workflow and introduce file or database behavior that the current domain model and tests do not need.

## The Decision

Keep planner state in memory for this version. A `Planner` instance owns its task collection, and the app does not read or write tasks to durable storage. Chronological ordering remains a domain operation over that collection.

## Alternatives Considered

- **Persist tasks as JSON.** This would preserve a user's planner across runs with little infrastructure, but requires choosing a file location and defining serialization, file error, and compatibility behavior.
- **Store tasks in SQLite.** This would provide durable structured storage and room for queries, but brings a schema and migration lifecycle that the current single-user, single-session app does not require.
- **Keep the current in-memory collection.** This is the selected option: it supports the implemented add-and-sort workflow without storage configuration, I/O failure handling, or a persistence dependency.

## Consequences

- The app remains small: the domain model has no storage API, file format, database schema, or persistence setup to maintain.
- The planner is straightforward to test because each test can create a fresh `Planner` without filesystem or database cleanup.
- **Tasks are lost when the process exits.** Users cannot close the app and resume their list, and there is no recovery after a crash. This is an accepted limitation, not an accidental guarantee of persistence.
- The app cannot share planner state between processes or devices. Adding multi-user or synchronized access would require a different storage and ownership design.
- Adding persistence later will require choosing stable task identity and a serialization/schema contract, handling read/write failures and existing data, and extending tests beyond the current in-memory behavior. The `Task` data class is a useful starting point, but it is not itself a persistence boundary.
- The decision should be revisited if the product requirement changes to resume work across runs, back up tasks, or share them across users or devices.
