# Critique of the AI First Draft

The comparison uses the project concept brief in the README as the stated requirements. The current implementation and tests are used only to check how the built program realizes that brief; they are not treated as extra assignment requirements.

## Where the draft was right

- `Task` is the central domain concept. A task/objective needs a title and a due date and time.
- A `Planner` groups tasks and presents them in chronological order.
- The planner-to-task relationship is one planner holding zero or more tasks in this program.

## Where it over-modelled

The draft adds `User`, `Role`, `Permission`, `Category`, `AuditLog`, and `Settings`, as well as identity, email, descriptions, status, priority, timestamps, notification settings, and view preferences. Neither the concept brief nor the program has accounts, authorization, categorization, auditing, notifications, persistence, or a task lifecycle. Those additions turn a small in-memory deadline list into a multi-user platform without evidence or need.

## Where it guessed relationships

The user-to-planner ownership, user-to-role assignment, role-to-permission grants, task-to-category assignment, user-generated audit entries, and user-owned settings are all invented. The app has a single interactive CLI session, not a `User` concept or any of those connections. Even the proposed one-planner-per-user cardinality has no basis in the requirements.

The draft's `Planner`-to-`Task` relationship is the one supported relationship: the code stores tasks in a planner's collection. The corrected diagram uses a directed association to express that the planner holds tasks in memory, without implying database persistence.

## What it under-modelled

The first draft lists many task attributes but misses the behavior that defines this app: task ordering by due date/time. It also misses the actual input invariant that a title is trimmed and cannot be empty. Equal deadlines preserve addition order in the implementation and are covered by a test. These are important model rules, while the draft's `status`, `completedAt`, and `priority` fields have no corresponding behavior.

## Conclusion

The corrected model keeps only `Planner` and `Task`. It captures the collection relationship, title and due-time data, chronological presentation, and the observed title/tie-order constraints. No separate user, category, settings, permission, or audit entity is justified by the stated scope.
