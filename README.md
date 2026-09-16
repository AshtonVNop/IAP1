# IAP1
EECE-4081-002 Individual Project

Date Started: 8/31/26

Declared stack - 
Langauge: Python
IDE: VS Code
OS/Platform: macOS

Concept - 
Planner for college students
One paragraph concept brief - 
I would like to make a simple planner for college students to use. It will allow the user to add what they need to do, and allow them to put a due date to said objective. It will automatically organize the student's planner based on chronologic order. Example, if you add an obective that is due at 04:00 PM, but add an objective at 03:00 PM, the 3pm objective will be shown above the 04:00 PM. 

Toolchain -
Language runtime: python3
Package manager: pip
Test runner: pytest
version control: GitHub

## Current implementation

The planner currently includes:

- A `Task` domain model with a title and due date/time.
- A `Planner` that validates objectives and returns them in chronological order.
- A command-line interface for adding objectives and displaying the sorted planner.
- Pytest coverage for chronological ordering, equal deadlines, and empty titles.

## Run the planner

Activate the virtual environment and run:

```bash
source .venv/bin/activate
python app.py
```

Enter due dates using `YYYY-MM-DD HH:MM`. Enter `q` when you are finished adding objectives.

## Run tests

```bash
python -m pytest
```


USER STORY 1: Add Assignment with Deadline
  Story: As a college student, I want to add an assignment with a title and 
         due date/time, so that I can track my upcoming academic deadlines 
         in one place.
  Acceptance Criteria:
    - Given a non-empty title string and valid timestamp, when the user adds 
      a task, the system instantiates a Task entity and stores it in the planner.
    - Given an empty or whitespace-only title, when the user attempts to add a 
      task, the system raises a ValueError with the message "Task title cannot 
      be empty".
    - Given a valid task addition, the aggregate root automatically updates 
      internal state without crashing or corrupting existing tasks.

USER STORY 2: Chronological Schedule View
  Story: As a busy student, I want my task list automatically ordered from 
         earliest to latest deadline, so that I immediately know what item 
         requires my attention next.
  Acceptance Criteria:
    - Given multiple tasks added in arbitrary or reverse chronological order, 
      when the user queries planner.tasks(), the returned list is ordered 
      strictly by due_at ascending.
    - Given two tasks sharing identical due dates, the system maintains 
      deterministic ordering without raising comparison errors.
    - Given a planner with zero tasks, querying planner.tasks() returns an 
      empty list without throwing an exception.

USER STORY 3: Interactive CLI Parsing
  Story: As a terminal user, I want to enter task details using standard date 
         strings in the command line, so that I can rapidly input assignments 
         without writing Python code.
  Acceptance Criteria:
    - Given standard input format YYYY-MM-DD HH:MM, when entered into app.py, 
      the application parses the string into a valid native datetime object.
    - Given an unparseable timestamp string ("next Tuesday"), the 
      application displays a descriptive error message and re-prompts the 
      user without exiting the process.

USER STORY 4: Task Immutability
  Story: As a system developer, I want task objects to be immutable once created, 
         so that task state cannot be accidentally modified across application layers.
  Acceptance Criteria:
    - Given an instantiated Task object, attempting to modify task.title or 
      task.due at directly raises a dataclass.FrozenInstanceError.
    - Given a modified assignment requirement, changes must be made by 
      creating a new Task instance through Planner methods.

USER STORY 5: Automated Domain Testing
  Story: As a developer maintaining the codebase, I want an automated unit test 
         suite, so that I can verify domain invariants after every code change.
  Acceptance Criteria:
    - Given the test file test_planner.py, running pytest executes all test 
      cases and reports 100% pass status.
    - Given edge-case tests (e.g., empty titles, duplicate deadlines), all 
      assertions validate expected behavior without unhandled exceptions.

USER STORY 6: Terminal Task Display
  Story: As a user reviewing my day, I want tasks formatted clearly in the 
         console output, so that I can read assignment deadlines at a glance.
  Acceptance Criteria:
    - Given a list of scheduled tasks, each line printed to the console 
      displays the task title side-by-side with a formatted string timestamp.
    - Given a list query from app.py, tasks display in ascending order matching 
      planner.tasks().

NFR 1: Task Query Execution Latency
  - Requirement: Querying planner.tasks() on a collection of 1,000 Task objects 
    must execute in under 5.0 milliseconds total wall-clock time on standard 
    execution hardware (x86_64 / ARM64 processor, 2.0 GHz+).
  - Falsification Condition: If a benchmark script running 1,000 insertions 
    followed by planner.tasks() averages >= 5.0 ms across 100 test runs, the 
    requirement is falsified.

NFR 2: Unit Test Suite Execution Time & Coverage
  - Requirement: Executing pytest test_planner.py must complete in under 2.0 
    seconds total wall-clock time while achieving >= 95% line coverage of planner.py.
  - Falsification Condition: Running pytest --cov=planner test_planner.py that 
    takes >= 2.0s or yields < 95% coverage metric falsifies the requirement.

NFR 3: Zero External Package Dependencies
  - Requirement: The core domain module (planner.py) must rely strictly on standard 
    library imports (dataclasses, datetime) and contain zero third-party dependencies 
    in requirements.txt.
  - Falsification Condition: If planner.py requires installing any third-party 
    package via pip to run, the requirement is falsified.

PROMPT GIVEN TO AI:
"I am building a CLI student planner app in Python called Chronos. It takes task 
titles and due dates, stores them in a class, and outputs them sorted chronologically. 
Act as a business analyst and elicit functional and non-functional requirements 
for this app concept."

AI ELICITATION OUTPUT:
Functional Requirements:
  1. User Authentication: System must allow students to create accounts with email/password and log in securely.
  2. Task Creation & Categorization: Users can input task title, due date, course code, priority tag (High/Med/Low), and estimated completion time.
  3. Chronological Sorting: System sorts active tasks by due date ascending.
  4. Push Notifications: Send desktop/email notifications 2 hours before a task is due.
  5. Calendar Export: Export tasks to .ics format for Google Calendar / Apple Calendar sync.

Non-Functional Requirements:
  1. Security: Encrypt user passwords using bcrypt with a salt factor of 12.
  2. Usability: The CLI must feature full color-coded terminal outputs using Rich/Colorama.
  3. Persistence: Store all tasks in a PostgreSQL relational database with automatic daily backups.

WHAT THE MODEL MISSED:
  - Domain Invariants & Error Validation: Failed to elicit validation constraints 
    (e.g., rejecting blank task titles, handling malformed datetime input strings, 
    or enforcing immutable dataclass structures).
  - Decoupled Architecture: Overlooked the separation between presentation 
    (app.py) and domain logic (planner.py), assuming functionality sits in a 
    monolithic script.
  - Automated Testing Requirements: Omitted requirements regarding unit testing 
    suites (pytest) and domain test coverage metrics.

WHAT THE MODEL INVENTED (UNWANTED / OUT OF SCOPE):
  - User Authentication & Multi-Tenancy: Invented login/password accounts and 
    bcrypt password encryption, adding unnecessary complexity to a lightweight CLI tool.
  - Database Infrastructure: Invented a full PostgreSQL relational database setup 
    with daily backups, violating the design constraint of an in-memory Python architecture.
  - Cloud Push Notifications: Added email/push notification infrastructure 
    requiring background worker processes and external SMTP server integrations.

WHAT THE MODEL GOT RIGHT (INSIGHTFUL / FUTURE VALUE):
  - Calendar (.ics) Export: Exporting scheduled tasks to standard .ics format for 
    syncing with Google Calendar or Apple Calendar is a practical feature for Version 2.0.
  - Course Code & Tags: Tagging tasks by course name or estimated duration provides 
    useful metadata for organizing university assignments.
  - Color-Coded Terminal UI: Using terminal styling tools (like rich) improves 
    readability when scanning deadlines in a CLI environment.
